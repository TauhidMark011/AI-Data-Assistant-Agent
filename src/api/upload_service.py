#This module will handle file validation and storage.
import csv
import logging
import uuid

from io import StringIO
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile

from src.api.config import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE,
    UPLOAD_DIR,
)

logger = logging.getLogger(__name__)


def parse_and_normalize_csv(content: bytes) -> tuple[pd.DataFrame, bytes]:
    """
    Parse a CSV using supported encodings and delimiters.

    Values are initially loaded as strings to avoid premature
    type inference. The resulting dataset is serialized into
    a standard UTF-8, comma-separated CSV for downstream tools.
    """

    #Try UTF-8 (including BOM) first, followed by common
    #legacy Windows encoding used by many real-world datasets.
    decoded_content = None

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            decoded_content = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if decoded_content is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported or invalid CSV text encoding.",
        )

    #Detect common CSV delimiters instead of assuming commas.
    try:
        dialect = csv.Sniffer().sniff(
            decoded_content[:8192],
            delimiters=",;\t|",
        )
        delimiter = dialect.delimiter

    except csv.Error:
        #Use comma as the default when automatic detection
        #cannot confidently identify a delimiter.
        delimiter = ","

    try:
        #Preserve original cell values during ingestion.
        #Avoid interpreting empty strings or identifiers as numbers.
        df = pd.read_csv(
            StringIO(decoded_content),
            sep=delimiter,
            dtype=str,
            keep_default_na=False,
            na_filter=False,
            skip_blank_lines=False,
        )

    except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid readable CSV.",
        ) from exc

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="The CSV contains no data rows.",
        )

    if len(df.columns) == 0:
        raise HTTPException(
            status_code=400,
            detail="The CSV contains no columns.",
        )

    #Standardize the file format for existing downstream tools.
    #This changes serialization, not the intended cell values.
    normalized_content = df.to_csv(
        index=False,
        sep=",",
    ).encode("utf-8")

    return df, normalized_content

async def save_uploaded_csv(file: UploadFile) -> dict:
    """Validate and safely store an uploaded CSV file."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the maximum allowed size of 10 MB.",
        )

    #Parse the uploaded CSV and normalize it for downstream processing.
    df, normalized_content = parse_and_normalize_csv(content)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_id = uuid.uuid4().hex
    stored_filename = f"{file_id}.csv"
    stored_path = UPLOAD_DIR / stored_filename

    try:
        stored_path.write_bytes(normalized_content)

    except OSError as exc:
        logger.exception("Failed to store uploaded CSV.")
        raise HTTPException(
            status_code=500,
            detail="Unable to store the uploaded file.",
        ) from exc

    logger.info(
        "CSV uploaded successfully: %s (%s rows, %s columns)",
        stored_filename,
        len(df),
        len(df.columns),
    )

    return {
        "file_id": file_id,
        "original_filename": Path(file.filename).name,
        "stored_filename": stored_filename,
        "file_path": str(stored_path.resolve()),
        "rows": len(df),
        "columns": len(df.columns),
        "status": "uploaded",
    }


def resolve_uploaded_file(file_id: str) -> Path:
    """
    Resolve a server-stored CSV using its unique file ID.

    Only valid UUID-based file IDs are accepted. The resolved
    path must remain inside the configured upload directory,
    and the corresponding file must exist.
    """

    #Validate the identifier before constructing a filesystem path.
    try:
        validated_file_id = uuid.UUID(hex=file_id)

        #Accept only the canonical 32-character hexadecimal UUID.
        if validated_file_id.hex != file_id.lower():
            raise ValueError("Invalid file ID format.")

    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid file ID.",
        ) from exc

    #Resolve the upload directory and construct the stored CSV path.
    upload_dir = UPLOAD_DIR.resolve()
    stored_path = (upload_dir / f"{validated_file_id.hex}.csv").resolve()

    #Ensure the resolved file is inside the configured upload directory.
    if stored_path.parent != upload_dir:
        raise HTTPException(
            status_code=400,
            detail="Invalid file location.",
        )

    #Return 404 when the requested uploaded file does not exist.
    if not stored_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded CSV file not found.",
        )

    return stored_path

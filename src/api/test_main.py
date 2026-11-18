
from fastapi.testclient import TestClient
import pytest
from src.api.main import app
from src.api import upload_service
from pathlib import Path
import uuid

from unittest.mock import Mock
from fastapi import HTTPException

client = TestClient(app)

def test_health_endpoint_returns_200():
    """Verify that the health endpoint returns HTTP 200."""

    response = client.get("/health")

    assert response.status_code == 200

def test_health_endpoint_returns_expected_response():
    """Verify the health endpoint response payload."""

    response = client.get("/health")

    assert response.json() == {
        "status": "healthy",
        "service": "AI Data Assistant API",
        "version": "1.0.0",
    }

def test_health_endpoint_uses_json_response():
    """Verify that the health endpoint returns JSON."""

    response = client.get("/health")

    assert response.headers["content-type"].startswith(
        "application/json"
    )


def test_upload_valid_csv(tmp_path, monkeypatch):
    """
    Verify that a valid CSV is accepted and stored.

    tmp_path provides an isolated temporary directory so the test
    does not create files in the project's real upload directory.
    """

    monkeypatch.setattr(
        upload_service,
        "UPLOAD_DIR",
        tmp_path,
    )

    csv_content = b"id,name,amount\n1,John,100\n2,Alex,200\n"

    response = client.post(
        "/api/v1/upload",
        files={
            "file": (
                "sales.csv",
                csv_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "uploaded"
    assert result["original_filename"] == "sales.csv"
    assert result["rows"] == 2
    assert result["columns"] == 3
    assert result["file_id"]

    # Confirm the file was physically stored.
    stored_file = tmp_path / result["stored_filename"]
    assert stored_file.is_file()

    # The API must not expose the server's absolute file path.
    assert "file_path" not in result

def test_upload_rejects_non_csv_file():
    """Verify that unsupported file extensions are rejected."""

    response = client.post(
        "/api/v1/upload",
        files={
            "file": (
                "document.txt",
                b"This is a text file.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only CSV files are supported."
    )

def test_upload_rejects_empty_file(tmp_path, monkeypatch):
    """Verify that an empty upload is rejected."""

    monkeypatch.setattr(
        upload_service,
        "UPLOAD_DIR",
        tmp_path,
    )

    response = client.post(
        "/api/v1/upload",
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The uploaded file is empty."
    )

def test_upload_rejects_oversized_file(tmp_path, monkeypatch):
    """
    Verify that uploads exceeding the configured size limit
    are rejected before CSV parsing or file storage.
    """

    monkeypatch.setattr(
        upload_service,
        "UPLOAD_DIR",
        tmp_path,
    )

    # Use a small limit for testing instead of creating a 10 MB file.
    monkeypatch.setattr(
        upload_service,
        "MAX_UPLOAD_SIZE",
        20,
    )

    csv_content = b"id,value\n1," + (b"x" * 30)

    response = client.post(
        "/api/v1/upload",
        files={
            "file": (
                "large.csv",
                csv_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "File exceeds the maximum allowed size of 10 MB."
    )

    # Confirm that the rejected file was not stored.
    assert list(tmp_path.iterdir()) == []


def test_resolve_uploaded_file_returns_existing_csv(tmp_path, monkeypatch):
    """Resolve a valid file ID to its stored CSV path."""

    from src.api import upload_service

    # Use a temporary directory instead of the actual upload directory.
    monkeypatch.setattr(upload_service, "UPLOAD_DIR", tmp_path)

    # Generate a valid UUID and create its corresponding CSV file.
    file_id = uuid.uuid4().hex
    csv_path = tmp_path / f"{file_id}.csv"
    csv_path.write_text("id,name\n1,John\n", encoding="utf-8")

    # Resolve the file using its server-generated identifier.
    resolved_path = upload_service.resolve_uploaded_file(file_id)

    assert resolved_path == csv_path.resolve()
    assert resolved_path.is_file()


def test_resolve_uploaded_file_rejects_invalid_file_id():
    """Reject identifiers that are not valid UUIDs."""

    from fastapi import HTTPException
    from src.api.upload_service import resolve_uploaded_file

    with pytest.raises(HTTPException) as exc_info:
        resolve_uploaded_file("../../sensitive_file")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid file ID."


def test_resolve_uploaded_file_returns_404_for_missing_file(
    tmp_path, monkeypatch
):
    """Return 404 when a valid file ID has no stored CSV."""

    from fastapi import HTTPException
    from src.api import upload_service

    monkeypatch.setattr(upload_service, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex

    with pytest.raises(HTTPException) as exc_info:
        upload_service.resolve_uploaded_file(file_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Uploaded CSV file not found."


def test_analyze_uploaded_csv_success(monkeypatch):
    """Return the complete analysis when the pipeline succeeds."""

    from pathlib import Path
    from src.api import main

    file_id = uuid.uuid4().hex
    expected_path = Path("temporary_upload.csv").resolve()

    # Mock file resolution so the test does not access real storage.
    monkeypatch.setattr(
        main,
        "resolve_uploaded_file",
        lambda received_id: expected_path,
    )

    # Provide a representative result matching the real pipeline.
    mock_analysis = {
        "status": "success",
        "report": "Sample data quality report.",
        "decision_result": {"recommendations": []},
        "explanation_result": {"summary": "Sample explanation."},
    }

    # Prevent actual CrewAI and Gemini execution.
    mock_pipeline = Mock(return_value=mock_analysis)
    monkeypatch.setattr(main, "run_pipeline", mock_pipeline)

    response = TestClient(main.app).post(
        f"/api/v1/analyze/{file_id}"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["file_id"] == file_id
    assert response.json()["analysis"] == mock_analysis

    mock_pipeline.assert_called_once_with(file_path=expected_path)


def test_analyze_uploaded_csv_rejects_invalid_file_id():
    """Return HTTP 400 when the file ID is invalid."""

    response = TestClient(app).post(
        "/api/v1/analyze/invalid-file-id"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file ID."


def test_analyze_uploaded_csv_returns_404_for_missing_file(
    tmp_path, monkeypatch
):
    """Return HTTP 404 when the uploaded CSV does not exist."""

    from src.api import main, upload_service

    monkeypatch.setattr(
        upload_service,
        "UPLOAD_DIR",
        tmp_path,
    )

    file_id = uuid.uuid4().hex

    response = TestClient(main.app).post(
        f"/api/v1/analyze/{file_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Uploaded CSV file not found."


def test_analyze_uploaded_csv_handles_pipeline_failure(monkeypatch):
    """Return a safe HTTP 500 response when the pipeline fails."""

    from src.api import main

    file_id = uuid.uuid4().hex

    monkeypatch.setattr(
        main,
        "resolve_uploaded_file",
        lambda received_id: Path("temporary_upload.csv"),
    )

    mock_pipeline = Mock(
        side_effect=RuntimeError("Internal pipeline failure.")
    )
    monkeypatch.setattr(main, "run_pipeline", mock_pipeline)

    response = TestClient(main.app).post(
        f"/api/v1/analyze/{file_id}"
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Data quality analysis failed. Check server logs."
    )

    # Internal exception details must not leak to the API client.
    assert "Internal pipeline failure." not in response.text


def test_analyze_uploaded_csv_rejects_unexpected_pipeline_result(
    monkeypatch,
):
    """Reject incomplete results returned by the pipeline."""

    from src.api import main

    file_id = uuid.uuid4().hex

    monkeypatch.setattr(
        main,
        "resolve_uploaded_file",
        lambda received_id: Path("temporary_upload.csv"),
    )

    mock_pipeline = Mock(
        return_value={"status": "success"}
    )
    monkeypatch.setattr(main, "run_pipeline", mock_pipeline)

    response = TestClient(main.app).post(
        f"/api/v1/analyze/{file_id}"
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Data quality analysis failed. Check server logs."
    )


def test_upload_accepts_semicolon_delimited_csv(tmp_path, monkeypatch):
    """Accept and normalize a semicolon-separated CSV."""

    from src.api import upload_service

    monkeypatch.setattr(upload_service, "UPLOAD_DIR", tmp_path)

    csv_content = (
        "id;name;amount\n"
        "001;John;100\n"
        "002;Alex;200\n"
    )

    response = TestClient(app).post(
        "/api/v1/upload",
        files={
            "file": (
                "semicolon_data.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["rows"] == 2
    assert result["columns"] == 3

    # Verify the stored file uses the normalized comma delimiter.
    stored_path = tmp_path / result["stored_filename"]

    stored_content = stored_path.read_text(encoding="utf-8")

    assert "id,name,amount" in stored_content
    assert "001,John,100" in stored_content
    assert "002,Alex,200" in stored_content

def test_upload_accepts_cp1252_encoded_csv(tmp_path, monkeypatch):
    """Accept and normalize a CSV containing CP1252 characters."""

    from src.api import upload_service

    monkeypatch.setattr(upload_service, "UPLOAD_DIR", tmp_path)

    csv_content = (
        "id;name;city\n"
        "1;José;Málaga\n"
        "2;François;Paris\n"
    )

    response = TestClient(app).post(
        "/api/v1/upload",
        files={
            "file": (
                "cp1252_data.csv",
                csv_content.encode("cp1252"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["rows"] == 2
    assert result["columns"] == 3

    stored_path = tmp_path / result["stored_filename"]

    stored_content = stored_path.read_text(encoding="utf-8")

    assert "José" in stored_content
    assert "François" in stored_content
    assert "Málaga" in stored_content

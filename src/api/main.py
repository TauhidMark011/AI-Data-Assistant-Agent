# FastAPI application and endpoints, Receives HTTP requests and returns responses
"""
FastAPI application for the Data Assistant Agent.

This module exposes the existing data-quality pipeline
through an independent HTTP API.
"""

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile

from src.api.upload_service import (
    resolve_uploaded_file,
    save_uploaded_csv,
)
from src.orchestration.crew.crew import run_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Data Assistant API",
    description=(
        "API for automated data-quality analysis "
        "using deterministic validation, decision-making, "
        "and RAG-grounded explanations."
    ),
    version="1.0.0",
)

#confirms API availability
@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Check whether the API application is running."""

    return {
        "status": "healthy",
        "service": "AI Data Assistant API",
        "version": "1.0.0",
    }


@app.post("/api/v1/upload", tags=["Data Upload"])
async def upload_csv(file: UploadFile = File(...)) -> dict:
    """
    Upload and validate a CSV dataset.

    This endpoint delegates(passes) file validation and storage to the
    upload service. It does not execute the data-quality pipeline.

    The server-generated file ID will be used in a later API
    endpoint to identify the uploaded dataset.
    """

    #Validate and store the uploaded CSV.
    upload_result = await save_uploaded_csv(file)

    #Return only client-safe metadata.
    #Do not expose the server's absolute filesystem path.
    return {
        "status": upload_result["status"],
        "message": "CSV uploaded and validated successfully.",
        "file_id": upload_result["file_id"],
        "original_filename": upload_result["original_filename"],
        "stored_filename": upload_result["stored_filename"],
        "rows": upload_result["rows"],
        "columns": upload_result["columns"],
    }

@app.post("/api/v1/analyze/{file_id}", tags=["Data Analysis"])
def analyze_uploaded_csv(file_id: str) -> dict:
    """
    Analyse an uploaded CSV using the existing CrewAI pipeline.

    The endpoint resolves the server-generated file ID,
    executes the data-quality pipeline, and returns the
    final analysis report.

    The existing pipeline and dataset are not modified by
    this API endpoint.
    """

    # Step 1: Resolve the uploaded CSV using its server-generated ID.
    # Invalid IDs and missing files raise their own HTTP exceptions.
    csv_path = resolve_uploaded_file(file_id)

    try:
        # Step 2: Execute the existing pipeline with the resolved CSV.
        # This reuses deterministic analysis, DecisionEngine, RAG,
        # Gemini explanation generation, and report assembly.
        analysis_result = run_pipeline(file_path=csv_path)

        # Step 3: Validate the pipeline's returned structure.
        required_fields = {
            "status",
            "report",
            "decision_result",
            "explanation_result",
        }

        if not isinstance(analysis_result, dict):
            raise RuntimeError(
                "The analysis pipeline returned an invalid result."
            )

        missing_fields = required_fields.difference(analysis_result)

        if missing_fields:
            raise RuntimeError(
                "The analysis pipeline returned an incomplete result."
            )

        if analysis_result["status"] != "success":
            raise RuntimeError(
                "The analysis pipeline did not complete successfully."
            )

        # Step 4: Return the verified analysis result to the client.
        return {
            "status": "success",
            "message": "Data quality analysis completed successfully.",
            "file_id": file_id,
            "analysis": analysis_result,
        }

    except Exception as exc:
        # Log technical details on the server without exposing
        # internal paths, stack traces, or sensitive details to clients.
        logger.exception(
            "Data quality analysis failed for file_id=%s",
            file_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Data quality analysis failed. Check server logs.",
        ) from exc

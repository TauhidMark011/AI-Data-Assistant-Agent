
"""
Integration test for deterministic tools using an uploaded CSV.

This script verifies that the existing DataLoadTool,
SchemaInferenceTool, and QualityCheckTool can process
a normalized CSV stored by the FastAPI upload service.
"""

import json
import logging

from src.api.upload_service import resolve_uploaded_file
from src.orchestration.tools.file_tool import DataLoadTool
from src.orchestration.tools.schema_tool import SchemaInferenceTool
from src.orchestration.tools.quality_tool import QualityCheckTool


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Use the actual file ID returned by the upload endpoint.
FILE_ID = "82cceefd93964feaaa74e859d9d99227"


def test_uploaded_dataset_tools() -> None:
    """Run all three deterministic tools against the uploaded CSV."""

    # Resolve the stored CSV using the secure file-ID resolver.
    csv_path = resolve_uploaded_file(FILE_ID)

    logger.info("Testing uploaded dataset: %s", csv_path)

    # ---------------------------------------------------------
    # STEP 1: Data loading and preview
    # ---------------------------------------------------------

    loader = DataLoadTool()

    loader_result = loader._run(file_path=str(csv_path))

    print("\n========== DATA LOAD TOOL ==========")
    print(loader_result)

    assert not loader_result.startswith("Error loading file:"), (
        "DataLoadTool could not read the uploaded CSV."
    )

    # ---------------------------------------------------------
    # STEP 2: Schema inference
    # ---------------------------------------------------------

    schema_tool = SchemaInferenceTool()

    schema_result = schema_tool._run(file_path=str(csv_path))

    schema_text = schema_result.replace("Inferred schema:\n", "")
    schema = json.loads(schema_text)
    print("\nIMDb Release year profile:")
    print(json.dumps(schema["Release year"], indent=4))

    print("\n========== SCHEMA INFERENCE TOOL ==========")
    print(schema_result)

    assert not schema_result.startswith("Error inferring schema:"), (
        "SchemaInferenceTool could not process the uploaded CSV."
    )

    # ---------------------------------------------------------
    # STEP 3: Deterministic quality analysis
    # ---------------------------------------------------------

    quality_tool = QualityCheckTool()

    quality_result = quality_tool._run(file_path=str(csv_path))

    print("\n========== QUALITY CHECK TOOL ==========")

    # Parse and format the returned JSON evidence.
    quality_data = json.loads(quality_result)

    print(json.dumps(quality_data, indent=2))

    assert "critical_system_failure" not in quality_data, (
        "QualityCheckTool reported a critical system failure."
    )

    logger.info(
        "All three deterministic tools processed the uploaded CSV."
    )


if __name__ == "__main__":
    test_uploaded_dataset_tools()

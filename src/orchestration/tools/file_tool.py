#src/orchestration/tools/file_tool.py(Load + preview data)
#loads and previews CSV datasets
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
from pathlib import Path

class DataLoadInput(BaseModel):
    file_path: str = Field(..., description="Path to the CSV file")

class DataLoadTool(BaseTool):
    name: str = "data_loader_tool"
    description: str = "Loads the CSV and provides a human-readable preview of the actual records."
    args_schema: type[BaseModel] = DataLoadInput

    # file_tool.py — add _default_path and update _run
    _default_path: str = str(
        Path(__file__).resolve().parents[2] / "data" / "dirty_cafe_sales.csv"
    )

    def _run(self, file_path: str = None, **_: object) -> str:
        resolved = file_path or self._default_path
        if isinstance(resolved, dict):
            resolved = resolved.get("file_path", self._default_path)
        try:
            #We load the data without any cleaning to show exactly what is on the disk
            df = pd.read_csv(resolved)

            #Format the output for a Human-Readable response
            stats = (
                f"File: {resolved}\n"
                f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
            )
            columns = f"Columns: {', '.join(df.columns)}\n"
            #.to_string() creates a clean, readable table format
            preview = f"\n--- ACTUAL DATA PREVIEW (First 10 Rows) ---\n{df.head(10).to_string(index=False)}"

            return stats + columns + preview
        except Exception as e:
            return f"Error loading file: {str(e)}"
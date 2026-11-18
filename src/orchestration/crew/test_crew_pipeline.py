
from pathlib import Path

import pytest

from src.orchestration.crew import crew as crew_module


@pytest.mark.parametrize(
    ("failure_type", "expected_message"),
    [
        ("loader", "Data loader"),
        ("schema", "Schema inference"),
        ("quality", "Quality analysis"),
    ],
)
def test_pipeline_stops_on_critical_tool_failure(
    monkeypatch,
    failure_type,
    expected_message,
):
    """Stop before decision-making and explanation if a tool fails."""

    monkeypatch.setattr(
        crew_module,
        "RAW_DATA_PATH",
        Path(__file__),
    )

    loader_result = "Valid loader result"
    schema_result = "Valid schema result"
    quality_result = {
        "summary": {
            "total_records": 5,
            "total_missing_dirty_values": 0,
        }
    }

    if failure_type == "loader":
        loader_result = (
            "CRITICAL_TOOL_FAILURE: "
            "data_loader_tool failed: simulated failure"
        )

    elif failure_type == "schema":
        schema_result = (
            "CRITICAL_TOOL_FAILURE: "
            "schema_inference_tool failed: simulated failure"
        )

    elif failure_type == "quality":
        quality_result = {
            "critical_system_failure": (
                "quality_check_tool failed: simulated failure"
            )
        }

    def mock_deterministic_analysis(*args, **kwargs):
        return (
        loader_result,
        schema_result,
        quality_result,
    )

    monkeypatch.setattr(
    crew_module,
    "run_deterministic_analysis",
    mock_deterministic_analysis,
    )

    def unexpected_decision(*args, **kwargs):
        pytest.fail(
            "Decision engine must not run after a critical tool failure."
        )

    def unexpected_explanation(*args, **kwargs):
        pytest.fail(
            "Explanation pipeline must not run after a critical tool failure."
        )

    monkeypatch.setattr(
        crew_module,
        "run_decision_engine",
        unexpected_decision,
    )

    monkeypatch.setattr(
        crew_module,
        "run_explanation_pipeline",
        unexpected_explanation,
    )

    with pytest.raises(
        RuntimeError,
        match="Critical deterministic-tool failure",
    ) as exc_info:
        crew_module.run_pipeline()

    assert expected_message in str(exc_info.value)


def test_flow_success_path_calls_decision_and_explanation_once(
    monkeypatch,
):
    """Verify successful Flow orchestration without calling Gemini."""

    monkeypatch.setattr(
        crew_module,
        "RAW_DATA_PATH",
        Path(__file__),
    )

    analysis_results = {
        "loader_result": "File: test.csv\nShape: (5, 2)",
        "schema_result": "Inferred schema: test schema",
        "quality_result": {
            "summary": {
                "total_records": 5,
                "total_missing_dirty_values": 0,
            }
        },
    }

    def mock_deterministic_analysis(*args, **kwargs):
        return (
        analysis_results["loader_result"],
        analysis_results["schema_result"],
        analysis_results["quality_result"],
    )

    monkeypatch.setattr(
    crew_module,
    "run_deterministic_analysis",
    mock_deterministic_analysis,
    )

    decision_calls = []
    explanation_calls = []

    decision_result = {
        "decision_engine": {
            "llm_used": False,
            "dataset_modified": False,
        },
        "recommendations": [],
    }

    def fake_decision_engine(quality_result):
        decision_calls.append(quality_result)
        return decision_result

    explanation_result = {
        "explanation": {
            "summary": "Mocked grounded explanation for testing."
        },
        "grounded_context": {
            "status": "ok",
            "sources": ["test_source.md"],
        },
        "generation_calls_requested": 1,
    }

    def fake_explanation_pipeline(decision_result):
        explanation_calls.append(decision_result)
        return explanation_result

    monkeypatch.setattr(
        crew_module,
        "run_decision_engine",
        fake_decision_engine,
    )

    monkeypatch.setattr(
        crew_module,
        "run_explanation_pipeline",
        fake_explanation_pipeline,
    )

    monkeypatch.setattr(
        crew_module,
        "format_decision_result",
        lambda result: "Mocked deterministic decision report.",
    )

    result = crew_module.run_pipeline()

    assert len(decision_calls) == 1
    assert decision_calls[0] is analysis_results["quality_result"]

    assert len(explanation_calls) == 1
    assert explanation_calls[0] is decision_result

    assert result["status"] == "success"
    assert result["decision_result"] is decision_result
    assert result["explanation_result"] == explanation_result["explanation"]
    assert "Mocked deterministic decision report." in result["report"]
    assert "Mocked grounded explanation" in result["report"]
    assert "Dataset modified: False" in result["report"]

def test_flow_stops_when_explanation_pipeline_fails(monkeypatch):
    """Ensure explanation failure cannot produce a successful report."""

    monkeypatch.setattr(
        crew_module,
        "RAW_DATA_PATH",
        Path(__file__),
    )

    quality_result = {
        "summary": {
            "total_records": 5,
            "total_missing_dirty_values": 0,
        }
    }

    def mock_deterministic_analysis(*args, **kwargs):
        return (
        "File: test.csv\nShape: (5, 2)",
        "Inferred schema: test schema",
        quality_result,
    )

    monkeypatch.setattr(
    crew_module,
    "run_deterministic_analysis",
    mock_deterministic_analysis,
    )

    decision_result = {
        "decision_engine": {
            "llm_used": False,
            "dataset_modified": False,
        },
        "recommendations": [],
    }

    monkeypatch.setattr(
        crew_module,
        "run_decision_engine",
        lambda quality: decision_result,
    )

    def fail_explanation(decision_result):
        raise RuntimeError("Simulated Gemini/API failure")

    monkeypatch.setattr(
        crew_module,
        "run_explanation_pipeline",
        fail_explanation,
    )

    def unexpected_report(*args, **kwargs):
        pytest.fail(
            "A final report must not be assembled after explanation failure."
        )

    monkeypatch.setattr(
        crew_module,
        "format_decision_result",
        unexpected_report,
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated Gemini/API failure",
    ):
        crew_module.run_pipeline()

#This test verifies that:
#- A custom CSV file exists.
#- The supplied path reaches deterministic analysis.
#- The default dataset is not substituted.
#- The rest of the Flow completes without calling Gemini.

def test_flow_uses_supplied_input_file_path(
    monkeypatch,
    tmp_path,
):
    """Verify that a custom CSV path reaches deterministic analysis."""

    csv_path = tmp_path / "uploaded_dataset.csv"
    csv_path.write_text(
        "id,value\n1,100\n2,200\n",
        encoding="utf-8",
    )

    received_paths = []

    def mock_deterministic_analysis(file_path=None):
        received_paths.append(Path(file_path).resolve())

        return (
            "File: uploaded_dataset.csv\nShape: 2 rows, 2 columns",
            "Inferred schema: test schema",
            {
                "summary": {
                    "total_records": 2,
                    "total_missing_dirty_values": 0,
                }
            },
        )

    decision_result = {
        "decision_engine": {
            "mode": "deterministic",
            "llm_used": False,
            "dataset_modified": False,
        },
        "human_in_the_loop": {
            "enabled": True,
            "approval_required": False,
        },
        "recommendations": [],
    }

    monkeypatch.setattr(
        crew_module,
        "run_deterministic_analysis",
        mock_deterministic_analysis,
    )

    monkeypatch.setattr(
        crew_module,
        "run_decision_engine",
        lambda quality_result: decision_result,
    )

    monkeypatch.setattr(
        crew_module,
        "run_explanation_pipeline",
        lambda decision_result: {
            "explanation": {
                "summary": "Mocked explanation."
            }
        },
    )

    monkeypatch.setattr(
        crew_module,
        "format_decision_result",
        lambda result: "Mocked decision report.",
    )

    result = crew_module.run_pipeline(file_path=csv_path)

    assert received_paths == [csv_path.resolve()]
    assert result["status"] == "success"
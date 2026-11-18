#Latest
#Core multi-agent controller — Phase 4 Delegated DQ Pipeline, The Agent provides the logic (the "why" and "how").
# crew.py — top of file
#D:\DataAssistant_AI-Agent\src\orchestration\crew\crew.py
"""
Phase 4A — Controller-Based Lightweight Data Quality Pipeline

Architecture:

    CSV Dataset
        |
        v
    Python Controller
        |
        +--> DataLoadTool
        |
        +--> SchemaInferenceTool
        |
        +--> QualityCheckTool
        |
        v
    Deterministic Evidence
        |
        v
    1 CrewAI Agent
        |
        v
    1 Gemini Synthesis Call
        |
        v
    Final Data Quality Report

Design Principles:

    - Python tools are the source of truth.
    - Deterministic tools execute outside the LLM agent loop.
    - Each deterministic tool executes exactly once.
    - The CrewAI Agent has NO tools.
    - Gemini is used only for explanation and assessment.
    - No autonomous tool selection.
    - No repeated tool execution.
    - No dataset calculations by the LLM.
    - No unnecessary dataset content is sent to Gemini.
    - Missing/dirty-value terminology is explicit.
    - Statistical outliers are not automatically classified as errors.
"""
"""
Phase 4B — Lightweight CrewAI Data Quality Pipeline

Architecture:
1 Agent
1 Task
3 deterministic tools

Principle:
Python tools are the source of truth.
Gemini is responsible for orchestration and explanation only.
"""

import sys
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Windows UTF-8 console hardening
# ---------------------------------------------------------------------------

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace",
    )

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace",
    )

from dotenv import load_dotenv
from crewai.flow.flow import Flow, listen, start
from src.orchestration.explanation_pipeline import (
    run_explanation_pipeline,
)

# ============================================================================
# PATH BOOTSTRAP
# ============================================================================

_THIS_FILE = Path(__file__).resolve()
_SRC_DIR = _THIS_FILE.parents[2]

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

RAW_DATA_PATH = _SRC_DIR / "data" / "dirty_cafe_sales.csv"

# ============================================================================
# ENVIRONMENT
# ============================================================================

load_dotenv()

# ============================================================================
# DETERMINISTIC TOOLS
# ============================================================================

from orchestration.tools.file_tool import DataLoadTool
from orchestration.tools.quality_tool import QualityCheckTool
from orchestration.tools.schema_tool import SchemaInferenceTool
from orchestration.decision.decision_engine import DecisionEngine

data_tool = DataLoadTool(
    name="data_loader_tool"
)

schema_tool = SchemaInferenceTool(
    name="schema_inference_tool"
)

quality_tool = QualityCheckTool(
    name="quality_check_tool"
)

#helper function
def parse_quality_evidence(raw_result: str) -> dict:
    """
    Convert the deterministic QualityCheckTool JSON output
    into the canonical Python evidence dictionary.

    The quality tool remains responsible only for producing evidence.
    The controller owns serialization/deserialization boundaries.
    """
    try:
        evidence = json.loads(raw_result)
    except (TypeError, json.JSONDecodeError) as exc:
        return {
            "critical_system_failure": (
                "Phase 4A quality evidence could not be parsed: "
                f"{exc}"
            )
        }

    if not isinstance(evidence, dict):
        return {
            "critical_system_failure": (
                "Phase 4A quality evidence must deserialize to a dictionary."
            )
        }

    return evidence

# ============================================================================
# DETERMINISTIC CONTROLLER
# ============================================================================

def run_deterministic_analysis(
    file_path: str | Path | None = None,
) -> tuple[str, str, dict]:
    """
    Execute the three deterministic tools exactly once.

    IMPORTANT:

        This function executes outside the CrewAI Agent.

    Therefore:

        - Gemini does not decide which tool to call.
        - Gemini cannot repeatedly call a tool.
        - Tool execution is deterministic.
        - Tool failures are captured as evidence.
    """

    file_path = file_path = str(file_path or RAW_DATA_PATH)


    print("\n=== STEP 1/3 — Data Loading ===")

    try:
        loader_result = data_tool.run(
            file_path=file_path
        )
        print("[OK] Data loader completed.")

    except Exception as exc:
        print(f"[ERROR] Data loader failed: {exc}")
        loader_result = (
            "CRITICAL_TOOL_FAILURE: "
            f"data_loader_tool failed: {exc}"
        )

    print("\n=== STEP 2/3 — Schema Inference ===")

    try:
        schema_result = schema_tool.run(
            file_path=file_path
        )
        print("[OK] Schema inference completed.")

    except Exception as exc:
        print(f"[ERROR] Schema inference failed: {exc}")
        schema_result = (
            "CRITICAL_TOOL_FAILURE: "
            f"schema_inference_tool failed: {exc}"
        )

    print("\n=== STEP 3/3 — Data Quality Analysis ===")

    try:
        quality_result_raw = quality_tool.run(
            file_path=file_path
        )
        quality_result = parse_quality_evidence(
            quality_result_raw
        )
        print("[OK] Quality analysis completed.")

    except Exception as exc:
        print(f"[ERROR] Quality analysis failed: {exc}")
        quality_result = {
            "critical_system_failure": (
                "quality_check_tool failed: "
                f"{exc}"
            )
        }

    return (
        loader_result,
        schema_result,
        quality_result,
    )

# ============================================================================
# PHASE 4B — DETERMINISTIC DECISION ENGINE
# ============================================================================

def run_decision_engine(quality_result: dict) -> dict:
    """
    Convert real Phase 4A quality evidence into Phase 4B
    deterministic recommendations.

    IMPORTANT:
        - No LLM is used.
        - No dataset is re-read.
        - No quality tool is executed again.
        - The original evidence is preserved.
        - The DecisionEngine only recommends actions.
        - No remediation is performed.
    """

    engine = DecisionEngine()

    return engine.evaluate(quality_result)

#A deterministic presentation helper to crew.py(gives the exact same identical input/output values)
def format_decision_result(decision_result: dict) -> str:
    """
    Render the authoritative Phase 4B decision result
    as a human-readable report section.

    This function is deterministic.
    Gemini is not involved.
    """

    lines = [
        "## Phase 4B — Decision & Recommendations",
        "",
        (
            "- Decision mode: "
            f"{decision_result['decision_engine']['mode']}"
        ),
        (
            "- LLM used for decision-making: "
            f"{decision_result['decision_engine']['llm_used']}"
        ),
        (
            "- Dataset modified: "
            f"{decision_result['decision_engine']['dataset_modified']}"
        ),
        (
            "- Human-in-the-loop enabled: "
            f"{decision_result['human_in_the_loop']['enabled']}"
        ),
        (
            "- Approval required: "
            f"{decision_result['human_in_the_loop']['approval_required']}"
        ),
        "",
    ]

    recommendations = decision_result.get(
        "recommendations",
        [],
    )

    if not recommendations:
        lines.append(
            "No actionable recommendations were generated."
        )
        return "\n".join(lines)

    lines.append("### Recommendations")
    lines.append("")

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        lines.extend(
            [
                f"#### {index}. {recommendation['issue_type']}",
                (
                    f"- Severity: "
                    f"{recommendation['severity']}"
                ),
                (
                    f"- Priority: "
                    f"{recommendation['priority']}"
                ),
                (
                    f"- Action: "
                    f"{recommendation['action']}"
                ),
                (
                    "- Human approval required: "
                    f"{recommendation['human_approval_required']}"
                ),
                (
                    f"- Recommendation: "
                    f"{recommendation['recommendation']}"
                ),
                "",
            ]
        )

    summary = decision_result.get("summary", {})

    lines.extend(
        [
            "### Decision Summary",
            "",
            (
                "- Total recommendations: "
                f"{summary.get('total_recommendations', 0)}"
            ),
            (
                "- Review required: "
                f"{summary.get('review_required', 0)}"
            ),
        ]
    )

    return "\n".join(lines)

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def validate_deterministic_results(
    loader_result,
    schema_result,
    quality_result,
) -> None:
    """Stop the pipeline if any deterministic tool failed."""

    failures = []

    # Data loader failure
    if (
        isinstance(loader_result, str)
        and loader_result.startswith("CRITICAL_TOOL_FAILURE:")
    ):
        failures.append(f"Data loader: {loader_result}")

    # Schema inference failure
    if (
        isinstance(schema_result, str)
        and schema_result.startswith("CRITICAL_TOOL_FAILURE:")
    ):
        failures.append(f"Schema inference: {schema_result}")

    # Quality tool failure

    # Quality tool failure
    if isinstance(quality_result, dict):
        if "critical_system_failure" in quality_result:
            failures.append(
                "Quality analysis: "
                f"{quality_result['critical_system_failure']}"
            )

    elif isinstance(quality_result, str):
        if quality_result.startswith("CRITICAL_TOOL_FAILURE:"):
            failures.append(
                f"Quality analysis: {quality_result}"
            )
        else:
            try:
                parsed_quality = json.loads(quality_result)
            except json.JSONDecodeError:
                parsed_quality = None

            if (
                isinstance(parsed_quality, dict)
                and "critical_system_failure" in parsed_quality
            ):
                failures.append(
                    "Quality analysis: "
                    f"{parsed_quality['critical_system_failure']}"
                )

    if failures:
        details = "\n".join(f"- {failure}" for failure in failures)
        raise RuntimeError(
            "Critical deterministic-tool failure. "
            "The pipeline has stopped before decision-making "
            "and explanation generation.\n"
            f"{details}"
        )

class DataQualityFlow(Flow):
    """Coordinate deterministic analysis, decisions, RAG, and explanation."""

    @start()
    def analyse_data(self):
        """Run deterministic tools and stop if a critical tool fails."""

        file_path = Path(
        self.state.get("input_file_path") or RAW_DATA_PATH
        ).resolve()

        if not file_path.is_file():
            raise FileNotFoundError(
            f"Input dataset not found: {file_path}"
        )

        loader_result, schema_result, quality_result = (
            run_deterministic_analysis(file_path)
            )

        validate_deterministic_results(
        loader_result,
        schema_result,
        quality_result,
        )

        return {
        "input_file_path": str(file_path),
        "loader_result": loader_result,
        "schema_result": schema_result,
        "quality_result": quality_result,
        }

    @listen(analyse_data)
    def make_deterministic_decisions(self, analysis: dict):
        """Create recommendations without an LLM decision."""

        decision_result = run_decision_engine(
            analysis["quality_result"]
        )

        return {
            **analysis,
            "decision_result": decision_result,
        }

    @listen(make_deterministic_decisions)
    def generate_grounded_explanation(self, package: dict):
        """Retrieve knowledge and request the validated explanation."""

        pipeline_result = run_explanation_pipeline(
            decision_result=package["decision_result"]
        )

        return {
            **package,
            "pipeline_result": pipeline_result,
        }

    @listen(generate_grounded_explanation)
    def assemble_report(self, package: dict):
        """Prepare the final report without another LLM request."""

        decision_result = package["decision_result"]
        explanation_result = package["pipeline_result"]["explanation"]

        decision_report = format_decision_result(decision_result)

        report_lines = [
            "=" * 72,
            "DATA QUALITY ASSISTANT — FINAL REPORT",
            "=" * 72,
            "",
            "DETERMINISTIC DECISION REPORT",
            "-" * 72,
            decision_report,
            "",
            "GROUNDED EXPLANATION",
            "-" * 72,
            json.dumps(
                explanation_result,
                indent=2,
                ensure_ascii=False,
            ),
            "",
            "PIPELINE SAFETY STATUS",
            "-" * 72,
            f"Dataset modified: "
            f"{decision_result['decision_engine']['dataset_modified']}",
            "Decisions made by: Deterministic Python decision engine",
            "Explanation generated through: RAG + Gemini",
            "Additional LLM synthesis in CrewAI Flow: No",
        ]

        report = "\n".join(report_lines)
        print(report)

        return {
            "status": "success",
            "report": report,
            "decision_result": decision_result,
            "explanation_result": explanation_result,
        }

def run_pipeline(
    file_path: str | Path | None = None,
):
    """Run the data-quality workflow for the supplied CSV dataset."""

    print("\n=== Starting Data Quality Flow ===")

    flow = DataQualityFlow()

    if file_path is not None:
        flow.state["input_file_path"] = str(
            Path(file_path).resolve()
        )

    result = flow.kickoff()

    return result

if __name__ == "__main__":
    run_pipeline()

# ============================================================================
# ENTRY POINT
# ============================================================================
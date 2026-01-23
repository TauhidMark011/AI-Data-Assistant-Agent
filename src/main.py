#this block: Orchestrates the full validation pipeline,
#Ensures the run_validation() pipeline is engaged with schema + prompt + parser
#Renders the final structured CLI output (Phase 3.7)
#Keeps the code clean and modular for future extensions (like Streamlit or CrewAI)

#Testing Structured Agent Output Format of Phase 3.7
from agent.validation_agent import run_validation
from agent_output.structured_report import generate_structured_report

# === Step 1: Run validation on IMDb dataset ===
#Trigger the full validation pipeline
if __name__ == "__main__":
    file_path = "data/dirty_cafe_sales.csv"
# === Step 1: Run validation (calls schema loading + LLM prompting) ===
    result = run_validation(file_path)

# === Step 2: Extract structured fields into formatted output === Use real parsed fields from the agent output
report_str = generate_structured_report(
    result["null_issues"],
    result["malformed_columns"],
    result["auto_fixes"],
    result["suggested_fixes"],
    result["blocked_fixes"],
    result["nlg_messages"],
    return_format="string"
)
#This result dict now comes from: AgentOutputParser.parse(), Which receives response.response (true LLM response)
#And this response is from dq_agent.invoke(...), So there’s no hardcoded test running at all when we run main.py

#Print for CLI
print(report_str)
print("--- Parsed Result Dictionary(Main script) ---")
print(result)
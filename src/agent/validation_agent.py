#This wraps our existing DQAgent pipeline to: Load CSV, Run through the validation agent, 
#Return structured fields: null_issues, malformed_columns, etc.
#Now entering the final wiring of Phase 3.7 — dynamic integration of real agent output into the structured reporting logic.
#Phase 3.8 — Dynamic Field Extraction from Raw Agent Output

from agent.dq_agent import create_agent
from agent_output.agent_output_parser import AgentOutputParser

#from llama_index.core.agent import AgentOutputParser

def run_validation(file_path: str):
    #Step 1: Load and run the DQ Agent
    dq_agent = create_agent()
    response = dq_agent.invoke(f"Run full data quality check on {file_path}")

    #Step 2: Extract raw text, (true LLM response)
    output_text = response.response if hasattr(response, "response") else str(response)
    print("/n === Raw Agent Response === \n") #debug
    print(output_text)

    #Step 3: Parse known outputs (TEMPORARY - to be replaced with structured parsing)
    #You should enhance this logic to parse actual model output fields
    #For now, simulate stub result(pre-determined response, dummy)
    #NEW: Dynamically parse agent response

    parser = AgentOutputParser()
    parsed_fields = parser.parse(output_text)

    return { 
        **parsed_fields,
        "raw_agent_output" : output_text                 
    }

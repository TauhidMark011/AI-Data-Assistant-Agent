from crewai import Crew, Agent, Task, LLM
import os
from dotenv import load_dotenv
load_dotenv()
# from langchain_community.llms.ollama import Ollama

#1. Define the LLM using CrewAI's native LLM class
#This forces it to point to your local Ollama instance
my_local_llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434",
    api_key= "NA"
)

#2. Define the Agent and pass the new LLM object
agent = Agent(
    role="Greeter",
    goal="Say hello to the user",
    backstory="Loves greetings",
    llm=my_local_llm,  # Use the CrewAI LLM object here
    allow_delegation=False,
    verbose=True
)

task = Task(
    description="Say hello to Commander Tauhid",
    expected_output="A short friendly greeting",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])

#Kickoff the process
result = crew.kickoff()
print(result)


# from crewai import Crew, Agent, Task
# from langchain_ollama import OllamaLLM
# from dotenv import load_dotenv
# load_dotenv()


# llm = OllamaLLM(model="mistral")  #or llama2, etc.

# agent = Agent(role="Greeter", goal="Say hello to the user", backstory="Loves greetings", llm=llm, allow_delegation=False)

# task = Task(
#     description="Say hello",
#     expected_output="A short friendly greeting",
#     agent=agent
# )

# crew = Crew(agents=[agent], tasks=[task])
# crew.kickoff()

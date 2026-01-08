from agent.dq_agent import create_agent

if __name__ == "__main__":
    agent = create_agent()

    result = agent.invoke(
        "Check data quality of data/messy_IMDB_dataset.csv"
    )

    print("\n=== DATA QUALITY REPORT ===")
    print(result)

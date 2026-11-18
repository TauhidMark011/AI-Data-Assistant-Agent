#tools/ → capabilities (what can be done)
# (Rule: Business logic lives in tools/. The agent only decides when to call tools.)
#pandas is used to read and analyze tabular data (CSV).
import pandas as pd

"""Reads a CSV file from the given path
    and returns it as a pandas DataFrame.
    """
def load_csv(path: str) -> pd.DataFrame: #path: str → path of the CSV file (example: data/sales.csv)
    """
    Robust CSV loader.
    Handles common real-world issues:
    - Non-UTF8 encodings
    - Non-standard delimiters
    """
    try :     
        return pd.read_csv(path) #Loads CSV into memory and returns a DataFrame (table-like structure)
    
    except UnicodeDecodeError:
    #Fallback for common encodings in messy datasets
        return pd.read_csv(
            path,
            encoding="latin1",
            sep=";",
            engine="python" 
        )

"""Calculates percentage of NULL values
    for each column in the DataFrame.
    Returns only columns where NULLs exist.
    """
def check_nulls(df: pd.DataFrame) -> dict:
    null_pct = (df.isnull().mean() * 100).round(2)
    return null_pct[null_pct > 0].to_dict()

def check_duplicates(df: pd.DataFrame) -> int:
    """
    Counts how many duplicate rows exist
    in the dataset.
    """
    return int(df.duplicated().sum())

def basic_stats(df: pd.DataFrame) -> dict:
    """
    Generates basic statistics (count, mean, min, max)
    for numeric and non-numeric columns.
    """
    desc = df.describe(include="all").fillna("").to_dict()
    return desc


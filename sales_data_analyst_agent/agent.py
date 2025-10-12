import pandas as pd
from google.adk.agents import Agent
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# In-memory storage for the DataFrame
data_store: dict[str, Any] = {"dataframe": None}


def read_csv_and_get_schema(file_path: str, encoding: str = "utf-8") -> dict[str, Any]:
    """
    Reads a CSV file from the given path, stores it in-memory, and returns the schema.
    It will try to read with 'utf-8' and then 'latin1' if the first fails.

    Args:
        file_path (str): The temporary path to the CSV file.
        encoding (str): The encoding of the file. Defaults to 'utf-8'.

    Returns:
        Dict[str, Any]: A dictionary containing the status and the schema (column names and dtypes) or an error message.
    """
    try:
        # Try to read with the specified encoding, default to utf-8
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError:
        try:
            # If default fails, try latin1 as a common fallback
            df = pd.read_csv(file_path, encoding="latin1")
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Failed to read CSV with both 'utf-8' and 'latin1' encodings. Error: {e}",
            }
    except FileNotFoundError:
        return {"status": "error", "error_message": f"File not found at: {file_path}"}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while reading the CSV: {e}",
        }

    data_store["dataframe"] = df
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    return {"status": "success", "schema": schema, "num_rows": len(df)}


def execute_query(expression: str) -> dict[str, Any]:
    """
    Executes a pandas expression on the in-memory DataFrame using eval().

    Args:
        expression (str): A string containing a pandas expression to execute.
                          The DataFrame is available as the variable 'df'.
                          Example: "df[df['Sales'] > 100].to_json(orient='records')"

    Returns:
        Dict[str, Any]: A dictionary containing the status and the query result (as a JSON string) or an error message.
    """
    df = data_store.get("dataframe")
    if df is None:
        return {
            "status": "error",
            "error_message": "No data has been loaded. Please read a CSV file first.",
        }

    try:
        # Use eval to execute the expression. The dataframe is available as 'df'.
        result = eval(expression, {"pd": pd, "df": df})

        # If the result is a DataFrame or Series, convert it to JSON.
        if isinstance(result, (pd.DataFrame, pd.Series)):
            result_json = result.to_json(orient="records")
        else:
            # Otherwise, assume the expression already produced a serializable result (e.g., a JSON string).
            result_json = result

        return {"status": "success", "result": result_json}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while executing the query: {e}",
        }


root_agent = Agent(
    name="csv_data_analyst_agent",
    model="gemini-2.5-flash",
    description="Agent that can read a CSV, determine its schema, and answer questions about it by generating and executing queries.",
    instruction=(
        "You are an agent that analyzes data from a CSV file. "
        "1. For EVERY query Call the `read_csv_and_get_schema` tool first to determine the schema and number of rows. "
        "2. Based on the user's question and the schema, formulate a valid pandas expression to execute. "
        "   The dataframe is available in a variable named `df`. The expression MUST be a valid, executable pandas operation. "
        "   For example: `df[df['column'] == 'value'].to_json(orient='records')` or `df.groupby('column')['other_column'].sum().to_json()`"
        "3. Call the `execute_query` tool with the expression string you generated. "
        "4. Present the resulting JSON data to the user in a clear, readable format."
    ),
    tools=[read_csv_and_get_schema, execute_query],
)

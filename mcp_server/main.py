from fastmcp import FastMCP
import datetime

app = FastMCP()


@app.tool()
def get_weather(city: str):
    """
    This is a dummy function that returns a hardcoded weather forecast.
    In a real application, this would call a weather API.
    """
    return {"weather": f"The weather in {city} is sunny and 25 degrees Celsius."}


@app.tool()
def get_current_time():
    """
    Returns the current time.
    """
    return {"time": datetime.datetime.now().isoformat()}


if __name__ == "__main__":
    app.run(transport="http", port=8000)

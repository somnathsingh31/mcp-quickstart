import aiohttp
import logging
from typing import Optional, Dict
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize FastMCP server
mcp = FastMCP("My Server")


async def fetch_weather(city: str) -> Optional[Dict]:
    """Fetch current weather details for a given city from wttr.in API.

    Args:
        city (str): City name.

    Returns:
        Optional[Dict]: Dictionary containing weather details or None if error occurs.
    """
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.error(f"Failed to fetch weather data. Status code: {response.status}")
                    return None

                try:
                    data = await response.json()
                except Exception as json_err:
                    logging.error(f"Error parsing JSON: {json_err}")
                    return None

                current_condition = data.get("current_condition")
                if current_condition and isinstance(current_condition, list):
                    condition = current_condition[0]
                    return {
                        "temperature_celsius": condition.get("temp_C"),
                        "temperature_fahrenheit": condition.get("temp_F"),
                        "humidity": condition.get("humidity"),
                        "weather_description": condition.get("weatherDesc", [{}])[0].get("value"),
                        "wind_speed_kmph": condition.get("windspeedKmph"),
                        "wind_speed_miles": condition.get("windspeedMiles")
                    }
                else:
                    logging.warning("Missing or malformed 'current_condition' data.")
                    return None

    except aiohttp.ClientError as e:
        logging.error(f"HTTP error occurred while fetching weather data: {e}")
        return None

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get formatted weather details of a city.

    Args:
        city (str): City name (e.g., "Mumbai").

    Returns:
        str: Weather information as a formatted string, or an empty string if data is not available.
    """
    try:
        weather_data = await fetch_weather(city)
        if weather_data:
            weather_details = (
                f"Weather details for {city}:\n"
                f"Temperature (°C): {weather_data['temperature_celsius']}\n"
                f"Temperature (°F): {weather_data['temperature_fahrenheit']}\n"
                f"Humidity: {weather_data['humidity']}%\n"
                f"Description: {weather_data['weather_description']}\n"
                f"Wind Speed: {weather_data['wind_speed_kmph']} km/h "
                f"({weather_data['wind_speed_miles']} mph)"
            )
            return weather_details
        else:
            logging.info(f"No weather data found for '{city}'")
            return ""
    except Exception as e:
        logging.error(f"Error occurred while fetching weather data for '{city}': {e}")
        return ""


@mcp.tool()
async def fetch_gold_silver_prices() -> str:
    """Fetch and format latest gold and silver prices in USD per troy ounce.

    Returns:
        str: Formatted price summary including current, previous, and change values for gold and silver,
             or an error message if data is unavailable.
    """
    url = "https://data-asg.goldprice.org/dbXRates/USD"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                item = data["items"][0]

                result = {
                    "currency": item["curr"],
                    "date_ny": data.get("date", "N/A"),
                    "gold": {
                        "current_price": item["xauPrice"],
                        "previous_close": item["xauClose"],
                        "change_absolute": item["chgXau"],
                        "change_percent": item["pcXau"]
                    },
                    "silver": {
                        "current_price": item["xagPrice"],
                        "previous_close": item["xagClose"],
                        "change_absolute": item["chgXag"],
                        "change_percent": item["pcXag"]
                    }
                }

                return f"The gold and silver prices are in USD per troy ounce:\n{result}"

    except Exception as e:
        logging.error(f"Error fetching price data: {e}")
        return "Failed to fetch gold/silver prices."

@mcp.tool()
async def fetch_bitcoin_price() -> str:
    """Fetch and format the current Bitcoin price in USD.

    Returns:
        str: Bitcoin price as a formatted string, or an error message if data is unavailable.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                price = data["bitcoin"]["usd"]
                return f"Bitcoin Price in USD: {price}"

    except Exception as e:
        logging.error(f"Error fetching Bitcoin price: {e}")
        return "Failed to fetch Bitcoin price."


# Initialize and run the server
mcp.run(transport='stdio')
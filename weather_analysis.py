import requests
from datetime import datetime, timedelta
import statistics

# =========================
# Configuration
# =========================
city = "Rexburg,US"
api_key = "defe990ec0c36decfad57ab9949d688a"
units = "imperial"

# =========================
# Helper functions
# =========================
def fetch_weather_data(city, api_key, units="imperial"):
    """Fetch 5-day / 3-hour forecast from OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={units}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching weather data: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def group_by_day(forecast_list):
    """Group 3-hour forecasts into days."""
    daily_data = {}
    for entry in forecast_list:
        dt = datetime.fromtimestamp(entry['dt'])
        date_str = dt.strftime("%A")  # Monday, Tuesday, etc.
        if date_str not in daily_data:
            daily_data[date_str] = []
        daily_data[date_str].append(entry)
    return daily_data

def analyze_daily_weather(daily_data):
    """Compute daily highs, lows, and averages."""
    analysis = {}
    for day, entries in daily_data.items():
        highs = [e['main']['temp_max'] for e in entries]
        lows = [e['main']['temp_min'] for e in entries]
        avg_high = round(statistics.mean(highs), 1)
        avg_low = round(statistics.mean(lows), 1)
        analysis[day] = {
            "highs": highs,
            "lows": lows,
            "avg_high": avg_high,
            "avg_low": avg_low
        }
    return analysis

def calculate_comfort_index(avg_high, avg_low):
    """Simple comfort index from 1-10."""
    # Scale: ideal temp ~ 72°F = 10, hotter/colder lower
    ideal = 72
    avg_temp = (avg_high + avg_low) / 2
    diff = abs(avg_temp - ideal)
    score = max(1, round(10 - (diff / 5), 1))
    return score

def print_weather_report(analysis):
    """Prints a formatted weather report."""
    print("\n=== Weekly Weather Analysis ===")

    # Weekly averages
    all_highs = [v['avg_high'] for v in analysis.values()]
    all_lows = [v['avg_low'] for v in analysis.values()]
    print(f"Average High: {round(statistics.mean(all_highs), 1)}°F")
    print(f"Average Low:  {round(statistics.mean(all_lows), 1)}°F")

    # Hottest / coldest day
    hottest_day = max(analysis.items(), key=lambda x: x[1]['avg_high'])[0]
    coldest_day = min(analysis.items(), key=lambda x: x[1]['avg_low'])[0]
    print(f"Hottest Day:  {hottest_day} ({analysis[hottest_day]['avg_high']}°F)")
    print(f"Coldest Day:  {coldest_day} ({analysis[coldest_day]['avg_low']}°F)")

    print("\nTemperature Trend:")
    print("  Temperatures varied throughout the week.\n")

    print("Comfort Index (1-10 scale):")
    for day, data in analysis.items():
        ci = calculate_comfort_index(data['avg_high'], data['avg_low'])
        print(f"  {day}: {ci}")

    print("\nTemperature Bar Chart (Highs):")
    for day, data in analysis.items():
        bar_length = int(data['avg_high'] // 2)
        print(f"{day[:3]} | {'█' * bar_length} {data['avg_high']}°F")

    print("\nUnusual Weather Days:")
    for day, data in analysis.items():
        if max(data['highs']) - min(data['lows']) > 20:
            print(f"  {day} had large temperature swings ({max(data['highs'])}°F / {min(data['lows'])}°F)")

# =========================
# Main program
# =========================
def main():
    print("Fetching live weather data...")
    data = fetch_weather_data(city, api_key, units)
    if not data:
        print("Failed to retrieve weather data.")
        return

    daily_data = group_by_day(data['list'])
    analysis = analyze_daily_weather(daily_data)
    print_weather_report(analysis)

# Run the program
if __name__ == "__main__":
    main()

# tools.py
# These are the REAL functions that execute when the LLM requests a tool.
# In production: replace with actual API calls (OpenWeather, Exchange Rate API, etc.)
# For this lab: realistic simulated data so no extra API keys are needed.

from __future__ import annotations

# ── Tool 1: Weather ──────────────────────────────────────────────────────
WEATHER_DATA = {
    'islamabad': {'temp': 28, 'condition': 'Partly Cloudy', 'humidity': 55},
    'karachi': {'temp': 34, 'condition': 'Hot and Sunny', 'humidity': 70},
    'lahore': {'temp': 32, 'condition': 'Hazy', 'humidity': 60},
    'london': {'temp': 16, 'condition': 'Overcast', 'humidity': 80},
    'dubai': {'temp': 40, 'condition': 'Clear and Hot', 'humidity': 45},
    'new york': {'temp': 22, 'condition': 'Sunny', 'humidity': 50},
}


def get_weather(city: str, unit: str = 'celsius') -> dict:
    """Return current weather for a city."""
    data = WEATHER_DATA.get(city.lower())
    if not data:
        return {'error': f'No weather data available for {city}'}

    temp = data['temp']
    if unit == 'fahrenheit':
        temp = round(temp * 9 / 5 + 32, 1)

    return {
        'city': city.title(),
        'temperature': f'{temp}°{unit[0].upper()}',
        'condition': data['condition'],
        'humidity': f"{data['humidity']}%",
    }


# ── Tool 2: Currency Converter ───────────────────────────────────────────
RATES = {
    'USD': 278.5,
    'GBP': 352.0,
    'EUR': 303.0,
    'AED': 75.8,
    'SAR': 74.3,
    'PKR': 1.0,
}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert amount between currencies."""
    from_c = from_currency.upper()
    to_c = to_currency.upper()

    if from_c not in RATES or to_c not in RATES:
        return {'error': f'Currency not supported. Supported: {list(RATES.keys())}'}

    pkr_amount = amount * RATES[from_c]
    result = pkr_amount / RATES[to_c]
    return {
        'original': f'{amount} {from_c}',
        'converted': f'{round(result, 2)} {to_c}',
        'rate': f'1 {from_c} = {round(RATES[from_c] / RATES[to_c], 4)} {to_c}',
    }


# ── Tool 3: Flight Cost Estimator ────────────────────────────────────────
FLIGHT_BASE = {
    ('islamabad', 'karachi'): 8500,
    ('islamabad', 'lahore'): 6000,
    ('islamabad', 'dubai'): 35000,
    ('islamabad', 'london'): 85000,
    ('karachi', 'dubai'): 28000,
    ('lahore', 'london'): 80000,
}


def estimate_flight_cost(origin: str, destination: str, passengers: int = 1) -> dict:
    """Estimate economy flight cost between two cities in PKR."""
    key = (origin.lower(), destination.lower())
    rev_key = (destination.lower(), origin.lower())
    base = FLIGHT_BASE.get(key) or FLIGHT_BASE.get(rev_key)

    if not base:
        return {'error': f'Route {origin} to {destination} not available in estimator'}

    total = base * passengers
    return {
        'route': f'{origin.title()} → {destination.title()}',
        'passengers': passengers,
        'per_person': f'PKR {base:,}',
        'total_cost': f'PKR {total:,}',
        'note': 'Economy class estimate. Actual prices may vary.',
    }


# ── Tool 4: Prayer Times ────────────────────────────────────────────────────
PRAYER_TIMES = {
    'islamabad': {
        'Fajr': '04:32 AM', 'Dhuhr': '12:08 PM',
        'Asr': '03:45 PM', 'Maghrib': '06:52 PM', 'Isha': '08:15 PM'
    },
    'karachi': {
        'Fajr': '04:51 AM', 'Dhuhr': '12:18 PM',
        'Asr': '03:52 PM', 'Maghrib': '06:58 PM', 'Isha': '08:20 PM'
    },
    'lahore': {
        'Fajr': '04:22 AM', 'Dhuhr': '12:02 PM',
        'Asr': '03:38 PM', 'Maghrib': '06:45 PM', 'Isha': '08:10 PM'
    },
    'dubai': {
        'Fajr': '04:41 AM', 'Dhuhr': '12:14 PM',
        'Asr': '03:48 PM', 'Maghrib': '06:55 PM', 'Isha': '08:18 PM'
    },
    'london': {
        'Fajr': '03:15 AM', 'Dhuhr': '01:05 PM',
        'Asr': '05:30 PM', 'Maghrib': '09:10 PM', 'Isha': '10:45 PM'
    },
}


def get_prayer_times(city: str, date: str = 'today') -> dict:
    """Return prayer times for a Pakistani or major city."""
    data = PRAYER_TIMES.get(city.lower())
    if not data:
        return {'error': f'No prayer times available for {city}. Supported: Islamabad, Karachi, Lahore, Dubai, London'}
    return {
        'city': city.title(),
        'date': date,
        'Fajr': data['Fajr'],
        'Dhuhr': data['Dhuhr'],
        'Asr': data['Asr'],
        'Maghrib': data['Maghrib'],
        'Isha': data['Isha'],
    }

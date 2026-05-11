# schemas.py
# JSON schemas registered with the LLM via the API.
# The LLM reads ONLY these descriptions to decide when and how to call a tool.
# It never sees the actual Python code in tools.py.

from __future__ import annotations

from tools import convert_currency, estimate_flight_cost, get_weather, get_prayer_times

TOOL_SCHEMAS = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Get current weather for a city. Call this when the user asks about temperature, weather, or travel conditions.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {
                        'type': 'string',
                        'description': 'City name, e.g. Islamabad, Dubai, London',
                    },
                    'unit': {
                        'type': 'string',
                        'enum': ['celsius', 'fahrenheit'],
                        'description': 'Temperature unit. Default: celsius',
                    },
                },
                'required': ['city'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'convert_currency',
            'description': 'Convert an amount between currencies. Call this when the user asks about currency conversion, exchange rates, or costs in a different currency.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'amount': {'type': 'number', 'description': 'Amount to convert'},
                    'from_currency': {'type': 'string', 'description': 'Source currency code, e.g. USD, PKR, GBP'},
                    'to_currency': {'type': 'string', 'description': 'Target currency code'},
                },
                'required': ['amount', 'from_currency', 'to_currency'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'estimate_flight_cost',
            'description': 'Estimate economy flight cost between two cities in PKR. Call when the user asks about flight prices or travel budget.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'origin': {'type': 'string', 'description': 'Departure city'},
                    'destination': {'type': 'string', 'description': 'Arrival city'},
                    'passengers': {'type': 'integer', 'description': 'Number of passengers. Default: 1'},
                },
                'required': ['origin', 'destination'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_prayer_times',
            'description': 'Get prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha) for a city. Call this when the user asks about prayer times, namaz times, salah schedule, or Islamic prayer schedule for any city.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {
                        'type': 'string',
                        'description': 'City name, e.g. Islamabad, Karachi, Lahore, Dubai, London'
                    },
                    'date': {
                        'type': 'string',
                        'description': 'Date for prayer times, e.g. today, tomorrow, 2024-12-01. Default: today'
                    },
                },
                'required': ['city']
            }
        }
    },
]

# Tool dispatcher - maps tool name string -> actual Python function.
TOOL_FUNCTIONS = {
    'get_weather': get_weather,
    'convert_currency': convert_currency,
    'estimate_flight_cost': estimate_flight_cost,
    'get_prayer_times': get_prayer_times,
}

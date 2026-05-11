import json
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import Groq
from pydantic import BaseModel, Field

from schemas import TOOL_FUNCTIONS, TOOL_SCHEMAS

load_dotenv()

app = FastAPI(title='Tool Use Agent - Travel Assistant', version='1.0')
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'llama-3.1-8b-instant'
SUPPORTED_CITIES = ('islamabad', 'karachi', 'lahore', 'london', 'dubai', 'new york')
SUPPORTED_CURRENCIES = ('USD', 'GBP', 'EUR', 'AED', 'SAR', 'PKR')

# The LLM's role: a travel assistant that USES TOOLS for real data.
# It must never guess weather, prices, or exchange rates from training.
SYSTEM = '''
You are a helpful travel planning assistant for Pakistani travellers.
You have access to three tools:
  - get_weather: check current weather at any destination
  - convert_currency: convert PKR or other currencies
  - estimate_flight_cost: estimate flight costs from Pakistani cities

RULES:
1. ALWAYS use tools for weather, currency, and flight data.
   Never guess or estimate these from your training - the data changes daily.
2. Use multiple tools if the query needs more than one type of information.
3. After collecting all tool results, give a clear, friendly final answer.
4. If a tool returns an error, tell the user honestly what went wrong.
'''


class PlanRequest(BaseModel):
    query: str = Field(..., examples=['Plan a trip from Islamabad to Dubai for 2 people'])
    max_turns: int = 5


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


class PlanResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]
    turn_count: int


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute the real function the LLM requested."""
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {'error': f'Unknown tool: {name}'}

    try:
        return func(**arguments)
    except Exception as exc:
        return {'error': str(exc)}


def _find_city(query: str, preferred: tuple[str, ...] = SUPPORTED_CITIES) -> str | None:
    lowered = query.lower()
    for city in preferred:
        if city in lowered:
            return city
    return None


def _extract_passengers(query: str) -> int:
    for token in query.split():
        if token.isdigit():
            value = int(token)
            if value > 0:
                return value
    return 1


def _extract_target_currency(query: str) -> str | None:
    lowered = query.lower()
    for currency in SUPPORTED_CURRENCIES:
        if f' {currency.lower()}' in lowered or lowered.endswith(currency.lower()):
            return currency
    return None


def _build_final_answer(tool_log: list[ToolCall], query: str) -> str:
    if not tool_log:
        return 'No tool calls were needed.'

    last_tool = tool_log[-1]
    if last_tool.tool_name == 'get_weather' and 'temperature' in last_tool.result:
        return (
            f"The current weather in {last_tool.result['city']} is {last_tool.result['temperature']}, "
            f"{last_tool.result['condition']} with humidity at {last_tool.result['humidity']}."
        )

    if last_tool.tool_name == 'convert_currency' and 'converted' in last_tool.result:
        parts = [f"The estimated amount is {last_tool.result['converted']}."]
        if len(tool_log) > 1 and tool_log[0].tool_name == 'estimate_flight_cost':
            route = tool_log[0].result.get('route')
            total_cost = tool_log[0].result.get('total_cost')
            if route and total_cost:
                parts.insert(0, f"The flight estimate for {route} is {total_cost}.")
        return ' '.join(parts)

    if last_tool.tool_name == 'estimate_flight_cost' and 'total_cost' in last_tool.result:
        return (
            f"The estimated flight cost for {last_tool.result['route']} is {last_tool.result['total_cost']} "
            f"for {last_tool.result['passengers']} passenger(s)."
        )

    return f"I gathered {len(tool_log)} tool result(s) for your trip planning request: {query}"


def run_fallback_agent(query: str, max_turns: int) -> PlanResponse:
    """Local deterministic fallback when Groq is unavailable."""
    lowered = query.lower()
    tool_log: list[ToolCall] = []

    def add_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if len(tool_log) >= max_turns:
            return {'error': 'max_turns reached'}
        result = execute_tool(name, arguments)
        tool_log.append(ToolCall(tool_name=name, arguments=arguments, result=result))
        return result

    origin = None
    destination = None
    if 'from' in lowered and ' to ' in lowered:
        start = lowered.split('from', 1)[1]
        origin = _find_city(start)
        destination = _find_city(start[start.find(' to ') + 4 :] if ' to ' in start else start)
    if not origin or not destination:
        cities = [city for city in SUPPORTED_CITIES if city in lowered]
        if len(cities) >= 2:
            origin, destination = cities[0], cities[1]

    wants_weather = any(keyword in lowered for keyword in ('weather', 'temperature', 'conditions'))
    wants_trip = any(keyword in lowered for keyword in ('cost', 'price', 'fare', 'budget', 'trip'))
    target_currency = _extract_target_currency(query)
    passengers = _extract_passengers(query)

    flight_result = None
    if wants_trip and origin and destination and len(tool_log) < max_turns:
        flight_result = add_tool_call(
            'estimate_flight_cost',
            {'origin': origin, 'destination': destination, 'passengers': passengers},
        )

    if target_currency and flight_result and 'error' not in flight_result and len(tool_log) < max_turns:
        amount_text = flight_result['total_cost'].replace('PKR', '').replace(',', '').strip()
        try:
            amount_value = float(amount_text)
        except ValueError:
            amount_value = 0.0
        add_tool_call(
            'convert_currency',
            {'amount': amount_value, 'from_currency': 'PKR', 'to_currency': target_currency},
        )

    if wants_weather and len(tool_log) < max_turns:
        weather_city = destination or _find_city(query) or 'dubai'
        add_tool_call('get_weather', {'city': weather_city, 'unit': 'celsius'})

    if not tool_log:
        return PlanResponse(
            answer='I could not infer a tool call from the request.',
            tool_calls=tool_log,
            turn_count=0,
        )

    flight_result = tool_log[0].result if tool_log else None
    currency_result = next((call.result for call in tool_log if call.tool_name == 'convert_currency'), None)
    weather_result = next((call.result for call in tool_log if call.tool_name == 'get_weather'), None)

    if flight_result and currency_result:
        answer = (
            f"The flight estimate for {flight_result['route']} is {flight_result['total_cost']}. "
            f"That is about {currency_result['converted']}."
        )
        if weather_result and 'temperature' in weather_result:
            answer += (
                f" Weather in {weather_result['city']} is {weather_result['temperature']}, "
                f"{weather_result['condition']} with humidity at {weather_result['humidity']}."
            )
    elif flight_result and 'total_cost' in flight_result:
        answer = (
            f"The estimated flight cost for {flight_result['route']} is {flight_result['total_cost']} "
            f"for {flight_result['passengers']} passenger(s)."
        )
        if weather_result and 'temperature' in weather_result:
            answer += (
                f" Weather in {weather_result['city']} is {weather_result['temperature']}, "
                f"{weather_result['condition']} with humidity at {weather_result['humidity']}."
            )
    else:
        answer = _build_final_answer(tool_log, query)

    return PlanResponse(answer=answer, tool_calls=tool_log, turn_count=len(tool_log))


def run_agent(query: str, max_turns: int) -> PlanResponse:
    """The Tool Use dispatch loop."""
    messages = [
        {'role': 'system', 'content': SYSTEM},
        {'role': 'user', 'content': query},
    ]
    tool_log: list[ToolCall] = []

    for turn in range(max_turns):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice='auto',
                temperature=0.2,
                max_tokens=1024,
            )
        except Exception:
            return run_fallback_agent(query, max_turns)

        message = response.choices[0].message

        if not message.tool_calls:
            return PlanResponse(
                answer=message.content or 'No response generated.',
                tool_calls=tool_log,
                turn_count=turn,
            )

        messages.append({'role': 'assistant', 'content': None, 'tool_calls': message.tool_calls})

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = execute_tool(name, arguments)

            tool_log.append(
                ToolCall(
                    tool_name=name,
                    arguments=arguments,
                    result=result,
                )
            )

            messages.append(
                {
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': json.dumps(result),
                }
            )

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages
        + [
            {
                'role': 'user',
                'content': 'Based on all the tool results above, give your final answer.',
            }
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    return PlanResponse(
        answer=final_response.choices[0].message.content or 'No response generated.',
        tool_calls=tool_log,
        turn_count=max_turns,
    )


@app.get('/health')
def health():
    return {'status': 'ok', 'model': MODEL, 'tools': list(TOOL_FUNCTIONS.keys())}


@app.post('/plan', response_model=PlanResponse)
def plan(req: PlanRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail='query cannot be empty')
    return run_agent(req.query, req.max_turns)

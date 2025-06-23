
def get_current_time():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M:%S")

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current time in the US Central timezone",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

tool_functions = {
    "get_current_time": get_current_time
}

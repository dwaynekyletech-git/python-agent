import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from tools import tool_definitions, tool_functions  # Updated variable name for clarity

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat():
    print("\U0001F9E0 Agent with tools ready! Type something or 'exit' to quit.")
    messages = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})

        # First call to OpenAI to see if a tool needs to be used
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tool_definitions,  # type: ignore
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            # Add the assistant's message with tool calls to the conversation
            messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})
            
            for call in msg.tool_calls:
                tool_name = call.function.name
                if tool_name in tool_functions:
                    result = tool_functions[tool_name]()  # Call the actual Python function

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    })

            # Second call to OpenAI after the tool result is added
            final_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            print("Agent:", final_response.choices[0].message.content)

        else:
            print("Agent:", msg.content)
            messages.append({"role": "assistant", "content": msg.content})

if __name__ == "__main__":
    chat()

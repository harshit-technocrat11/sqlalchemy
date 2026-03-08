import os
from dotenv import load_dotenv
from openai import OpenAI
from agent_tools import  add_task, add_user, update_user, query_tasks, query_users, delete_task, delete_user
from system_prompt import system_prompt

import json
load_dotenv(override=False)

# creating agent
api_key = os.getenv("OPENAI_API_KEY ")

client = OpenAI(api_key=api_key)

system_prompt = system_prompt

# tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_user",
            "description": "Create a new user in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"}
                },
                "required": ["name", "email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a task for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["email", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_users",
            "description": "List all users in the database",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_tasks",
            "description": "Get tasks for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_user",
            "description": "Update user name or email",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "new_name": {"type": "string"},
                    "new_email": {"type": "string"},
                    
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_user",
            "description": "Delete a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task of a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "task_id": {"type": "integer"}
                },
                "required": ["email", "task_id"]
            }
        }
    }
]

# tool map
tool_map = {
    "add_user": add_user,
    "add_task": add_task,
    "query_users": query_users,
    "query_tasks": query_tasks,
    "update_user": update_user,
    "delete_user": delete_user,
    "delete_task": delete_task
}

# agent memory
memory = [
    {"role":"system", "content":system_prompt}
]

# chat function
import json

def chat(user_input):

    # store user message
    memory.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory,
        tools=tools
    )

    message = response.choices[0].message

    # If the model wants to call a tool
    if message.tool_calls:

        # IMPORTANT: store assistant message that contains tool_calls
        memory.append(message)

        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_call_id = tool_call.id

        args = json.loads(tool_call.function.arguments or "{}")

        tool_function = tool_map.get(tool_name)

        if not tool_function:
            return f"Unknown tool requested: {tool_name}"

        try:
            result = tool_function(**args)
        except TypeError:
            result = "Some required information is missing. Please provide the necessary details."

        # Send tool result back to the model
        memory.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": str(result)
        })

        # Second model call → convert tool result to natural language
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=memory
        )

        reply = final_response.choices[0].message.content

        memory.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    else:

        reply = message.content

        memory.append({
            "role": "assistant",
            "content": reply
        })

        return reply

# agent loop
while True:
    user_input = input("🙂You: ")
    
    if user_input.lower() == "exit":
        break

    reply = chat(user_input)

    print("🤖Agent: ", reply)
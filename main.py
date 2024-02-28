import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
organization = os.getenv("OPENAI_ORG_ID")
client = OpenAI(organization=organization, api_key=api_key)


# Function to send an email with a quote
def translate_korean(english, recipient="your@email.com"):
    # Print the quote and recipient for debugging purposes
    print(f"Generated quote:\n {english}\n\nSending via email to: {recipient}")
    # Return a success message
    return "Message sent to " + recipient


# A list of tools used in this script
# Notice the "Function" tool type
tools = [{
    "type": "function",
    "function": {
        "name": "translate_korean",
        "description": "한글로 직독직해 합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "english": {
                    "type": "string",
                    "description": "번역을 시도할 영어 문장."
                }
            },
            "required": [
                "english"
            ]
        }
    }
}]


# Function to get the response from a thread
def get_response(thread):
    """
    This function retrieves the messages from a thread in ascending order.
    Parameters:
    thread (Thread): The thread to retrieve messages from.
    """
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


# Function to create an AI assistant
def create_assistant():
    """
    This function creates an assistant with a specific name, instructions, model, and tools.
    """
    assistant = client.beta.assistants.create(
        name="한글 직독직해 조수",
        instructions="너는 영어를 한글로 직독직해 해주는 전문가야.",
        model="gpt-4-1106-preview",
        tools=tools
    )

    return assistant


# Function to create a thread
def create_thread():
    """
    This function creates a new thread.
    """
    thread = client.beta.threads.create()
    return thread


assistants = client.beta.assistants.list(
    order="desc",
    limit="20",
)

if not assistants.data:
    assistant = create_assistant()
else:
    assistant = assistants.data[0]


# Function to send a message and run the thread
def send_and_run(content):
    """
    This function sends a message to the thread and runs it.
    Parameters:
    content (str): The content of the message to send.
    """
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content,
    )

    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )


# Function to wait for a run to finish
# OpenAI says streaming support coming "soon"
def wait_on_run(run):
    """
    This function waits for a run to finish.
    Parameters:
    run (Run): The run to wait for.
    """
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )

        print(run.status)
        time.sleep(0.5)
    return run


# Create an assistant and thread
assistant = create_assistant()
thread = create_thread()

run = wait_on_run(send_and_run("To whom it may concern,My name is Michael Brown"))

if run.status == "requires_action":
    tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print("Waiting for custom Function:", name)
    print("Function arguments:")
    print(arguments)

    task = translate_korean(**arguments)

    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": "done",
            }
        ],
    )

    run = wait_on_run(run)

    print(get_response(thread))

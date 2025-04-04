import os
import re
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",  # LM Studio local endpoint
    api_key="lm-studio",  # dummy value; LM Studio doesn't validate API keys
)

def llm_call(prompt: str, system_prompt: str = "", model="local-model") -> str:
    """
    Calls the local LM Studio model with the given prompt and returns the response.

    Args:
        prompt (str): The user prompt to send to the model.
        system_prompt (str, optional): The system prompt to send to the model. Defaults to "".
        model (str, optional): The model to use for the call. Defaults to "local-model".

    Returns:
        str: The response from the language model.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=4096,
        temperature=1,
    )
    return response.choices[0].message.content

def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text.

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""

import requests
import json

def interact_with_local_llm(prompt, base_url="http://localhost:11434"):
    """
    Interact with a local LLM using the Ollama API.

    :param prompt: The input prompt for the LLM.
    :param base_url: The base URL of the Ollama API.
    :return: The response from the LLM.
    """
    endpoint = f"{base_url}/api/generate"
    payload = {
        "model": "llama3.2:latest",  # Replace with your model name
        "prompt": prompt,
        "max_tokens": 2048  # Adjust as needed
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        # START OF HIGHLIGHTED SECTION
        # The response might contain multiple JSON objects. We only parse the first line.
        data_lines = response.text.strip().splitlines()
        if data_lines:
            data = json.loads(data_lines[0])
            return data.get('response', '')
        return ''
        # END OF HIGHLIGHTED SECTION
    except requests.exceptions.RequestException as e:

        return None

# Example usage
if __name__ == "__main__":
    prompt = "Hello, how are you?"
    response = interact_with_local_llm(prompt)
    if response:
        print(f"LLM Response: {response}")

from langchain_ollama.chat_models import ChatOllama
import json

with open("Vuori_Final_Approval_2024_09_24.json", "r") as file:
    shap_values_json = json.load(file).get("shap_values")
with open("system.prompt", "r") as file:
    sys_prompt = file.read().strip()

prompt = f"""
{shap_values_json}
"""

chat = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.2",
    system_message=sys_prompt
)

response = chat([{"role": "user", "content": prompt}])
print(response.content)

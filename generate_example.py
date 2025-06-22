from editbench.evaluation import generate_editbench, test_editbench
from json import loads

# 1: define a function to construction the prompt
def prompt_constructor(original_code_content, highlighted_section, user_instruction):
    with open("prompts/python_whole_file.txt", "r") as f:
        template = f.read()
    return template.format(original_code=original_code_content,\
                           highlighted=highlighted_section,\
                            user=user_instruction)
                        


# 2: define a function to generate code snippets given a prompt or question
def generate_from_prompt(prompt, qid):
    example_llm_response = """
```python
def example_function():
    print(1 + 2)
example_function()
```"""
    # Returned code should be a valid Python code snippet
    return example_llm_response.replace("```python\n", "").replace("\n```", "")

# 3: generate and evaluate
generate_editbench(generate_from_prompt, "prompts/python_whole_file.txt", js_only=True)
test_editbench("/root/hf_editbench", "output.json")

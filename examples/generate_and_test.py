from editbench.evaluation import generate_editbench, test_editbench

def some_generation_function_for_your_model(prompt):
    # query the model with the prompt ....
    example_llm_response = """
```python
def example_function():
    print(1 + 2)
example_function()
```"""

    return example_llm_response


# 1: define a function to generate code snippets given the prompt specified in file
#    (in this case: prompts/python_whole_file.txt)
def generate_from_prompt(prompt):
    response = some_generation_function_for_your_model(prompt)
    # Returned code should be a valid Python code snippet
    return response.replace("```python\n", "").replace("\n```", "")


# 2: generate the code snippets for the EVAL_MODEL, store in generations folder
generate_editbench(generate_from_prompt, "prompts/python_whole_file.txt", js_only=True)

# Evaluate code snippets and put results in output file (in this case: output.json)
test_editbench("output.json")

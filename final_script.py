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
def example_generate(prompt, qid):
    example_llm_response = """
```python
def example_function():
    print(1 + 2)
example_function()
```"""
    # Returned code should be a valid Python code snippet
    return example_llm_response.replace("```python\n", "").replace("\n```", "")

def example_move(prompt, qid):
    # if the model generation for each question is stored in a different location, use qid to locate rather than regenerate
    # In this example, I am loading generated files from gpt-o3-mini
    with open("og_mappings.txt") as f:
        og_mappings = loads(f.read())
    pair_id = og_mappings[str(qid)]

    try:
        example_path = f"/project/EditBench/EditBenchEvaluations/EditBench_generations/gpt-o3-mini/{pair_id}.py"
        with open(example_path, "r") as f:
            content = f.read()
    except Exception:
        try:
            example_path = f"/project/EditBench/EditBenchEvaluations/EditBench_generations_js/gpt-o3-mini/{pair_id}.js"
            with open(example_path, "r") as f:
                content = f.read()
        except Exception:
            raise Exception(f"File not found for pair_id: {pair_id}\tqid: {qid}")
    
    return content 


# 3: generate and evaluate
generate_editbench(example_move, prompt_constructor, "/root/hf_editbench")
test_editbench("/root/hf_editbench", "output.json")


# 4? give a function to only generate code snippets to a directory to make #2 example_move easier 
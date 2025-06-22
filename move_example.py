from editbench.evaluation import generate_editbench, test_editbench
from json import loads

# 1: define a function to construction the prompt
def prompt_constructor(original_code_content, highlighted_section, user_instruction):
    with open("prompts/python_whole_file.txt", "r") as f:
        template = f.read()
    return template.format(original_code=original_code_content,\
                           highlighted=highlighted_section,\
                            user=user_instruction)
                        


# 2: define a function to 
def move_existing_generations(prompt, qid):
    # if the model generation for each question is stored in a different location, use qid to locate rather than regenerate
    # In this example, I am loading generated files from gpt-o3-mini
    with open("pairid_to_qid_mappings.txt") as f:
        og_mappings = loads(f.read())
    pair_id = og_mappings[str(qid)]

    try:
        example_path = f"/project/EditBenchEvaluations/EditBench_generations/gpt-o3-mini/{pair_id}.py"
        with open(example_path, "r") as f:
            content = f.read()
    except Exception:
        try:
            example_path = f"/project/EditBenchEvaluations/EditBench_generations_js/gpt-o3-mini/{pair_id}.js"
            with open(example_path, "r") as f:
                content = f.read()
        except Exception:
            raise Exception(f"File not found for pair_id: {pair_id}\tqid: {qid}")
    
    return content 


# 3: generate and evaluate
generate_editbench(move_existing_generations, "prompts/python_whole_file.txt",)
# test_editbench("/root/hf_editbench", "output.json")

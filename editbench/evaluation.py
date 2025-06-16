import json
import subprocess
import threading
import time
import shutil
import sys
import re

from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from copy import deepcopy
from datasets import load_dataset
from datasets.utils.logging import disable_progress_bar, enable_progress_bar
from pathlib import Path
from tqdm import tqdm

def modify_test_utils_content(file_content):
    """
    Modify the patterns list in the test_utils.py file content to include
    all implementation_*.py files, even those with periods in the name.
    """
    # Find the patterns list
    patterns_regex = re.compile(
        r'(patterns\s*=\s*\[\s*)(.*?)(\s*\])',
        re.DOTALL
    )
    
    # New pattern to add - this matches implementation_ followed by any characters (including periods)
    # until the final .py extension
    new_pattern = r"r'implementation_.*?\.py'"
    
    def replacement_function(match):
        pattern_list_start = match.group(1)
        pattern_list_content = match.group(2)
        pattern_list_end = match.group(3)
        
        # Check if our new pattern is already there or if the content already matches implementation_*
        if new_pattern not in pattern_list_content and "implementation_" not in pattern_list_content:
            # Add the new pattern to the list
            if pattern_list_content.strip().endswith(','):
                new_pattern_list = pattern_list_content + '\n    ' + new_pattern
            else:
                new_pattern_list = pattern_list_content + ',\n    ' + new_pattern
            
            return pattern_list_start + new_pattern_list + pattern_list_end
        
        # If pattern is already there, return the original
        return match.group(0)
    
    # Find and replace the patterns list
    new_content = patterns_regex.sub(replacement_function, file_content)
    
    # Check if any changes were made
    was_modified = new_content != file_content
    
    return new_content 

def create_question_folders(test_directory):
    data = load_dataset("waynechi/project-edit", split="test")
    existing_ids = [int(d.name) for d in test_directory.glob("*")]

    for question in tqdm(data, desc=" directories and test files"):
        if question['problem_id'] in existing_ids:
            continue
        
        curr_dir = test_directory / str(question['problem_id'])
        curr_dir.mkdir()

        if question["programming_language"] == "python":
            with open(curr_dir / "requirements.txt", "w") as f:
                f.write(question['requirements'])
            with open(curr_dir / "test_utils.py", "w") as f:
                f.write(modify_test_utils_content(question['test_utils']))
            with open(curr_dir / "conftest.py", "w") as f:
                f.write(question['conftest']) 
            with open(curr_dir / "test_code.py", "w") as f:
                f.write(question['test_code']) 

        elif question["programming_language"] == "javascript":
            with open(curr_dir / "package.json", "w") as f:
                f.write(question['package_json'])
            with open(curr_dir / "jest-setup.js", "w") as f:
                f.write(question['jest_setup'])
            
            test_folder = curr_dir / "tests"
            test_folder.mkdir()
            if 'react' in question['original_code']:
                with open(test_folder / "test_code.test.js", "w") as f:
                    f.write(question['test_code'])
            else:
                with open(test_folder / "test_code.test.js", "w") as f:
                    f.write(question['test_code'])

            for file_name, file_content in question['other_files'].items():
                if file_content is None:
                    continue
                other_file = curr_dir / file_name
                other_file.parent.mkdir(parents=True, exist_ok=True)
                with open(other_file, "w") as f:
                    f.write(file_content)

        else:
            # what is this
            continue

def populate_question_folders(generation_function, prompt_create_fn, test_directory):
    data = load_dataset("waynechi/project-edit", split="test")
    disable_progress_bar()
    for question in tqdm(data, desc="Generating code for questions"):
    # for dir in tqdm(list(test_directory.glob("*")), desc="Generating code for directories"):
        # id = int(dir.name)
        # question = data.filter(lambda x: x['problem_id'] == id)[0]
        id = question['problem_id']
        prompt = prompt_create_fn(question["original_code"],\
                         question["highlighted_code"],\
                         question["instruction"])
        generated_code = generation_function(prompt, id)

        dir = test_directory / str(id)
        if question["programming_language"] == "python":
            with open(dir / "implementation1.py", "w") as f:
                f.write(generated_code)
        elif question["programming_language"] == "javascript":
            with open(dir / "implementation1.js", "w") as f:
                f.write(generated_code)
    enable_progress_bar()

def generate_editbench(generation_function, prompt_create_fn, test_directory):
    output_dir = Path(test_directory)

    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"Output path {test_directory} is not a directory.")

    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    create_question_folders(output_dir)
    populate_question_folders(generation_function, prompt_create_fn, output_dir)




#########################################################################################


def test_editbench(test_directory, output_file):
    dir = Path(test_directory)
    run_tests(dir)
    parse_results(dir, output_file)


def parse_results(dir, output_file):
    import math
    # Parse the results from the test files
    results = {}
    model = "1" # JUST IMPLE 1 FOR NOW
    for q_dir in dir.glob("*"):
        id = int(q_dir.name)
        try:
            with open(q_dir / "test_results.json", "r") as f:
                file_data = json.load(f)
                results_dict = file_data["results"][f"implementation{model}"]
                # fields = "passed", "failed", "skipped", "total"
                results[id] = results_dict["passed"]/(results_dict["total"] + results_dict["skipped"])
            
        except FileNotFoundError as e:
            print(f"No results in {q_dir}")
            continue
        except KeyError as e:
            print(f"No results in {q_dir}")
            continue
    
    n_tests = len(results)
    results_floats = [v for k, v in results.items()]
    print("======== Results for Curr Batch ========")
    print(f"Number of tests: {n_tests}")
    print(f"{sum(1 for item in results_floats if item == 1.0)} perfect")
    print(f"{sum(v for v in results_floats)/n_tests} average score")

    print("======== Results Over All Batches ========")
    try:
        with open(output_file, "r") as f:
            old_results = json.load(f)
        
        all_results = old_results | results # if both have same key, the latter will overwrite the former
        n_tests = len(all_results)
        results_floats = [v for k, v in all_results.items()]
        print(f"Number of tests: {n_tests}")
        print(f"{sum(1 for item in results_floats if item == 1.0)} perfect")
        print(f"{sum(v for v in results_floats)/n_tests} average score")
    except Exception as e:
        # if the file doesn't exist, just save the current results
        print("No previous results found, saving current results")
        print(str(e))
        all_results = results
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=4, sort_keys=True)

PYTHON_311_PAIR_IDS = [
    '2024be6d-a509-4d2d-8c14-65818077eeee', "01c959a6-4f94-440a-a9dc-2194081dec02",\
    "e37b7c05-1abd-4243-9aee-e64ac1e7a5dc", "1c297716-3352-4366-b42e-c08393a12dd7", # session 1\ 
    "570dbdd9-5ae7-4b78-8ac9-fe3dbc3e0d31", "bd6aa2bd-6263-4199-ae98-58985ece0a8d",\
    "23690246-b1d2-4562-8239-3c305a3fa8a6", "253c3ee4-45ea-4070-8295-37cca39d1f0d",\
    "0aa1b02d-5377-483e-ad5a-fc667b674026", "0303e411-adc8-4745-bfcd-ef70540eeab0",\
    "3f0420a7-edea-4691-930a-98528bb43b66", "b265eeb8-d93f-4421-8547-33072f844005",\
    "464ca983-1222-45fc-a913-ede9ea14d1ec", #session 2\
    "facdffb8-badf-4efd-a983-f739c7bcb84d", "0571f85f-b386-4ecd-808b-4a3ede77753d", #session 3\
]
def get_python_commands(dir):
    """Generate commands with customizable arguments"""
    mapping = {
        "1": "5fb690e4-ef4d-4b97-829d-2b5b69ecc47a",
        "2": "aaec5f76-d35d-47f7-9931-c493eabf50ab",
        "3": "2da0c136-98b0-4708-98e3-29010f44cd8e",
        "4": "f4671d46-32af-40a7-a967-7cde49dd6d9c",
        "5": "8db7172d-cd1b-45d5-bf88-f7ce41c1d407",
        "6": "efeb069b-bc04-4835-9f8e-0bae13c84899",
        "7": "ee5cd234-fc95-4004-b2b7-dc6638479255",
        "8": "2b8db567-f99f-41e0-b1ea-f3aff0e916ac",
        "9": "e37b7c05-1abd-4243-9aee-e64ac1e7a5dc",
        "10": "a69fb763-9cc8-4fde-85d7-04eb2612a416",
        "11": "aaeb7c59-d104-4dc8-bbd7-6d7851f30bc0",
        "12": "c47c64a9-45fa-48a0-962d-90ff54589f68",
        "13": "eb9dd499-c98e-4895-8e0e-0f6efc811f5b",
        "14": "5bef7d2a-e642-4fe7-90ec-b2a1b5981674",
        "15": "20b55ad2-df3d-4d7c-b7b1-f22cdfc83f1d",
        "16": "f70f8e86-0972-4e63-8df4-75454f9bb2f8",
        "17": "c2cb31c6-6a17-410a-8eea-d865cc814f65",
        "18": "81c3950c-5435-4df9-8ac5-70c66f15f53f",
        "19": "595fc9c3-9b6c-4431-b764-ed1196b09ae4",
        "20": "f55bb22f-375c-4d4a-b433-2fa2a2c21cdb",
        "21": "236e868d-4337-4209-af8d-6eb3a0bda68c",
        "22": "b7bf5aaf-ce47-4e70-acb8-a274bf7fbe11",
        "23": "1ea4ea73-9e6a-4756-953c-e9a4cafab7e3",
        "24": "69d88449-c626-4eb7-bb84-1173ab1566b0",
        "25": "0772e506-05b1-4b50-887f-ec544255acc4",
        "26": "19142f56-4045-4a87-b089-3ac1dfd1286f",
        "27": "e1b72a5a-7771-4067-bd62-d5a76ea1f361",
        "28": "c94c9103-c3da-4046-93df-9c95b42665ee",
        "29": "3055b642-462a-49b7-9860-a2b464b1b996",
        "30": "e65a8560-c13a-416a-9c27-24c65c3e186c",
        "31": "abc3416e-2f9e-4020-8941-1137c9551661",
        "32": "b81465fb-fcc0-4ac5-b174-5324e0eefced",
        "33": "49fb5a8d-adc7-419f-b044-155aa71ed646",
        "34": "715c4262-31a7-4411-bba2-947b774df28a",
        "35": "f1ea813b-f488-458f-9d74-4fc20adef01d",
        "36": "1b81571e-9242-4e8c-9218-7f6cbb27c438",
        "37": "b20c0bc5-c0ee-474f-8b70-b1add1ec332f",
        "38": "2024be6d-a509-4d2d-8c14-65818077eeee",
        "39": "376b0f8b-4ec0-4c25-8dcb-535fed1bae6f",
        "40": "0e233ddb-dc36-48ab-9763-a64b557ced50",
        "41": "dd8f4850-3299-4f6d-a2b1-adaba64cb514",
        "42": "e01f07e6-8374-4a6c-af5c-b030928e22a8",
        "43": "185d9b56-a325-4668-906d-33f730cdaa4f",
        "44": "3d82ff05-72e5-4727-8ed2-3fd2cd7eb7b2",
        "45": "1c297716-3352-4366-b42e-c08393a12dd7",
        "46": "ca3f4858-6d1a-486f-9612-1c94c9f30dc7",
        "47": "b872cb03-3d61-4003-b677-36b8f52ed6d4",
        "48": "08ac9457-b14f-4441-8af7-766a6c8185fa",
        "49": "01c959a6-4f94-440a-a9dc-2194081dec02",
        "50": "8088ff27-5504-4f39-86e0-ae2e65c9808c",
        "51": "de765e5c-a7f8-40e0-9a5b-27fa797e792a",
        "52": "f21b63ad-869a-4792-95b8-6fadf49dd913",
        "53": "f7a75003-0b8b-4cab-a907-784d8fefd00b",
        "54": "b8451da4-d914-442a-9eb5-6982148c1cab",
        "55": "f94d614e-4ea3-4da5-917f-6c7b9c8f1c99",
        "56": "81792a84-bde9-4cd1-8c0b-1d130c2e7704",
        "57": "0c551ff2-0f75-437a-89dd-935a2b3ef2a8",
        "58": "5c187fc7-9fe4-4403-9789-d3a4acde510b",
        "59": "a4f455b3-bd38-46fa-bae8-db215c209090",
        "60": "d76949d9-219b-4b6c-94ce-341d9f4e0bbe",
        "61": "0033f9c3-0f7c-4e24-b81a-881cc52cd7c5",
        "62": "4e3f1b8a-f076-4303-b03a-afa7cefe849c",
        "63": "27a0b3f7-096c-4fa2-b0ca-239042644c72",
        "64": "bd569d06-6f82-4b7d-b23b-8ed4da06ef2d",
        "65": "3f0420a7-edea-4691-930a-98528bb43b66",
        "66": "18312d1b-1bfd-4b5a-92f1-ba94a96a5480",
        "67": "b91e2aca-3dff-4ac5-b25b-a6366cd09597",
        "68": "f2ca4bc4-ac7d-4ccc-8605-5810bc41c779",
        "69": "fecc8ccf-c562-48d5-ac92-44c9dd195f21",
        "70": "bd8bfcc9-dbc2-4c85-b17b-3417ee12766e",
        "71": "4ae659e2-6fed-4d59-9409-5c684bf468e2",
        "72": "db020fb0-2fab-43d0-b8a5-fc6b5550377d",
        "73": "2b667530-3b73-4391-88f8-d18c31c83ae9",
        "74": "741ad8bd-9dda-4bdb-8d90-32bd58aa88de",
        "75": "01c217fa-9602-4f66-89ed-bfb2bc27e78f",
        "76": "e276fad9-fca5-4a08-9862-486e5ec4a066",
        "77": "e762b27b-af07-4aaf-a958-894e0b550035",
        "78": "1e8df9bb-9f72-424b-b6a1-641ae65ea396",
        "79": "b265eeb8-d93f-4421-8547-33072f844005",
        "80": "a6fc49b8-3026-48ae-979d-4592dace9502",
        "81": "0aa1b02d-5377-483e-ad5a-fc667b674026",
        "82": "199c6df9-6f8a-4216-8840-6a63142dad95",
        "83": "570dbdd9-5ae7-4b78-8ac9-fe3dbc3e0d31",
        "84": "23690246-b1d2-4562-8239-3c305a3fa8a6",
        "85": "6ac7d003-ec6a-41c3-a02d-1993594c8764",
        "86": "a73194a4-7d81-4468-867a-ba2177bf0e0c",
        "87": "c7b46b7a-fcc6-4218-8e6e-4ebceb0f143b",
        "88": "35347929-a470-4d8b-b402-2da7bf67318b",
        "89": "8dce0c1b-581e-4810-8b5c-42a090974e50",
        "90": "8615fab0-89e5-4593-b3f6-6aaa15efcf20",
        "91": "9e24a1c9-9b9e-446f-8a57-cc8cd09bc904",
        "92": "0303e411-adc8-4745-bfcd-ef70540eeab0",
        "93": "f2ef250f-9778-47ca-a46e-493006a57172",
        "94": "bd6aa2bd-6263-4199-ae98-58985ece0a8d",
        "95": "facdffb8-badf-4efd-a983-f739c7bcb84d",
        "96": "c3288d33-28df-45be-80c4-4ef40f8d053a",
        "97": "a041b30c-5f4a-4277-b9db-fb5ed3665624",
        "98": "ee78cd6a-363d-4720-a8ea-001ef6d04bba",
        "99": "24eea91f-b150-44ed-bde4-f3419937475b",
        "100": "7959e246-5f7f-4791-a086-80fe6e6f5c9f",
        "101": "4bc40209-f500-4b5a-929a-58714457164c",
        "102": "86a85d44-b1c0-4bee-a903-b46316eb8a86",
        "103": "0571f85f-b386-4ecd-808b-4a3ede77753d",
        "104": "306d7550-535c-47c0-b87e-b558b76d71e5",
        "105": "236664fb-a735-4808-aa25-a59e577ffb56",
        "106": "8a1d2574-c531-4520-b075-f85ff47ece80",
        "107": "c7d5db0e-1be4-481b-aab1-a0331f1b2939",
        "108": "ddc51039-4460-495f-8081-d668edb1fd42",
        "109": "8182a3aa-7d0a-462a-935d-b19b1129e708",
        "110": "4dd2d147-0e00-4542-a8d2-619cfc23a836",
        "111": "c1ac2858-57cd-400e-807a-79ca9db02179",
        "112": "c0f0ec9c-7fd2-4713-85b3-a117176c1a9b",
        "113": "c7f2ad26-828e-4bc0-a2d1-ec8171ff195a"
    }
    pair_id = mapping[dir.name]
    if pair_id in PYTHON_311_PAIR_IDS:
        # Use Python 3.11 for these pair_ids
        python_version = "3.11"
    else:
        python_version = "3.12"

    venv_path = str(dir / ".venv/bin/python")
    test_path = str(dir / "test_code.py")
    req_path = str(dir / "requirements.txt")
    tmp_dir = str(dir / "container_tmp")
    bind = f"{dir}:{dir},{tmp_dir}:/tmp,/data/user_data/rshar/.cache:/data/user_data/rshar/.cache"
    dir_str = str(dir)

    base_singularity_cmd = []

    remove_venv_cmd = deepcopy(base_singularity_cmd) + ["rm", "-rf", ".venv"]
    remove_results_cmd = deepcopy(base_singularity_cmd) + ["rm", "test_results.json"]
    setup_venv_cmd = deepcopy(base_singularity_cmd) + ["uv", "venv", "--python", python_version]
    install_deps_cmd = deepcopy(base_singularity_cmd) + ["uv", "pip", "install", "--python", venv_path,"-r", req_path]
    run_tests_cmd = deepcopy(base_singularity_cmd) + [venv_path, "-m", "pytest", test_path, "-v", "-s"]
    
    # return [remove_venv_cmd, remove_results_cmd, #remove_container, mk_container, chmod_container,\
    #          setup_venv_cmd, install_deps_cmd, run_tests_cmd]
    return [setup_venv_cmd, install_deps_cmd, run_tests_cmd, remove_venv_cmd]

def get_javascript_commands(dir):
    install_cmd = ["npm", "install"]
    test_cmd = ["npm", "test"]

    return [install_cmd, test_cmd]

def run_sandbox_test(dir, lang, print_output=True, timeout=600):
    """Run tests for a single sandbox"""
    # I think for singularity, no need with docker?
    # tmp_dir = dir / "container_tmp"
    # # Remove the directory completely if it exists
    # if tmp_dir.exists():
    #     shutil.rmtree(tmp_dir)
    # # Create a fresh empty directory
    # tmp_dir.mkdir(parents=True, exist_ok=True)
    # # Set permissions
    # tmp_dir.chmod(0o777)

    if lang == "python":
        commands = get_python_commands(dir)
    elif lang == "javascript":
        commands = get_javascript_commands(dir)

    try:
        # Run each command in sequence
        command_outputs = []
        for command in commands:
            result = subprocess.run(
                command, 
                cwd=dir,
                check=False,  # Don't raise an exception on error
                stdout=subprocess.PIPE,  # Capture stdout
                stderr=subprocess.PIPE,  # Capture stderr
                text=True,  # Return strings rather than bytes
                timeout=timeout
            )
            command_outputs.append(result)
            
        with open(dir / "test_stdout.txt", "w") as f:
            for output in command_outputs:
                f.write(f"=== Command: {' '.join(output.args)} ===\n")
                f.write(f"=== Command output ===\n{output.stdout}\n")
                if output.stderr:
                    f.write(f"=== Command error ===\n{output.stderr}\n")

        if print_output:
            print(f"=========== {str(dir)} ===========")
            for output in command_outputs:
                print("=== Command: ", " ".join(output.args), " ===")
                print(f"=== Command output ===\n{output.stdout}")
                if output.stderr:
                    print(f"=== Command error ===\n{output.stderr}")
        return f"Ran tests for {str(dir)}"
    except subprocess.CalledProcessError as e:
        if "install" in str(e):
            # Handle pytest errors
            return f"Error installing dependencies in {str(dir)}: {e}"
        else:
            return f"failed running sandbox {str(dir)}: {e}"

# def watchdog_monitor(futures_dict, max_runtime=1200):  # 20-minute default max runtime
#     """Monitor running tasks for overall deadlock"""
#     start_time = time.time()
#     active_futures = set(futures_dict.keys())
    
#     while active_futures and (time.time() - start_time < max_runtime):
#         # Check which futures are still running
#         still_running = {f for f in active_futures if not f.done()}
        
#         # Update our set of active futures
#         active_futures = still_running
        
#         if not active_futures:
#             break  # All done
        
#         # Report long-running tasks
#         elapsed = time.time() - start_time
#         if elapsed > max_runtime / 2:  # Halfway warning
#             print(f"\nWARNING: Jobs running for {elapsed:.1f} seconds. Still waiting on {len(active_futures)} tasks:")
#             for f in active_futures:
#                 print(f"  - Sandbox {futures_dict[f]}")
                
#         time.sleep(60)  # Check every minute
    
#     # If we're here and have active futures, we've timed out
#     if active_futures:
#         print(f"\n!!! GLOBAL TIMEOUT: {len(active_futures)} tasks still running after {max_runtime} seconds")
#         for f in active_futures:
#             print(f"  - Cancelling sandbox {futures_dict[f]}")
#             f.cancel()
#         return False
    
#     return True

def run_tests(test_directory, max_workers=2):
    """Run tests in parallel using ThreadPoolExecutor"""
    futures_dict = {}
    errored_out = []

    questions = load_dataset("waynechi/project-edit", split="test")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs to the executor
        for question in tqdm(questions, desc="Running tests"):
            dir = test_directory / str(question['problem_id'])

            future = executor.submit(
                run_sandbox_test,
                dir,
                question["programming_language"],
                print_output=True,
                timeout=630,
            )
            futures_dict[future] = dir
        
        # watchdog = threading.Thread(
        #     target=watchdog_monitor, 
        #     args=(futures_dict,),
        #     daemon=True
        # )
        # watchdog.start()
        
        # Process results as they complete
        for future in tqdm(
            as_completed(futures_dict), 
            total=len(questions),
            desc="Running tests",
            unit="sandbox"
        ):
            sandbox_id = futures_dict[future]
            try:
                result = future.result()
                # print(result)
            except Exception as exc:
                # print(f"{sandbox_id} generated an exception: {exc}")
                errored_out.append(sandbox_id)

        # watchdog.join(timeout=10)
    
    if errored_out:
        print(f"Errored out sandboxes: {len(errored_out)}")
        for sandbox in errored_out:
            print(f"  - {sandbox}")

import json
import subprocess
import threading
import time
import shutil
import sys
import re

from os import getenv
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from datasets import load_dataset
from datasets.utils.logging import disable_progress_bar, enable_progress_bar
from pathlib import Path
from tqdm import tqdm

# path inside the docker container
TEST_DIR = Path("/root/editbench_sandboxes")


def create_question_folders(js_only=False):
    data = load_dataset("copilot-arena/EditBench", split="test")
    generation_folder = Path(getenv("WORKDIR"), "generations", getenv("EVAL_MODEL"))

    for question in tqdm(data, desc="Creating testing sandboxes"):
        if question["programming_language"] == "python" and js_only:
            continue

        curr_dir = TEST_DIR / str(question["problem_id"])
        curr_dir.mkdir(parents=True, exist_ok=True)

        qid_content = generation_folder / str(question["problem_id"])
        if not qid_content.exists():
            raise FileNotFoundError(
                f"Generation for {qid_content/ 'qid.txt'} does not exist. Please run the generation function first."
            )

        with open(qid_content, "r") as f:
            generated_code = f.read()

        if question["programming_language"] == "python":
            with open(curr_dir / "requirements.txt", "w") as f:
                f.write(question["requirements"])
            with open(curr_dir / "test_code.py", "w") as f:
                f.write(question["test_code"])
            with open(curr_dir / "original_code.py", "w") as f:
                f.write(question["original_code"])
            with open(curr_dir / "implementation1.py", "w") as f:
                f.write(generated_code)

        elif question["programming_language"] == "javascript":
            with open(curr_dir / "original_code.js", "w") as f:
                f.write(question["original_code"])
            with open(curr_dir / "implementation1.js", "w") as f:
                f.write(generated_code)

            test_folder = curr_dir / "tests"
            test_folder.mkdir(exist_ok=True)
            with open(test_folder / "test_code.test.js", "w") as f:
                f.write(question["test_code"])

        elif question["programming_language"] == "javascript/react":
            with open(curr_dir / "original_code.jsx", "w") as f:
                f.write(question["original_code"])
            with open(curr_dir / "implementation1.jsx", "w") as f:
                f.write(generated_code)

            test_folder = curr_dir / "tests"
            test_folder.mkdir(exist_ok=True)
            with open(test_folder / "test_code.test.js", "w") as f:
                f.write(question["test_code"])
        else:
            print(
                f"Unsupported programming language: {question['programming_language']}"
            )
            continue

        for file_name, file_content in question["test_harness"].items():
            if file_content is None:
                continue
            other_file = curr_dir / file_name
            other_file.parent.mkdir(parents=True, exist_ok=True)
            with open(other_file, "w") as f:
                f.write(file_content)


def generate_editbench(generation_function, prompt_file, js_only=False):
    output_dir = Path(getenv("WORKDIR"), "generations", getenv("EVAL_MODEL"))
    data = load_dataset("copilot-arena/EditBench", split="test")
    with open(prompt_file, "r") as f:
        prompt_template = f.read()

    disable_progress_bar()
    for question in tqdm(data, desc="Generating code for questions"):
        id = question["problem_id"]

        prompt = prompt_template.format(
            original_code=question["original_code"],
            highlighted_code=question["highlighted_code"],
            instruction=question["instruction"],
        )
        generated_code = generation_function(prompt)

        file_name = output_dir / str(id)
        if question["programming_language"] == "python":
            if js_only:
                continue
            with open(file_name, "w") as f:
                f.write(generated_code)
        elif question["programming_language"] == "javascript":
            with open(file_name, "w") as f:
                f.write(generated_code)
        elif question["programming_language"] == "javascript/react":
            with open(file_name, "w") as f:
                f.write(generated_code)

    enable_progress_bar()


#########################################################################################


def test_editbench(output_file, js_only=False):
    create_question_folders(js_only=js_only)
    run_tests()
    parse_results(output_file)


def parse_results(output_file):
    dir = TEST_DIR
    results = {}
    model = "1"  # since we just call the test file "implementation1.py"
    for q_dir in dir.glob("*"):
        id = int(q_dir.name)
        try:
            with open(q_dir / "test_results.json", "r") as f:
                file_data = json.load(f)
                results_dict = file_data["results"][f"implementation{model}"]
                # fields = "passed", "failed", "skipped", "total"
                results[id] = results_dict["passed"] / (
                    results_dict["total"] + results_dict["skipped"]
                )

        except FileNotFoundError as e:
            print(f"No results in {q_dir}")
            continue
        except KeyError as e:
            print(f"No results in {q_dir}")
            continue

    n_tests = len(results)
    results_floats = [v for k, v in results.items()]
    num_perfect = sum(1 for item in results_floats if item == 1.0)
    print("======== Results ========")
    print(f"Number of tests: {n_tests}")
    print(f"{num_perfect} perfect")
    print(f"{num_perfect / n_tests * 100:.2f}% pass rate")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4, sort_keys=True)


def get_python_commands(dir, python_version):
    """Generate commands with customizable arguments"""

    venv_path = str(dir / ".venv/bin/python")
    test_path = str(dir / "test_code.py")
    req_path = str(dir / "requirements.txt")

    setup_venv_cmd = ["uv", "venv", "--python", python_version]
    install_deps_cmd = ["uv", "pip", "install", "--python", venv_path, "-r", req_path]
    run_tests_cmd = [venv_path, "-m", "pytest", test_path, "-v", "-s"]
    remove_venv_cmd = ["rm", "-rf", ".venv"]

    return [setup_venv_cmd, install_deps_cmd, run_tests_cmd, remove_venv_cmd]


def get_javascript_commands(dir):
    install_cmd = ["npm", "install"]
    test_cmd = ["npm", "test"]

    return [install_cmd, test_cmd]


def run_sandbox_test(dir, lang, python_version, print_output=False, timeout=600):
    """Run tests for a single sandbox"""
    if lang == "python":
        commands = get_python_commands(dir, python_version)
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
                timeout=timeout,
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


def run_tests(max_workers=4):
    """Run tests in parallel using ThreadPoolExecutor"""
    futures_dict = {}
    errored_out = []

    questions = load_dataset("copilot-arena/EditBench", split="test")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs to the executor
        for question in tqdm(questions, desc="Creating test threads"):
            dir = TEST_DIR / str(question["problem_id"])

            future = executor.submit(
                run_sandbox_test,
                dir,
                question["programming_language"],
                question["python_version"],
                print_output=False,
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
            unit="sandbox",
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

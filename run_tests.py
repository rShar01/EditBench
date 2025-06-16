import json
import subprocess
import threading
import time
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from tqdm import tqdm
from copy import deepcopy
from common import *
from utils import get_research_df, map_pair_id_to_sandbox_id
from pathlib import Path


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

MANIM_QUESTIONS = [
    "0571f85f-b386-4ecd-808b-4a3ede77753d", "bd6aa2bd-6263-4199-ae98-58985ece0a8d",\
    "0aa1b02d-5377-483e-ad5a-fc667b674026","0303e411-adc8-4745-bfcd-ef70540eeab0"
]

def parse_results(pair_ids):
    import math
    pair_id_sandbox_map = map_pair_id_to_sandbox_id()
    for model in MODELS:
        save_path = DATA_DIR / f"{model}.json"
        # Parse the results from the test files
        results = {}
        for pair_id in pair_ids:
            curr_sandbox_dir =  pair_id_sandbox_map[pair_id]
            print(f"Parsing results in {curr_sandbox_dir}")
            # Run the test command
            try:
                with open(curr_sandbox_dir / "test_results.json", "r") as f:
                    file_data = json.load(f)
                    results_dict = file_data["results"][f"implementation_{model}"]
                    # fields = "passed", "failed", "skipped", "total"
                    results[pair_id] = results_dict["passed"]/(results_dict["total"] + results_dict["skipped"])
                
            except FileNotFoundError as e:
                print(f"No results in {curr_sandbox_dir}")
                continue
            except KeyError as e:
                print(f"No results in {curr_sandbox_dir}")
                continue
        
        n_tests = len(results)
        results_floats = [v for k, v in results.items()]
        print("======== Results for Curr Batch ========")
        print(f"Number of tests: {n_tests}")
        print(f"{sum(1 for item in results_floats if item == 1.0)} perfect")
        print(f"{sum(v for v in results_floats)/n_tests} average score")

        if save_path is not None:
            print("======== Results Over All Batches ========")
            try:
                with open(save_path, "r") as f:
                    old_results = json.load(f)
                
                all_results = old_results | results # if both have same key, the latter will overwrite the former
                n_tests = len(all_results)
                results_floats = [v for k, v in all_results.items()]
                print(f"Number of tests: {n_tests}")
                print(f"{sum(1 for v in results_floats if math.isclose(1, v))} close to perfect")
                print(f"{sum(1 for item in results_floats if item == 1.0)} perfect")
                print(f"{sum(v for v in results_floats)/n_tests} average score")
            except Exception as e:
                # if the file doesn't exist, just save the current results
                print("No previous results found, saving current results")
                print(str(e))
                all_results = results
            with open(save_path, "w") as f:
                json.dump(all_results, f, indent=4, sort_keys=True)


def get_commands(pair_id, sandbox_dir, additional_pytest_args=None):
    """Generate commands with customizable arguments"""
    if additional_pytest_args is None:
        additional_pytest_args = []

    if pair_id in PYTHON_311_PAIR_IDS:
        python_version = "3.11"
    else:
        python_version = "3.12"

    venv_path = str(sandbox_dir / ".venv/bin/python")
    test_path = str(sandbox_dir / "test_code.py")
    req_path = str(sandbox_dir / "requirements.txt")
    tmp_dir = str(sandbox_dir / "container_tmp")
    bind = f"{sandbox_dir}:{sandbox_dir},{tmp_dir}:/tmp,/data/user_data/rshar/.cache:/data/user_data/rshar/.cache"
    sandbox_dir_str = str(sandbox_dir)

    base_singularity_cmd = []

    remove_venv_cmd = deepcopy(base_singularity_cmd) + ["rm", "-rf", ".venv"]
    remove_results_cmd = deepcopy(base_singularity_cmd) + ["rm", "test_results.json"]
    setup_venv_cmd = deepcopy(base_singularity_cmd) + ["uv", "venv", "--python", python_version]
    install_deps_cmd = deepcopy(base_singularity_cmd) + ["uv", "pip", "install", "--python", venv_path,"-r", req_path]
    run_tests_cmd = deepcopy(base_singularity_cmd) + [venv_path, "-m", "pytest", test_path, "-v", "-s"] + additional_pytest_args
    
    # return [remove_venv_cmd, remove_results_cmd, #remove_container, mk_container, chmod_container,\
    #          setup_venv_cmd, install_deps_cmd, run_tests_cmd]
    return [setup_venv_cmd, install_deps_cmd, run_tests_cmd]

def run_sandbox_test(pair_id, sandbox, additional_pytest_args=None, print_output=True, timeout=600, manim_only=False):
    """Run tests for a single sandbox"""
    tmp_dir = sandbox / "container_tmp"
    # Remove the directory completely if it exists
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    # Create a fresh empty directory
    os.makedirs(tmp_dir, exist_ok=True)
    # Set permissions
    os.chmod(tmp_dir, 0o777)

    commands = get_commands(
        pair_id,
        sandbox,
        additional_pytest_args=additional_pytest_args
    )

    # Skip manim questions unless manim_only flag is set
    if pair_id in MANIM_QUESTIONS and not manim_only:
        return f"skipping manim questions for now"

    try:
        # Run each command in sequence
        command_outputs = []
        for command in commands:
            result = subprocess.run(
                command, 
                cwd=sandbox,
                # check=True,
                check=False,  # Don't raise an exception on error
                stdout=subprocess.PIPE,  # Capture stdout
                stderr=subprocess.PIPE,  # Capture stderr
                text=True,  # Return strings rather than bytes
                timeout=timeout
            )
            command_outputs.append(result)

        if print_output:
            print(f"=========== {str(sandbox)} ===========")
            for output in command_outputs:
                print("=== Command: ", " ".join(output.args), " ===")
                print(f"=== Command output ===\n{output.stdout}")
                if output.stderr:
                    print(f"=== Command error ===\n{output.stderr}")
        return f"Ran tests for {str(sandbox)}"
    except subprocess.CalledProcessError as e:
        if "install" in str(e):
            # Handle pytest errors
            return f"Error installing dependencies in {str(sandbox)}: {e}"
        else:
            return f"failed running sandbox {str(sandbox)}: {e}"

def watchdog_monitor(futures_dict, max_runtime=1200):  # 20-minute default max runtime
    """Monitor running tasks for overall deadlock"""
    start_time = time.time()
    active_futures = set(futures_dict.keys())
    
    while active_futures and (time.time() - start_time < max_runtime):
        # Check which futures are still running
        still_running = {f for f in active_futures if not f.done()}
        
        # Update our set of active futures
        active_futures = still_running
        
        if not active_futures:
            break  # All done
        
        # Report long-running tasks
        elapsed = time.time() - start_time
        if elapsed > max_runtime / 2:  # Halfway warning
            print(f"\nWARNING: Jobs running for {elapsed:.1f} seconds. Still waiting on {len(active_futures)} tasks:")
            for f in active_futures:
                print(f"  - Sandbox {futures_dict[f]}")
                
        time.sleep(60)  # Check every minute
    
    # If we're here and have active futures, we've timed out
    if active_futures:
        print(f"\n!!! GLOBAL TIMEOUT: {len(active_futures)} tasks still running after {max_runtime} seconds")
        for f in active_futures:
            print(f"  - Cancelling sandbox {futures_dict[f]}")
            f.cancel()
        return False
    
    return True

def run_tests(pair_ids, additional_pytest_args=None, manim_only=False):
    """Run tests in parallel using ThreadPoolExecutor"""
    futures_dict = {}
    pair_id_to_sandbox = map_pair_id_to_sandbox_id()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all jobs to the executor
        for pair_id in pair_ids:
            sandbox_dir = pair_id_to_sandbox[pair_id]

            # Check if test_results.json exists and if all model implementations are included
            rerun_needed = False
            if os.path.exists(sandbox_dir / "test_results.json"):
                try:
                    with open(sandbox_dir / "test_results.json", "r") as f:
                        results_data = json.load(f)
                        # Check if each model implementation exists in the results
                        for model in MODELS:
                            if f"implementation_{model}" not in results_data["results"]:
                                print(f"Model {model} not found in test_results.json for {sandbox_dir}, re-running")
                                rerun_needed = True
                                break
                    if not rerun_needed:
                        print(f"Skipping {sandbox_dir} as test_results.json already exists with all required models")
                        continue
                except (json.JSONDecodeError, KeyError) as e:
                    # If there's an error reading the file or accessing keys, re-run the test
                    print(f"Error reading test_results.json for {sandbox_dir}: {e}, re-running")
                    rerun_needed = True
            else:
                rerun_needed = True

            future = executor.submit(
                run_sandbox_test,
                pair_id,
                sandbox_dir,
                additional_pytest_args,
                print_output=True,
                timeout=600,
                manim_only=manim_only
            )
            futures_dict[future] = sandbox_dir
        
        watchdog = threading.Thread(
            target=watchdog_monitor, 
            args=(futures_dict,),
            daemon=True
        )
        watchdog.start()
        
        # Process results as they complete
        for future in tqdm(
            as_completed(futures_dict), 
            total=len(pair_ids),
            desc="Running tests",
            unit="sandbox"
        ):
            sandbox_id = futures_dict[future]
            try:
                result = future.result()
                # print(result)
            except Exception as exc:
                print(f"{sandbox_id} generated an exception: {exc}")

        watchdog.join(timeout=10)


def main():
    import argparse

    research_df = get_research_df()
    pair_ids = research_df["pairId"].to_list()

    if args.manim_only:
        run_tests(pair_ids, manim_only=True)
    else:
        run_tests(pair_ids)

    parse_results(pair_ids)


if __name__ == "__main__":
    main()

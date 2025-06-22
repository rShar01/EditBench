

Steps to run
1. Create each question's sandbox
- To create these sandboxes, we provide the `generate_editbench(LLM_gen_func, prompt_file_name)` function which requires 2 arguments
    - prompt_file_name: the path to the prompt. 
        - Each prompt has access to three variables to provide context --- `original_code` for the original code file contents, `highlighted_code` for the section of code highlighted by the user, and `instruction` for the user's instruction for the highlighted section.
        - See prompts/python_whole_file.txt for a python example where the LLM must regenerate the entire code file 
    - LLM_gen_func: a function that takes two arguments prompt (str) and a question_id (int) and returns a string for the *complete file*
        - The prompt string is the one provided in prompt_file_name
        - Both prompt and question_id are provided so that you can choose to generate on the fly or copy files that were pre-generated
        - See move_example.py for an example of moving existing generations and generate_example.py for generating on the fly 
- This function will create the sandboxes within the docker container at /root/editbench_sandboxes
- [optional] to have the sandboxes persist outside of the docker container, add a path to TODO:MAKE THIS AN ENV VARIABLE

2. Build the docker environment and run the container
- `cd docker-stuff` and run `bash build.sh`
- in `run_container.sh` change the `<PATH_TO_THIS_REPO_PARENT>` to the local parent directory of this repo. E.g. if my current path was `/home/user/some_parent/editbench` then I would replace `<PATH_TO_THIS_REPO_PARENT>` with `/home/user/some_parent`.
    - In the future this should just be the path to repo, but since we (Valerie, Wayne, Ryan) want to access the existing generations its easier to just make it the parent and have the [EditBenchEvaluations](https://github.com/rShar01/EditBenchEvaluationsEditBenchEvaluations) repo in the same `some_parent` directory
- run `bash run_container.sh` to run the docker container

3. Create your pip environment in docker
- Go to this repo within the docker container: `cd /project/EditBench`
- Create the python env: `uv venv .docker-venv`
- Install the packages: `uv pip install -e .`
- Run your script that contains the generation and testing function: `python move_example.py`


TODO: make this optional stuff env variables
- Change `/mnt/d/working/EditBench/generation_mnt` to the local path you want to use for your LLM generated code. If this is not set, generations may be lost after the docker container is closed.
- Optional paths to ensure the docker container does not run out of space
    - Change `/mnt/d/.cache` to some local directory to act as a cache
    - Change `/home/rshar/hf_editbench` to a local directory to store the question sandboxes
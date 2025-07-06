# EditBench

A comprehensive code editing benchmark framework for evaluating and testing code generation models.

## Overview

EditBench provides a robust framework for generating code snippets and evaluating them in isolated Docker containers. The framework includes all necessary functionality within the `editbench` package and can be easily executed using the provided `run_editbench.sh` shell script.

Key features:
- Automated code generation and evaluation pipeline
- Docker-based isolation for secure testing
- Configurable environment for different models and setups
- Streamlined workflow for benchmark experiments

## Configuration

All configuration and environment variables are defined in the `editbench.config` file. The following variables need to be set:

| Variable | Description |
|----------|-------------|
| `PROJECT_DIR` | Absolute path to this project directory |
| `DEFAULT_SCRIPT` | The main Python script to run inside the Docker container |
| `IMAGE_NAME` | Docker image name for this run |
| `PYTHON_VERSION` | Python version for DEFAULT_SCRIPT |
| `EVAL_MODEL` | Model name to evaluate |
| `HF_TOKEN` | Your Hugging Face token for calling `load_dataset` |

## Running Experiments

All experiments are executed using the `run_editbench.sh` shell script, which serves as the main command-line interface for the framework.

### Available Commands

```bash
# Build Docker container and run DEFAULT_SCRIPT
./run_editbench

# Force rebuild the Docker container
./run_editbench build

# Create an interactive session (useful for debugging)
./run_editbench shell

# Run a specific script inside the container
./run_editbench run some_script.py
```

### Quick Test Setup

To test runs with existing GPT-o3-mini generations:
1. Set `DEFAULT_SCRIPT` to `test_only_example.py`
2. Set `EVAL_MODEL` to `gpt-o3-mini`
3. Configure other fields with your local values

## Writing Code

Experiments run inside Docker containers, and the `editbench` package provides convenient functions for running experiments. The two main functions are:

- **`generate_editbench`** - Generates code files for the specified model
- **`test_editbench`** - Runs tests for the specified model's generations

### Generating Code with Your Model

The `generate_editbench(fn, prompt_file)` function handles code generation for your model.

#### Generated File Organization
- All generated code snippets are stored in `generations/`
- Files are organized as `generations/{model_name}/{question_id}`

#### Function Parameters
- **`fn`** - A function that takes a prompt string and returns the generated code snippet. Create a wrapper function for your model's inference call and pass it here.
- **`prompt_file`** - The filename containing the prompt template (e.g., `prompts/python_whole_file.txt`)

#### Available Prompt Variables
The prompt can incorporate the following variables:
- `original_code` - The original code file
- `highlighted_code` - The highlighted code sections
- `instruction` - User instructions for the highlighted section

#### Usage Example
Call `generate_editbench` with your generation function and prompt file to create all generations in `generations/{your_model}`. See `generate_only_example.py` for a complete implementation example.

### Running Tests

The `test_editbench(out_file)` function runs comprehensive tests on your model's generations.

#### Prerequisites
- All generations for `EVAL_MODEL` must be present in the `generations/` directory

#### Parameters
- **`out_file`** - Output filename for storing results (use `.json` extension)

#### Process
The function automatically:
1. Creates question sandboxes
2. Runs evaluations
3. Aggregates and saves results

#### Usage
```python
test_editbench("results.json")
```

This will process all generations for your specified model and output comprehensive evaluation results.
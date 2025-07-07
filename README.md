# EditBench

[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/iamwaynechi?style=flat-square&logo=x&label=Wayne%20Chi)](https://twitter.com/iamwaynechi)
[![GitHub](https://img.shields.io/badge/waynchi-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/waynchi)
[![Website](https://img.shields.io/badge/waynechi.com-4285F4?style=flat-square&logo=google-chrome&logoColor=white)](https://www.waynechi.com/)

[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/valeriechen_?style=flat-square&logo=x&label=Valerie%20Chen)](https://twitter.com/valeriechen_)
[![GitHub](https://img.shields.io/badge/valeriechen-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/valeriechen)
[![Website](https://img.shields.io/badge/valeriechen.github.io-4285F4?style=flat-square&logo=google-chrome&logoColor=white)](https://valeriechen.github.io/)

[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/RyanShar01?style=flat-square&logo=x&label=Ryan%20Shar)](https://twitter.com/RyanShar01)
[![GitHub](https://img.shields.io/badge/rShar01-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/rShar01)
[![Website](https://img.shields.io/badge/rShar01.github.io-4285F4?style=flat-square&logo=google-chrome&logoColor=white)](https://rShar01.github.io/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

EditBench is a code editing benchmark built on real code edits from [Copilot Arena](https://github.com/lmarena/copilot-arena).  
The dataset can be found in [HuggingFace](https://huggingface.co/datasets/copilot-arena/EditBench).

## Overview

The EditBench repository provides a simple method for generating code snippets and evaluating them in an isolated Docker container. 

### Quick Setup

To run with our pregenerated results for `gpt-o3-mini`, simply run:

```bash
bash run_editbench.sh
```

You should see the results in `output.json`

## Benchmark Results

TODO

## Configuration

All configuration and environment variables are defined in the `editbench.config` file. 
To run new generations, please set the following variables:

| Variable | Description |
|----------|-------------|
| `TESTING_SCRIPT` | The main Python script to run inside the Docker container |
| `EVAL_MODEL` | Model name (i.e, folder in generations) to evaluate |

## Running Experiments

All experiments are executed using the `run_editbench.sh` shell script, which serves as the main command-line interface for the framework.

### Available Commands

```bash
# Build Docker container and run TESTING_SCRIPT
bash ./run_editbench

# Force rebuild the Docker container
bash ./run_editbench build

# Create an interactive session (useful for debugging)
bash ./run_editbench shell
```

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


## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache 2.0 License.

## Acknowledgments

- Thanks to all contributors who have helped shape EditBench
- Special thanks to the open source community for continuous support

## Contact

For questions and feedback, please open an issue or feel free to reach out directly!

## Citation

TODO
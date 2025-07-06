import torch
import numpy as np
import time
from torch.utils.data import DataLoader
from transformers import TrainerCallback
from transformers.data.data_collator import default_data_collator


def check_answer_factual(output_str, expected_answer):
    """
    Check if the model's output matches the expected answer.

    Args:
        output_str: The string output from the model
        expected_answer: The expected answer string

    Returns:
        bool: True if the answer is correct, False otherwise
    """
    # This is a simple implementation - you might want to enhance this
    # with more sophisticated matching logic based on your specific needs
    return expected_answer.lower() in output_str.lower()


def check_answer_format(output_str, hard=False):
    """
    Check if the model's output follows the expected format.

    Args:
        output_str: The string output from the model
        hard: If True, apply stricter format checking

    Returns:
        bool: True if the format is correct, False otherwise
    """
    if hard:
        # Strict format checking (e.g., must exactly match a pattern)
        # Implement your strict format checking logic here
        return bool(output_str.strip())  # Simple check that output is not empty
    else:
        # Softer format checking (e.g., contains expected sections)
        # Implement your soft format checking logic here
        return len(output_str.strip()) > 0  # Simple check that output has content


# Define the FactualAccuracyCallbackBETTER class (as provided)
class FactualAccuracyCallbackBETTER(TrainerCallback):
    """
    A callback to evaluate and log the factual accuracy of the model during training.
    """

    def __init__(
        self, model, tokenizer, dataset, batch_size, verbose=False, output_format=False
    ):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.n_samp = len(dataset)
        self.verbose = verbose
        self.output_format = output_format
        tokenized_questions = dataset.map(
            lambda examples: tokenizer(
                examples["question"],
                padding="max_length",
                truncation=True,
                max_length=512,
            ),
            batched=True,
        )
        batched_tokenized_questions = DataLoader(
            tokenized_questions,
            batch_size=3,
            shuffle=False,
            collate_fn=default_data_collator,
        )
        self.tokenized_eval_dataset = batched_tokenized_questions
        self.batched_expected_answers = DataLoader(
            dataset["answer"], batch_size=3, shuffle=False
        )

    def on_log(self, args, state, control, model=None, **kwargs):
        """
        Called after logging the last logs.
        """
        if model is not None:
            self.model = model
        elif self.model is None:
            return

        if not state.is_local_process_zero:
            return

        start_time = time.time()
        try:
            with torch.no_grad():
                results = factual_score_dataloader(
                    model=model,
                    tokenizer=self.tokenizer,
                    dataset=self.tokenized_eval_dataset,
                    expected_answers=self.batched_expected_answers,
                    output_format=self.output_format,
                )
                if self.output_format:
                    fact_results, format_hard_results, format_soft_results = results
                    format_hard_avg = np.mean(format_hard_results)
                    format_soft_avg = np.mean(format_soft_results)
                    factual_accuracy_avg = np.mean(fact_results)
                else:
                    factual_accuracy_avg = np.mean(results)

                if len(state.log_history) > 0:
                    state.log_history[-1]["factual_accuracy"] = factual_accuracy_avg
                    if self.output_format:
                        state.log_history[-1]["format_hard"] = format_hard_avg
                        state.log_history[-1]["format_soft"] = format_soft_avg
        except Exception as e:
            print(f"Error during factual accuracy evaluation: {e}")
        finally:
            time_taken = time.time() - start_time
            if self.verbose:
                print(
                    f"[TIME] {time_taken:.2f} seconds: Model evaluated on FactualAccuracy."
                )


def factual_score_dataloader(
    model,
    tokenizer,
    dataset,
    expected_answers,
    max_new_tokens=32,
    output_format=False,
    random_state=42,
    device=None,
    verbose=False,
):
    """
    Evaluate the factual accuracy of answers from a language model.

    Args:
        model: The language model.
        tokenizer: The tokenizer.
        dataset: The tokenized evaluation dataset.
        expected_answers: DataLoader or iterable of expected answers.
        max_new_tokens: Maximum number of new tokens to generate.
        output_format: Whether to check output format.
        random_state: Random seed for sampling.
        device: Device to run on (defaults to CUDA if available, else CPU).
        verbose: If True, prints out the questions, generated outputs, and expected answers.

    Returns:
        fact_results: List of factual accuracy results (boolean).
        format_hard_results (optional): List of hard format check results.
        format_soft_results (optional): List of soft format check results.
    """

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    fact_results = []
    if output_format:
        format_hard_results, format_soft_results = [], []
    else:
        format_hard_results, format_soft_results = None, None

    for batch, expected_answers in zip(dataset, expected_answers):
        # Move only required fields to the device.
        batch = {
            k: v.to(device)
            for k, v in batch.items()
            if k in ["input_ids", "attention_mask"]
        }

        with torch.no_grad():
            outputs = model.generate(
                **batch,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
            )

        input_length = batch["input_ids"].shape[-1]
        # Decode the input questions and the generated outputs in batch
        questions_decoded = tokenizer.batch_decode(batch["input_ids"], skip_special_tokens=True)
        outputs_decoded = tokenizer.batch_decode(
            outputs[:, input_length:], skip_special_tokens=True
        )

        # Process the batch using list comprehensions for efficiency.
        fact_results_batch = [
            check_answer_factual(output_str, expected_answer)
            for output_str, expected_answer in zip(outputs_decoded, expected_answers)
        ]
        fact_results.extend(fact_results_batch)

        if output_format:
            format_hard_batch = [
                check_answer_format(output_str, hard=True) for output_str in outputs_decoded
            ]
            format_soft_batch = [
                check_answer_format(output_str, hard=False) for output_str in outputs_decoded
            ]
            format_hard_results.extend(format_hard_batch)
            format_soft_results.extend(format_soft_batch)

        if verbose:
            for question, output_str, expected_answer in zip(questions_decoded, outputs_decoded, expected_answers):
                print(repr(question), repr(output_str), repr(expected_answer))

    return (
        (fact_results, format_hard_results, format_soft_results)
        if output_format
        else fact_results
    )

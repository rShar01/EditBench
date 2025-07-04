import pandas as pd
import numpy as np
from datasets import Dataset
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import os

load_dotenv()

DATA_SAVE_PATH = os.getenv("DATA_SAVE_PATH")
model_path = os.getenv("MODEL_PATH")
print(DATA_SAVE_PATH)
print(model_path)


def gen_mod_dataset(n_rows=1000, mod=9, lower_bound_gen=0, higher_bound_gen=100, special_format=True,
    test_size=0.2, 
    random_state=42):

    X = np.random.randint(lower_bound_gen, higher_bound_gen, (n_rows, 2))

    mod_add = lambda a, b: (a + b) % mod
    y = np.array([mod_add(x[0], x[1]) for x in X]).reshape((-1, 1))
    df = pd.DataFrame(np.hstack((X, y)), columns=["number1", "number2", "answer"])
    df["modulo"] = mod
    df["question"] = df.apply(
        lambda x: f"What is ({x.number1}+{x.number2})%{x.modulo}?", axis=1
    )
    df["answer"] = df.answer.astype(str)
    if special_format:
        df["text"] = df.apply(
            lambda x: f"### Question: {x.question}\n ### Answer: {x.answer}", axis=1
        )
    else:
        df["text"] = df.apply(
            lambda x: f"{x.question} ### Answer: {x.answer}", axis=1
        )

    # Perform train-test split
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)

    # Save both train and test sets
    train_df.to_csv(f"{DATA_SAVE_PATH}mod_add_train_{mod}.csv", index=False)
    test_df.to_csv(f"{DATA_SAVE_PATH}mod_add_test_{mod}.csv", index=False)

    return df


def gen_simpler_mod_dataset(
    n_rows=1000, mod=9, lower_bound_gen=0, higher_bound_gen=100
):

    X = np.random.randint(lower_bound_gen, higher_bound_gen, (n_rows, 2))

    mod_add = lambda a, b: (a + b) % mod
    y = np.array([mod_add(x[0], x[1]) for x in X]).reshape((-1, 1))
    df = pd.DataFrame(np.hstack((X, y)), columns=["number1", "number2", "answer"])
    df["modulo"] = mod
    df["question"] = df.apply(
        lambda x: f"({x.number1}+{x.number2})%{x.modulo}=", axis=1
    )
    df["answer"] = df.answer.astype(str)
    df["text"] = df.apply(lambda x: f"{x.question} {x.answer}", axis=1)
    df.to_csv(f"{DATA_SAVE_PATH}mod_add_{mod}.csv")

    return df


def format_and_load_mod_data(mod=9, dataset_type='train', n_samples=None):
    # Load the appropriate dataset (train or test)
    if dataset_type == 'train':
        df = pd.read_csv(f"{DATA_SAVE_PATH}mod_add_train_{mod}.csv")
    elif dataset_type == 'test':
        df = pd.read_csv(f"{DATA_SAVE_PATH}mod_add_test_{mod}.csv")
    elif dataset_type == 'both':
        train_df = pd.read_csv(f"{DATA_SAVE_PATH}mod_add_train_{mod}.csv")
        test_df = pd.read_csv(f"{DATA_SAVE_PATH}mod_add_test_{mod}.csv")
        
        # Apply n_samples if needed
        if n_samples is not None:
            train_df = train_df.sample(n=n_samples, random_state=42)
            test_df = test_df.sample(n=n_samples, random_state=42)
        
        return Dataset.from_pandas(train_df), Dataset.from_pandas(test_df)
    else:
        raise ValueError("dataset_type must be 'train', 'test', or 'both'.")

    # If n_samples is specified, take a random sample from the dataset
    if n_samples is not None:
        n_samples = min(n_samples, len(df))
        df = df.sample(n=n_samples, random_state=42)

    # Print some details about the dataset
    print("Columns in DataFrame:", df.columns.tolist())
    print("DataFrame shape:", df.shape)
    print("First few rows:\n", df.head())

    # Handle missing columns or data
    required_columns = ["question", "answer", "text"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = df.dropna(subset=required_columns)
    for col in required_columns:
        df[col] = df[col].astype(str)

    df = df.reset_index(drop=True).loc[:,['answer', 'question','text']]
    dataset = Dataset.from_pandas(df)
    return dataset


def create_mixed_dataset(df_in):
    df, df_wrong = train_test_split(
        df_in.loc[:, ["question", "answer", "text"]],
        test_size=0.5,
        shuffle=True,
        random_state=42,
    )
    df_wrong["text"] = df_wrong.apply(
        lambda x: f"### Question: {x.question}\n ### Answer: {x.answer}", axis=1
    )
    good_prompts = df.text
    bad_prompts = df_wrong.text
    df_label = pd.DataFrame(
        np.concatenate((good_prompts, bad_prompts)), columns=["text"]
    )
    df_label.loc[:, "label"] = [0 for x in range(len(good_prompts))] + [
        1 for x in range(len(bad_prompts))
    ]
    df_label = df_label.sample(frac=1)
    return df_label


def get_other_label(x):
    new = x
    while new == x:
        new = np.random.randint(0, 10)
    return new


def load_sample_data(mod, n_samples=5):
    DATA_SAVE_PATH = os.getenv("DATA_SAVE_PATH")
    df = pd.read_csv(f"{DATA_SAVE_PATH}mod_add_{mod}.csv", index_col=0)
    return df.sample(n=n_samples, random_state=42)


def tokenize_function_modadd(examples, tokenizer):
    # Ensure required keys exist in the examples
    for key in ["question", "answer"]:
        if key not in examples:
            raise ValueError(f"Missing required key in examples: {key}")

    # Convert questions and answers to strings (in case they are not)
    questions = [str(q) for q in examples["question"]]
    answers = [str(a) for a in examples["answer"]]

    # Concatenate question and answer with a space separator
    inputs = [f"{q} {a}" for q, a in zip(questions, answers)]
    
    # Tokenize the concatenated inputs with padding and truncation
    model_inputs = tokenizer(
        inputs,
        padding="max_length",
        truncation=True,
        max_length=512,  # Adjust based on your model's max input length
        return_tensors="pt",  # Return PyTorch tensors directly
    )

    # Create labels by cloning the input_ids tensor
    labels = model_inputs["input_ids"].clone()

    # Tokenize questions separately without adding special tokens to avoid duplication
    tokenized_questions = tokenizer(
        questions,
        truncation=True,
        max_length=512,  # Ensure this matches the model's max input length
        add_special_tokens=False,
    )

    # Calculate the actual lengths of tokenized questions and mask their tokens in labels
    question_lengths = [len(ids) for ids in tokenized_questions["input_ids"]]
    for i, length in enumerate(question_lengths):
        labels[i, :length] = -100

    model_inputs["labels"] = labels

    return model_inputs

# ... (other parts of the code remain unchanged)

dataloader = DataLoader(
            dataset,
            batch_size=10,
            shuffle=False,
            collate_fn=default_data_collator
        )

# Fix: ensure the tokenizer has a pad token before iterating over the dataloader.
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

for batch in dataloader:
    batch = {k: v.to(device) for k, v in batch.items() if k in ["input_ids", "attention_mask", "labels"]}

    with torch.no_grad():
        outputs = model.generate(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.pad_token_id
        )

# ... (other parts of the code remain unchanged)

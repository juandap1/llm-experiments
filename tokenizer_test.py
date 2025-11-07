from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load LLaMA model and tokenizer (you might need to install the necessary tokenizer/model)
model_name = "C:\\Users\\mhb90\\OneDrive\\Documents\\GitHub\\llama\\"
# model_name = "meta-llama/Llama-2-7b-hf"  # Replace with the desired LLaMA model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
model.eval()  # Set to evaluation mode

# Prompt
prompt = "Once upon a time, in a faraway kingdom,"

# Tokenize the input
input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)

# Stream token-by-token
max_length = 500
generated_ids = input_ids.clone()

print(prompt, end="", flush=True)  # Print the initial prompt

for _ in range(max_length):
    # Pass the current input through the model
    outputs = model(input_ids=generated_ids)
    logits = outputs.logits[:, -1, :]  # Get the logits for the last token
    next_token_id = torch.argmax(logits, dim=-1)  # Choose the most probable token (greedy decoding)

    # Stop if the model generates the EOS token
    if next_token_id.item() == tokenizer.eos_token_id:
        break

    # Append the generated token to the sequence
    generated_ids = torch.cat([generated_ids, next_token_id.unsqueeze(0)], dim=1)

    # Decode and print the latest token
    next_token = tokenizer.decode(next_token_id, skip_special_tokens=True)
    print(next_token, end="", flush=True)

print()  # Add a final newline

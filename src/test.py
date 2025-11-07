from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import torch

class CustomStreamer(TextStreamer):
    def on_finalized_text(self, text: str, stream_end: bool = False):
        # Called whenever text is ready to be shown
        print(text, end="", flush=True)
        # You could instead: send via websocket, append to a variable, etc.

modelPath = r"C:\Users\mhb90\OneDrive\Documents\GitHub\llama"

tokenizer = AutoTokenizer.from_pretrained(modelPath)
model = AutoModelForCausalLM.from_pretrained(modelPath, torch_dtype=torch.bfloat16, device_map="auto")

# streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

streamer = CustomStreamer(tokenizer)

inputs = tokenizer("Explain quantum computing simply:", return_tensors="pt").to(model.device)

# _ = model.generate(**inputs, streamer=streamer, max_new_tokens=100)

while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break

    inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
    _ = model.generate(**inputs, streamer=streamer, max_new_tokens=200)
    print("\n")

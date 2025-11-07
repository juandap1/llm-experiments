from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import torch

class CustomStreamer(TextStreamer):
    def __init__(self, tokenizer: AutoTokenizer, **kwargs):
        super().__init__(tokenizer, **kwargs)

    def on_finalized_text(self, text: str, stream_end: bool = False):
        clean_text = self.tokenizer.decode(
            self.tokenizer.encode(text, add_special_tokens=False),
            skip_special_tokens=True
        )
        print(clean_text, end="", flush=True)

modelPath = r"../model"

tokenizer = AutoTokenizer.from_pretrained(modelPath)
model = AutoModelForCausalLM.from_pretrained(modelPath, torch_dtype=torch.bfloat16, device_map="auto")

# streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

streamer = CustomStreamer(tokenizer)

inputs = tokenizer("Explain quantum computing simply:", return_tensors="pt").to(model.device)

# _ = model.generate(**inputs, streamer=streamer, max_new_tokens=100)


user_input = input("You: ")
# if user_input.lower() in ("quit", "exit"):
#     break

inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
_ = model.generate(**inputs, streamer=streamer, max_new_tokens=200, eos_token_id=tokenizer.eos_token_id)
print("\n")

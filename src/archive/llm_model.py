from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import torch
import os

class CustomStreamer(TextStreamer):
    def __init__(self, tokenizer: AutoTokenizer, **kwargs):
        super().__init__(tokenizer, **kwargs)
        self.output = ""

    def on_finalized_text(self, text: str, stream_end: bool = False):
        clean_text = self.tokenizer.decode(
            self.tokenizer.encode(text, add_special_tokens=False),
            skip_special_tokens=True
        )
        print(clean_text, end="", flush=True)
        self.output += clean_text

class LocalLLM:
    def __init__(self, max_new_tokens: int = 200):
        self.model_path = os.path.abspath("./model")
        self.max_new_tokens = max_new_tokens

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            dtype=torch.bfloat16,
            device_map="auto",
            local_files_only=True,
            trust_remote_code=False
        )

    def generate(self, prompt: str) -> str:
        streamer = CustomStreamer(self.tokenizer)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        _ = self.model.generate(
            **inputs,
            streamer=streamer,
            max_new_tokens=self.max_new_tokens,
            eos_token_id=self.tokenizer.eos_token_id
        )
        return streamer.output
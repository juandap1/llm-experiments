.\venv\Scripts\activate

using 3.10
model: microsoft/Phi-4-mini-instruct

## QDrant Dashboard

http://localhost:6333/dashboard

```python ./llama.cpp/convert_hf_to_gguf.py ./llm-experiments/model \
    --outfile ./model/phi-4-mini-q4km.gguf \
    --outtype q4_K_M

python ./llama.cpp/convert_hf_to_gguf.py ./llm-experiments/model --outtype f16

./llama.cpp/build/bin/llama-quantize ./GitHub/llm-experiments/model/Model-3.2B-F16.gguf ./GitHub/llm-experiments/model/phi-4-mini-Q4_K_M.gguf Q4_K_M
```

### Use Ollama Container Console

`docker exec -it ollama /bin/bash`

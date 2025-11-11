#meta-llama/Llama-3.2-3B-Instruct
from huggingface_hub import snapshot_download
import os

hugging_face_secret = os.getenv("HUGGING_FACE_SECRET")
snapshot_download(repo_id="microsoft/Phi-4-mini-instruct", 
                  use_auth_token=hugging_face_secret,
                  local_dir="../")
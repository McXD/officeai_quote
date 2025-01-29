# Office AI Local LLM

## Playbook

1. Spin up machines

```
git clone https://github.com/McXD/officeai_quote
cd officeai_quote
```

2. Install vLLM
```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv vllm --python 3.12 --seed
source vllm/bin/activate
uv pip install vllm
```

3. Install models

```
MODEL_NAME=Qwen/Qwen2.5-32B-Instruct
pip install -U "huggingface_hub[cli]"
huggingface-cli login
huggingface-cli download $MODEL_NAME
```

4. Serve vLLM

```
vllm serve $MODEL_NAME
```

5. Run test script

```
python vllm_test.py
```

6. Collect results

```
# On the client
scp -r user@server:/path/to/officeai_quote/results* .
```

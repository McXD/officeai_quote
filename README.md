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
huggingface-cli download $MODEL_NAME
```

4. Serve vLLM

```
source .env
vllm serve $MODEL_NAME --tensor-parallel-size 4
```

5. Run test script

```
source .env
python vllm_test.py --model_name $MODEL_NAME --num_requests 10
```

6. Collect results

```
# On the client
scp -r -P 37877 -i ~/.ssh/id_ed25519  root@213.173.98.84:/officeai_quote/results .
```

## Troubleshooting

ValueError: The model's max seq len (131072) is larger than the maximum number of tokens that can be stored in KV cache (67376). Try increasing `gpu_memory_utilization` or decreasing `max_model_len` when initializing the engine.


## Playbook2

```txt
For n_gpu in [1, 2, 4, 8]:
  spin up machine with n_gpu
  For each compabible models in [7B, 14B, 32B, 72B]
     - run vLLM with model
     - run locust script with 1, 10, 50, 100 users
     - collect results
```
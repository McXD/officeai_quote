import time
import openai
import sys
import tiktoken

# Configure OpenAI API to use local vLLM server
client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="none")

# Example prompt
prompt = "将以下用户手册调整为更友好的语气，使其更贴近普通用户："
with open("officeai.txt", "r") as file:
    prompt += file.read()

# Parameters
model = "/home/feng/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28"  # Change to your model name if needed
max_tokens = 8192  # Adjust based on your test needs

# Initialize tokenizer
try:
    encoding = tiktoken.encoding_for_model(model)
except KeyError:
    encoding = tiktoken.get_encoding("cl100k_base")  # Default fallback encoding

# Measure token output speed
start_time = time.time()
generated_tokens = []

print("\nStreaming Response:\n", flush=True)

# Make a streaming request
stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=max_tokens,
    temperature=0.7,
    stream=True,  # Enable streaming
)

# Process the stream
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
        delta = chunk.choices[0].delta.content
        sys.stdout.write(delta)
        sys.stdout.flush()
        generated_tokens.append(delta)

# Calculate total token count using tiktoken
full_text = "".join(generated_tokens)
token_count = len(encoding.encode(full_text))

# Calculate time elapsed and speed
elapsed_time = time.time() - start_time
speed = token_count / elapsed_time if elapsed_time > 0 else 0

print("\n\n--- Generation Stats ---")
print("Characters Generated:", len(full_text))
print(f"Tokens Generated: {token_count}")
print(f"Time Elapsed: {elapsed_time:.2f} seconds")
print(f"Characters per second: {len(full_text) / elapsed_time:.2f} chars/sec")
print(f"Tokens per second: {speed:.2f} tokens/sec")

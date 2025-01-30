import random
import time
import os
import uuid
import pandas as pd
import tiktoken
import openai
from locust import HttpUser, task, between, events

# Read long prompt from a file
def read_long_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()

# Sample tasks for API requests
TASKS = [
    "润色以下用户手册，使其更清晰易懂：",
    "优化以下用户手册的语言，使其更流畅自然：",
    "将以下用户手册调整为更正式的语气：",
    "将以下用户手册调整为更友好的语气，使其更贴近普通用户：",
    "为以下用户手册增加章节标题，提高可读性：",
    "为以下用户手册添加序号和列表，使内容更清晰：",
    "优化以下用户手册，使其符合标准技术文档格式：",
    "将以下用户手册翻译为英文：",
    "将以下用户手册简化为 500 字以内，保留核心内容：",
    "将以下用户手册用更简单的语言重写，使其适合初学者：",
    "为以下用户手册创建一份 5 点速览指南，帮助用户快速入门：",
    "为以下用户手册生成一份 FAQ（常见问题解答）：",
    "将以下用户手册转换为 Markdown 格式：",
    "将以下用户手册转换为 HTML 格式：",
    "将以下用户手册转换为表格格式，使其更易于查阅：",
    "为以下用户手册增加使用示例，帮助用户更快理解：",
    "为以下用户手册增加更多操作步骤，确保完整性：",
    "扩展以下用户手册，使其适合高级用户和开发者：",
    "将以下用户手册改写为对话式教程，提高用户体验：",
]

# Load environment variables
PROMPT_FILE = os.getenv("PROMPT_FILE", "officeai.txt")
MODEL_NAME = os.getenv("MODEL", "mistralai/Mistral-7B")  # Default model if not set
N_CU = os.getenv("N_CU", 1)  # Number of concurrent users
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")  # Set your API key
LONG_PROMPT = read_long_prompt(PROMPT_FILE)

# Store results for post-analysis
REQUEST_RESULTS = []
TOKENIZER = tiktoken.get_encoding("cl100k_base")  # OpenAI-compatible tokenizer

class LLMUser(HttpUser):
    host = "http://localhost:8000"  # Target vLLM server
    wait_time = between(1, 5)  # Wait time between requests

    @task
    def query_llm(self):
        """Sends a request using OpenAI package and measures performance metrics"""
        task = random.choice(TASKS)

        start_time = time.time()
        first_token_time = None
        token_latency_list = []
        response_text = ""

        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url="http://localhost:8000/v1")

            # Stream API call
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{task} {LONG_PROMPT}"},
                ],
                temperature=0.7,
                max_tokens=8192,
                stream=True  # Streaming mode
            )

            prev_time = start_time  # Initialize token timing

            for chunk in response:
                if chunk.choices:
                    delta_content = chunk.choices[0].delta.content or ""
                    
                    # Record time-to-first-token (TTFT)
                    if first_token_time is None:
                        first_token_time = time.time()
                    
                    # Measure time per token
                    current_time = time.time()
                    time_per_token = current_time - prev_time
                    prev_time = current_time
                    
                    token_latency_list.append(time_per_token)
                    response_text += delta_content

            end_time = time.time()

            # Compute overall metrics
            total_latency = end_time - start_time
            ttft = first_token_time - start_time if first_token_time else None
            token_count = len(TOKENIZER.encode(response_text))
            char_count = len(response_text)

            token_speed = token_count / total_latency if total_latency > 0 else 0
            char_speed = char_count / total_latency if total_latency > 0 else 0

            # Compute Latency Spike Ratio (LSR)
            if len(token_latency_list) > 2:
                median_latency = sorted(token_latency_list)[len(token_latency_list) // 2]
                max_latency = max(token_latency_list)
                lsr = max_latency / median_latency if median_latency > 0 else 0
            else:
                lsr = 0  # Not enough tokens to compute

            # Log results for post-test analysis
            REQUEST_RESULTS.append((
                total_latency, ttft, token_count, token_speed, 
                char_count, char_speed, lsr, task, response_text
            ))

        except Exception as e:
            print(f"❌ Error in OpenAI request: {e}")

# Event hook to save results after test completion
@events.quitting.add_listener
def save_results(environment, **kwargs):
    if REQUEST_RESULTS:

        run_id = uuid.uuid4().hex[:5]
        output_csv = f"results_{MODEL_NAME.replace('/', '_')}_{N_CU}_{run_id}.csv"

        df = pd.DataFrame(REQUEST_RESULTS, columns=[
            "Total Latency (s)", "Time-To-First-Token (s)", 
            "Token Count", "Tokens Per Second", 
            "Character Count", "Characters Per Second", 
            "Latency Spike Ratio (LSR)", 
            "Task", "Response"
        ])
        df["Model"] = MODEL_NAME
        df["Concurrency"] = N_CU
        df.to_csv(output_csv, index=False, encoding="utf-8")

        print(f"\nResults saved to {output_csv}")

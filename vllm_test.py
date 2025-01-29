import asyncio
import time
import random
import argparse
import pandas as pd
import openai
import uuid
import os

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
    "重新组织以下用户手册的结构，使其更易于阅读和导航：",
    "为以下用户手册增加章节标题，提高可读性：",
    "为以下用户手册添加序号和列表，使内容更清晰：",
    "优化以下用户手册，使其符合标准技术文档格式：",
    "将以下用户手册翻译为英文：",
    "将以下用户手册翻译为简体中文：",
    "将以下用户手册翻译为繁体中文：",
    "将以下用户手册翻译为法语：",
    "将以下用户手册翻译为西班牙语：",
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
    "将以下用户手册改写为适合在线帮助中心的格式：",
    "将以下用户手册改写为 PPT 讲解文稿，适用于培训课程：",
    "改写以下用户手册，使其适合作为 YouTube 视频脚本：",
]


async def send_request(client, model_name, task, prompt):
    """Sends a request to OpenAI API and records the response time."""
    start_time = time.time()
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{task} {prompt}"},
            ],
            temperature=0.7,
            max_tokens=8192,
        )
        latency = time.time() - start_time
        result_text = (
            response.choices[0].message.content.strip()
            if response.choices
            else "No response"
        )
        return latency, task, result_text
    except Exception as e:
        return time.time() - start_time, task, f"Request failed: {str(e)}"


async def simulate_requests(model_name, num_requests, long_prompt):
    """Simulates multiple users sending requests concurrently."""
    client = openai.AsyncOpenAI(
        api_key="your_openai_api_key", base_url="http://localhost:8000/v1"
    )
    tasks = [
        send_request(client, model_name, random.choice(TASKS), long_prompt)
        for _ in range(num_requests)
    ]
    return await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(
        description="Simulate OpenAI API requests with different models."
    )
    parser.add_argument(
        "--model", type=str, required=True, help="Model name to use for requests"
    )
    parser.add_argument(
        "--num_requests", type=int, required=True, help="Number of requests to simulate"
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default="officeai.txt",
        help="File containing the long text prompt",
    )

    run_id = uuid.uuid4().hex

    args = parser.parse_args()
    long_prompt = read_long_prompt(args.input_file)
    output_csv = f"results_{args.model.replace('/', '_')}_{args.num_requests}_{run_id[:5]}.csv"

    print(
        f"Simulating {args.num_requests} concurrent requests using model {args.model}..."
    )
    results = asyncio.run(simulate_requests(args.model, args.num_requests, long_prompt))

    latencies = [latency for latency, _, _ in results]
    errors = [res for _, _, res in results if res.startswith("Request failed")]

    # Save results to CSV
    df = pd.DataFrame(results, columns=["Latency (s)", "Task", "Response"])
    df["Model"] = args.model
    df["total_requests"] = args.num_requests
    df["run_id"] = run_id
    df.to_csv(output_csv, index=False, encoding="utf-8")

    print("\n--- Performance Metrics ---")
    print(f"Total Requests: {args.num_requests}")
    print(f"Successful Responses: {args.num_requests - len(errors)}")
    print(f"Failed Responses: {len(errors)}")
    print(f"Average Latency: {sum(latencies) / len(latencies):.2f} seconds")
    print(f"Max Latency: {max(latencies):.2f} seconds")
    print(f"Min Latency: {min(latencies):.2f} seconds")
    print(f"\nResults saved to {output_csv}")

    if errors:
        print("\n--- Sample Errors ---")
        for err in errors[:5]:
            print(err)


if __name__ == "__main__":
    main()

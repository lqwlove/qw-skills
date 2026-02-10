"""
文生图工作流调用脚本
"""

import requests
import json
import time
import os
import argparse

# 配置
API_BASE = "https://www.runninghub.cn"
API_KEY = "4ac87db41cd64276aaba0cc05b0fbeb1"  # 替换为你的API Key
WORKFLOW_ID = "1992047551864172546"  # 替换为你的工作流ID

HEADERS = {
    "Host": "www.runninghub.cn",
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def get_workflow_info(workflow_id: str) -> dict:
    """获取工作流详情"""
    url = f"{API_BASE}/v1/workflow/{workflow_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def run_workflow(
    workflow_id: str, prompt: str, width: int, height: int, batch_size: int
) -> dict:
    """执行工作流"""
    url = f"{API_BASE}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id,
        "nodeInfoList": [
            {"nodeId": "13", "fieldName": "text", "fieldValue": prompt},
            {"nodeId": "21", "fieldName": "value", "fieldValue": width},
            {"nodeId": "23", "fieldName": "value", "fieldValue": height},
        ],
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def get_task_result(task_id: str) -> dict:
    """获取任务结果"""
    url = f"{API_BASE}/task/openapi/outputs"
    payload = {"apiKey": API_KEY, "taskId": task_id}
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    print(url, payload, response.json())
    return response.json()


def wait_for_completion(task_id: str, interval: int = 3, timeout: int = 300) -> dict:
    """等待任务完成"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = get_task_result(task_id)
        status = result.get("msg")
        if status == "success":
            return result
        elif status == "APIKEY_TASK_STATUS_ERROR":
            failedReason = (
                result.get("data").get("failedReason").get("exception_message")
            )
            raise Exception(f"任务失败: {failedReason}")
        elif status in ["APIKEY_TASK_IS_RUNNING", "APIKEY_TASK_IS_QUEUED"]:
            print(f"任务正在运行... {status}")
            time.sleep(interval)
        else:
            print(f"任务状态异常: {status}")
            time.sleep(interval)

    raise TimeoutError("任务超时")


def download_images(images: list, output_dir: str = None) -> list:
    """下载图片到output文件夹，文件名自动递增"""
    # 默认输出到项目根目录的output文件夹
    if output_dir is None:
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        output_dir = os.path.join(project_root, "output")
    # 创建output文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 获取已有图片的最大序号
    existing_files = os.listdir(output_dir)
    max_index = 0
    for f in existing_files:
        if f.startswith("image_") and f.endswith(".png"):
            try:
                index = int(f.replace("image_", "").replace(".png", ""))
                if index > max_index:
                    max_index = index
            except ValueError:
                continue

    saved_paths = []
    for i, img in enumerate(images):
        image_url = img.get("fileUrl")
        if not image_url:
            continue

        # 生成文件名（自动递增）
        ext = os.path.splitext(image_url)[1] or ".png"
        filename = f"image_{max_index + i + 1}{ext}"
        filepath = os.path.join(output_dir, filename)

        # 下载图片
        print(f"下载图片: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        saved_paths.append(filepath)
        print(f"已保存: {filepath}")

    return saved_paths


def txt2img_example(
    prompt: str, width: int = 1080, height: int = 1920, batch_size: int = 1
):
    # 2. 执行工作流
    print(f"执行工作流，提示词: {prompt}")
    print(f"参数: width={width}, height={height}, batch_size={batch_size}")
    run_result = run_workflow(WORKFLOW_ID, prompt, width, height, batch_size)
    print("执行工作流完成...", run_result)
    task_id = run_result.get("data", {}).get("taskId")
    print(f"任务ID: {task_id}")

    if not task_id:
        print(f"错误: {run_result}")
        return

    # 3. 等待任务完成
    print("等待生成完成...")
    result = wait_for_completion(task_id, 30)

    # 4. 输出结果
    print("生成完成!")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 获取图片URL并下载
    images = result.get("data", [])
    if images:
        saved_paths = download_images(images)
        print(f"\n共下载 {len(saved_paths)} 张图片到 output 文件夹")
    else:
        print("未找到生成的图片")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文生图脚本")
    parser.add_argument("--prompt", type=str, required=True, help="生成图片的提示词")
    parser.add_argument("--width", type=int, default=1080, help="图片宽度，默认1080")
    parser.add_argument("--height", type=int, default=1920, help="图片高度，默认1920")
    parser.add_argument("--batch", type=int, default=1, help="批次数量，默认1")
    args = parser.parse_args()

    txt2img_example(args.prompt, args.width, args.height, args.batch)

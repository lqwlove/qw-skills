"""
RunningHub 图生图工作流调用脚本
直接使用已上传的图片fileName运行工作流
"""

import requests
import json
import argparse
import time

# 配置
API_BASE = "https://www.runninghub.cn"
API_KEY = "4ac87db41cd64276aaba0cc05b0fbeb1"  # 替换为你的API Key
WORKFLOW_ID = "1995690953929273345"  # 替换为你的工作流ID

HEADERS = {
    "Host": "www.runninghub.cn",
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def run_workflow(image_name: str, prompt: str = None) -> dict:
    """执行图生图工作流"""
    url = f"{API_BASE}/task/openapi/create"

    node_info_list = [
        {
            "nodeId": "16",
            "fieldName": "image",
            "fieldValue": image_name,
        }
    ]

    if prompt:
        node_info_list.append(
            {"nodeId": "8", "fieldName": "prompt", "fieldValue": prompt}
        )

    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": node_info_list,
    }

    print(f"请求参数: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def get_task_result(task_id: str) -> dict:
    """获取任务结果"""
    url = f"{API_BASE}/task/openapi/outputs"
    payload = {"apiKey": API_KEY, "taskId": task_id}
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def get_output_image_url(task_result: dict) -> str:
    """获取生成的图片URL"""
    images = task_result.get("data", [])
    if images:
        return images[0].get("fileUrl")
    return None


def img2img(image_name: str, prompt: str, timeout: int = 300) -> str:
    """图生图主流程，直接返回图片URL"""
    print("=" * 50)
    print("执行图生图工作流")
    print(f"图片fileName: {image_name}")

    run_result = run_workflow(image_name, prompt)
    task_id = run_result.get("data", {}).get("taskId")
    print(f"任务ID: {task_id}")

    if not task_id:
        raise Exception(f"创建任务失败: {run_result}")

    # 轮询获取结果
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = get_task_result(task_id)
        status = result.get("msg")

        if status == "success":
            image_url = get_output_image_url(result)
            print(f"\n生成完成! 图片URL: {image_url}")
            return image_url
        elif status == "APIKEY_TASK_STATUS_ERROR":
            failed_reason = (
                result.get("data", {})
                .get("failedReason", {})
                .get("exception_message", "未知错误")
            )
            raise Exception(f"任务失败: {failed_reason}")
        elif status in ["APIKEY_TASK_IS_RUNNING", "APIKEY_TASK_IS_QUEUED"]:
            print(f"任务正在运行... {status}")
            time.sleep(3)
        else:
            print(f"任务状态异常: {status}")
            time.sleep(3)

    raise TimeoutError("任务超时")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunningHub 图生图脚本")
    parser.add_argument(
        "--image", type=str, required=True, help="输入已上传图片的fileName"
    )
    parser.add_argument("--prompt", type=str, required=True, help="生成图片的提示词")
    args = parser.parse_args()
    result = img2img(args.image, args.prompt)
    print(f"\n最终结果: {result}")

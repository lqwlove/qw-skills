"""
RunningHub 文件上传脚本
用于上传图片到RunningHub，并在工作流中使用
"""

import requests
import json
import os
import argparse

# 配置
API_BASE = "https://www.runninghub.cn"
API_KEY = "4ac87db41cd64276aaba0cc05b0fbeb1"  # 替换为你的API Key

HEADERS = {
    "Host": "www.runninghub.cn",
    "Authorization": f"Bearer {API_KEY}",
}


def upload_file(file_path: str) -> dict:
    """
    上传文件到RunningHub
    支持图片格式: .png, .jpg, .jpeg, .webp
    """
    url = f"{API_BASE}/openapi/v2/media/upload/binary"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 检查文件大小 (最大50MB)
    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:
        raise ValueError(f"文件大小超过50MB限制: {file_size / 1024 / 1024:.2f}MB")

    # 获取文件名和扩展名
    filename = os.path.basename(file_path)

    # 根据扩展名确定Content-Type
    ext = os.path.splitext(filename)[1].lower()
    content_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    content_type = content_types.get(ext, "application/octet-stream")

    print(f"上传文件: {file_path} ({file_size / 1024:.2f}KB)")

    with open(file_path, "rb") as f:
        files = {"file": (filename, f, content_type)}
        response = requests.post(url, files=files, headers=HEADERS)

    response.raise_for_status()
    result = response.json()

    if result.get("code") == 0:
        download_url = result.get("data", {}).get("download_url")
        print(f"上传成功! fileurl: {download_url}")
        return download_url
    else:
        raise Exception(f"上传失败: {result}")


def main():
    parser = argparse.ArgumentParser(description="RunningHub 文件上传脚本")
    parser.add_argument("--file", type=str, required=True, help="要上传的文件路径")
    args = parser.parse_args()
    download_url = upload_file(args.file)
    print("\n结果:")
    print(json.dumps(download_url, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

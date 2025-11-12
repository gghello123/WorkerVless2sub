import requests
import json
import os
import sys
from datetime import datetime

# -------------------------- 配置参数（根据实际接口修改）--------------------------
API_URL = "https://vps789.com/public/sum/cfIpApi"  # 目标接口 URL
REQUEST_METHOD = "GET"  # 请求方式：GET/POST
# 请求头（如需要 Token、User-Agent 等）
HEADERS = {
    "User-Agent": "GitHub Actions/1.0",
    "Authorization": "Bearer YOUR_TOKEN"  # 如有 Token，替换为实际值（私有信息建议用 Secrets）
}
# 请求参数（GET 用 params，POST 用 data/json）
PARAMS = {"page": 1, "limit": 100}  # GET 参数
# POST_DATA = {"key": "value"}  # POST 表单参数（如需用，在 requests.post 中指定 data=POST_DATA）
# POST_JSON = {"key": "value"}  # POST JSON 参数（如需用，在 requests.post 中指定 json=POST_JSON）

# 解析结果存储路径（与工作流配置中的 git add 路径一致）
OUTPUT_DIR = "data"
OUTPUT_FILENAME = f"result_{datetime.now().strftime('%Y%m%d')}.json"  # 按日期命名
# --------------------------------------------------------------------------------

def fetch_and_parse_api():
    # 1. 创建存储目录（如不存在）
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        # 2. 发送接口请求
        print(f"开始请求接口：{API_URL}")
        if REQUEST_METHOD.upper() == "GET":
            response = requests.get(
                API_URL,
                headers=HEADERS,
                params=PARAMS,
                timeout=30  # 超时时间30秒
            )
        elif REQUEST_METHOD.upper() == "POST":
            response = requests.post(
                API_URL,
                headers=HEADERS,
                # data=POST_DATA,  # 如需 POST 表单数据，解开注释
                # json=POST_JSON,  # 如需 POST JSON 数据，解开注释
                timeout=30
            )
        else:
            raise ValueError(f"不支持的请求方式：{REQUEST_METHOD}")

        # 3. 检查请求是否成功（状态码 200-299）
        response.raise_for_status()
        print("接口请求成功，开始解析数据...")

        # 4. 解析数据（JSON 接口示例，如需解析 XML 可改用 lxml 库）
        raw_data = response.json()  # 原始数据
        # -------------------------- 数据解析逻辑（根据实际需求修改）--------------------------
        data_list = raw_data.get("data", {}).get("CT",[]) + raw_data.get("data", {}).get("CU",[]) + raw_data.get("data", {}).get("CM",[]) + raw_data.get("data", {}).get("AllAvg",[])
        parsed_old_data = [
            item["ip"] for item in data_list
        ]

        parsed_data = " #vps\n".join(parsed_old_data)
        print(parsed_data+" #vps")
        #parsed_data = parsed_old_data.replace("[", "").replace("]", "").replace('",',"")



        # --------------------------------------------------------------------------------

        original_stdout = sys.stdout
        # 5. 保存解析结果到文件（格式化 JSON，方便查看）
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        with open(output_path, "w", encoding="utf-8") as f:
            sys.stdout = f
            print(parsed_data+" #vps")
            #json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        sys.stdout = original_stdout
        print(f"数据解析完成，已保存到：{output_path}")

    except requests.exceptions.RequestException as e:
        # 处理请求异常（超时、连接失败、状态码错误等）
        error_msg = f"接口请求失败：{str(e)}"
        print(error_msg)
        # 保存错误信息到文件（可选）
        error_path = os.path.join(OUTPUT_DIR, f"error_{datetime.now().strftime('%Y%m%d')}.txt")
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(error_msg)
        raise  # 抛出异常，让 GitHub Actions 标记任务失败

    except json.JSONDecodeError as e:
        # 处理 JSON 解析失败（接口返回非 JSON 数据）
        error_msg = f"JSON 解析失败：{str(e)}"
        print(error_msg)
        raise

if __name__ == "__main__":
    fetch_and_parse_api()

import requests
import json
import os
import sys
import re
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
OUTPUT_FILENAME = f"cfIpApi.txt"  # 按日期命名
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

        htmllist =fetch_and_parse_html()
        parsed_old_data = parsed_old_data + htmllist
        
        parsed_data = ":443#vps\n".join(parsed_old_data)
        parsed_data = parsed_data + ":8443#vps\n"
        
        result= '\n'.join(fetch_and_process_proxies("8443"))
        parsed_data = parsed_data + result
        parsed_data = parsed_data + "\n"

        parsed_data = parsed_data + extract_fast_ips_robust()
        
        print(parsed_data)
        #parsed_data = parsed_old_data.replace("[", "").replace("]", "").replace('",',"")

        #推送
        url = "https://shell.649879112.xyz/0fa36c91-3151-4528-8a14-b1940bd436d2//api/preferred-ips"
        ips = parsed_old_data
        default_port = 8443
        data = [
            {"ip": ip, "port": default_port, "name": f"vps{i+1}"}
            for i, ip in enumerate(ips)
        ]
        #response = requests.delete(url, json={"all": True}, headers={"Content-Type": "application/json"})
        #print(f"状态码: {response.status_code}")
        #print(f"响应内容: {response.text}")
        #response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        # --------------------------------------------------------------------------------

        original_stdout = sys.stdout
        # 5. 保存解析结果到文件（格式化 JSON，方便查看）
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        with open(output_path, "w", encoding="utf-8") as f:
            sys.stdout = f
            #print("saas.sin.fan#加入频道@kejiland00")
            print(parsed_data)
            #print("saas.sin.fan#gg")
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
#获取html中ip
def fetch_and_parse_html():
    # 正则表达式用于匹配IP地址
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    # 使用集合存储IP地址实现自动去重
    unique_ips = set()
    # 发送HTTP请求获取网页内容
    response = requests.get("https://ip.164746.xyz", timeout=5)

    # 确保请求成功
    if response.status_code == 200:
        # 获取网页的文本内容
        html_content = response.text

        # 使用正则表达式查找IP地址
        ip_matches = re.findall(ip_pattern, html_content, re.IGNORECASE)

        # 将找到的IP添加到集合中（自动去重）
        unique_ips.update(ip_matches)

    # 按IP地址的数字顺序排序（非字符串顺序）
    sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])
    return sorted_ips
#获取国家
def fetch_and_process_proxies(port:str):
    # 目标URL
    url = "https://ipdb.api.030101.xyz/?type=bestproxy&country=true"

    try:
        # 发送GET请求获取内容
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功

        # 确保使用正确的编码（通常为UTF-8）
        response.encoding = 'utf-8'
        content = response.text

        # 按行分割并处理
        processed_lines = []
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line:  # 跳过空行
                continue

            # 在#号前添加:443
            if '#' in line:
                # 将IP和后面的部分分开
                ip_part, country_part = line.split('#', 1)
                new_line = f"{ip_part}:{port}#{country_part}"
                processed_lines.append(new_line)
            else:
                # 如果没有#号（理论上不应该发生），保持原样
                processed_lines.append(line)

        return processed_lines

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return []
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return []

# 最可靠的方法：基于表格结构精确匹配
def extract_fast_ips_robust():
    """
    最可靠的方法：精确匹配表格行结构
    """
    # 目标URL
    url = "https://api.uouin.com/cloudflare.html"
    """从URL读取HTML"""
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        html_content = response.text

        results = []

        # 匹配完整的表格行（包含所有字段）
        # 使用更精确的模式
        pattern = r'<tr>\s*<th[^>]*>\s*\d+\s*</th>\s*<td[^>]*>\s*(电信|联通|移动|多线)\s*</td>\s*<td[^>]*>\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td[^>]*>\s*([\d.]+%)\s*</td>\s*<td[^>]*>\s*([\d.]+ms)\s*</td>\s*<td[^>]*>\s*([\d.]+mb/s)\s*</td>'

        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)

        for match in matches:
            line, ip, loss, delay, speed_text = match
            speed = float(re.search(r'(\d+(?:\.\d+)?)', speed_text).group(1))

            if speed > 5:
                # 这是多行注释（不会被赋值）
                """
                results.append({
                    'line': line,
                    'ip': ip,
                    'speed': speed,
                    'speed_text': speed_text,
                    'delay': delay,
                    'loss': loss
                })
                """
                # 拼接格式：ip:443#线路速度（速度保留一位小数）
                #result = f"{ip}:443#{line}{int(speed)}"
                result = f"{ip}:443#{line}{speed:.1f}"
                results.append(result)
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return ''
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return ''
    # 返回拼接后的字符串
    return '\n'.join(results)

if __name__ == "__main__":
    fetch_and_parse_api()

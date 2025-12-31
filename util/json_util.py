"""JSON 处理工具"""

import re
import json
import os


def extract_json(text: str) -> dict:
    """从文本中提取 JSON 并转换为对象
    
    使用方法:
        result = extract_json(ai_response)
        print(result["title"])
    """
    # 匹配 ```json ... ``` 代码块
    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    
    # 如果没有代码块，尝试直接匹配 {...}
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return json.loads(match.group(0))
    
    raise ValueError("未找到有效的 JSON")

def save_json(data: dict, file_path: str):
    os.makedirs(file_path, exist_ok=True)
    json_path = os.path.join(file_path, "content.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ data 已保存到 {json_path}")
    
def load_json(file_path: str) -> dict:
    json_path = os.path.join(file_path, "content.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
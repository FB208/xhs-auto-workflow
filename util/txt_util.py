"""文本文件工具"""

import os

# 默认文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SUBJECT_FILE = os.path.join(DATA_DIR, "subject.txt")


def read_subjects() -> list[str]:
    """从 subject.txt 读取所有行"""
    if not os.path.exists(SUBJECT_FILE):
        return []
    
    with open(SUBJECT_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    
    # 过滤空行
    return [line.strip() for line in lines if line.strip()]


def add_subject(text: str) -> None:
    """添加一行文本到 subject.txt 末尾"""
    # 确保目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(SUBJECT_FILE, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

from util.txt_util import read_subjects

def topic_discussion_prompt(command):
    prompt = ""
    if command == "1":
        prompt = """
我们一起来为易标AI生成自媒体推广选题工作。
易标AI是一款用AI生成投标技术方案的工具，具备智能解析招标文件、快速生成投标文件、标书查重等功能。
你需要联网搜索关于AI写标书和易标AI的相关资料，生成5个选题。
选题面向中小企业老板。
"""
    elif command == "2":
        prompt = """
我们一起来完成自媒体内容的选题工作。媒体内容是面向招投标行业的。
我们旨在为用户提供一些有价值的内容，让用户看过之后觉得有用，想要把内容收藏起来，以便日后参考、学习、查询等。
你需要联网搜索关于招投标行业的相关资料，并生成5个选题。
    """
    else:
        prompt = f"""我们一起来完成自媒体内容的选题工作。
        你需要结合我提出的要求，联网搜索最新资料，并生成5个选题。
        我的要求如下：
        {command}
        """
        
    
    # 添加历史选题，避免重复
    old_subject = read_subjects()
    if old_subject:
        prompt += f"""以下是之前使用过的选题，以<old_subject包裹>,你确保新生成的选题不要和之前的重复：
        <old_subject>
        {old_subject}
        </old_subject>
        """
    return prompt
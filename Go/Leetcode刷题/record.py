from datetime import datetime
import os
import re
import urllib.parse

def scan_md_files(directory):
    """
    扫描指定目录下的所有Markdown文件，提取题目名、题号及其位置锚点。

    Args:
        directory (str): 要扫描的目录路径。

    Returns:
        list: 包含元组(title, number, link)的列表。
    """
    # 用于存储题目名、题号和链接的列表
    problems = []

    # 遍历指定目录下的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            # 排除掉题号记录文件
            if file.endswith('.md') and file != "README.md":
                # 构建文件的完整路径
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.readlines()

                    # 逐行扫描，查找二级标题
                    for line in content:
                        # 跳过空行或非二级标题
                        if len(line.strip()) == 0 or not line.startswith('##'):
                            continue
                        # 正则匹配形如 "## 1. 两数之和（1）" 的标题
                        match = re.match(r"##\s*(\d+)\.\s*(.*?)\s*（(\d+)）", line)
                        if match:
                            # 从正则中捕获编号、题目名和内部编号
                            prefix_number = match.group(1).strip()  # 前缀编号，如 "1"
                            title = match.group(2).strip()          # 题目名，如 "两数之和"
                            internal_number = match.group(3).strip()# 内部编号，如 "1"

                            # 生成锚点，包含前缀编号和题目名
                            full_title = f"{prefix_number}. {title}（{internal_number}）"
                            anchor = generate_anchor(full_title)

                            # 生成相对路径
                            relative_path = os.path.relpath(file_path, directory).replace(os.sep, '/')

                            # 获取文件名（包含扩展名）作为链接文字
                            display_name = file  # 如果不需要扩展名，可以使用 os.path.splitext(file)[0]

                            # 构建Markdown链接
                            link = f"[{display_name}]({urllib.parse.quote(relative_path)}#{urllib.parse.quote(anchor)})"

                            # 添加到列表中
                            problems.append((title, int(internal_number), link))

    return problems

def generate_anchor(full_title):
    """
    根据完整的标题生成Markdown锚点。

    Args:
        full_title (str): 完整的标题文本。

    Returns:
        str: 生成的锚点。
    """
    # 将标题转换为小写（可选，根据Typora的锚点规则）
    anchor = full_title.lower()

    # 移除特殊字符（保留中文字符、字母、数字和连字符）
    # 这里保留了中文字符
    anchor = re.sub(r'[^\w\s\-]', '', anchor)

    # 用空格和下划线替换为连字符
    anchor = re.sub(r'[\s_]+', '-', anchor)

    return anchor

def generate_markdown(problems, output_path):
    """
    根据提取到的题目信息生成Markdown记录文件。

    Args:
        problems (list): 包含题目信息的列表。
        output_path (str): 输出Markdown文件的路径。
    """
    # 按照题号进行排序
    problems.sort(key=lambda x: x[1])  # 根据题号升序排序

    # 生成 Markdown 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 题号记录\n\n")

        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"记录时间：{formatted_time}\n\n")
        f.write(f"总共有 {len(problems)} 个题目。\n\n")

        # 写入表头
        f.write("| 题目名       | 题号 | 链接 |\n")
        f.write("|--------------|------|------|\n")

        # 写入每一行数据
        for title, number, link in problems:
            f.write(f"| {title} | {number} | {link} |\n")
        
        # 最后加几个换行
        f.write("\n\n")
        

def main():
    # 输入目录路径
    directory = './'

    # 扫描目录下的所有 .md 文件
    problems = scan_md_files(directory)

    if problems:
        # 在当前目录下生成 README.md 文件
        output_path = os.path.join(directory, "README.md")
        generate_markdown(problems, output_path)
        print(f"题号记录已保存到 {output_path}")
    else:
        print("未在目录下找到符合要求的二级标题。")

if __name__ == "__main__":
    main()

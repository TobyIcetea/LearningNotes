from datetime import datetime
import os
import re


def scan_md_files(directory):
    # 用于存储题目名和题号的列表
    problems = []

    # 遍历指定目录下的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            # 排除掉题号记录文件
            if file.endswith('.md') and file != "record.md":
                # 构建文件的完整路径
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.readlines()

                    # 逐行扫描，查找二级标题
                    for line in content:
                        # 正则匹配形如 "## 1. 两数之和（1）" 的标题
                        if len(line.strip()) == 0 or not line.startswith('##'):
                            continue
                        match = re.match(r"##\s*\d+\.\s*(.*?)\s*（(\d+)）", line)
                        if match:
                            title = match.group(1).strip()  # 题目名
                            number = int(match.group(2))  # 题号（转换为整数以便排序）
                            problems.append((title, number))

    return problems


def generate_markdown(problems, output_path):
    # 按照题号进行排序
    problems.sort(key=lambda x: x[1])  # 根据题号升序排序

    # 生成 Markdown 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 题号记录\n\n")

        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"记录时间：{formatted_time}\n\n")

        f.write("| 题目名       | 题号 |\n")
        f.write("|--------------|------|\n")

        for title, number in problems:
            f.write(f"| {title} | {number} |\n")


def main():
    # 输入目录路径
    directory = './'

    # 扫描目录下的所有 .md 文件
    problems = scan_md_files(directory)

    if problems:
        # 在当前目录下生成 record.md 文件
        output_path = os.path.join(directory, "record.md")
        generate_markdown(problems, output_path)
        print(f"题号记录已保存到 {output_path}")
    else:
        print("未在目录下找到符合要求的二级标题。")


if __name__ == "__main__":
    main()

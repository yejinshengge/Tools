import os
import re
import requests
from urllib.parse import urlparse
from pathlib import Path

def download_image(url, save_dir):
    """下载图片到指定目录"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 从URL中获取文件名
            filename = os.path.basename(urlparse(url).path)
            if not filename:  # 如果URL没有文件名，使用URL的最后一部分
                filename = url.split('/')[-1]
            
            # 确保文件名有扩展名
            if not os.path.splitext(filename)[1]:
                # 从Content-Type中获取扩展名
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    filename += '.jpg'
                elif 'png' in content_type:
                    filename += '.png'
                elif 'gif' in content_type:
                    filename += '.gif'
                else:
                    filename += '.png'  # 默认使用png

            # 保存图片
            save_path = os.path.join(save_dir, filename)
            os.makedirs(save_dir, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return filename
    except Exception as e:
        print(f"下载图片失败: {url}")
        print(f"错误信息: {str(e)}")
        return None

def process_markdown_file(md_file_path):
    """处理单个Markdown文件"""
    # 创建图片保存目录
    md_dir = os.path.dirname(md_file_path)
    images_dir = os.path.join(md_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # 读取Markdown文件内容
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找所有图片链接
    # 匹配 ![任意文本](URL) 格式
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.finditer(pattern, content)

    # 记录所有需要替换的内容
    replacements = []
    
    for match in matches:
        alt_text = match.group(1)
        url = match.group(2)
        
        # 如果已经是本地路径，跳过
        if url.startswith('./') or url.startswith('../') or url.startswith('/'):
            continue

        # 下载图片
        filename = download_image(url, images_dir)
        if filename:
            # 构建新的本地路径（使用相对路径）
            new_path = f'./images/{filename}'
            # 构建新的图片标记
            new_image_mark = f'![{alt_text}]({new_path})'
            # 添加到替换列表
            replacements.append((match.group(0), new_image_mark))

    # 执行所有替换
    new_content = content
    for old, new in replacements:
        new_content = new_content.replace(old, new)

    # 保存修改后的文件
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def process_all_markdown_files(directory):
    """处理目录下的所有Markdown文件"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                print(f"处理文件: {md_path}")
                process_markdown_file(md_path)

if __name__ == "__main__":
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"开始处理目录: {current_dir}")
    process_all_markdown_files(current_dir) 
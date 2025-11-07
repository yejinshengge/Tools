#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML转EPUB电子书工具
支持将一组HTML文档转换为EPUB格式的电子书
"""

import os
import re
import argparse
import json
from pathlib import Path
from bs4 import BeautifulSoup
from ebooklib import epub
from urllib.parse import urljoin, urlparse
from PIL import Image
import io

class HtmlToEpub:
    def __init__(self, input_dir, output_file, title="电子书", author="未知作者", language="zh-CN"):
        """
        初始化HTML转EPUB转换器
        
        Args:
            input_dir: HTML文件所在目录
            output_file: 输出的EPUB文件路径
            title: 电子书标题
            author: 作者
            language: 语言代码
        """
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.title = title
        self.author = author
        self.language = language
        
        # 创建EPUB书籍对象
        self.book = epub.EpubBook()
        
        # 设置书籍元数据
        self.book.set_identifier('html_to_epub_' + str(hash(str(input_dir))))
        self.book.set_title(self.title)
        self.book.set_language(self.language)
        self.book.add_author(self.author)
        
        # 章节列表
        self.chapters = []
        # 图片资源
        self.images = {}
        # CSS样式
        self.styles = []
        # 文件顺序映射 (文件路径 -> 顺序索引)
        self.file_order = {}
        # HTML文件信息 (文件路径 -> (标题, 内容))
        self.html_files_info = {}
        
    def get_html_files(self):
        """获取所有HTML文件（不排序，排序由get_ordered_html_files处理）"""
        html_files = []
        for ext in ['*.html', '*.htm']:
            html_files.extend(self.input_dir.rglob(ext))
        return html_files
    
    def find_toc_in_html(self, html_file):
        """从HTML文件中查找目录结构"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 尝试多种常见的目录结构
            toc_selectors = [
                'nav',
                'nav.toc',
                'nav#toc',
                'div.toc',
                'div#toc',
                'ul.toc',
                'ul#toc',
                'ol.toc',
                'ol#toc',
                '[class*="toc"]',
                '[id*="toc"]',
                '[class*="table-of-contents"]',
                '[id*="table-of-contents"]',
                '[class*="contents"]',
                '[id*="contents"]',
            ]
            
            toc_element = None
            for selector in toc_selectors:
                toc_element = soup.select_one(selector)
                if toc_element:
                    break
            
            if not toc_element:
                return None
            
            # 提取目录中的链接
            links = []
            for link in toc_element.find_all('a', href=True):
                href = link.get('href')
                if href:
                    # 处理相对路径
                    if not urlparse(href).scheme:
                        # 相对路径，转换为绝对路径
                        link_path = (html_file.parent / href).resolve()
                    else:
                        # 绝对路径或URL
                        link_path = Path(href)
                    
                    # 检查是否是HTML文件
                    if link_path.suffix.lower() in ['.html', '.htm']:
                        # 检查文件是否存在
                        if link_path.exists():
                            links.append({
                                'path': link_path,
                                'title': link.get_text(strip=True) or link_path.stem,
                                'href': href
                            })
            
            return links if links else None
            
        except Exception as e:
            print(f"查找目录失败 {html_file}: {str(e)}")
            return None
    
    def load_order_from_config(self, config_file):
        """从配置文件加载文件顺序"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            order_list = config.get('order', [])
            if not order_list:
                return False
            
            # 构建文件路径到顺序的映射
            for idx, item in enumerate(order_list):
                if isinstance(item, str):
                    # 简单字符串，作为相对路径
                    file_path = (self.input_dir / item).resolve()
                elif isinstance(item, dict):
                    # 字典格式，包含path和title
                    path_str = item.get('path', '')
                    file_path = (self.input_dir / path_str).resolve()
                else:
                    continue
                
                if file_path.exists():
                    self.file_order[file_path] = idx
            
            return len(self.file_order) > 0
            
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return False
    
    def detect_toc_from_files(self, html_files):
        """从HTML文件中检测目录结构"""
        print("正在检测目录结构...")
        
        # 如果文件太多，只检查常见的目录文件，不遍历所有文件
        file_count = len(html_files)
        max_files_to_check = 1000  # 最多检查1000个文件
        
        if file_count > max_files_to_check:
            print(f"文件数量较多（{file_count}个），仅检查常见的目录文件...")
            # 只检查常见的目录文件
            toc_candidates = [
                'index.html', 'index.htm',
                'toc.html', 'toc.htm',
                'contents.html', 'contents.htm',
                '目录.html', '目录.htm',
            ]
            
            # 构建文件名到文件的映射（只针对候选文件）
            candidate_files = {}
            for html_file in html_files:
                if html_file.name.lower() in [c.lower() for c in toc_candidates]:
                    candidate_files[html_file.name.lower()] = html_file
            
            # 按优先级检查候选文件
            for candidate in toc_candidates:
                candidate_lower = candidate.lower()
                if candidate_lower in candidate_files:
                    html_file = candidate_files[candidate_lower]
                    toc_links = self.find_toc_in_html(html_file)
                    if toc_links:
                        print(f"在 {html_file.name} 中找到目录，包含 {len(toc_links)} 个链接")
                        # 构建文件顺序映射
                        for idx, link_info in enumerate(toc_links):
                            self.file_order[link_info['path']] = idx
                            # 保存标题信息
                            self.html_files_info[link_info['path']] = {
                                'title': link_info['title'],
                                'from_toc': True
                            }
                        return True
        else:
            # 文件数量不多，可以完整检查
            # 优先查找常见的目录文件
            toc_candidates = [
                'index.html', 'index.htm',
                'toc.html', 'toc.htm',
                'contents.html', 'contents.htm',
                '目录.html', '目录.htm',
            ]
            
            for candidate in toc_candidates:
                for html_file in html_files:
                    if html_file.name.lower() == candidate.lower():
                        toc_links = self.find_toc_in_html(html_file)
                        if toc_links:
                            print(f"在 {html_file.name} 中找到目录，包含 {len(toc_links)} 个链接")
                            # 构建文件顺序映射
                            for idx, link_info in enumerate(toc_links):
                                self.file_order[link_info['path']] = idx
                                # 保存标题信息
                                self.html_files_info[link_info['path']] = {
                                    'title': link_info['title'],
                                    'from_toc': True
                                }
                            return True
            
            # 如果没有找到专门的目录文件，尝试从前100个文件中查找
            print("检查其他文件中的目录结构（最多检查100个文件）...")
            checked = 0
            for html_file in html_files[:100]:  # 只检查前100个文件
                checked += 1
                if checked % 10 == 0:
                    print(f"  已检查 {checked} 个文件...")
                toc_links = self.find_toc_in_html(html_file)
                if toc_links and len(toc_links) >= 3:  # 至少3个链接才认为是目录
                    print(f"在 {html_file.name} 中找到目录，包含 {len(toc_links)} 个链接")
                    for idx, link_info in enumerate(toc_links):
                        self.file_order[link_info['path']] = idx
                        self.html_files_info[link_info['path']] = {
                            'title': link_info['title'],
                            'from_toc': True
                        }
                    return True
        
        return False
    
    def get_ordered_html_files(self, html_files):
        """获取排序后的HTML文件列表"""
        # 如果已经有文件顺序映射，使用它
        if self.file_order:
            # 按顺序排序
            ordered_files = []
            unordered_files = []
            
            for html_file in html_files:
                resolved_path = html_file.resolve()
                if resolved_path in self.file_order:
                    ordered_files.append((self.file_order[resolved_path], html_file))
                else:
                    unordered_files.append(html_file)
            
            # 排序已有序的文件
            ordered_files.sort(key=lambda x: x[0])
            result = [f for _, f in ordered_files]
            
            # 添加未在目录中的文件（按文件名排序）
            unordered_files.sort(key=lambda x: str(x))
            result.extend(unordered_files)
            
            return result
        else:
            # 没有目录，按文件名排序
            html_files.sort(key=lambda x: str(x))
            return html_files
    
    def clean_html(self, soup, base_path):
        """清理HTML内容，提取主要内容，处理图片和样式"""
        # 移除script和style标签
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()
        
        # 移除注释
        from bs4 import Comment
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # 处理图片
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # 处理相对路径
                if not urlparse(src).scheme:
                    # 相对路径，转换为绝对路径
                    img_path = (base_path.parent / src).resolve()
                else:
                    # 绝对路径或URL
                    img_path = Path(src)
                
                # 检查图片是否存在
                if img_path.exists() and img_path.is_file():
                    # 处理图片
                    img_id = self.process_image(img_path)
                    if img_id:
                        img['src'] = img_id
                    else:
                        # 如果处理失败，移除图片标签
                        img.decompose()
                else:
                    # 图片不存在，移除标签
                    img.decompose()
            else:
                img.decompose()
        
        # 处理链接，移除外部链接的href
        for a in soup.find_all('a'):
            href = a.get('href')
            if href:
                # 如果是外部链接，移除href或改为#号
                parsed = urlparse(href)
                if parsed.scheme and parsed.scheme not in ['', 'file']:
                    a['href'] = '#'
                # 如果是本地HTML文件链接，可以保留（但EPUB中可能无法跳转）
                elif href.startswith('#'):
                    # 锚点链接保留
                    pass
                else:
                    # 本地文件链接，移除或改为#
                    a['href'] = '#'
        
        # 提取内联样式或添加基本样式
        style_tag = soup.find('style')
        if style_tag:
            self.styles.append(style_tag.string)
        
        return soup
    
    def process_image(self, img_path):
        """处理图片，添加到EPUB中并返回图片ID"""
        try:
            # 检查是否已处理过
            img_str = str(img_path)
            if img_str in self.images:
                return self.images[img_str]
            
            # 读取图片
            with open(img_path, 'rb') as f:
                img_data = f.read()
            
            # 获取文件扩展名
            ext = img_path.suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                return None
            
            # 转换webp为png（如果支持）
            if ext == '.webp':
                try:
                    img = Image.open(io.BytesIO(img_data))
                    output = io.BytesIO()
                    img.save(output, format='PNG')
                    img_data = output.getvalue()
                    ext = '.png'
                except:
                    return None
            
            # 生成图片ID
            img_id = f'image_{len(self.images)}'
            
            # 确定MIME类型
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml'
            }
            mime_type = mime_type_map.get(ext, 'image/png')
            
            # 添加到EPUB
            self.book.add_item(epub.EpubItem(
                uid=img_id,
                file_name=f'images/{img_id}{ext}',
                media_type=mime_type,
                content=img_data
            ))
            
            # 保存映射
            self.images[img_str] = f'images/{img_id}{ext}'
            
            return f'images/{img_id}{ext}'
            
        except Exception as e:
            print(f"处理图片失败 {img_path}: {str(e)}")
            return None
    
    def create_chapter(self, html_file, content):
        """创建EPUB章节"""
        # 尝试从目录信息中获取标题，否则使用文件名
        resolved_path = html_file.resolve()
        if resolved_path in self.html_files_info:
            chapter_title = self.html_files_info[resolved_path].get('title', html_file.stem)
        else:
            # 尝试从HTML内容中提取标题
            try:
                soup = BeautifulSoup(content, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    chapter_title = title_tag.get_text(strip=True)
                else:
                    h1_tag = soup.find('h1')
                    if h1_tag:
                        chapter_title = h1_tag.get_text(strip=True)
                    else:
                        chapter_title = html_file.stem
            except:
                chapter_title = html_file.stem
        
        # 创建章节
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapter_{len(self.chapters)}.xhtml',
            lang=self.language
        )
        
        # 添加内容
        chapter.content = content.encode('utf-8')
        
        # 添加到书籍
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        
        return chapter
    
    def add_default_css(self):
        """添加默认CSS样式"""
        default_css = """
        body {
            font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
            line-height: 1.6;
            margin: 1em;
            padding: 0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        p {
            margin: 0.5em 0;
            text-align: justify;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }
        code {
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: "Consolas", "Monaco", monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        blockquote {
            border-left: 4px solid #ddd;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        table th, table td {
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }
        table th {
            background-color: #f4f4f4;
            font-weight: bold;
        }
        """
        
        # 创建CSS文件
        nav_css = epub.EpubItem(
            uid="nav_css",
            file_name="style/nav.css",
            media_type="text/css",
            content=default_css.encode('utf-8')
        )
        self.book.add_item(nav_css)
        
        # 为所有章节添加CSS引用
        for chapter in self.chapters:
            chapter.add_item(nav_css)
    
    def convert(self, order_config=None):
        """执行转换"""
        print(f"开始转换HTML文件为EPUB...")
        print(f"输入目录: {self.input_dir}")
        print(f"输出文件: {self.output_file}")
        print(f"标题: {self.title}")
        print(f"作者: {self.author}")
        print("-" * 60)
        
        # 获取所有HTML文件
        html_files = self.get_html_files()
        
        if not html_files:
            print("错误: 未找到任何HTML文件！")
            return False
        
        print(f"找到 {len(html_files)} 个HTML文件")
        
        # 尝试加载配置文件中的顺序
        if order_config and Path(order_config).exists():
            if self.load_order_from_config(order_config):
                print(f"已从配置文件加载文件顺序: {len(self.file_order)} 个文件")
        
        # 如果没有配置文件，尝试从HTML文件中检测目录
        if not self.file_order:
            self.detect_toc_from_files(html_files)
            if self.file_order:
                print(f"已从HTML文件中检测到目录: {len(self.file_order)} 个文件")
        
        # 获取排序后的文件列表
        ordered_files = self.get_ordered_html_files(html_files)
        
        if self.file_order:
            print(f"将按照检测到的目录顺序处理文件")
        else:
            print(f"将按照文件名顺序处理文件")
        
        print("-" * 60)
        
        # 处理每个HTML文件
        for i, html_file in enumerate(ordered_files, 1):
            print(f"[{i}/{len(ordered_files)}] 处理: {html_file.name}")
            
            try:
                # 读取HTML文件
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 解析HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 清理HTML
                cleaned_soup = self.clean_html(soup, html_file)
                
                # 获取body内容
                body = cleaned_soup.find('body')
                if not body:
                    # 如果没有body标签，使用整个文档
                    body_content = str(cleaned_soup)
                else:
                    body_content = str(body)
                
                # 创建完整的XHTML内容
                xhtml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>{html_file.stem}</title>
    <link rel="stylesheet" type="text/css" href="style/nav.css"/>
</head>
<body>
{body_content}
</body>
</html>"""
                
                # 创建章节
                self.create_chapter(html_file, xhtml_content)
                
            except Exception as e:
                print(f"处理文件失败 {html_file}: {str(e)}")
                continue
        
        if not self.chapters:
            print("错误: 没有成功创建任何章节！")
            return False
        
        # 添加默认CSS
        self.add_default_css()
        
        # 创建目录
        self.book.toc = tuple(self.chapters)
        
        # 添加导航文件
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        
        # 设置书籍封面（如果有）
        # 可以在这里添加封面图片
        
        # 设置书籍的spine（阅读顺序）
        self.book.spine = ['nav'] + self.chapters
        
        # 保存EPUB文件
        print("-" * 60)
        print(f"正在保存EPUB文件...")
        epub.write_epub(self.output_file, self.book, {})
        
        print(f"✅ 转换完成！")
        print(f"   输出文件: {self.output_file}")
        print(f"   章节数: {len(self.chapters)}")
        print(f"   图片数: {len(self.images)}")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='HTML转EPUB电子书工具 - 将一组HTML文档转换为EPUB格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python html_to_epub.py input_dir -o output.epub
  
  # 指定标题和作者
  python html_to_epub.py input_dir -o output.epub -t "我的电子书" -a "作者名"
  
  # 递归处理子目录中的HTML文件
  python html_to_epub.py docs -o book.epub -t "文档集" -a "文档作者"
  
  # 使用配置文件指定章节顺序
  python html_to_epub.py docs -o book.epub -c order.json
        """
    )
    
    parser.add_argument('input_dir', help='HTML文件所在目录')
    parser.add_argument('-o', '--output', required=True,
                       help='输出的EPUB文件路径（必需）')
    parser.add_argument('-t', '--title', default='电子书',
                       help='电子书标题（默认: 电子书）')
    parser.add_argument('-a', '--author', default='未知作者',
                       help='作者（默认: 未知作者）')
    parser.add_argument('-l', '--language', default='zh-CN',
                       help='语言代码（默认: zh-CN）')
    parser.add_argument('-c', '--config',
                       help='章节顺序配置文件（JSON格式）')
    
    args = parser.parse_args()
    
    # 检查输入目录
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"错误: 输入目录不存在: {args.input_dir}")
        return
    
    if not input_path.is_dir():
        print(f"错误: 输入路径不是目录: {args.input_dir}")
        return
    
    # 创建转换器并执行转换
    converter = HtmlToEpub(
        input_dir=args.input_dir,
        output_file=args.output,
        title=args.title,
        author=args.author,
        language=args.language
    )
    
    converter.convert(order_config=args.config)


if __name__ == '__main__':
    main()


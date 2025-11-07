#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页文档下载工具
支持下载整个文档网站，包括HTML页面、CSS、JS、图片等资源
特别优化了Unity文档网站的下载
"""

import os
import re
import time
import argparse
import requests
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
from bs4 import BeautifulSoup
from collections import deque
import json

class DocDownloader:
    def __init__(self, base_url, output_dir, max_depth=10, delay=0.5):
        """
        初始化文档下载器
        
        Args:
            base_url: 起始URL
            output_dir: 输出目录
            max_depth: 最大爬取深度
            delay: 请求之间的延迟（秒）
        """
        self.base_url = base_url.rstrip('/')
        parsed_base = urlparse(self.base_url)
        self.base_domain = parsed_base.netloc
        # 保存基础路径前缀，用于限制下载范围
        self.base_path = parsed_base.path.rstrip('/')
        if not self.base_path:
            self.base_path = '/'
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.delay = delay
        
        # 已访问的URL集合
        self.visited_urls = set()
        # 待下载的URL队列 (url, depth, parent_url)
        self.url_queue = deque([(base_url, 0, None)])
        # 下载统计
        self.stats = {
            'pages': 0,
            'assets': 0,
            'errors': 0,
            'skipped': 0
        }
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载之前的下载记录（断点续传）
        self.load_progress()
        
        # 创建资源目录
        self.assets_dir = self.output_dir / 'assets'
        self.assets_dir.mkdir(exist_ok=True)
        
        # 会话对象，保持连接
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def should_download(self, url, is_asset=False):
        """
        判断是否应该下载该URL
        
        Args:
            url: 要检查的URL
            is_asset: 是否是资源文件（CSS、JS、图片等），资源文件不受路径限制
        """
        # 如果是相对URL，需要先转换为绝对URL
        parsed = urlparse(url)
        
        # 只下载同域名下的内容
        if parsed.netloc and parsed.netloc != self.base_domain:
            return False
        
        # 跳过已访问的URL
        if url in self.visited_urls:
            return False
        
        # 跳过非HTTP(S)协议
        if parsed.scheme not in ['http', 'https', '']:
            return False
        
        # 对于资源文件，只检查域名，不检查路径（资源文件可能在根目录或其他路径）
        if is_asset:
            # 跳过常见的不需要下载的文件类型
            skip_extensions = ['.pdf', '.zip', '.exe', '.dmg', '.deb', '.rpm']
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in skip_extensions):
                return False
            return True
        
        # 对于页面文件，检查路径前缀，确保只下载指定路径下的内容
        url_path = parsed.path
        if not url_path:
            url_path = '/'
        
        # 如果基础路径不是根路径，检查URL路径是否在基础路径下
        if self.base_path != '/':
            # 标准化路径（移除末尾斜杠进行比较）
            url_path_normalized = url_path.rstrip('/') or '/'
            base_path_normalized = self.base_path.rstrip('/')
            
            # 确保URL路径以基础路径开头
            if not url_path_normalized.startswith(base_path_normalized):
                return False
            
            # 额外检查：如果URL路径不是基础路径本身，确保下一个字符是斜杠
            if url_path_normalized != base_path_normalized:
                # 检查基础路径后是否跟着斜杠或路径结束
                if len(url_path_normalized) > len(base_path_normalized):
                    if url_path_normalized[len(base_path_normalized)] != '/':
                        return False
        
        # 跳过常见的不需要下载的文件类型
        skip_extensions = ['.pdf', '.zip', '.exe', '.dmg', '.deb', '.rpm']
        path = parsed.path.lower()
        if any(path.endswith(ext) for ext in skip_extensions):
            return False
        
        return True
    
    def get_local_path(self, url):
        """将URL转换为本地文件路径"""
        parsed = urlparse(url)
        path = parsed.path
        
        # 移除开头的斜杠
        if path.startswith('/'):
            path = path[1:]
        
        # 如果没有路径或路径为空，使用index.html
        if not path or path == '':
            path = 'index.html'
        
        # 如果是目录（以/结尾），添加index.html
        elif path.endswith('/'):
            path = path + 'index.html'
        
        # 如果没有扩展名，假设是HTML
        elif '.' not in os.path.basename(path):
            path = path + '.html'
        
        # 解码URL编码
        path = unquote(path)
        
        # 替换Windows不支持的字符
        path = path.replace(':', '_').replace('?', '_').replace('*', '_')
        path = path.replace('<', '_').replace('>', '_').replace('|', '_')
        
        return self.output_dir / path
    
    def load_progress(self):
        """加载之前的下载记录（断点续传）"""
        record_file = self.output_dir / 'download_record.json'
        if record_file.exists():
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                # 检查是否是同一个基础URL
                if record.get('base_url') == self.base_url:
                    # 恢复已访问的URL集合
                    self.visited_urls = set(record.get('visited_urls', []))
                    print(f"检测到之前的下载记录，已恢复 {len(self.visited_urls)} 个已下载的URL")
                    print(f"将继续下载未完成的页面...")
            except Exception as e:
                print(f"无法加载下载记录: {str(e)}")
    
    def download_file(self, url, local_path):
        """下载文件（支持断点续传）"""
        # 检查文件是否已存在（断点续传）
        if local_path.exists():
            self.visited_urls.add(url)
            return True
        
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # 确保目录存在
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"下载失败: {url}")
            print(f"错误: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def extract_links(self, html_content, base_url):
        """从HTML中提取所有链接"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        # 提取所有链接
        for tag in soup.find_all(['a', 'link', 'script', 'img', 'source']):
            url = None
            attr = None
            
            if tag.name == 'a':
                url = tag.get('href')
                attr = 'href'
            elif tag.name == 'link':
                url = tag.get('href')
                attr = 'href'
            elif tag.name == 'script':
                url = tag.get('src')
                attr = 'src'
            elif tag.name == 'img':
                url = tag.get('src')
                attr = 'src'
            elif tag.name == 'source':
                url = tag.get('src')
                attr = 'src'
            
            if url:
                # 转换为绝对URL
                absolute_url = urljoin(base_url, url)
                links.append((absolute_url, attr, tag))
        
        return links
    
    def process_html(self, html_content, page_url):
        """处理HTML内容，更新链接为本地路径"""
        soup = BeautifulSoup(html_content, 'html.parser')
        page_local_path = self.get_local_path(page_url)
        page_dir = page_local_path.parent
        
        # 处理所有链接
        for tag in soup.find_all(['a', 'link', 'script', 'img', 'source']):
            url = None
            attr = None
            is_resource = False  # 是否是资源文件（CSS、JS、图片）
            
            if tag.name == 'a':
                url = tag.get('href')
                attr = 'href'
            elif tag.name == 'link':
                url = tag.get('href')
                attr = 'href'
                is_resource = True
            elif tag.name == 'script':
                url = tag.get('src')
                attr = 'src'
                is_resource = True
            elif tag.name == 'img':
                url = tag.get('src')
                attr = 'src'
                is_resource = True
            elif tag.name == 'source':
                url = tag.get('src')
                attr = 'src'
                is_resource = True
            
            if url:
                absolute_url = urljoin(page_url, url)
                parsed = urlparse(absolute_url)
                
                # 只处理同域名的链接
                if parsed.netloc == self.base_domain or not parsed.netloc:
                    if is_resource:
                        # 资源文件保存在assets目录
                        resource_filename = os.path.basename(urlparse(absolute_url).path)
                        if not resource_filename:
                            resource_filename = url.split('/')[-1]
                        # 确保有扩展名
                        if '.' not in resource_filename:
                            if tag.name == 'link':
                                resource_filename += '.css'
                            elif tag.name == 'script':
                                resource_filename += '.js'
                        relative_path = os.path.relpath(self.assets_dir / resource_filename, page_dir)
                    else:
                        # 页面文件使用正常路径
                        target_local_path = self.get_local_path(absolute_url)
                        relative_path = os.path.relpath(target_local_path, page_dir)
                    
                    # Windows路径转换为正斜杠
                    relative_path = relative_path.replace('\\', '/')
                    
                    # 更新标签属性
                    tag[attr] = relative_path
        
        return str(soup)
    
    def download_page(self, url, depth, parent_url):
        """下载单个页面"""
        # 检查文件是否已存在（断点续传）
        local_path = self.get_local_path(url)
        if local_path.exists() and url not in self.visited_urls:
            # 文件已存在，标记为已访问，但需要提取链接继续下载
            self.visited_urls.add(url)
            print(f"[已存在] {url}")
            # 读取HTML内容以提取链接
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # 提取链接并添加到队列
                if depth < self.max_depth:
                    links = self.extract_links(html_content, url)
                    for link_url, attr, tag in links:
                        if self.should_download(link_url):
                            self.url_queue.append((link_url, depth + 1, url))
            except:
                pass
            return
        
        if not self.should_download(url):
            self.stats['skipped'] += 1
            if depth <= 2:  # 只在前几层显示跳过的URL，避免输出过多
                parsed = urlparse(url)
                url_path_normalized = (parsed.path or '/').rstrip('/') or '/'
                base_path_normalized = self.base_path.rstrip('/')
                if self.base_path != '/' and not url_path_normalized.startswith(base_path_normalized):
                    print(f"[跳过] {url} (不在基础路径 {self.base_path} 下)")
            return
        
        self.visited_urls.add(url)
        
        print(f"[深度 {depth}] {url}")
        
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            
            local_path = self.get_local_path(url)
            
            if 'text/html' in content_type:
                # HTML页面
                html_content = response.text
                
                # 处理HTML，更新链接
                processed_html = self.process_html(html_content, url)
                
                # 保存HTML
                local_path.parent.mkdir(parents=True, exist_ok=True)
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(processed_html)
                
                self.stats['pages'] += 1
                
                # 提取链接并添加到队列
                if depth < self.max_depth:
                    links = self.extract_links(html_content, url)
                    for link_url, attr, tag in links:
                        if self.should_download(link_url):
                            self.url_queue.append((link_url, depth + 1, url))
                
                # 下载资源文件（CSS、JS、图片等）
                self.download_assets(html_content, url)
                
            else:
                # 其他资源文件
                if self.download_file(url, local_path):
                    self.stats['assets'] += 1
            
            # 延迟
            time.sleep(self.delay)
            
        except Exception as e:
            print(f"处理失败: {url}")
            print(f"错误: {str(e)}")
            self.stats['errors'] += 1
    
    def download_assets(self, html_content, page_url):
        """下载页面中的资源文件（CSS、JS、图片等）"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 下载CSS文件
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                css_url = urljoin(page_url, href)
                # 资源文件使用 is_asset=True，不受路径限制
                if self.should_download(css_url, is_asset=True):
                    css_path = self.assets_dir / os.path.basename(urlparse(css_url).path)
                    if css_path.suffix == '':
                        css_path = css_path.with_suffix('.css')
                    if self.download_file(css_url, css_path):
                        self.stats['assets'] += 1
        
        # 下载JS文件
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                js_url = urljoin(page_url, src)
                # 资源文件使用 is_asset=True，不受路径限制
                if self.should_download(js_url, is_asset=True):
                    js_path = self.assets_dir / os.path.basename(urlparse(js_url).path)
                    if js_path.suffix == '':
                        js_path = js_path.with_suffix('.js')
                    if self.download_file(js_url, js_path):
                        self.stats['assets'] += 1
        
        # 下载图片
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                img_url = urljoin(page_url, src)
                # 资源文件使用 is_asset=True，不受路径限制
                if self.should_download(img_url, is_asset=True):
                    img_path = self.assets_dir / os.path.basename(urlparse(img_url).path)
                    if self.download_file(img_url, img_path):
                        self.stats['assets'] += 1
    
    def run(self):
        """开始下载"""
        print(f" 开始下载文档")
        print(f"   起始URL: {self.base_url}")
        print(f"   输出目录: {self.output_dir}")
        print(f"   最大深度: {self.max_depth}")
        print(f"   请求延迟: {self.delay}秒")
        print("-" * 60)
        
        start_time = time.time()
        
        while self.url_queue:
            url, depth, parent_url = self.url_queue.popleft()
            self.download_page(url, depth, parent_url)
        
        elapsed_time = time.time() - start_time
        
        print("-" * 60)
        print(" 下载完成！")
        print(f"   页面数: {self.stats['pages']}")
        print(f"   资源数: {self.stats['assets']}")
        print(f"   错误数: {self.stats['errors']}")
        print(f"   跳过数: {self.stats['skipped']}")
        print(f"   总耗时: {elapsed_time:.2f}秒")
        
        # 保存下载记录
        record_file = self.output_dir / 'download_record.json'
        record = {
            'base_url': self.base_url,
            'download_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': self.stats,
            'visited_urls': list(self.visited_urls)
        }
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description='网页文档下载工具 - 支持下载整个文档网站',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载文档
  python doc_downloader.py https://example.com/docs -o docs
  
  # 下载指定深度的文档
  python doc_downloader.py https://example.com/docs -o output -d 5
  
  # 设置请求延迟（避免服务器压力）
  python doc_downloader.py https://example.com/docs -o output --delay 1.0
        """
    )
    
    parser.add_argument('url', help='要下载的文档网站URL')
    parser.add_argument('-o', '--output', default='downloaded_docs',
                       help='输出目录（默认: downloaded_docs）')
    parser.add_argument('-d', '--depth', type=int, default=10,
                       help='最大爬取深度（默认: 10）')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='请求之间的延迟秒数（默认: 0.5）')
    
    args = parser.parse_args()
    
    downloader = DocDownloader(
        base_url=args.url,
        output_dir=args.output,
        max_depth=args.depth,
        delay=args.delay
    )
    
    downloader.run()


if __name__ == '__main__':
    main()


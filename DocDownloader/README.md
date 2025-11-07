# 网页文档下载工具

一个功能强大的网页文档下载工具，支持下载整个文档网站，包括HTML页面、CSS样式表、JavaScript脚本、图片等所有资源。特别优化了对Unity文档网站的下载支持。

## 功能特点

- ✅ **完整下载** - 自动下载文档网站的所有页面和资源
- ✅ **智能链接处理** - 自动将网页中的链接转换为本地相对路径
- ✅ **资源管理** - 自动下载并整理CSS、JS、图片等资源文件（不受路径限制）
- ✅ **路径过滤** - 只下载指定路径下的页面，避免下载其他版本或无关内容
- ✅ **断点续传** - 支持中断后继续下载，自动跳过已下载的文件
- ✅ **深度控制** - 可设置最大爬取深度，避免无限下载
- ✅ **请求延迟** - 支持设置请求间隔，避免对服务器造成压力
- ✅ **错误处理** - 完善的错误处理和统计信息
- ✅ **下载记录** - 自动保存下载记录，方便追踪和恢复
- ✅ **跨平台** - 支持Windows、Linux、macOS

## 安装要求

- Python 3.7+
- 需要安装以下依赖包

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install requests beautifulsoup4 lxml
```

## 使用方法

### 基本用法

```bash
# 下载Unity手册
python doc_downloader.py https://example.com/docs/ -o docs
```

### 命令行参数

```
python doc_downloader.py [URL] [选项]

必需参数:
  URL                     要下载的文档网站URL

可选参数:
  -o, --output DIR        输出目录（默认: downloaded_docs）
  -d, --depth N           最大爬取深度（默认: 10）
  --delay SECONDS         请求之间的延迟秒数（默认: 0.5）
  -h, --help              显示帮助信息
```

### 使用示例

#### 1. 下载文档

```bash
python doc_downloader.py https://example.com/docs/ -o docs
```

#### 2. 限制下载深度

```bash
# 只下载3层深度的页面
python doc_downloader.py https://example.com/docs -o output -d 3
```

#### 3. 设置请求延迟

```bash
# 每个请求之间延迟1秒（避免服务器压力）
python doc_downloader.py https://example.com/docs -o output --delay 1.0
```

#### 4. 下载其他文档网站

```bash
# 下载任何文档网站
python doc_downloader.py https://docs.python.org/3/ -o python_docs
```

## 输出结构

下载完成后，文件会按照以下结构组织：

```
output_dir/
├── index.html              # 主页
├── Documentation/          # 文档目录
│   └── Manual/
│       └── index.html
├── assets/                 # 资源文件目录
│   ├── style.css
│   ├── script.js
│   └── images/
│       └── logo.png
└── download_record.json    # 下载记录
```

## 工作原理

1. **URL队列管理** - 使用队列管理待下载的URL，按深度逐层下载
2. **链接提取** - 从HTML页面中提取所有链接（a、link、script、img等标签）
3. **链接转换** - 将绝对URL转换为本地相对路径
4. **资源下载** - 自动下载CSS、JS、图片等资源文件（资源文件不受路径限制）
5. **路径过滤** - 只下载指定路径下的页面，避免下载其他版本的内容
6. **断点续传** - 检查文件是否已存在，加载之前的下载记录，继续未完成的下载
7. **去重处理** - 避免重复下载相同的URL
8. **错误处理** - 记录下载失败的URL，继续处理其他页面

## 许可证

MIT License



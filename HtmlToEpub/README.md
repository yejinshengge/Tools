# HTML转EPUB电子书工具

一个功能强大的工具，可以将一组HTML文档转换为EPUB格式的电子书。支持自动处理图片、样式、链接等，生成标准的EPUB电子书文件。

## 功能特点

- ✅ **批量转换** - 自动扫描目录中的所有HTML文件并转换为EPUB
- ✅ **智能处理** - 自动提取HTML主要内容，移除脚本和样式标签
- ✅ **图片支持** - 自动处理HTML中的图片，嵌入到EPUB中
- ✅ **样式优化** - 提供默认的阅读样式，支持自定义CSS
- ✅ **章节管理** - 每个HTML文件自动成为一个章节
- ✅ **智能目录检测** - 自动从HTML文件中检测目录结构，按目录顺序排列章节
- ✅ **配置文件支持** - 支持通过JSON配置文件指定章节顺序
- ✅ **元数据设置** - 支持设置标题、作者、语言等元数据
- ✅ **递归扫描** - 支持扫描子目录中的HTML文件
- ✅ **错误处理** - 完善的错误处理，跳过无法处理的文件
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
pip install ebooklib beautifulsoup4 lxml Pillow
```

## 使用方法

### 基本用法

```bash
# 将目录中的HTML文件转换为EPUB
python html_to_epub.py input_dir -o output.epub
```

### 命令行参数

```
python html_to_epub.py [输入目录] [选项]

必需参数:
  input_dir               HTML文件所在目录

必需选项:
  -o, --output FILE      输出的EPUB文件路径

可选参数:
  -t, --title TITLE      电子书标题（默认: 电子书）
  -a, --author AUTHOR    作者（默认: 未知作者）
  -l, --language CODE    语言代码（默认: zh-CN）
  -c, --config FILE      章节顺序配置文件（JSON格式）
  -h, --help             显示帮助信息
```

### 使用示例

#### 1. 基本转换

```bash
# 将docs目录中的HTML文件转换为book.epub
python html_to_epub.py docs -o book.epub
```

#### 2. 指定标题和作者

```bash
python html_to_epub.py docs -o book.epub -t "Unity文档" -a "Unity官方"
```

#### 3. 处理子目录

工具会自动递归扫描子目录中的所有HTML文件：

```bash
# 扫描docs目录及其所有子目录
python html_to_epub.py docs -o complete_docs.epub -t "完整文档集"
```

#### 4. 指定语言

```bash
# 英文文档
python html_to_epub.py docs -o book.epub -l "en-US"
```

#### 5. 使用配置文件指定章节顺序

如果HTML文档中有目录结构，工具会自动检测并使用。也可以手动创建配置文件：

```bash
# 使用配置文件
python html_to_epub.py docs -o book.epub -c order.json
```

配置文件格式（`order.json`）：

```json
{
  "order": [
    "intro.html",
    "chapter1.html",
    "chapter2.html",
    {
      "path": "chapter3.html",
      "title": "第三章：高级主题"
    },
    "conclusion.html"
  ]
}
```

配置文件支持两种格式：
- **简单格式**：直接列出文件路径（相对于输入目录）
- **详细格式**：使用对象，可以指定路径和自定义标题

## 功能说明

### HTML文件处理

- 工具会自动扫描指定目录中的所有 `.html` 和 `.htm` 文件
- 每个HTML文件会成为一个独立的章节
- **智能排序**：工具会按以下优先级确定章节顺序：
  1. 如果提供了配置文件（`-c` 参数），使用配置文件中的顺序
  2. 如果HTML文档中包含目录结构（如 `<nav>`, `<div class="toc">` 等），自动检测并使用目录顺序
  3. 否则，按文件名排序

### 内容清理

工具会自动：
- 移除 `<script>` 和 `<style>` 标签
- 移除注释
- 处理图片链接，将本地图片嵌入到EPUB中
- 处理外部链接，避免EPUB中的链接问题

### 图片处理

- 支持 JPG、PNG、GIF、WebP、SVG 格式
- 自动将图片嵌入到EPUB中
- 自动调整图片大小以适应阅读器
- 如果图片不存在或无法处理，会自动移除图片标签

### 样式支持

- 提供默认的中文阅读样式
- 支持自定义CSS（通过HTML文件中的 `<style>` 标签）
- 优化了代码块、表格、引用等元素的显示

## 输出格式

生成的EPUB文件符合EPUB 3.0标准，可以在以下设备/软件上阅读：
- Apple Books (iOS/macOS)
- Adobe Digital Editions
- Calibre
- Kindle (需要转换)
- 其他支持EPUB的阅读器

## 注意事项

1. **文件编码**: HTML文件必须是UTF-8编码，否则可能出现乱码
2. **图片路径**: 图片路径可以是相对路径或绝对路径，工具会自动处理
3. **文件大小**: 如果HTML文件很多或图片很大，生成的EPUB文件可能会比较大
4. **链接跳转**: EPUB中的本地HTML文件链接可能无法正常工作，这是EPUB格式的限制
5. **样式兼容**: 某些复杂的CSS样式可能在EPUB阅读器中显示效果不同
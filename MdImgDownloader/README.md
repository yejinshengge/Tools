# Markdown 图片下载工具

这是一个用于自动下载 Markdown 文件中的在线图片并替换为本地链接的 Python 工具。

## 功能特点

- 自动扫描指定目录下的所有 Markdown 文件
- 自动下载 Markdown 文件中的在线图片
- 将图片保存到与 Markdown 文件同目录下的 `images` 文件夹中
- 自动替换 Markdown 文件中的图片链接为本地路径
- 支持常见图片格式（jpg、png、gif）
- 保留原始图片文件名
- 自动处理无扩展名的图片 URL

## 使用要求

- Python 3.x
- requests 库

## 安装依赖

```bash
pip install requests
```

## 使用方法

1. 将 `download_md_images.py` 文件放置在包含 Markdown 文件的目录中。

2. 运行脚本：
   ```bash
   python download_md_images.py
   ```

3. 脚本会自动：
   - 扫描当前目录及其子目录中的所有 `.md` 文件
   - 为每个 Markdown 文件创建对应的 `images` 文件夹
   - 下载文件中的在线图片到 `images` 文件夹
   - 更新 Markdown 文件中的图片链接为本地路径

## 注意事项

- 脚本只会处理在线图片链接（以 `http://` 或 `https://` 开头的 URL）
- 已经是本地路径的图片链接（以 `./`、`../` 或 `/` 开头）会被跳过
- 下载失败的图片会在控制台输出错误信息
- 图片将被保存在与 Markdown 文件同级的 `images` 目录下

## 示例

原始 Markdown 文件内容：
```markdown
![示例图片](https://example.com/image.jpg)
```

处理后的 Markdown 文件内容：
```markdown
![示例图片](./images/image.jpg)
```

## 错误处理

如果在下载过程中遇到问题：
- 检查网络连接是否正常
- 确认图片 URL 是否可访问
- 查看控制台输出的错误信息

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。 
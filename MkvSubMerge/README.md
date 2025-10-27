# MKV 字幕批量合并工具

## 项目简介

`mkv_sub_merge.sh` 是一个用于批量将字幕文件合并到视频文件中的 Shell 脚本（使用 POSIX sh）。该脚本设计用于在 `jlesage/mkvtoolnix` Docker 容器中运行，利用 MKVToolNix 工具集中的 `mkvmerge` 命令实现自动化批量处理。

## 功能特性

- ✅ 批量处理多个视频文件
- ✅ 支持多种视频格式（mp4, mkv, avi, mov, wmv, flv, webm, m4v, mpg, mpeg）
- ✅ 支持多种字幕格式（srt, ass, ssa, vtt）
- ✅ 自动识别多语言字幕（基于文件名）
- ✅ 智能语言代码提取和验证
- ✅ 详细的处理日志输出
- ✅ 错误处理和状态反馈

## 先决条件

### 1. Docker 环境
确保已安装 Docker 和 Docker Compose。

### 2. jlesage/mkvtoolnix 容器

该脚本需要在 `jlesage/mkvtoolnix` 容器中执行。这个容器提供了完整的 MKVToolNix 工具集。

## 安装和配置

### 1. 启动 Docker 容器

使用以下命令启动 `jlesage/mkvtoolnix` 容器：

```bash
docker run -d \
  --name=mkvtoolnix \
  -p 5800:5800 \
  -v /path/to/videos:/storage/videos:rw \
  -v /path/to/subs:/storage/subs:rw \
  -v /path/to/output:/storage/output:rw \
  -v /path/to/script:/scripts:rw \
  jlesage/mkvtoolnix
```

#### 参数说明：
- `-p 5800:5800`：映射 Web UI 端口（可选，用于图形界面操作）
- `-v /path/to/videos:/storage/videos:rw`：视频文件目录挂载
- `-v /path/to/subs:/storage/subs:rw`：字幕文件目录挂载
- `-v /path/to/output:/storage/output:rw`：输出文件目录挂载
- `-v /path/to/script:/scripts:rw`：脚本目录挂载

### 2. Docker Compose 配置（推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  mkvtoolnix:
    image: jlesage/mkvtoolnix
    container_name: mkvtoolnix
    ports:
      - "5800:5800"
    volumes:
      - ./videos:/storage/videos:rw
      - ./subs:/storage/subs:rw
      - ./output:/storage/output:rw
      - ./mkv_sub_merge.sh:/scripts/mkv_sub_merge.sh:ro
    environment:
      - USER_ID=1000
      - GROUP_ID=1000
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

启动容器：
```bash
docker-compose up -d
```

### 3. 复制脚本到容器

如果没有使用卷挂载脚本，可以手动复制：

```bash
docker cp mkv_sub_merge.sh mkvtoolnix:/scripts/
docker exec mkvtoolnix chmod +x /scripts/mkv_sub_merge.sh
```

## 使用方法

### 1. 准备文件

将视频文件和字幕文件分别放置在对应的目录中：

```
/path/to/videos/
  ├── movie1.mp4
  ├── movie2.mkv
  └── series_s01e01.mkv

/path/to/subs/
  ├── movie1.zh.srt        # 中文字幕
  ├── movie1.en.srt        # 英文字幕
  ├── movie2.srt           # 未标记语言（将使用 und）
  └── series_s01e01.zh.ass # 中文 ASS 字幕
```

### 2. 文件命名规范

字幕文件命名格式：`<视频文件名>.<语言代码>.<字幕扩展名>`

#### 语言代码示例：
- `zh` 或 `chi` - 中文
- `en` 或 `eng` - 英文
- `ja` 或 `jpn` - 日文
- `ko` 或 `kor` - 韩文
- `und` - 未定义（脚本自动使用）

#### 示例：
- ✅ `movie.zh.srt` - 正确：包含语言代码
- ✅ `movie.en.ass` - 正确：包含语言代码
- ⚠️ `movie.srt` - 可用：将使用默认语言代码 `und`
- ✅ `movie.chinese.srt` - 可用：但 `chinese` 不是标准代码，将使用 `und`

### 3. 执行脚本

进入容器并运行脚本：

```bash
# 进入容器
docker exec -it mkvtoolnix /bin/sh

# 执行脚本
/scripts/mkv_sub_merge.sh
```

或者直接从宿主机执行：

```bash
docker exec mkvtoolnix /scripts/mkv_sub_merge.sh
```

### 4. 查看输出

脚本会在 `/storage/output` 目录（对应宿主机的挂载目录）生成合并后的 MKV 文件。

## 脚本输出示例

```
正在处理: movie1.mp4
  找到字幕: movie1.zh.srt (语言: zh)
  找到字幕: movie1.en.srt (语言: en)
✓ 成功: movie1.mkv

正在处理: movie2.mkv
  找到字幕: movie2.srt (语言: und)
✓ 成功: movie2.mkv

⊘ 跳过: movie3 (未找到匹配的字幕文件)

批量处理完成！
```

## 脚本配置

如需修改脚本的目录配置，编辑以下变量：

```bash
VIDEO_DIR="/storage/videos"    # 视频文件目录
SUB_DIR="/storage/subs"        # 字幕文件目录
OUTPUT_DIR="/storage/output"   # 输出目录
```

支持的文件格式：

```bash
# 视频格式
VIDEO_EXTENSIONS="mp4|mkv|avi|mov|wmv|flv|webm|m4v|mpg|mpeg"

# 字幕格式
SUBTITLE_EXTENSIONS="srt|ass|ssa|vtt"
```

## 故障排除

### 问题 1：权限错误

**错误信息**：`Permission denied`

**解决方案**：
```bash
# 在容器内设置脚本为可执行
docker exec mkvtoolnix chmod +x /scripts/mkv_sub_merge.sh

# 或者在宿主机上设置
chmod +x mkv_sub_merge.sh
```

### 问题 2：找不到视频或字幕文件

**解决方案**：
- 检查 Docker 卷挂载是否正确
- 确认文件确实在指定目录中
- 检查文件权限（容器内的用户需要读取权限）

```bash
# 进入容器检查文件
docker exec -it mkvtoolnix ls -la /storage/videos
docker exec -it mkvtoolnix ls -la /storage/subs
```

### 问题 3：输出文件无法写入

**解决方案**：
```bash
# 在容器内创建输出目录并设置权限
docker exec mkvtoolnix mkdir -p /storage/output
docker exec mkvtoolnix chmod 777 /storage/output
```

### 问题 4：mkvmerge 命令失败

**可能原因**：
- 视频文件损坏
- 字幕文件编码问题
- 磁盘空间不足

**解决方案**：
```bash
# 检查磁盘空间
docker exec mkvtoolnix df -h

# 手动测试 mkvmerge
docker exec mkvtoolnix mkvmerge --version

# 手动测试单个文件合并
docker exec mkvtoolnix mkvmerge -o /storage/output/test.mkv \
  /storage/videos/movie.mp4 \
  --language 0:zh /storage/subs/movie.zh.srt
```

### 问题 5：字幕语言代码识别错误

**解决方案**：
- 确保字幕文件名格式正确：`<basename>.<lang>.<ext>`
- 使用标准的 ISO 639-2 语言代码（2-3个字母）
- 如果无法识别，脚本会自动使用 `und`（未定义）

## 高级用法

### 自动化执行

使用 cron 定时执行脚本：

```bash
# 进入容器
docker exec -it mkvtoolnix /bin/sh

# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨2点执行）
0 2 * * * /scripts/mkv_sub_merge.sh >> /storage/output/merge.log 2>&1
```

### 批量处理后清理

在脚本末尾添加清理逻辑（可选）：

```bash
# 可选：处理成功后移动原文件到备份目录
# BACKUP_DIR="/storage/backup"
# mkdir -p "$BACKUP_DIR"
# mv "$video_file" "$BACKUP_DIR/"
```

## 注意事项

1. ⚠️ **备份重要文件**：在批量处理前，请备份原始视频和字幕文件
2. ⚠️ **磁盘空间**：确保输出目录有足够的磁盘空间（至少是输入文件的总大小）
3. ⚠️ **文件覆盖**：如果输出目录中已存在同名文件，会被覆盖
4. ⚠️ **字幕编码**：建议使用 UTF-8 编码的字幕文件
5. ✅ **MKV 格式**：所有输出文件都是 MKV 格式，即使输入是其他格式

## 技术细节

### Shell 兼容性

- 脚本使用 POSIX sh（`#!/bin/sh`）而不是 Bash
- 具有更好的跨平台兼容性
- 可在大多数 Unix-like 系统上运行
- 避免使用 Bash 特有的语法特性

### 特殊文件名处理

- 脚本正确处理包含空格和特殊字符的文件名
- 使用引号和 `eval` 确保路径参数正确传递给 `mkvmerge`
- 建议避免在文件名中使用特殊字符以获得最佳兼容性

### 语言代码提取逻辑

脚本使用以下逻辑提取语言代码：

1. 统计文件名中的点号数量
2. 如果有至少2个点（如 `movie.zh.srt`），提取倒数第二个部分
3. 验证提取的代码是否为2-3个字母
4. 如果验证失败，使用默认值 `und`

### 支持的语言代码格式

- ISO 639-1：2字母代码（如 `zh`, `en`, `ja`）
- ISO 639-2：3字母代码（如 `chi`, `eng`, `jpn`）

## 许可证

本项目采用 MIT 许可证。

## 参考资料

- [MKVToolNix 官方文档](https://mkvtoolnix.download/doc/mkvmerge.html)
- [jlesage/mkvtoolnix Docker 镜像](https://github.com/jlesage/docker-mkvtoolnix)
- [ISO 639 语言代码列表](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)


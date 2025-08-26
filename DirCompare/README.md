# 目录文件名对比工具

一个用于对比不同目录下文件名差异的Python工具，支持多种配置选项和输出格式。

## 功能特性

- ✅ 支持对比两个或多个目录
- ✅ 可配置是否递归扫描子目录
- ✅ 可选择忽略文件扩展名
- ✅ 支持按分割字符对比文件名的特定部分
- ✅ 生成详细的对比报告
- ✅ 支持文本和JSON两种输出格式
- ✅ 支持配置文件和命令行参数两种配置方式
- ✅ 显示共同文件、独有文件和缺失文件
- ✅ 完善的错误处理和用户提示

## 安装要求

- Python 3.7+
- 无需额外依赖，仅使用Python标准库

## 使用方法

### 1. 命令行使用

#### 基本对比两个目录
```bash
python dir_compare.py -p ./dir1 ./dir2
```

#### 对比多个目录（非递归，忽略扩展名）
```bash
python dir_compare.py -p ./dir1 ./dir2 ./dir3 --no-recursive --ignore-ext
```

#### 输出为JSON格式
```bash
python dir_compare.py -p ./dir1 ./dir2 --output json
```

#### 保存结果到文件
```bash
python dir_compare.py -p ./dir1 ./dir2 --save-to result.txt
```

#### 使用分割字符对比特定部分
```bash
# 对比文件名按下划线分割后的第2部分（下标1）
python dir_compare.py -p ./dir1 ./dir2 --split-char "_" --split-index 1

# 对比文件名按点号分割后的最后一部分（负数下标）
python dir_compare.py -p ./dir1 ./dir2 --split-char "." --split-index -1

# 对比文件名按横线分割后的第1部分（下标0）
python dir_compare.py -p ./dir1 ./dir2 --split-char "-" --split-index 0
```

### 2. 使用配置文件

#### 创建示例配置文件
```bash
# 在脚本目录下生成配置文件
python dir_compare.py --create-config

# 在指定位置生成配置文件
python dir_compare.py --create-config ./my_config.json
```

这会生成一个 `compare_config.json` 文件：
```json
{
  "paths": ["./dir1", "./dir2"],
  "recursive": true,
  "ignore_extension": false,
  "output_format": "text",
  "split_char": null,
  "split_index": null
}
```

#### 使用配置文件运行
```bash
python dir_compare.py -c compare_config.json
```

### 3. 命令行参数说明

| 参数 | 说明 |
|------|------|
| `-p, --paths` | 要对比的目录路径列表（至少2个） |
| `-c, --config` | 配置文件路径 |
| `--no-recursive` | 不递归扫描子目录 |
| `--ignore-ext` | 忽略文件扩展名 |
| `--split-char` | 分割字符，如 "_", "-", "." |
| `--split-index` | 分割后要对比的下标位置（支持负数） |
| `--output` | 输出格式：text（默认）或 json |
| `--save-to` | 保存结果到指定文件 |
| `--create-config` | 创建示例配置文件 |

## 输出说明

### 文本格式输出

工具会生成详细的对比报告，包含：

1. **对比配置**：显示使用的配置选项
2. **摘要信息**：总体统计数据
3. **目录文件统计**：每个目录的文件数量
4. **共同文件**：所有目录都包含的文件
5. **各目录独有文件**：每个目录独有的文件
6. **各目录缺失文件**：其他目录有但当前目录没有的文件

### JSON格式输出

包含相同信息的结构化JSON数据，适合程序化处理。

## 使用场景

1. **代码同步检查**：对比不同分支或版本的代码目录
2. **备份完整性验证**：检查备份目录和原目录的文件差异
3. **部署验证**：确认部署后的文件和预期一致
4. **文件整理**：找出重复或遗漏的文件
5. **项目对比**：比较相似项目的文件结构差异
6. **版本文件对比**：只对比文件的核心名称，忽略版本号部分
7. **带前缀/后缀的文件对比**：专注于文件名的特定部分

## 分割功能使用示例

假设有以下文件：
```
目录1: user_profile_v1.txt, admin_settings_v2.txt, log_data_v1.txt
目录2: user_profile_v3.txt, admin_settings_v2.txt, debug_info_v1.txt
```

使用分割功能对比核心名称：
```bash
python dir_compare.py -p ./dir1 ./dir2 --split-char "_" --split-index 0
```

结果会对比：`user`, `admin`, `log` vs `user`, `admin`, `debug`，忽略版本号部分。

## 配置选项详解

### recursive（递归扫描）
- `true`：扫描目录及其所有子目录
- `false`：仅扫描指定目录的直接文件

### ignore_extension（忽略扩展名）
- `true`：比较时忽略文件扩展名（如 `file.txt` 和 `file.py` 视为相同）
- `false`：完整比较文件名包括扩展名

### output_format（输出格式）
- `text`：人类可读的文本格式
- `json`：结构化的JSON格式

### split_char 和 split_index（分割对比）
- `split_char`：指定分割字符，如 `_`、`-`、`.` 等
- `split_index`：指定要对比的部分下标（从0开始，支持负数）
- 两个参数必须同时设置才能启用分割对比功能
- 当文件名按分割字符分割后，只对比指定下标位置的字符串

## 示例输出

```
============================================================
目录文件名对比报告
============================================================

对比配置:
  递归扫描: 是
  忽略扩展名: 否

摘要信息:
  对比目录数: 2
  总文件数: 8
  共同文件数: 3

目录文件统计:
  ./dir1: 5 个文件
  ./dir2: 6 个文件

所有目录都包含的文件 (3 个):
  ✓ common1.txt
  ✓ common2.py
  ✓ subfolder/shared.md

各目录独有文件:
  ./dir1 独有 (2 个):
    + unique1.txt
    + only_in_dir1.py
  ./dir2 独有 (3 个):
    + unique2.txt
    + only_in_dir2.js
    + extra.md

各目录缺失文件:
  ./dir1 缺失 (3 个):
    - unique2.txt
    - only_in_dir2.js
    - extra.md
  ./dir2 缺失 (2 个):
    - unique1.txt
    - only_in_dir1.py
```

## 错误处理

工具具有完善的错误处理机制：

- 目录不存在时显示警告并跳过
- 权限不足时显示错误信息
- 配置文件格式错误时提供详细错误说明
- 参数不足时显示帮助信息

## 注意事项

1. 确保对所有目录都有读取权限
2. 大型目录结构可能需要较长处理时间
3. 递归模式下会包含子目录中的所有文件
4. 忽略扩展名选项会影响文件匹配逻辑
5. 分割字符和分割下标必须同时指定才能启用分割功能
6. 如果分割后的下标超出范围，会显示警告并使用原文件名
7. 支持负数下标（从末尾开始计算）

## 扩展开发

如需自定义功能，可以：
1. 修改 `CompareConfig` 类添加新的配置选项
2. 扩展 `DirCompare` 类添加新的对比逻辑
3. 自定义输出格式化函数
4. 添加文件过滤规则

## 许可证

MIT License 
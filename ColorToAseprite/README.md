# 🎨 颜色调色板转换器 (Color to Aseprite)

将多种格式的颜色数据转换为 GIMP Palette (.gpl) 格式，可用于 Aseprite、GIMP、Photoshop 等图像编辑软件。

## ✨ 功能特性

- 📂 支持多种输入格式：JavaScript 数组、Excel 文件
- 🔄 将十六进制颜色值 (HEX) 转换为 RGB 格式
- 💾 生成标准的 GIMP Palette (.gpl) 文件
- 🚀 支持命令行参数，灵活指定输入输出文件
- 📝 自动生成调色板名称
- ✅ 完善的错误处理和提示信息
- 📊 Excel 格式支持，方便批量管理颜色

## 📁 文件说明

- `convert_to_gpl.py` - JavaScript 格式转换脚本
- `convert_excel_to_gpl.py` - Excel 格式转换脚本（⭐ 新增）
- `example.js` - JavaScript 格式示例文件
- `requirements.txt` - Python 依赖库列表
- `README.md` - 说明文档（本文件）

## 🚀 使用方法

### 方式 A：转换 JavaScript 格式

#### 方法 1：使用默认文件名

```bash
python3 convert_to_gpl.py
```

默认读取 `colors.js`，生成 `palette.gpl`

#### 方法 2：指定输入文件

```bash
python3 convert_to_gpl.py your_colors.js
```

自动生成同名的 `.gpl` 文件（例如：`your_colors.gpl`）

#### 方法 3：完全自定义

```bash
python3 convert_to_gpl.py <输入文件> <输出文件>
```

示例：
```bash
python3 convert_to_gpl.py my_palette.js custom_output.gpl
```

### 方式 B：转换 Excel 格式

#### 安装依赖（首次使用）

```bash
pip install openpyxl
```

#### 转换 Excel 文件

```bash
# 使用默认文件名
python3 convert_excel_to_gpl.py

# 指定输入文件（自动命名输出）
python3 convert_excel_to_gpl.py colors.xlsx

# 完全自定义
python3 convert_excel_to_gpl.py colors.xlsx output.gpl
```

## 📝 输入格式

### 格式 1：JavaScript 数组

输入文件应为 JavaScript 数组格式，包含颜色对象：

```javascript
[
    { name: 'ColorName1', color: 'RRGGBB' },
    { name: 'ColorName2', color: 'RRGGBB' },
    // 支持注释
    { name: 'Red', color: 'ff0000' },
    { name: 'Green', color: '00ff00' },
    { name: 'Blue', color: '0000ff' },
]
```

**格式要求：**
- 每个颜色对象包含 `name` 和 `color` 两个字段
- `name`: 颜色名称（字符串）
- `color`: 6 位十六进制颜色值（不需要 # 前缀）
- 支持单引号或双引号
- 支持 JavaScript 注释

### 格式 2：Excel 表格

Excel 文件格式（.xlsx 或 .xls）：

| 列 A（颜色名称） | 列 B（颜色值） |
|-----------------|---------------|
| ZG1             | #DAABB3       |
| ZG2             | #E5C1CD       |
| Red             | #FF0000       |
| Green           | #00FF00       |
| Blue            | #0000FF       |

**格式要求：**
- 第一列：颜色名称（如 ZG1）
- 第二列：颜色值（6 位十六进制，可带或不带 # 前缀）
- 无需表头行，从第一行开始即可
- 空行会自动跳过
- 无效颜色值会显示警告并跳过

**示例文件：**
- 或创建 `.xlsx` / `.xls` 格式的 Excel 文件

## 📤 输出格式

输出为标准的 GIMP Palette (.gpl) 格式：

```
GIMP Palette
#
# Your Colors Palette
# Converted from your_colors.js
#
255   0   0	Red
  0 255   0	Green
  0   0 255	Blue
...
```

**格式说明：**
- 第一行固定为 `GIMP Palette`
- 注释行以 `#` 开头
- 每个颜色占一行：`R G B [Tab] ColorName`
- RGB 值为 0-255 的整数，右对齐 3 位

## 🎨 在软件中使用

### Aseprite

1. 运行转换脚本生成 `.gpl` 文件
2. 在 Aseprite 中：`Palette` → `Load Palette`
3. 选择生成的 `.gpl` 文件
4. 调色板即可使用 ✅

### GIMP

1. 将 `.gpl` 文件复制到 GIMP 调色板目录
   - Windows: `C:\Users\用户名\.gimp-2.10\palettes\`
   - macOS: `~/Library/Application Support/GIMP/2.10/palettes/`
   - Linux: `~/.config/GIMP/2.10/palettes/`
2. 重启 GIMP 或刷新调色板
3. 在调色板面板中选择使用

### Photoshop

1. 在 Photoshop 中打开：`Window` → `Swatches`
2. 点击面板菜单 → `Load Swatches`
3. 选择 `.gpl` 文件（部分版本支持）

## 📋 完整使用示例

### 示例 1：JavaScript 格式转换

```bash
# 1. 准备颜色数据文件 my_colors.js
# [
#     { name: 'Sky Blue', color: '87ceeb' },
#     { name: 'Sunset Orange', color: 'ff6347' },
# ]

# 2. 运行转换
python3 convert_to_gpl.py my_colors.js

# 3. 输出结果
# 📖 正在读取 my_colors.js...
# ✓ 找到 2 个颜色
# 💾 正在写入 my_colors.gpl...
# ✅ 转换成功！已生成 my_colors.gpl
#    调色板名称: My Colors Palette
#    颜色数量: 2

# 4. 在 Aseprite 中加载 my_colors.gpl
```

### 示例 2：Excel 格式转换

```bash
# 1. 准备 Excel 文件 palette.xlsx
#    列A     列B
#    ZG1     #DAABB3
#    ZG2     #E5C1CD
#    Red     #FF0000

# 2. 安装依赖（首次）
pip install openpyxl

# 3. 运行转换
python3 convert_excel_to_gpl.py palette.xlsx

# 4. 输出结果
# 📖 正在读取 palette.xlsx...
# ✓ 找到 3 个有效颜色
# 💾 正在写入 palette.gpl...
# ✅ 转换成功！已生成 palette.gpl
#    调色板名称: Palette Palette
#    颜色数量: 3

# 5. 在 Aseprite 中加载 palette.gpl
```

## 🛠️ 系统要求

### 基本要求
- **Python**: 3.6 或更高版本
- **操作系统**: Windows / macOS / Linux

### 依赖库
- **JavaScript 转换**: 无需额外依赖（仅使用 Python 标准库）
- **Excel 转换**: 需要安装 `openpyxl`

```bash
# 安装 Excel 转换所需的依赖
pip install openpyxl

# 或使用 requirements.txt
pip install -r requirements.txt
```

## ❓ 常见问题

### Q: 支持哪些颜色格式？
A: 目前仅支持 6 位十六进制格式（如 `ff0000` 或 `#ff0000`），不支持 3 位缩写或 rgba 格式。

### Q: 颜色名称有限制吗？
A: 建议使用英文、数字和下划线，避免特殊字符，以确保兼容性。

### Q: Excel 文件需要表头吗？
A: 不需要。直接从第一行开始输入数据即可。第一列为颜色名称，第二列为颜色值。

### Q: Excel 转换提示缺少依赖怎么办？
A: 运行 `pip install openpyxl` 安装所需的库。如果使用 pandas，则运行 `pip install pandas openpyxl`。

### Q: Excel 文件中有无效颜色会怎样？
A: 脚本会显示警告信息并跳过无效行，继续处理其他有效颜色。

### Q: 可以转换在线调色板吗？
A: 需要先将在线调色板数据整理成支持的格式（JS 数组或 Excel），然后使用本工具转换。

### Q: 输出文件乱码怎么办？
A: 脚本使用 UTF-8 编码，确保你的编辑器也使用 UTF-8 打开文件。

## 📜 许可证

本工具为开源软件，可自由使用和修改。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！


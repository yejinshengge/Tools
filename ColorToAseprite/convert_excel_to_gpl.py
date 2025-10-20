#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os


def hex_to_rgb(hex_color):
    """
    将十六进制颜色转换为 RGB 元组
    
    参数：
        hex_color (str): 十六进制颜色值，支持带或不带 # 前缀
                        例如: 'ffffff', '#ffffff', 'FF0000'
    
    返回：
        tuple: (r, g, b) 三个整数值，范围 0-255
    
    异常：
        ValueError: 如果颜色值不是有效的 6 位十六进制
    """
    # 移除可能的 # 符号并转为小写
    hex_color = str(hex_color).strip().lstrip('#').lower()
    
    # 确保是 6 位十六进制
    if len(hex_color) != 6:
        raise ValueError(f"无效的十六进制颜色值: {hex_color} (需要 6 位)")
    
    # 转换为 RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return r, g, b


def parse_excel_with_openpyxl(file_path):
    """
    使用 openpyxl 解析 Excel 文件，提取颜色信息
    
    参数：
        file_path (str): Excel 文件路径
    
    返回：
        list: 包含颜色字典的列表，每个字典包含 'name' 和 'color' 键
    
    异常：
        ImportError: openpyxl 未安装
        FileNotFoundError: 文件不存在
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError("请先安装 openpyxl: pip install openpyxl")
    
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active
    
    colors = []
    for row_idx, row in enumerate(sheet.iter_rows(min_row=1, values_only=True), start=1):
        # 跳过空行
        if not row or (not row[0] and not row[1]):
            continue
        
        # 获取颜色名称和颜色值
        color_name = row[0] if len(row) > 0 else None
        color_value = row[1] if len(row) > 1 else None
        
        # 验证数据
        if not color_name or not color_value:
            print(f"⚠️  警告：第 {row_idx} 行数据不完整，已跳过")
            continue
        
        # 清理和验证颜色值
        color_value = str(color_value).strip()
        
        try:
            # 验证颜色值格式
            hex_to_rgb(color_value)
            colors.append({
                'name': str(color_name).strip(),
                'color': color_value.lstrip('#')
            })
        except ValueError as e:
            print(f"⚠️  警告：第 {row_idx} 行颜色值无效 ({color_value})，已跳过")
            continue
    
    workbook.close()
    return colors


def parse_excel_with_pandas(file_path):
    """
    使用 pandas 解析 Excel 文件，提取颜色信息
    
    参数：
        file_path (str): Excel 文件路径
    
    返回：
        list: 包含颜色字典的列表，每个字典包含 'name' 和 'color' 键
    
    异常：
        ImportError: pandas 未安装
        FileNotFoundError: 文件不存在
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("请先安装 pandas: pip install pandas openpyxl")
    
    # 读取 Excel 文件，不使用表头
    df = pd.read_excel(file_path, header=None, engine='openpyxl')
    
    colors = []
    for idx, row in df.iterrows():
        # 跳过空行
        if pd.isna(row[0]) and pd.isna(row[1]):
            continue
        
        color_name = row[0]
        color_value = row[1]
        
        # 验证数据
        if pd.isna(color_name) or pd.isna(color_value):
            print(f"⚠️  警告：第 {idx + 1} 行数据不完整，已跳过")
            continue
        
        # 清理和验证颜色值
        color_value = str(color_value).strip()
        
        try:
            # 验证颜色值格式
            hex_to_rgb(color_value)
            colors.append({
                'name': str(color_name).strip(),
                'color': color_value.lstrip('#')
            })
        except ValueError as e:
            print(f"⚠️  警告：第 {idx + 1} 行颜色值无效 ({color_value})，已跳过")
            continue
    
    return colors


def parse_excel(file_path, use_pandas=False):
    """
    解析 Excel 文件，自动选择可用的库
    
    参数：
        file_path (str): Excel 文件路径
        use_pandas (bool): 是否优先使用 pandas
    
    返回：
        list: 包含颜色字典的列表
    """
    if use_pandas:
        try:
            return parse_excel_with_pandas(file_path)
        except ImportError:
            print("📌 pandas 未安装，尝试使用 openpyxl...")
            return parse_excel_with_openpyxl(file_path)
    else:
        try:
            return parse_excel_with_openpyxl(file_path)
        except ImportError:
            print("📌 openpyxl 未安装，尝试使用 pandas...")
            return parse_excel_with_pandas(file_path)


def write_gpl(colors, output_path, palette_name="Custom Palette"):
    """
    将颜色数据写入 GIMP Palette (.gpl) 格式文件
    
    参数：
        colors (list): 颜色列表，每个元素是包含 'name' 和 'color' 的字典
        output_path (str): 输出文件路径
        palette_name (str): 调色板名称，默认为 "Custom Palette"
    
    文件格式：
        GIMP Palette
        #
        # Palette Name
        #
        R G B    ColorName
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入 GIMP Palette 头部
        f.write("GIMP Palette\n")
        f.write("#\n")
        f.write(f"# {palette_name}\n")
        f.write(f"# Converted from {os.path.basename(output_path).replace('.gpl', '.xlsx')}\n")
        f.write("#\n")
        
        # 写入颜色数据，格式：R G B [Tab] ColorName
        for color_data in colors:
            r, g, b = hex_to_rgb(color_data['color'])
            # RGB 值右对齐 3 位，后跟制表符和颜色名称
            f.write(f"{r:3d} {g:3d} {b:3d}\t{color_data['name']}\n")


def main():
    """
    主函数：处理命令行参数并执行转换
    
    用法：
        python3 convert_excel_to_gpl.py                        # 使用默认文件名
        python3 convert_excel_to_gpl.py input.xlsx             # 指定输入文件
        python3 convert_excel_to_gpl.py input.xlsx output.gpl  # 指定输入输出文件
    """
    # 默认输入输出文件路径
    input_file = 'colors.xlsx'
    output_file = 'palette.gpl'
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        # 如果只提供输入文件，自动生成输出文件名
        if len(sys.argv) == 2:
            output_file = os.path.splitext(input_file)[0] + '.gpl'
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    try:
        # 解析输入文件
        print(f"📖 正在读取 {input_file}...")
        colors = parse_excel(input_file)
        
        if not colors:
            print("❌ 错误：未找到有效的颜色数据")
            print("   请检查 Excel 文件格式：")
            print("   - 第一列：颜色名称（如 ZG1）")
            print("   - 第二列：颜色值（如 #DAABB3）")
            sys.exit(1)
        
        print(f"✓ 找到 {len(colors)} 个有效颜色")
        
        # 生成调色板名称（基于输入文件名）
        palette_name = os.path.splitext(os.path.basename(input_file))[0].title() + " Palette"
        
        # 写入输出文件
        print(f"💾 正在写入 {output_file}...")
        write_gpl(colors, output_file, palette_name)
        
        print(f"✅ 转换成功！已生成 {output_file}")
        print(f"   调色板名称: {palette_name}")
        print(f"   颜色数量: {len(colors)}")
        
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {input_file}")
        print(f"   请确保文件存在且路径正确")
        sys.exit(1)
    except ImportError as e:
        print(f"❌ 缺少依赖库：{e}")
        print(f"\n请安装所需的库：")
        print(f"   pip install openpyxl")
        print(f"   # 或者")
        print(f"   pip install pandas openpyxl")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 颜色格式错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


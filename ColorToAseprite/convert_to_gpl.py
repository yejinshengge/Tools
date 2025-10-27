#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
颜色调色板转换器 (Color to Aseprite Palette Converter)

将 JavaScript 数组格式的颜色数据转换为 GIMP Palette (.gpl) 格式
可用于 Aseprite、GIMP 等图像编辑软件

支持的输入格式：
    [
        { name: 'ColorName', color: 'RRGGBB' },
        ...
    ]

输出格式：GIMP Palette (.gpl)
    GIMP Palette
    #
    # Palette Name
    #
    R G B    ColorName
    ...

作者：AI Assistant
创建日期：2024
"""

import re
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
    hex_color = hex_color.lstrip('#').lower()
    
    # 确保是 6 位十六进制
    if len(hex_color) != 6:
        raise ValueError(f"无效的十六进制颜色值: {hex_color} (需要 6 位)")
    
    # 转换为 RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return r, g, b


def parse_color_js(file_path):
    """
    解析 JavaScript 颜色数组文件，提取颜色信息
    
    参数：
        file_path (str): JavaScript 文件路径
    
    返回：
        list: 包含颜色字典的列表，每个字典包含 'name' 和 'color' 键
              [{'name': 'A1', 'color': 'fff5ca'}, ...]
    
    异常：
        FileNotFoundError: 文件不存在
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配 name 和 color
    # 匹配格式: { name: 'ColorName', color: 'RRGGBB' }
    # 支持单引号和双引号，支持多种空格格式
    pattern = r"\{\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*color:\s*['\"]([^'\"]+)['\"]\s*\}"
    matches = re.findall(pattern, content)
    
    colors = []
    for name, color in matches:
        colors.append({
            'name': name.strip(),
            'color': color.strip()
        })
    
    return colors


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
        f.write(f"# Converted from {os.path.basename(output_path).replace('.gpl', '.js')}\n")
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
        python3 convert_to_gpl.py                        # 使用默认文件名
        python3 convert_to_gpl.py input.js               # 指定输入文件
        python3 convert_to_gpl.py input.js output.gpl    # 指定输入输出文件
    """
    # 默认输入输出文件路径
    input_file = 'colors.js'
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
        colors = parse_color_js(input_file)
        print(f"✓ 找到 {len(colors)} 个颜色")
        
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
    except ValueError as e:
        print(f"❌ 颜色格式错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


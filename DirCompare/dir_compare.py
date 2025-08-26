#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录文件名对比工具

支持对比两个或多个目录下的文件名差异，提供以下功能：
- 配置多个对比路径
- 可选择是否递归查询子目录
- 可选择是否忽略文件扩展名
- 生成详细的对比报告
"""

import os
import argparse
import json
from pathlib import Path
from typing import Set, List, Dict, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CompareConfig:
    """对比配置类"""
    paths: List[str]  # 要对比的目录路径列表
    recursive: bool = True  # 是否递归查询子目录
    ignore_extension: bool = False  # 是否忽略文件扩展名
    output_format: str = 'text'  # 输出格式: text, json
    split_char: str = None  # 分割字符，如 '_', '-', '.'
    split_index: int = None  # 分割后要对比的下标位置


class DirCompare:
    """目录文件名对比工具"""
    
    def __init__(self, config: CompareConfig):
        self.config = config
        self.file_sets: Dict[str, Set[str]] = {}
        
    def get_files_in_dir(self, dir_path: str) -> Set[str]:
        """获取目录中的所有文件名"""
        files = set()
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            print(f"警告: 目录 '{dir_path}' 不存在")
            return files
            
        if not dir_path.is_dir():
            print(f"警告: '{dir_path}' 不是一个目录")
            return files
        
        try:
            if self.config.recursive:
                # 递归获取所有文件
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        # 计算相对路径
                        relative_path = file_path.relative_to(dir_path)
                        filename = str(relative_path)
                        
                        if self.config.ignore_extension:
                            # 忽略扩展名，但保留路径
                            stem = relative_path.stem
                            parent = relative_path.parent
                            if parent != Path('.'):
                                filename = str(parent / stem)
                            else:
                                filename = stem
                        
                        # 处理分割字符和下标
                        filename = self._process_split_filename(filename)
                        
                        files.add(filename)
            else:
                # 只获取当前目录下的文件
                for item in dir_path.iterdir():
                    if item.is_file():
                        filename = item.name
                        
                        if self.config.ignore_extension:
                            filename = item.stem
                        
                        # 处理分割字符和下标
                        filename = self._process_split_filename(filename)
                            
                        files.add(filename)
                        
        except PermissionError:
            print(f"错误: 没有权限访问目录 '{dir_path}'")
        except Exception as e:
            print(f"错误: 读取目录 '{dir_path}' 时发生异常: {e}")
            
        return files
    
    def _process_split_filename(self, filename: str) -> str:
        """根据分割字符和下标处理文件名"""
        if not self.config.split_char or self.config.split_index is None:
            return filename
        
        # 分割文件名
        parts = filename.split(self.config.split_char)
        
        try:
            # 获取指定下标的部分
            if self.config.split_index < 0:
                # 支持负数下标（从末尾开始）
                result = parts[self.config.split_index]
            else:
                result = parts[self.config.split_index]
            return result
        except IndexError:
            # 如果下标超出范围，返回原文件名并显示警告
            print(f"警告: 文件 '{filename}' 按 '{self.config.split_char}' 分割后，下标 {self.config.split_index} 超出范围")
            return filename
    
    def compare_directories(self) -> Dict:
        """执行目录对比"""
        print("开始扫描目录...")
        
        # 获取每个目录的文件集合
        for path in self.config.paths:
            print(f"扫描目录: {path}")
            self.file_sets[path] = self.get_files_in_dir(path)
            print(f"  找到 {len(self.file_sets[path])} 个文件")
        
        # 计算对比结果
        result = self._analyze_differences()
        return result
    
    def _analyze_differences(self) -> Dict:
        """分析文件差异"""
        paths = list(self.file_sets.keys())
        
        if len(paths) < 2:
            return {"error": "至少需要两个目录进行对比"}
        
        # 计算交集和差集
        all_files = set()
        for files in self.file_sets.values():
            all_files.update(files)
        
        result = {
            "config": asdict(self.config),
            "summary": {
                "total_directories": len(paths),
                "total_unique_files": len(all_files)
            },
            "directories": {},
            "common_files": set(),
            "unique_files": {},
            "missing_files": {}
        }
        
        # 记录每个目录的信息
        for path in paths:
            result["directories"][path] = {
                "file_count": len(self.file_sets[path]),
                "files": sorted(list(self.file_sets[path]))
            }
        
        # 计算所有目录都有的文件（交集）
        if len(paths) >= 2:
            common_files = self.file_sets[paths[0]]
            for path in paths[1:]:
                common_files = common_files.intersection(self.file_sets[path])
            result["common_files"] = sorted(list(common_files))
        
        # 计算每个目录独有的文件
        for path in paths:
            other_files = set()
            for other_path in paths:
                if other_path != path:
                    other_files.update(self.file_sets[other_path])
            
            unique = self.file_sets[path] - other_files
            result["unique_files"][path] = sorted(list(unique))
        
        # 计算每个目录缺失的文件（其他目录有但当前目录没有的）
        for path in paths:
            other_files = set()
            for other_path in paths:
                if other_path != path:
                    other_files.update(self.file_sets[other_path])
            
            missing = other_files - self.file_sets[path]
            result["missing_files"][path] = sorted(list(missing))
        
        result["summary"]["common_files_count"] = len(result["common_files"])
        
        return result
    
    def format_output(self, result: Dict) -> str:
        """格式化输出结果"""
        if self.config.output_format == 'json':
            # 转换 set 为 list 以便 JSON 序列化
            json_result = self._convert_sets_to_lists(result)
            return json.dumps(json_result, ensure_ascii=False, indent=2)
        else:
            return self._format_text_output(result)
    
    def _convert_sets_to_lists(self, obj):
        """递归转换集合为列表以便JSON序列化"""
        if isinstance(obj, set):
            return sorted(list(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_sets_to_lists(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_sets_to_lists(item) for item in obj]
        else:
            return obj
    
    def _format_text_output(self, result: Dict) -> str:
        """格式化文本输出"""
        if "error" in result:
            return f"错误: {result['error']}"
        
        output = []
        output.append("=" * 60)
        output.append("目录文件名对比报告")
        output.append("=" * 60)
        output.append("")
        
        # 配置信息
        config = result["config"]
        output.append("对比配置:")
        output.append(f"  递归扫描: {'是' if config['recursive'] else '否'}")
        output.append(f"  忽略扩展名: {'是' if config['ignore_extension'] else '否'}")
        
        # 显示分割配置
        if config.get('split_char') and config.get('split_index') is not None:
            output.append(f"  分割字符: '{config['split_char']}'")
            output.append(f"  对比下标: {config['split_index']}")
        else:
            output.append("  分割模式: 未启用")
        
        output.append("")
        
        # 摘要信息
        summary = result["summary"]
        output.append("摘要信息:")
        output.append(f"  对比目录数: {summary['total_directories']}")
        output.append(f"  总文件数: {summary['total_unique_files']}")
        output.append(f"  共同文件数: {summary['common_files_count']}")
        output.append("")
        
        # 各目录文件统计
        output.append("目录文件统计:")
        for path, info in result["directories"].items():
            output.append(f"  {path}: {info['file_count']} 个文件")
        output.append("")
        
        # 共同文件
        if result["common_files"]:
            output.append(f"所有目录都包含的文件 ({len(result['common_files'])} 个):")
            for file in result["common_files"]:
                output.append(f"  ✓ {file}")
            output.append("")
        
        # 各目录独有文件
        output.append("各目录独有文件:")
        for path, unique_files in result["unique_files"].items():
            if unique_files:
                output.append(f"  {path} 独有 ({len(unique_files)} 个):")
                for file in unique_files:
                    output.append(f"    + {file}")
            else:
                output.append(f"  {path}: 无独有文件")
        output.append("")
        
        # 各目录缺失文件
        output.append("各目录缺失文件:")
        for path, missing_files in result["missing_files"].items():
            if missing_files:
                output.append(f"  {path} 缺失 ({len(missing_files)} 个):")
                for file in missing_files:
                    output.append(f"    - {file}")
            else:
                output.append(f"  {path}: 无缺失文件")
        
        return "\n".join(output)


def load_config_from_file(config_file: str) -> CompareConfig:
    """从配置文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return CompareConfig(**config_data)
    except FileNotFoundError:
        print(f"错误: 配置文件 '{config_file}' 不存在")
        return None
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件格式错误: {e}")
        return None
    except Exception as e:
        print(f"错误: 读取配置文件时发生异常: {e}")
        return None


def create_sample_config(output_file: str = None):
    """创建示例配置文件"""
    if output_file is None:
        # 默认在脚本所在目录下生成配置文件
        script_dir = Path(__file__).parent
        output_file = script_dir / "compare_config.json"
    
    sample_config = CompareConfig(
        paths=["./dir1", "./dir2"],
        recursive=True,
        ignore_extension=False,
        output_format="text",
        split_char=None,
        split_index=None
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(sample_config), f, ensure_ascii=False, indent=2)
    
    print(f"已创建示例配置文件: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="目录文件名对比工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 对比两个目录（递归）
  python dir_compare.py -p ./dir1 ./dir2
  
  # 对比多个目录（非递归，忽略扩展名）
  python dir_compare.py -p ./dir1 ./dir2 ./dir3 --no-recursive --ignore-ext
  
  # 按分割字符对比文件名的特定部分
  python dir_compare.py -p ./dir1 ./dir2 --split-char "_" --split-index 1
  
  # 使用配置文件
  python dir_compare.py -c config.json
  
  # 输出为JSON格式
  python dir_compare.py -p ./dir1 ./dir2 --output json
  
  # 创建示例配置文件（默认在脚本目录）
  python dir_compare.py --create-config
  
  # 创建配置文件到指定位置
  python dir_compare.py --create-config ./my_config.json
        """
    )
    
    parser.add_argument('-p', '--paths', nargs='+', 
                       help='要对比的目录路径列表')
    parser.add_argument('-c', '--config', 
                       help='配置文件路径')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归扫描子目录')
    parser.add_argument('--ignore-ext', action='store_true',
                       help='忽略文件扩展名')
    parser.add_argument('--split-char', 
                       help='分割字符，如 "_", "-", "."')
    parser.add_argument('--split-index', type=int,
                       help='分割后要对比的下标位置（支持负数）')
    parser.add_argument('--output', choices=['text', 'json'], default='text',
                       help='输出格式 (默认: text)')
    parser.add_argument('--save-to', 
                       help='保存结果到文件')
    parser.add_argument('--create-config', nargs='?', const=True, metavar='FILE',
                       help='创建示例配置文件，可选择指定文件路径')
    
    args = parser.parse_args()
    
    # 创建示例配置文件
    if args.create_config:
        if args.create_config is True:
            # 没有指定文件路径，使用默认路径
            create_sample_config()
        else:
            # 用户指定了文件路径
            create_sample_config(args.create_config)
        return
    
    # 确定配置
    config = None
    if args.config:
        config = load_config_from_file(args.config)
        if not config:
            return
    elif args.paths:
        if len(args.paths) < 2:
            print("错误: 至少需要指定两个目录进行对比")
            return
        
        # 验证分割配置
        if (args.split_char is None) != (args.split_index is None):
            print("错误: 分割字符和分割下标必须同时指定或同时不指定")
            return
        
        config = CompareConfig(
            paths=args.paths,
            recursive=not args.no_recursive,
            ignore_extension=args.ignore_ext,
            output_format=args.output,
            split_char=args.split_char,
            split_index=args.split_index
        )
    else:
        print("错误: 请指定要对比的目录路径或配置文件")
        parser.print_help()
        return
    
    # 执行对比
    comparer = DirCompare(config)
    result = comparer.compare_directories()
    
    # 格式化输出
    output = comparer.format_output(result)
    
    # 输出结果
    if args.save_to:
        with open(args.save_to, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.save_to}")
    else:
        print(output)


if __name__ == "__main__":
    main() 
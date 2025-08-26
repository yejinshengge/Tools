import re
import os
import yaml
import json
from typing import Set, List, Dict
import sys
from datetime import datetime

# 默认配置文件路径
DEFAULT_CONFIG_FILE = "config.json"

class NodeChecker:
    def __init__(self):
        self.code_nodes = set()
        self.prefab_nodes = set()
    
    def extract_nodes_from_lua_code(self, lua_file_path: str) -> Set[str]:
        """从Lua代码中提取所有self:GetObject调用的节点名称"""
        nodes = set()
        
        # 规范化路径
        lua_file_path = os.path.normpath(lua_file_path)
        
        try:
            with open(lua_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # 匹配 self:GetObject("节点名") 和 self:GetObject("节点名", child) 等模式
            patterns = [
                r'self:GetObject\s*\(\s*["\']([^"\']+)["\']',  # self:GetObject("_Btn_Video")
                # r'self:SetValue\s*\([^,]+,\s*["\']([^"\']+)["\']',  # self:SetValue(ui_do_type.Active, "_Btn_Continue", false)
                # r'self:AddListener\s*\([^,]+,\s*["\']([^"\']+)["\']',  # self:AddListener(..., "_Btn_Date", ...)
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.startswith('_'):  # 通常UI节点以下划线开头
                        nodes.add(match)
                        
        except FileNotFoundError:
            print(f"文件未找到: {lua_file_path}")
        except Exception as e:
            print(f"读取Lua文件时出错: {e}")
            
        return nodes
    
    def extract_nodes_from_prefab(self, prefab_file_path: str) -> Set[str]:
        """从Unity预制体文件中提取所有GameObject节点名称"""
        nodes = set()
        
        # 规范化路径
        prefab_file_path = os.path.normpath(prefab_file_path)
        
        try:
            with open(prefab_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Unity预制体文件是YAML格式，但我们可以用正则表达式简单提取
            # 匹配 m_Name: 节点名称
            name_pattern = r'm_Name:\s*([^\n\r]+)'
            matches = re.findall(name_pattern, content)
            
            for match in matches:
                # 清理名称，移除引号和空格
                clean_name = match.strip().strip('"\'')
                if clean_name and clean_name.startswith('_'):
                    nodes.add(clean_name)
                    
            # 也可以尝试解析为YAML（如果格式标准的话）
            try:
                # 分割文档（Unity预制体通常包含多个YAML文档）
                documents = content.split('---')
                for doc in documents:
                    if 'GameObject:' in doc:
                        try:
                            yaml_doc = yaml.safe_load(doc)
                            if yaml_doc and isinstance(yaml_doc, dict):
                                if 'GameObject' in yaml_doc:
                                    game_object = yaml_doc['GameObject']
                                    if 'm_Name' in game_object:
                                        name = game_object['m_Name']
                                        if name and name.startswith('_'):
                                            nodes.add(name)
                        except:
                            continue
            except:
                pass  # 如果YAML解析失败，使用正则表达式的结果
                
        except FileNotFoundError:
            print(f"预制体文件未找到: {prefab_file_path}")
        except Exception as e:
            print(f"读取预制体文件时出错: {e}")
            
        return nodes
    
    def find_missing_nodes(self, lua_file_path: str, prefab_file_path: str) -> Dict[str, Set[str]]:
        """查找代码中存在但预制体中不存在的节点"""
        code_nodes = self.extract_nodes_from_lua_code(lua_file_path)
        prefab_nodes = self.extract_nodes_from_prefab(prefab_file_path)
        
        missing_nodes = code_nodes - prefab_nodes
        existing_nodes = code_nodes & prefab_nodes
        
        return {
            'missing': missing_nodes,
            'existing': existing_nodes,
            'code_total': code_nodes,
            'prefab_total': prefab_nodes
        }
    
    def print_results(self, results: Dict, output_file=None):
        """打印检查结果到控制台或文件"""
        # 设置输出流，默认为控制台
        out = sys.stdout
        close_file = False
        
        if output_file:
            try:
                out = open(output_file, 'w', encoding='utf-8')
                close_file = True
            except Exception as e:
                print(f"无法打开输出文件: {e}")
                return
        
        try:
            print("=" * 80, file=out)
            print("节点检查结果", file=out)
            print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=out)
            print("=" * 80, file=out)
            
            for file_pair, result in results.items():
                print(f"\n文件: {file_pair}", file=out)
                print("-" * 60, file=out)
                
                if 'error' in result:
                    print(f"错误: {result['error']}", file=out)
                    if 'code_total' in result and result['code_total']:
                        print(f"代码中的节点 ({len(result['code_total'])}): {sorted(result['code_total'])}", file=out)
                    continue
                
                missing = result.get('missing', set())
                existing = result.get('existing', set())
                code_total = result.get('code_total', set())
                prefab_total = result.get('prefab_total', set())
                
                print(f"代码中的节点总数: {len(code_total)}", file=out)
                print(f"预制体中的节点总数: {len(prefab_total)}", file=out)
                print(f"匹配的节点数: {len(existing)}", file=out)
                print(f"缺失的节点数: {len(missing)}", file=out)
                
                if missing:
                    print(f"\n⚠️  缺失的节点 (在代码中但不在预制体中):", file=out)
                    for node in sorted(missing):
                        print(f"   - {node}", file=out)
                else:
                    print("\n✅ 所有节点都存在于预制体中", file=out)
                
                if existing:
                    print(f"\n✅ 存在的节点:", file=out)
                    for node in sorted(existing):
                        print(f"   - {node}", file=out)
                
                # 显示预制体中有但代码中没用到的节点
                unused_nodes = prefab_total - code_total
                if unused_nodes:
                    print(f"\n💡 预制体中未使用的节点:", file=out)
                    for node in sorted(unused_nodes):
                        print(f"   - {node}", file=out)
        finally:
            if close_file:
                out.close()

def load_config(config_file: str = DEFAULT_CONFIG_FILE) -> Dict:
    """从配置文件加载设置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            if config_file.endswith('.json'):
                return json.load(file)
            elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                return yaml.safe_load(file)
            else:
                # 尝试按JSON解析，失败则按YAML解析
                content = file.read()
                try:
                    return json.loads(content)
                except:
                    return yaml.safe_load(content)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return {}

def create_default_config(config_file: str = DEFAULT_CONFIG_FILE):
    """创建默认配置文件"""
    config = {
        "lua_file": "",
        "prefab_file": "",
        "output_file": "node_check_results.txt"
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4, ensure_ascii=False)
        print(f"已创建默认配置文件: {config_file}")
        print("请根据实际路径修改配置文件中的路径设置")
    except Exception as e:
        print(f"创建配置文件失败: {e}")

def main():
    """主函数"""
    print("Prefab节点比较工具")
    print("=" * 50)
    
    # 检查配置文件是否存在
    if not os.path.exists(DEFAULT_CONFIG_FILE):
        print(f"未找到配置文件 {DEFAULT_CONFIG_FILE}，正在创建默认配置...")
        create_default_config()
        print("请修改配置文件中的路径设置，然后重新运行脚本")
        return
    
    # 加载配置
    config = load_config()
    if not config:
        print("配置文件为空或无效")
        return
    
    # 获取配置项
    lua_file = config.get('lua_file')
    prefab_file = config.get('prefab_file')
    output_file = config.get('output_file')
    
    # 验证配置
    if not lua_file or not prefab_file:
        print("配置文件中缺少必要的路径设置 (lua_file 和 prefab_file)")
        return
    
    # 规范化路径
    lua_file = os.path.normpath(lua_file)
    prefab_file = os.path.normpath(prefab_file)
    
    # 检查文件是否存在
    if not os.path.exists(lua_file):
        print(f"Lua文件不存在: {lua_file}")
        return
    
    if not os.path.exists(prefab_file):
        print(f"预制体文件不存在: {prefab_file}")
        return
    
    # 执行检查
    print(f"正在检查文件:")
    print(f"  Lua文件: {lua_file}")
    print(f"  预制体文件: {prefab_file}")
    
    checker = NodeChecker()
    result = checker.find_missing_nodes(lua_file, prefab_file)
    
    # 输出结果
    file_pair = f"{os.path.basename(lua_file)} -> {os.path.basename(prefab_file)}"
    checker.print_results({file_pair: result}, output_file)
    
    if output_file:
        print(f"\n结果已输出到文件: {output_file}")
    
    print("\n检查完成！")

if __name__ == "__main__":
    main()
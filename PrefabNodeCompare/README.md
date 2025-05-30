# Prefab节点比较工具

这是一个用于检查Lua代码中的UI节点是否在Unity预制体文件中存在的工具。

## 功能说明

- 从Lua代码中提取UI节点引用（如 `self:GetObject`, `self:SetValue`, `self:AddListener` 等）
- 从Unity预制体文件中提取GameObject节点名称
- 比较两者差异，找出缺失的节点
- 生成详细的检查报告

## 使用方法

1. **首次运行**：
   ```bash
   python prefab_node_compare.py
   ```
   脚本会自动创建默认配置文件 `config.json`

2. **修改配置文件**：
   根据实际项目路径修改 `config.json` 中的设置：
   ```json
   {
       "lua_file": "",
       "prefab_file": "",
       "output_file": "node_check_results.txt"
   }
   ```

3. **运行检查**：
   ```bash
   python prefab_node_compare.py
   ```

## 配置文件说明

- `lua_file`: Lua文件的路径
- `prefab_file`: Unity预制体文件的路径  
- `output_file`: 结果输出文件路径（可选，不设置则输出到控制台）

## 输出说明

检查结果包含以下信息：
- 代码中的节点总数
- 预制体中的节点总数
- 匹配的节点数
- 缺失的节点数
- ⚠️ 缺失的节点列表（在代码中但不在预制体中）
- ✅ 存在的节点列表
- 💡 预制体中未使用的节点列表

## 支持的Lua模式

工具会识别以下Lua代码模式中的节点引用：
- `self:GetObject("节点名")`
- `self:SetValue(ui_do_type.Active, "节点名", false)`
- `self:AddListener(event_type, "节点名", callback)`

## 注意事项

- 只检查以下划线 `_` 开头的节点名称
- 支持 `.lua` 和 `.lua.txt` 文件格式
- Unity预制体文件必须是标准的YAML格式

## 环境要求

- Python 3.6+
- PyYAML库（用于解析Unity预制体文件）

安装依赖：
```bash
pip install PyYAML
```


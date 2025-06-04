#!/usr/bin/env python3
"""
组件调试脚本 - 分析和打印所有组件的注册情况
"""

import os
import re
import sys
from pathlib import Path

def find_cmake_files(components_dir):
    """查找所有组件的CMakeLists.txt文件"""
    cmake_files = []
    for item in os.listdir(components_dir):
        component_path = os.path.join(components_dir, item)
        if os.path.isdir(component_path):
            cmake_file = os.path.join(component_path, "CMakeLists.txt")
            if os.path.exists(cmake_file):
                cmake_files.append((item, cmake_file))
    return cmake_files

def analyze_component_registration(cmake_file):
    """分析组件的注册情况"""
    with open(cmake_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 检查是否有armino_component_register调用
    has_register = "armino_component_register" in content
    
    # 提取REQUIRES和PRIV_REQUIRES
    requires = []
    priv_requires = []
    
    # 查找armino_component_register调用
    register_pattern = r'armino_component_register\s*\((.*?)\)'
    register_match = re.search(register_pattern, content, re.DOTALL)
    
    if register_match:
        register_content = register_match.group(1)
        
        # 提取REQUIRES
        requires_pattern = r'REQUIRES\s+(.*?)(?=\s+(?:PRIV_REQUIRES|INCLUDE_DIRS|SRCS|$))'
        requires_match = re.search(requires_pattern, register_content, re.DOTALL)
        if requires_match:
            requires_text = requires_match.group(1).strip()
            # 移除注释行
            requires_lines = [line.strip() for line in requires_text.split('\n') 
                            if line.strip() and not line.strip().startswith('#')]
            if requires_lines:
                requires = ' '.join(requires_lines).split()
        
        # 提取PRIV_REQUIRES
        priv_requires_pattern = r'PRIV_REQUIRES\s+(.*?)(?=\s+(?:REQUIRES|INCLUDE_DIRS|SRCS|$))'
        priv_requires_match = re.search(priv_requires_pattern, register_content, re.DOTALL)
        if priv_requires_match:
            priv_requires_text = priv_requires_match.group(1).strip()
            priv_requires_lines = [line.strip() for line in priv_requires_text.split('\n') 
                                 if line.strip() and not line.strip().startswith('#')]
            if priv_requires_lines:
                priv_requires = ' '.join(priv_requires_lines).split()
    
    return {
        'has_register': has_register,
        'requires': requires,
        'priv_requires': priv_requires,
        'content': content
    }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    components_dir = os.path.join(script_dir, "bk_idk", "components")
    
    if not os.path.exists(components_dir):
        print(f"错误: 组件目录不存在: {components_dir}")
        sys.exit(1)
    
    print("=" * 80)
    print("组件注册情况分析")
    print("=" * 80)
    
    cmake_files = find_cmake_files(components_dir)
    
    registered_components = []
    unregistered_components = []
    component_dependencies = {}
    
    for component_name, cmake_file in sorted(cmake_files):
        analysis = analyze_component_registration(cmake_file)
        
        if analysis['has_register']:
            registered_components.append(component_name)
            component_dependencies[component_name] = {
                'requires': analysis['requires'],
                'priv_requires': analysis['priv_requires']
            }
        else:
            unregistered_components.append(component_name)
    
    print(f"\n已注册组件 ({len(registered_components)}):")
    print("-" * 40)
    for component in sorted(registered_components):
        deps = component_dependencies[component]
        print(f"  ✓ {component}")
        if deps['requires']:
            print(f"    REQUIRES: {', '.join(deps['requires'])}")
        if deps['priv_requires']:
            print(f"    PRIV_REQUIRES: {', '.join(deps['priv_requires'])}")
        print()
    
    print(f"\n未注册组件 ({len(unregistered_components)}):")
    print("-" * 40)
    for component in sorted(unregistered_components):
        print(f"  ✗ {component}")
    
    # 检查特定的依赖关系
    print(f"\n依赖关系分析:")
    print("-" * 40)
    
    # 查找依赖'common'的组件
    common_dependents = []
    for comp, deps in component_dependencies.items():
        if 'common' in deps['requires'] or 'common' in deps['priv_requires']:
            common_dependents.append(comp)
    
    if common_dependents:
        print(f"依赖'common'的组件: {', '.join(common_dependents)}")
    else:
        print("没有组件依赖'common'")
    
    # 检查是否存在'common'组件
    if 'common' in registered_components:
        print("'common'组件: 已注册")
    elif 'common' in unregistered_components:
        print("'common'组件: 存在但未注册")
    else:
        print("'common'组件: 不存在")
    
    # 检查'bk_common'组件
    if 'bk_common' in registered_components:
        print("'bk_common'组件: 已注册")
        deps = component_dependencies['bk_common']
        if deps['requires'] or deps['priv_requires']:
            print(f"  依赖: {deps['requires'] + deps['priv_requires']}")
    else:
        print("'bk_common'组件: 未找到或未注册")
    
    print("=" * 80)

if __name__ == "__main__":
    main() 
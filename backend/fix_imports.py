"""
批量修复导入语句 - 移除 backend. 前缀
"""
import os
import re

# 需要修复的目录
directories = [
    r"E:\OmniMarket-Financial-Monitor\backend\api\endpoints",
    r"E:\OmniMarket-Financial-Monitor\backend\services",
]

# 替换模式
patterns = [
    (r'from backend\.', 'from '),
    (r'import backend\.', 'import '),
]

def fix_file(filepath):
    """修复单个文件的导入"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用所有替换模式
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"错误处理 {filepath}: {e}")
        return False

def main():
    """批量处理所有 Python 文件"""
    fixed_count = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"目录不存在: {directory}")
            continue
            
        print(f"\n处理目录: {directory}")
        
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                filepath = os.path.join(directory, filename)
                if fix_file(filepath):
                    print(f"  ✓ 修复: {filename}")
                    fixed_count += 1
    
    print(f"\n总共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main()

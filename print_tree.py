import os

def print_tree(startpath):
    # 設定要忽略的資料夾
    ignore_dirs = {'.venv', '.git', '__pycache__', '.idea', '.vscode'}
    
    for root, dirs, files in os.walk(startpath):
        # 修改 dirs 列表以過濾不需要遍歷的目錄 (in-place modification)
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
        
        print(f'{indent}{os.path.basename(root)}/')
        
        subindent = '│   ' * level + '├── '
        for f in files:
            # 也可以順便過濾掉 .pyc 檔
            if not f.endswith('.pyc') and f != '.DS_Store': 
                print(f'{subindent}{f}')

if __name__ == '__main__':
    print_tree('.')
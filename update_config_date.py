import re
import sys
from datetime import datetime
from pathlib import Path


def update_date_in_file(filepath):
    today = datetime.now().strftime("%Y%m%d")
    update_pattern = re.compile(r"^(#update:\s*)\d{8}", re.IGNORECASE)
    changed = False
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if update_pattern.match(line):
                newline = update_pattern.sub(r"\1" + today, line)
                lines.append(newline)
                changed = True
            else:
                lines.append(line)
    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[OK] {filepath} 日期已更新为 {today}")
    else:
        print(f"[SKIP] {filepath} 未找到 #update: 行，无需更改")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python update_config_date.py 文件1 [文件2 ...]")
        sys.exit(1)
    for file in sys.argv[1:]:
        path = Path(file)
        if path.exists() and path.is_file():
            update_date_in_file(str(path))
        else:
            print(f"[ERROR] 文件不存在: {file}")

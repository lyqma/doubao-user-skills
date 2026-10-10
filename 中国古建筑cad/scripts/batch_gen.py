#!/usr/bin/env python3
"""
古建CAD批量出图脚本 V4.12
读取JSON目录，批量生成所有建筑的平面图和剖面图。
用法: python batch_gen.py <json_dir> [--output <dir>] [--mode quick_shell]
"""
import json
import sys
import argparse
from pathlib import Path
import subprocess

def main():
    parser = argparse.ArgumentParser(description="古建参数化批量出图工具 V4.12")
    parser.add_argument("input_dir", help="JSON配置文件所在目录")
    parser.add_argument("--output", "-o", help="输出目录（默认同输入目录）")
    parser.add_argument("--mode", "-m", choices=["quick_shell", "full_detail"], default="quick_shell")
    parser.add_argument("--skip-existing", "-s", action="store_true", help="跳过已存在的文件")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output) if args.output else input_path
    output_path.mkdir(parents=True, exist_ok=True)

    # 收集所有JSON文件
    json_files = sorted(input_path.glob("*.json"))
    if not json_files:
        # 也检查assets/templates子目录
        json_files = sorted(input_path.rglob("*.json"))

    if not json_files:
        print(f"[ERROR] 在 {input_path} 中未找到JSON文件")
        sys.exit(1)

    print(f"找到 {len(json_files)} 个JSON配置:")
    for jf in json_files:
        print(f"  - {jf.name}")
    print()

    # 获取gen_scr.py路径
    script_dir = Path(__file__).parent
    gen_scr = script_dir / "gen_scr.py"

    success = 0
    failed = 0
    skipped = 0

    for json_file in json_files:
        output_dir = output_path
        skip_flag = ["--skip-existing"] if args.skip_existing else []

        cmd = [
            sys.executable, str(gen_scr),
            str(json_file),
            "--output", str(output_dir),
            "--mode", args.mode
        ]

        print(f"[{json_file.name}]...", end=" ", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

        if result.returncode == 0:
            # 提取输出文件名
            for line in result.stdout.strip().split("\\n"):
                if line.startswith("  "):
                    print(line.strip())
            success += 1
        else:
            print(f"FAILED")
            print(f"  Error: {result.stderr.strip()}")
            failed += 1

    print()
    print(f"完成: 成功 {success}, 失败 {failed}, 共 {len(json_files)} 个")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

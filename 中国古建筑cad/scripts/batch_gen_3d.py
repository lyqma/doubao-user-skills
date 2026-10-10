#!/usr/bin/env python3
"""
批量 3D 渲染生成器
扫描 assets/templates/ 目录，为每个 JSON 生成 Blender 渲染脚本。
用法: python batch_gen_3d.py [--output <dir>] [--render]
"""
import json
import argparse
import subprocess
from pathlib import Path
import sys

SKILL_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"

# 渲染模式
MODES = ["studio", "outdoor", "dawn"]
CAMERA_ANGLES = [0, 30, 45, 60]  # 常用拍摄角度

def generate_all(output_dir=None, render=False):
    """为所有模板生成 3D 渲染脚本"""
    out = Path(output_dir) if output_dir else SKILL_DIR / "renders_3d_batch"
    out.mkdir(parents=True, exist_ok=True)
    
    templates = sorted(TEMPLATE_DIR.glob("*.json"))
    if not templates:
        print("未找到模板文件")
        return
    
    results = []
    for tpl in templates:
        try:
            with open(tpl, encoding="utf-8") as f:
                cfg = json.load(f)
            
            name = cfg.get("name", tpl.stem)
            safe_name = name.replace(" ", "_")
            
            # 为每种渲染模式和角度生成
            for mode in MODES:
                for angle in CAMERA_ANGLES:
                    script_name = f"{safe_name}_{mode}_{angle}deg.py"
                    script_path = out / script_name
                    
                    # 读取模板
                    tpl_content = open(SKILL_DIR / "scripts" / "gen_3d.py", encoding="utf-8").read()
                    
                    # 提取模板部分并替换
                    import re
                    template_match = re.search(r"BLENDER_PY_TEMPLATE = '''(.+?)'''", tpl_content, re.DOTALL)
                    if not template_match:
                        print(f"[SKIP] {name}: 找不到模板定义")
                        continue
                    
                    template = template_match.group(1)
                    config_json = json.dumps(cfg, ensure_ascii=False)
                    
                    script_content = template.format(
                        config_json=config_json,
                        output_dir=str(out),
                        render_mode=mode,
                        camera_angle=angle,
                    )
                    
                    script_path.write_text(script_content, encoding="utf-8")
                    
                    cmd = f"blender -b --python \"{script_path}\""
                    print(f"[OK] {name} | {mode} | {angle}° → {script_path.name}")
                    
                    if render:
                        r = subprocess.run(["blender", "-b", "--python", str(script_path)],
                                          capture_output=True, timeout=300)
                        if r.returncode != 0:
                            print(f"  [ERR] {r.stderr.decode()[-200:]}")
                    results.append(script_path)
                    
        except Exception as e:
            print(f"[FAIL] {tpl.name}: {e}")
    
    print(f"\n共生成 {len(results)} 个渲染脚本到: {out}")
    return results

def main():
    parser = argparse.ArgumentParser(description="批量 3D 渲染生成器")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--render", "-r", action="store_true", help="立即渲染")
    parser.add_argument("--template", "-t", help="只生成指定模板")
    args = parser.parse_args()
    
    generate_all(args.output, args.render)

if __name__ == "__main__":
    main()

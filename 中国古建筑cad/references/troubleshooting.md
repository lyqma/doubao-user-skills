# CAD-MCP 故障排除与正确使用方法

## 问题诊断

### 当前遇到的问题

**错误信息**:
```
成功连接到已运行的AutoCAD实例
启动CAD失败: <unknown>.Count
```

**原因分析**:
1. AutoCAD 2024 正在执行命令（如 EXTRUDE），COM 接口被忙碌状态拒绝
2. CAD-MCP 的 COM 连接重试机制未能正确处理这种情况
3. 需要使用正确的流程来等待 CAD 空闲

---

## 解决方案

### 方案一：等待 CAD 空闲后再操作

**步骤**:

1. **检查 CAD 是否正在执行命令**
   ```powershell
   # 查看 AutoCAD 进程状态
   Get-Process -Name "acad*" | Select-Object Id, ProcessName, MainWindowTitle, Responding
   ```

2. **在 CAD 中手动按 ESC 清除命令**
   - 点击 CAD 窗口
   - 按 `ESC` 键 5-10 次，确保命令行没有等待输入
   - 等待约 3-5 秒让 CAD 完全空闲

3. **验证 CAD 状态**
   ```powershell
   Get-Process -Name "acad*" | Select-Object Id, ProcessName, MainWindowTitle, Responding
   ```
   确认 `Responding` 为 `True`

4. **重启 CAD-MCP 服务**
   ```powershell
   # 停止现有进程
   Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
   
   # 等待 2 秒
   Start-Sleep -Seconds 2
   
   # 启动新服务
   cd D:\CAD-MCP
   .\.venv\Scripts\python.exe src\server.py
   ```

---

### 方案二：使用 SCR 脚本文件（推荐）

**优势**: 不依赖 COM 实时连接，避免繁忙状态问题

**步骤**:

1. **打开 AutoCAD**
   - 确保 CAD 已打开且处于空闲状态
   - 命令行无等待输入

2. **运行 SCR 脚本**
   ```
   命令行输入: SCRIPT
   选择文件: D:\CAD-MCP\清式四柱三间冲天牌楼_平面.scr
   回车确认
   ```

3. **依次运行其他脚本**
   ```
   SCRIPT
   选择文件: D:\CAD-MCP\清式四柱三间冲天牌楼_剖面.scr
   回车确认
   
   SCRIPT
   选择文件: D:\CAD-MCP\清式四柱三间冲天牌楼_3D建模.scr
   回车确认
   ```

4. **调整视图**
   ```
   命令: ZOOM
   选项: E ( extents )
   ```

---

### 方案三：使用 pyautogui 发送命令（备选）

**适用场景**: COM 连接失败时的备选方案

```powershell
cd D:\CAD-MCP

python -c "
import pyautogui
import time

# 确保 CAD 窗口在最前
# pyautogui 需要窗口在前台才能发送键盘输入

# 发送 ESC 清除命令
print('发送 ESC...')
for _ in range(10):
    pyautogui.press('esc')
    time.sleep(0.1)

time.sleep(2)

# 发送 ZOOM E
print('发送 ZOOM E...')
pyautogui.typewrite('_ZOOM\n')
time.sleep(0.5)
pyautogui.typewrite('E\n')
time.sleep(2)

print('完成')
"
```

---

## CAD-MCP 正确工作流程

### 前置条件检查

```powershell
# 1. 检查 Python 版本
python --version
# 应输出: Python 3.10+

# 2. 检查 AutoCAD 是否运行
Get-Process -Name "acad*" | Select-Object Id, ProcessName, MainWindowTitle, Responding

# 3. 检查虚拟环境
Test-Path "D:\CAD-MCP\.venv\Scripts\python.exe"

# 4. 检查依赖
cd D:\CAD-MCP
\.venv\Scripts\python.exe -m pip list | Select-String "mcp|pywin32|pydantic"
```

### 启动 CAD-MCP 服务

```powershell
# 方法1: 前台运行（调试用）
cd D:\CAD-MCP
\.venv\Scripts\python.exe src\server.py

# 方法2: 后台运行
cd D:\CAD-MCP
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "src\server.py" -WindowStyle Hidden
```

### MCP 配置

**配置文件位置**: `C:\Users\Administrator\.codex\mcp.json`

```json
{
  "mcpServers": {
    "CAD-MCP": {
      "command": "D:\\CAD-MCP\\.venv\\Scripts\\python.exe",
      "args": [
        "D:\\CAD-MCP\\src\\server.py"
      ]
    }
  }
}
```

### 验证 MCP 连接

```powershell
# 运行验证脚本
cd D:\CAD-MCP
python _verify_handshake.py

# 查看结果
Get-Content "_verify_result.txt"
```

---

## 常见问题与解决

### Q1: CAD-MCP 连接失败 "启动CAD失败: <unknown>.Count"

**原因**: AutoCAD 正在执行命令，COM 接口被拒绝

**解决**:
1. 在 CAD 中按 ESC 清除所有命令
2. 等待 5 秒让 CAD 完全空闲
3. 重启 CAD-MCP 服务
4. 如果仍然失败，关闭并重新打开 AutoCAD

### Q2: SendCommand 方法不存在

**原因**: AutoCAD 版本兼容性问题

**解决**:
- AutoCAD 2024+ 可能修改了 COM 接口
- 使用 `_call_with_com_retry` 重试机制
- 或者改用 SCR 脚本方式

### Q3: COM 调用返回 "RPC_E_CALL_REJECTED"

**原因**: CAD 正在处理其他任务

**解决**:
```powershell
# 等待 CAD 空闲
Start-Sleep -Seconds 10

# 发送 ESC 清除命令
python -c "
import win32com.client, pythoncom, time
pythoncom.CoInitialize()
cad = win32com.client.GetActiveObject('AutoCAD.Application')
for _ in range(5):
    cad.ActiveDocument.SendCommand(chr(255))  # ESC
    time.sleep(0.2)
time.sleep(3)
print('CAD 已清除空闲状态')
"
```

### Q4: 图层创建失败

**原因**: 图层已存在或 CAD 繁忙

**解决**:
- 先检查图层是否存在
- 使用 `create_layer` 时会自动跳过已存在的图层

---

## 推荐的完整工作流

### 步骤 1: 准备阶段

```powershell
# 1. 打开 AutoCAD
# 2. 等待 CAD 完全加载
# 3. 按 ESC 清除任何命令
# 4. 输入 ZOOM ALL 适应视图
```

### 步骤 2: 启动 CAD-MCP

```powershell
cd D:\CAD-MCP
\.venv\Scripts\python.exe src\server.py
```

### 步骤 3: 验证连接

```powershell
python _verify_handshake.py
Get-Content _verify_result.txt
```

### 步骤 4: 使用 MCP 工具绘图

```python
# 通过 Codex++ 调用 MCP 工具
send_command("_.ERASE All")
create_layer("BASE", 8)
create_layer("WOOD_FRAME", 3)
create_layer("DOUGONG", 6)
create_layer("ROOF", 5)
create_layer("DECORATION", 10)

# 绘制台基层
set_current_layer("BASE")
draw_rectangle(-8840, -1300, 8840, 1300)
draw_rectangle(-6000, -1000, 6000, 1000)
draw_rectangle(-4000, -800, 4000, 800)

# 切换到3D视图
send_command("_VPOINT -1,-1,1")
send_command("_HIDE")
send_command("_ZOOM _E")
```

### 步骤 5: 保存图纸

```
命令: SAVEAS
文件名: D:\CAD-MCP\银丝古建牌楼_银丝版.dwg
```

---

## 备用方案：纯 SCR 脚本流程

如果 CAD-MCP 始终无法连接，可以使用纯 SCR 脚本方式：

```powershell
# 1. 确保 CAD 已打开且空闲
# 2. 在 CAD 命令行依次执行：

SCRIPT
选择: D:\CAD-MCP\清式四柱三间冲天牌楼_平面.scr

SCRIPT
选择: D:\CAD-MCP\清式四柱三间冲天牌楼_剖面.scr

SCRIPT
选择: D:\CAD-MCP\清式四柱三间冲天牌楼_3D建模.scr

ZOOM ALL
SAVEAS
D:\CAD-MCP\银丝古建牌楼_最终版.dwg
```

---

## 生成的文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| 平面图脚本 | `D:\CAD-MCP\清式四柱三间冲天牌楼_平面.scr` | AutoCAD 平面图 |
| 剖面图脚本 | `D:\CAD-MCP\清式四柱三间冲天牌楼_剖面.scr` | AutoCAD 剖面图 |
| 3D建模脚本 | `D:\CAD-MCP\清式四柱三间冲天牌楼_3D建模.scr` | AutoCAD 3D实体 |
| 配件尺寸数据 | `D:\CAD-MCP\清式四柱三间冲天牌楼_配件尺寸.json` | 完整尺寸参数 |
| 脚本生成器 | `D:\CAD-MCP\generate_paifang_3d.py` | 重新生成脚本 |
| MCP配置 | `C:\Users\Administrator\.codex\mcp.json` | Codex++ 加载配置 |

---

**版本**: V2.0  
**最后更新**: 2026-09-19

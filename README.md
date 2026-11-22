# 知序 AI · 高等数学私人导师

在本机完成第一学期高数的诊断、学习、纠错和复习。内置 10 个原创单元、10 道诊断题和 40 道分级练习。首次打开即可学习，无需账号或 API Key。

![学习总览的真实运行截图](docs/evidence/dashboard.png)

## Windows 启动

1. 安装 64 位 **Python 3.12**，安装时保留 Python Launcher。安装 **Node.js 22.12 或更新的 LTS 版本**，包含 npm。在新终端运行 `py -3.12 --version` 和 `node -v` 可检查版本。已有 Python 3.14 可以与 3.12 并存，启动器明确选择 3.12。
2. 将本分支下载、解压到可写目录，双击根目录的 **start.cmd**。第一次需要联网，脚本在项目内创建虚拟环境、安装依赖并构建界面。保留控制台窗口，浏览器会打开本地应用。浏览器未自动打开时，在地址栏输入 `http://127.0.0.1:8765`。
3. 按 Ctrl+C 停止服务。再次双击同一目录的启动脚本即可继续。安装和构建成功后，启动器根据文件摘要复用已有依赖与界面，日常学习可离线运行。

如果端口已占用，在已完成构建的项目目录执行 `.venv\Scripts\python.exe server.py --port 8766 --open`。首次安装中断时，修复网络后再次双击启动脚本。原生 Windows 实机验收仍待执行，云端已验证同一 Python 启动器与完整浏览器流程。

## 十分钟体验一次闭环

1. 打开资料库，导入随仓库提供的两页原创 PDF。切换到第 2 页，可看到 Peano 余项的原文和对应知识单元。点击「按此资料优先诊断」可优先测试材料中出现的知识点。[示例 PDF](examples/局部近似与相消.pdf)
2. 从首页「开始诊断」进入通用诊断。在正弦相消极限题中尝试输入 `0`。可以先看两级提示，提交后查看参考答案、建议排查的错因以及先修讲义。离开未完成的诊断后，可继续剩余题目。
3. 浏览知识图谱，点击节点进入学习页。泰勒单元可切换 1、3、5 阶多项式，比较局部逼近。数值和多项式使用 SymPy 验算，乘法写作 `*`，幂写作 `^`，分母限非零常数。
4. 在「错题与复习」中重做相消题，输入 `-1/6`。答对后，下次巩固日期为本机日期加三天。个人进度显示最近的作答记录。估计掌握度为该单元不同已答题中，最近一次答对的比例。
5. 在「个人进度」导出学习进度 JSON。换电脑后可勾选替换确认并恢复。资料原件请单独保管，恢复 JSON 后可再次导入。需要完整迁移时，先关闭服务，再复制 `data/learning.db`，其中包含原文片段与答题记录。

## 资料与模型

PDF 按页提取文本，Markdown 按标题分段，TXT 保留正文。导入限制为 4 MB、PDF 120 页，超限可分卷导入。扫描件请先在自己的设备上 OCR；混合 PDF 会列出无法读取的页码。文本提取可能改变公式排版，核对计算时应查看资料原件。

离线导读按术语将可定位的片段关联到课程，生成原文回忆题，并按资料覆盖和学习记录排序诊断题。原文回忆中的开放说明供自评，客观数学题均标记为内置原创示例。题库中的基础题含参数化变式，每个单元另设综合题。

可选追问使用已在本机运行的 Ollama。先在本机准备模型，再在 PowerShell 设置环境变量后启动，例如：

```powershell
$env:ZHIXU_OLLAMA_MODEL = "你已安装的模型名称"
.\start.cmd
```

打开一份资料，编辑授权片段和问题，勾选同意后提交。本机服务只向固定的 Ollama 回环地址发送该问题和选定片段（最多 1000 字）。未启用时会显示配置状态。核心功能无需模型，ChatGPT Plus 或 Codex 额度不参与应用运行。

## 开发与验证

单个 Python 本地 HTTP 服务提供 SQLite 存储、SymPy 判题与 pypdf 导入。前端使用 Vite、浏览器原生 JavaScript 模块和 KaTeX，字体随构建产物提供。此选型只需启动一个服务。

在 Linux 或 macOS 的仓库根目录可执行：

```bash
python3.12 -m venv .venv
.venv/bin/python launcher.py
```

Windows 开发者可在根目录用 PowerShell 复验：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
npm ci
npm run build
.venv\Scripts\python -m unittest discover -s tests -v
.venv\Scripts\python -m playwright install chromium
.venv\Scripts\python tests/e2e.py
```

Linux 将上述解释器路径替换为 `.venv/bin/python`。E2E 使用独立临时数据库、全新浏览器上下文及随机端口，优先使用系统 Chromium，亦支持 Playwright 安装的 Chromium。验证时会更新 `docs/evidence` 的浏览器截图。用环境变量 `ZHIXU_DB` 可另选数据库文件。

[验收清单与日志](docs/ACCEPTANCE.md)

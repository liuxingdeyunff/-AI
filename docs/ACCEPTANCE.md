# 第二轮验收记录

候选版本为 `v0.2.0-rc.3`。Windows 软件包使用构建时生成的界面和随包的 Python 运行时。用户通过 EXE 启动。

| 验收项 | 证据 |
| --- | --- |
| Windows x64 ZIP 构建、解压启动、重复启动、端口冲突与 SQLite 重启 | [Windows Runner 产物测试](https://github.com/liuxingdeyunff/-AI/actions/runs/45011942997/job/137175961448) |
| 无开发工具的 Windows 系统 | 同一 Windows 作业运行干净的 Server Core，确认不存在 Python、Node.js、npm、Vite 命令，然后用 ZIP 内的 EXE 判题 |
| 个性化教学 | 学生写步骤、确认展开方法，答错后变式难度由 2 降至 1；保存步骤、两级提示使用情况和独立判题证据。[浏览器日志](evidence/e2e.log) · [复盘截图](evidence/coaching.png) |
| 数学、引用、错误处理与备份 | 15 项后端测试。恢复时重新计算变式结果，拒绝无来源引用和循环先修关系，单独验证有限小数精度。[实际输出](evidence/backend.log) |
| 真实本机模型 | CI 在隔离的 Ollama 中运行 qwen2.5:3b，提交原创材料和合成学生步骤，保存实际回复、用时与模型摘要。本机推理 API 费用为零。[成功运行](https://github.com/liuxingdeyunff/-AI/actions/runs/45012019092) |
| 云端模型 | DeepSeek 为可选配置。已检查缺少针对目标服务的同意时不会发出请求。未使用付费密钥进行在线验收。 |

首轮真实模型集成测试曾失败，随后调整了先修边界处理，并保留无来源引用的拒绝机制。[失败作业](https://github.com/liuxingdeyunff/-AI/actions/runs/45011714379)

已知限制包括扫描 PDF 需先 OCR，模型研读每次最多选择 6 段、每段开头 1800 字，语言模型的讲解与开放题建议仍需核对。Windows 测试使用 Server Runner 与 Server Core，尚无 Windows 11 消费版实体机的人工验收记录。EXE 未做商业代码签名。

# 第一轮验收历史

云端实测环境为 Linux x86_64、Python 3.12.14、Node.js 24.22.3、npm 11.19.1、Chromium 156。以下截图均由 Playwright 在实际服务器页面上截取。测试数据库存放在临时目录，应用首页从空学习记录开始。

| 项目 | 状态 | 实际检查与证据 |
| --- | --- | --- |
| M1 本地启动、课程与构建 | PASS | 在独立 Python 3.12 虚拟环境安装固定版本，运行启动器、构建 Vite 产物，实际请求返回 10 个原创单元。[构建日志](evidence/build.log) · [启动日志](evidence/launcher.log) |
| 首页、桌面和窄屏导航 | PASS | 1440 像素首页截图，390 像素视窗可展开导航、进入图谱，无水平溢出。[首页](evidence/dashboard.png) · [手机](evidence/mobile.png) |
| 10 个单元与建议先修关系 | PASS | 测试检查单元编号、公式和先修边；图谱节点可跳转讲义。讲义包含来源、推导、例题和误区。[课程测试](../tests/test_courses.py) |
| 数值、符号、概念、推导选择 | PASS | 10 道诊断、40 道练习全部核对参考答案。符号题用 SymPy 的极限、级数和导数生成对照值，概念选择题使用明确选项。[数学测试](../tests/test_learning.py) |
| 正弦相消、指数相消、对数三阶展开 | PASS | 正弦相消得到 −1/6，指数相消得到 1/2，对数展开由 series 校验至三阶；输入 0、1、漏三次项的多项式分别判错。三阶余项的恒等误区也被拒绝。[后端输出](evidence/backend.log) |
| KaTeX、动态可视化与单元练习 | PASS | 浏览器检查泰勒课程无 KaTeX 错误节点，切换至五阶近似，提交相关多项式练习并获得正确反馈。[学习页](evidence/lesson.png) |
| 诊断 → 教学 → 纠错 → 复习 | PASS | 浏览器依次提交 10 题，逐级查看提示，故意答错相消题，进入先修讲义，重做答对，出现下次巩固日期。[复习页](evidence/review.png) · [E2E 输出](evidence/e2e.log) |
| 掌握估计、重试与复习时间 | PASS | 按不同题目的最近结果计算。重复答对只算一份证据，同一提交重传只记一次；测试检查重做成功后尚未到期。[单元测试输出](evidence/backend.log) |
| 文本 PDF、Markdown、TXT 和双向出处 | PASS | 实际导入两页中文原创 PDF，切至第 2 页并核验摘录；知识单元可按页回到原文。测试校验 Markdown 标题、TXT 正文、重复导入与混合 PDF 空页。[示例 PDF](../examples/局部近似与相消.pdf) · [原文页](evidence/source.png) |
| 材料驱动的学习与诊断 | PASS | 根据出现的术语生成带页码的导读与原文回忆题。导入仅含 Taylor 术语的材料后，从该文件启动诊断，第一题切换至泰勒单元并带来源链接。[E2E 测试](../tests/e2e.py) |
| 无文本与输入错误恢复 | PASS | 在浏览器导入无文本 PDF 得到 OCR 提示，随后成功导入中文 PDF。空文本、无效数学表达式和零分母在后端测试中被拒绝。[后端输出](evidence/backend.log) |
| SQLite 持久化与进度备份 | PASS | 导出包含 11 条记录的 JSON，终止服务器进程，使用同一数据库启动新进程，核验复习记录并通过界面恢复备份。无效备份不会部分覆盖数据。[E2E 输出](evidence/e2e.log) |
| 本地访问与模型授权 | PASS | 浏览器测试向本地服务发出跨源写请求得到 HTTP 403。模型适配层测试确认缺少发送同意时会报错。默认无模型的完整教学路径通过。[测试代码](../tests/test_materials.py) |
| 真实 Ollama 推理 | NOT TESTED | 云机未安装 Ollama 或模型。可在模型已就绪的本机设置环境变量，在资料页选择摘录并提问。 |
| Windows 双击启动实机验收 | NOT TESTED | 已提供 start.cmd 及版本固定的安装步骤，同一 Python 启动器在 Linux 虚拟环境已运行。原生 Windows 的批处理、浏览器唤起和整套验收需在 Windows 执行。[Windows 步骤](../README.md) |

## GitHub 审查状态

独立分支 `feature/zhixu-tutor` 已成功推送，M4 提交为 `5cd78c4`。通过 GitHub CLI 创建草稿 PR 时，GitHub API 请求返回 `Post "https://api.github.com/graphql": Forbidden`，权限重试结果相同。PR 描述已随代码提交，可使用 GitHub 网页创建草稿；目标分支为 main。

[创建 PR](https://github.com/liuxingdeyunff/-AI/pull/new/feature/zhixu-tutor) · [审查说明](PULL_REQUEST.md)

## 复现与输出

在仓库根目录安装依赖后运行下列命令。Playwright 依赖与浏览器安装步骤见 README。

```bash
npm ci
npm run build
python -m unittest discover -s tests -v
python tests/e2e.py
```

本次后端运行 9 项测试，全部通过。浏览器端为一条贯穿完整流程的测试，输出六组通过记录，最后断言没有页面脚本异常。403 和无文本文件返回的 400 是测试预期。以上功能均在无需模型的模式下验收。

## 开发中出现的失败

- M1 尝试安装 lucide-vanilla 时，npm 返回 E404。改用 lucide 包后，首次构建报告包入口无法解析。检查已发布的文件目录，改为从包内实际的 ESM 入口引入图标，并锁定依赖。后续干净安装和构建通过。
- npm 11 在安装时提示 esbuild 的 postinstall 未列入 allowScripts。当前平台的锁文件安装和 Vite 生产构建均成功。[安装输出](evidence/npm-ci.log)
- 首次浏览器截图检查发现，无 URL 片段时首页面包屑显示为学习单元。修正首页默认导航状态后重新生成了桌面、窄屏截图并重跑 E2E。

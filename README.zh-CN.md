<div align="center">

[English](README.md) · **中文**

<img src="assets/cover-zh.png" alt="AcademiCats · Paper Search" width="100%">

<br>

# 🐱 论文检索

**跨全球学术库检索真实论文，并深度精读任意开放获取 PDF。基于真实数据，绝不编造。**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-0064F4.svg)](LICENSE)
&nbsp;[![Claude](https://img.shields.io/badge/Claude-0064F4.svg)](https://claude.com/claude-code)
&nbsp;[![ChatGPT](https://img.shields.io/badge/ChatGPT-0064F4.svg)](https://chatgpt.com)
&nbsp;[![DeepSeek](https://img.shields.io/badge/DeepSeek-0064F4.svg)](https://chat.deepseek.com)
&nbsp;[![Full product](https://img.shields.io/badge/完整产品-academicats.com-0064F4.svg)](https://academicats.com)

</div>

---

> ### 🪶 这是 [**AcademiCats**](https://academicats.com) 的**开源轻量版**（正式版现处公测，免费试用）
> 完整产品在 **[academicats.com](https://academicats.com)** —— 一个 AI 研究工作台，带你从*找文献*一路走到*读、写、自审*：覆盖广度堪比 Google Scholar、支持中文文献、可保存文献库、界面精致，还带多智能体审稿。本 skill 把这套工作流里的检索部分免费开源，自包含、可直接在你自己的 AI 上运行——Claude、ChatGPT 或 DeepSeek 皆可。

---

## ✨ 它能做什么

🔍 **真正管用的检索** —— 一次同时查遍五大学术库（OpenAlex、Crossref、arXiv、Semantic Scholar、Europe PMC），自动去重，再按**真实研究契合度**排序——而不是只看关键词重不重合。

📄 **精读，而非略读** —— 任选一篇开放获取论文，它会解析 PDF、抽取正文，给你一份结构化的精读：研究问题、方法、核心发现、局限 —— 并在原文支持处尽量标注出处页码。

🛡️ **不编论文，不编结论** —— 每条结果都是公共 API 的真实记录，每份精读只基于真正抽取到的正文。论文被付费墙挡住时，它会**直说**，绝不杜撰内容。

<br>

## 🎬 演示

一句话说清——主题，外加任何选项：

> *"帮我找 20 篇 2020 年以后关于 CRISPR 脱靶效应的论文。"*

它**立刻就跑**——不用填表、不用来回确认——返回一份**带编号的结果列表**，每篇一行、方便扫读，你可以直接用序号操作。格式由脚本固定生成，**换任何大模型来跑都完全一致**：

> ## 🔎 共 5 条结果：CRISPR off-target effects
> 1. **[Off-target effects in CRISPR/Cas9 gene editing](https://doi.org/10.3389/fbioe.2023.1143157)** — Congting Guo et al. · 2023 · 被引 537 · 🟢 · [PDF](https://www.frontiersin.org/articles/10.3389/fbioe.2023.1143157/pdf)
> 2. **[Latest Developed Strategies to Minimize Off-Target Effects in CRISPR-Cas Genome Editing](https://doi.org/10.3390/cells9071608)** — Naeem et al. · 2020 · 被引 451 · 🟢 · [PDF](https://www.mdpi.com/2073-4409/9/7/1608/pdf)
> 3. **[CRISPR/Cas Systems in Genome Editing: sgRNA Design & Off‑Target Evaluation](https://doi.org/10.1002/advs.201902312)** — Manghwar et al. · 2020 · 被引 357 · 🟢 · [PDF](https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/advs.201902312)
> 4. **[CRISPR/Cas13 effectors have differing off-target effects in eukaryotic cells](https://doi.org/10.1093/nar/gkac159)** — Ai et al. · 2022 · 被引 151 · 🔒
> 5. **[Beyond the promise: evaluating & mitigating off-target effects for safer therapeutics](https://doi.org/10.3389/fbioe.2023.1339189)** — Lopes et al. · 2024 · 被引 62 · 🟢

标题直接链接原文；🟢 表示有可读全文的免费 PDF。然后你只要说 **"深读 #1"**——它就打开那篇的 PDF，逐条列出关键发现并标注出处页码，且完全基于论文原文。

> 每次检索还会把**完整结果**（全部条目、含摘要）写进一个 `search-results.md` 文件——完整列表一定被保存下来，绝不会被截断。

<br>

## 🚀 开始使用 —— 按你的平台选一种

按你常用的 AI 选一种，每种不到一分钟：

**🖥️ Claude Code** —— 本地运行、自动触发（完整能力版）
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/academicatstool-netizen/Cat_paper_search.git ~/.claude/skills/paper-search
python -m pip install -r ~/.claude/skills/paper-search/scripts/requirements.txt   # 用于读取 PDF
```
重启 Claude Code，然后直接说 —— *"找几篇关于…的最新论文"*、*"总结这篇 arXiv 论文…"*

**🌐 Claude 网页 / 桌面版** —— 下载 **[`paper-search.skill`](paper-search.skill)**，在 **Settings → Capabilities → Skills** 里上传。（检索与读 PDF 的脚本会在 Claude 自带的代码沙箱里运行。）

**🤖 ChatGPT** —— 打开 **[`PORTABLE_PROMPT.md`](PORTABLE_PROMPT.md)**，贴进**自定义 GPT** 的 *Instructions*（或第一条消息），并**开启联网浏览**，然后提问。

**💬 DeepSeek / 任意其他模型** —— 把 **[`PORTABLE_PROMPT.md`](PORTABLE_PROMPT.md)** 作为**系统提示**粘贴，并确保能联网，然后提问。

> ⚠️ **在 ChatGPT/DeepSeek 上需联网** —— 检索改用联网浏览（而非 Python 脚本），记得开启浏览。覆盖广度弱于 Claude 版，但每条结果都真实（没网时它会直说而不是编造）。想要完整能力，请用 Claude Code 那条路（或任何能跑 Python+联网的 agent，如 Cursor）。

<br>

## 💙 大家为什么喜欢它

|  | 论文检索（本 skill） | [AcademiCats 完整产品 →](https://academicats.com) |
|---|:---:|:---:|
| ⚡ **速度** | 几分钟（在你的模型上实时跑） | **数秒** —— 优化管线 + 缓存 |
| 真实论文、诚实精读 | ✅ | ✅ |
| 学术数据库 | 5 个（免 key） | 14+，含 Google Scholar 与中文源 |
| 文献库保存与历史 | — | ✅ |
| 据文献写作、自审稿 | — | ✅ Synthesis Lab + Paper Review |
| 精致的网页与移动端 | — | ✅ |

## 🐱 AcademiCats 技能家族

三个开源 skill，串起一条完整的研究工作流——按需安装其一或全部：

- 🔍 **论文检索** *（你在这里）* —— 找文献、读文献
- ✍️ [文献写作台](https://github.com/academicatstool-netizen/Cat_synthesis_lab) —— 用你的文献写出有据可查的成稿
- 🧪 [模拟同行评审](https://github.com/academicatstool-netizen/Cat_paper_review) —— 对你自己的草稿做同行评审

**一次装齐三个** —— clone 任意一个仓库后运行 `bash install.sh`。

## 🙋 常见问题

- **这些文件都是干嘛的？** 上面几种方式用其一即可——git clone（Claude Code）、`.skill` 文件（Claude 网页/桌面）、或 `PORTABLE_PROMPT.md`（ChatGPT/DeepSeek）。`SKILL.md`、`references/`、`scripts/` 是助手自动加载并运行的内部文件，无需手动打开。
- **没触发？** 安装后重启 Claude Code，并把话说成一个任务 —— *"找几篇关于…的最新论文"*。
- **某篇打不开？** 那是付费墙、没有免费副本——skill 会直说，而不是瞎编。换一篇，或直接粘 DOI / PDF 链接。
- **有时为什么不到 5 个库？** Semantic Scholar 对无 key 流量限流。脚本会自动重试，其余 4 个库照样兜底——或申请一个免费 [S2 API key](https://www.semanticscholar.org/product/api)，`export S2_API_KEY=...` 后就能稳定带上它。
- **用哪个模型？** 任何够强的模型都行——Claude Sonnet/Opus、GPT‑4o/o 系列、DeepSeek‑V3/R1 效果最好。
- **隐私 & 免费？** 全程跑在你自己的 AI 上——无需账号、不向我们回传任何东西，检索只访问公开学术 API。

<div align="center">
<br>

### 想要完整的研究工作流？
**→ [academicats.com](https://academicats.com) ←**

*🚀 正式版现处**公测阶段** —— 现在免费试用。*

<br>

由 [AcademiCats](https://academicats.com) 团队用 💙 打造 · [MIT 许可证](LICENSE)

</div>

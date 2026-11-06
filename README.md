# 知莹智能体（Zhying Agent）

一个**完全本地运行**的 AI 智能体：基于 [Ollama](https://ollama.com) + [LangChain](https://www.langchain.com) + [LangGraph](https://www.langchain.com/langgraph) + [Streamlit](https://streamlit.io)，拥有**长期记忆、自我反思、私有知识库（RAG）、联网搜索、文件操作**能力，全程不依赖任何云端 API，数据不出本机。

> 特性：无需任何 API Key，模型和数据都在你自己的电脑上，注重隐私与可控性。

---

## 一、功能特性

- 🤖 **ReAct 智能体**：基于 LangGraph 的 `create_react_agent`，自主选择工具完成任务，而非固定流程。
- 🔀 **双路检索（双路由）**：本地私有知识 + 联网搜索两条信息通道，按需路由——本地查不到就走网络，隐私与实时兼顾。
- 🧠 **长期记忆**：ChromaDB 向量库持久化记忆，跨会话记住你，支持记忆检索与自动写入。
- 📚 **私有知识库（RAG）**：上传 `.docx` 文档自动切分、向量化，回答时检索相关片段。
- 🔁 **自我反思**：每次回答后自动"自我审查"，给出修正后的最终答案。
- 🌐 **联网搜索 / 网页抓取**：DuckDuckGo 搜索 + BeautifulSoup 网页正文提取。
- 📝 **文件操作**：读写项目目录内文件、列出目录、执行 Python 代码（沙盒）。
- 🛡️ **安全加固**：路径越界拦截、禁止高危命令、文件操作限制在项目目录内。
- 🎨 **双入口 + 深色 Web 界面**：`app.py`（Streamlit 全功能 Web）+ `agent.py`（命令行轻量版）。

---

## 二、技术栈

| 层 | 技术 |
|---|---|
| Web 界面 | Streamlit |
| 大模型 | Ollama（本地推理） |
| 智能体框架 | LangGraph（ReAct Agent + SQLite 检查点） |
| 编排 | LangChain（ollama / chroma / community / text-splitters） |
| 向量数据库 | ChromaDB |
| 文档解析 | docx2txt |
| 搜索/抓取 | DuckDuckGo（ddgs）、requests、BeautifulSoup |

---

## 三、环境要求

- **操作系统**：Windows / macOS / Linux 均可。
- **Python**：3.11 及以上（开发环境为 3.12）。
- **内存**：建议 **8GB 以上**（7B 模型约需 4~6GB 内存；有 NVIDIA 显卡会更快，但不是必需）。
- **磁盘**：模型文件约 5~8GB（`qwen2.5:7b` 约 4.7GB + coder + embedding）。

---

## 四、安装步骤

### 第 1 步：安装 Ollama（本地模型服务）

这是最关键的一步，先把"模型引擎"装好：

1. 打开 <https://ollama.com/download> 下载对应系统的安装包。
2. 安装完成后，Ollama 会作为后台服务运行（默认端口 `11434`）。

验证是否安装成功：

```bash
ollama --version
```

### 第 2 步：下载所需模型

在命令行依次执行（会下载几个 GB，耐心等待）：

```bash
# 主脑：通用对话
ollama pull qwen2.5:7b

# 代码模型（app.py 中用于代码任务）
ollama pull qwen2.5-coder:7b

# 向量嵌入模型（知识库 / 记忆必需）
ollama pull nomic-embed-text
```

下载完成后可查看已安装模型：

```bash
ollama list
```

### 第 3 步：安装 Python 依赖

在项目根目录（本 `README.md` 同级目录）执行：

```bash
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 五、运行项目

### 方式 A：Web 界面（推荐，功能最全）

```bash
streamlit run app.py
```

浏览器会自动打开本地页面（默认 <http://localhost:8501>）。在左侧对话框输入指令，右侧可上传 `.docx` 文档到知识库。

### 方式 B：命令行交互（轻量版）

```bash
python agent.py
```

进入交互循环，输入 `exit` 退出。该入口提供：读取本地文件、联网搜索、网页抓取。

---

## 六、配置说明

| 环境变量 | 作用 | 默认值 |
|---|---|---|
| `ZHIYING_ROOT` | 智能体操作的工作目录（文件读写、代码执行都在这里） | 项目同级的 `project/`（自动创建） |
| `OLLAMA_MAX_LOADED_MODELS` | 显存优化：Ollama 同时驻留内存的模型数 | `1` |

> 正常情况下**无需任何配置**，开箱即用。所有路径都是基于脚本所在目录动态定位的，可以随意移动项目文件夹。

---

## 七、项目结构

```
my-agent-safe/
├── app.py              # 主程序：Streamlit Web 界面（完整版智能体）
├── agent.py            # 命令行入口（轻量版智能体）
├── requirements.txt    # Python 依赖清单
├── .gitignore          # Git 忽略规则
├── README.md           # 本文档（中文）
├── README_EN.md        # 英文文档
└── LICENSE             # MIT 开源协议

运行时自动生成（已被 .gitignore 忽略，请勿上传）：
├── project/            # 智能体工作目录（ZHIYING_ROOT）
├── chroma_db/          # 私有知识库向量数据
├── zhying_memory/      # 长期记忆向量数据
├── zhying_session.db   # 会话检查点（SQLite）
└── zhying_runtime.log  # 运行日志
```

---

## 八、工作原理与架构

### 核心组件一览

| 组件 | 用途 |
|---|---|
| `qwen2.5:7b` | 主脑：通用对话、推理、决策 |
| `qwen2.5-coder:7b` | 代码模型：代码相关任务 |
| `nomic-embed-text` | 向量嵌入：把文本转成向量，供检索使用 |
| `zhying_memory/` | 长期记忆库（ChromaDB） |
| `chroma_db/` | 私有知识库（ChromaDB） |
| `zhying_session.db` | 会话检查点（SQLite，LangGraph 使用） |

### 双路检索（双路由）

智能体获取信息有两条路，由 ReAct 决策中枢按需选择：

- **本地路由**：检索「长期记忆库 + 私有知识库」，处理隐私、离线、专有资料。
- **联网路由**：DuckDuckGo 搜索 + 网页抓取，处理实时、公开信息。

```
数据流示意：
  用户输入
     │
     ▼
 LangGraph ReAct 决策中枢（大脑）
     │
     ├─ 本地路由 ─► 长期记忆 + 知识库（RAG）
     ├─ 联网路由 ─► DuckDuckGo 搜索 + 网页抓取
     └─ 工具调用 ─► 文件读写 / 目录列表 / Python 沙盒
     │
     ▼
 Ollama 本地模型（qwen2.5:7b / qwen2.5-coder:7b）
     │
     ▼
 自我反思 → 最终回答 → 写入长期记忆
```

### 一次回答的完整流程

1. **输入**：用户在界面输入指令。
2. **检索**：Agent 从长期记忆库、私有知识库中检索相关信息。
3. **决策**：LangGraph 的 ReAct Agent 根据提示词决定调用哪个工具（文件操作 / 搜索 / 抓取 / 记忆检索 / 代码执行）。
4. **生成**：Ollama 本地模型生成初步回答。
5. **反思**：对初步回答进行"自我审查"，输出修正后的最终答案。
6. **记忆**：自动压缩本轮对话要点，写入长期记忆库。

---

## 九、安全说明

代码内置了以下安全约束：

- ✅ 所有文件操作**只能发生在 `ZHIYING_ROOT` 目录内**，越界会被拦截。
- ✅ 提示词层面**禁止 `rm` / `del` / `format` 等高危命令**。
- ✅ 自我迭代被限制在 `sandbox_test/` 或临时脚本内。
- ⚠️ `safe_python_execute` 目前是**弱隔离**（直接执行 Python 代码），仅建议**自用/受信任环境**运行，请勿对公网开放。

---

## 十、常见问题（FAQ）

**Q1：运行报 `ModuleNotFoundError`？**
确认已激活虚拟环境并执行了 `pip install -r requirements.txt`。若之前用旧版 `requirements.txt`（UTF-16 编码）报错，请用当前仓库的版本重新安装。

**Q2：提示 `ConnectionError` 或连不上 Ollama？**
Ollama 服务未启动。Windows 可在开始菜单启动 "Ollama"，或命令行执行 `ollama serve`。

**Q3：模型没下载会怎样？**
报 `model not found`。执行 `ollama pull qwen2.5:7b` 等命令补齐即可（见第四节）。

**Q4：上传 `.docx` 后知识库没反应？**
确认已下载 `nomic-embed-text` 嵌入模型，并查看页面提示与日志 `zhying_runtime.log`。

**Q5：电脑配置低，跑得慢？**
7B 模型对内存要求不高，但 CPU 推理会比 GPU 慢。可尝试换更小的模型（把 `app.py` 中的 `qwen2.5:7b` 改成 `qwen2.5:3b`）。

---

## 十一、许可

本项目采用 [MIT 协议](LICENSE) 开源。请同时遵守 Ollama、各开源模型及依赖库各自的许可证。

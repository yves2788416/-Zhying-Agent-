# ============================================================
# 知莹 app.py —— 安全/隐私修正版（用于上传 GitHub）
# 仅改动【安全修复】与【隐私脱敏】标注处，其余逻辑与原版一致
# ============================================================
import streamlit as st
import tempfile
import os
import sys
import subprocess
import time
import json
import logging
import sqlite3
import re
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.tools import DuckDuckGoSearchRun, tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver

# 显存优化
os.environ.setdefault("OLLAMA_MAX_LOADED_MODELS", "1")

# 【隐私脱敏】所有路径改为基于本文件所在目录动态定位，彻底去掉写死的本地用户名路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 可用环境变量 ZHIYING_ROOT 覆盖；默认取脚本同级的 project/ 子目录
ROOT_DIR = os.environ.get("ZHIYING_ROOT", os.path.join(BASE_DIR, "project"))
os.makedirs(ROOT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "zhying_runtime.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ZhyingAgent")
logger.info("知莹终极智能体系统启动。")

try:
    subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass

# ================= 1. 身份与核心法则 =================
# 【隐私脱敏 + 安全加固】去掉写死的绝对路径，改用 ROOT_DIR 变量动态注入；
# 增加禁止越出 ROOT_DIR 的硬约束，补上对路径穿越的防线。
EVOLUTION_MANUAL = f"""
你是知莹，一个拥有长期记忆和自我反思能力的终极AI助手。你的创造者是造物主。
【重要提示】你的项目根目录是 {ROOT_DIR}。
不要再去拼接多余的文件夹，直接在这个目录下操作。

【最高安全法则】
1. 严禁修改、删除 app.py。
2. 严禁使用 rm, del, format 等系统高危命令。
3. 所有文件操作只能在项目根目录之内，严禁读写根目录之外的任何路径。
4. 所有自我迭代必须在 sandbox_test/ 目录或以 .tmp.py 形式进行。
"""

# ================= 2. 核心大脑与知识库 =================
llm = ChatOllama(model="qwen2.5:7b", temperature=0.7, num_ctx=2048)
code_llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.0, num_ctx=2048)
embedding = OllamaEmbeddings(model="nomic-embed-text")

memory_db = Chroma(persist_directory=os.path.join(BASE_DIR, "zhying_memory"), embedding_function=embedding, collection_name="zhying_long_term_memory")
vectorstore = Chroma(persist_directory=os.path.join(BASE_DIR, "chroma_db"), embedding_function=embedding, collection_name="zhying_knowledge_base")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ================= 3. 真正的动手操作工具箱 =================
# 【安全修复】统一的路径越界校验：拼出来的真实路径必须落在 ROOT_DIR 之内，否则拒绝
def _safe_path(file_name: str) -> str:
    base = os.path.realpath(ROOT_DIR)
    p = os.path.realpath(os.path.join(base, file_name))
    if p != base and not p.startswith(base + os.sep):
        raise ValueError(f"越权访问被拦截：{file_name} 不在项目根目录内")
    return p

@tool
def write_file(file_name: str, content: str) -> str:
    """在项目的根目录直接写入或创建文件（例如：test.txt）。"""
    try:
        full_path = _safe_path(file_name)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"文件 '{file_name}' 已成功创建！"
    except Exception as e:
        return f"写入失败: {str(e)}"

@tool
def read_file(file_name: str) -> str:
    """读取项目根目录下的文件内容。"""
    try:
        full_path = _safe_path(file_name)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"读取失败: {str(e)}"

@tool
def list_directory() -> str:
    """列出项目根目录下的所有文件和文件夹。"""
    try:
        files = os.listdir(ROOT_DIR)
        if not files: return "根目录是空的。"
        return f"根目录内容: {', '.join(files)}"
    except Exception as e:
        return f"读取失败: {str(e)}"

@tool
def safe_python_execute(code: str) -> str:
    """用于运行 Python 代码脚本（沙盒环境，注意：当前为弱隔离，仅适合自用）。"""
    # 【安全修复】用当前解释器 sys.executable，避免误用系统裸 python；
    # 临时脚本固定在 ROOT_DIR 内并做越界校验。
    temp_file = _safe_path("temp_script.py")
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=10)
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)
    finally:
        if os.path.exists(temp_file): os.remove(temp_file)

@tool
def search_long_term_memory(query: str) -> str:
    """在长期记忆库中检索信息。"""
    results = memory_db.similarity_search(query, k=3)
    if not results: return "未找到相关记忆。"
    return "\n".join([doc.page_content for doc in results])

# ================= 4. 组装大脑 =================
all_tools = [
    write_file, read_file, list_directory, safe_python_execute, search_long_term_memory,
    retriever.as_tool(name="search_knowledge_base", description="查询本地私有知识库"),
    DuckDuckGoSearchRun(name="web_search", description="搜索互联网信息")
]

db_path = os.path.join(BASE_DIR, "zhying_session.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)
agent_executor = create_react_agent(llm, all_tools, prompt=EVOLUTION_MANUAL, checkpointer=memory)

# ================= 5. 记忆治理 & 6. 反思循环 =================
def summarize_for_memory(text, max_chars=200):
    prompt = f"将以下对话压缩为{max_chars}字内的要点，若无实际意义返回SKIP: {text}"
    res = llm.invoke(prompt).content.strip()
    return None if res.startswith("SKIP") else res

def run_self_reflection(prompt, initial_answer):
    reflection = f"你是知莹。审查你的回答是否完美解决了问题：'{initial_answer}'。若存在问题，请直接给出修正后的完美答案。"
    return llm.invoke(reflection).content

# ================= 7. Streamlit 界面 =================
st.set_page_config(page_title="知莹", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .stChatInput > div, .stFileUploader > div > div, .stAlert, .stSuccess {
        background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 12px !important;
    }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    .progress-container {
        background-color: #21262d; border-radius: 20px; height: 6px; width: 100%; overflow: hidden; margin-bottom: 15px;
    }
    .progress-bar {
        height: 100%; width: 0%; border-radius: 20px;
        background: linear-gradient(90deg, #1f6feb, #a371f7);
        transition: width 0.5s ease-in-out;
        box-shadow: 0 0 10px #1f6feb;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "rag_status" not in st.session_state: st.session_state.rag_status = "⚠️ 未加载任何文档"

# === 左侧对话区 ===
with st.container():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>🤖 知莹 | 终极智能体</h1>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("知莹，请执行你的任务..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            content_placeholder = st.empty()

            progress_placeholder.markdown('<div class="progress-container"><div class="progress-bar" style="width: 10%;"></div></div>', unsafe_allow_html=True)

            try:
                config = {"configurable": {"thread_id": "zhying_session"}}

                progress_placeholder.markdown('<div class="progress-container"><div class="progress-bar" style="width: 40%;"></div></div>', unsafe_allow_html=True)
                status_placeholder.info("🧠 正在激活海马体并连接知识库...")

                result = agent_executor.invoke({"messages": [{"role": "user", "content": prompt}]}, config=config)
                initial_answer = result["messages"][-1].content

                progress_placeholder.markdown('<div class="progress-container"><div class="progress-bar" style="width: 60%;"></div></div>', unsafe_allow_html=True)
                status_placeholder.markdown("🔄 **知莹正在进行自我审查与反思...**")

                final_answer = run_self_reflection(prompt, initial_answer)

                progress_placeholder.markdown('<div class="progress-container"><div class="progress-bar" style="width: 100%; background: #238636; box-shadow: 0 0 10px #238636;"></div></div>', unsafe_allow_html=True)
                time.sleep(0.5)
                progress_placeholder.empty()
                status_placeholder.empty()

                content_placeholder.markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})

                try:
                    combined_text = f"用户: {prompt[:120]} | 知莹: {final_answer[:240]}"
                    summary = summarize_for_memory(combined_text)
                    if summary and len(summary) > 4:
                        memory_db.add_texts([summary], metadatas=[{"timestamp": time.time(), "weight": 1.0}])
                except Exception:
                    pass

            except Exception as e:
                progress_placeholder.empty()
                status_placeholder.empty()
                content_placeholder.error(f"执行中断: {e}")

# === 右侧功能区 ===
with st.container():
    col_status, col_settings = st.columns([1, 1])
    with col_status:
        st.markdown("### 📚 知识库状态")
        bg_color = "#238636" if "已吸收" in st.session_state.rag_status else "#30363d"
        st.markdown(f'<div style="background: {bg_color}; color: white; padding: 12px; border-radius: 12px; text-align: center;">{st.session_state.rag_status}</div>', unsafe_allow_html=True)
    with col_settings:
        st.markdown("### 📂 上传私有文档 (.docx)")
        uploaded_file = st.file_uploader("支持 .docx 格式", type=["docx"], label_visibility="collapsed")
        if uploaded_file:
            if st.button("🚀 写入记忆库", use_container_width=True, type="primary"):
                logger.info(f"收到文档上传请求: {uploaded_file.name}")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                try:
                    loader = Docx2txtLoader(tmp_path)
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
                    chunks = splitter.split_documents(docs)
                    vectorstore.add_documents(chunks)
                    st.session_state.rag_status = "✅ 成功吸收：" + uploaded_file.name
                    st.success("🎉 写入成功，知莹已掌握新资料！")
                except Exception as e:
                    st.error(f"写入失败: {e}")
                finally:
                    os.remove(tmp_path)

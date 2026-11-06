from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ================= 1. 定义“手脚”（使用标准英文命名，让模型秒懂） =================

@tool
def read_local_file(file_path: str) -> str:
    """读取本地文本文件（txt/md/csv/py等）的内容。当用户要求读取、打开、查看某个文件时调用此工具。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取失败，原因: {str(e)}"

@tool
def web_search(query: str) -> str:
    """在互联网上搜索实时信息、新闻或答案。"""
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=3)
        if not results:
            return "未搜索到相关结果。"
        out = ""
        for r in results:
            out += f"标题: {r['title']}\n链接: {r['href']}\n摘要: {r['body']}\n\n"
        return out
    except Exception as e:
        return f"搜索暂时不可用（网络原因）：{str(e)}"

@tool
def web_grab(url: str) -> str:
    """抓取并提取指定网页（URL）的正文文字内容。"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for s in soup(["script", "style"]):
            s.decompose()
        return soup.get_text(separator=" ", strip=True)[:2000]
    except Exception as e:
        return f"抓取失败，原因: {str(e)}"

# ================= 2. 组装大脑与框架 =================
llm = ChatOllama(model="qwen2.5:7b", base_url="http://127.0.0.1:11434")
# 传入定义好的工具列表
tools = [read_local_file, web_search, web_grab]
agent = create_react_agent(llm, tools)

# ================= 3. 启动交互循环 =================
print("=== 🚀 终极智能体已上线！（支持读取/搜索/抓取） ===\n")
while True:
    prompt = input("你：")
    if prompt.lower() == "exit":
        print("智能体：下次见！")
        break
    try:
        response = agent.invoke({"messages": prompt})
        print(f"\n🤖 智能体：{response['messages'][-1].content}\n")
    except Exception as e:
        print(f"\n⚠️ 本轮出错了，但程序不会退出：{str(e)}\n")

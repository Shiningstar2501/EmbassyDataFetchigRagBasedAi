# import gradio as gr
# import pandas as pd
# import asyncio
# import time
# import os
# from urllib.parse import urljoin
# from playwright.async_api import async_playwright
# from langchain_community.llms import Ollama
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import FAISS
# from langchain.embeddings import HuggingFaceEmbeddings

# llm = Ollama(model="mistral")
# qa_prompt = PromptTemplate(
#     input_variables=["text", "question"],
#     template="""
# You are an expert at reading embassy websites.

# Use the content below to answer the question.

# CONTENT:
# {text}

# QUESTION:
# {question}

# ANSWER:
# """
# )

# async def crawl_all_pages_and_collect_text(url):
#     all_pages_data = []
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         await page.goto(url, timeout=60000)

#         try:
#             homePage = await page.inner_text('body')
#             all_pages_data.append(('Homepage', url, homePage))
#         except:
#             all_pages_data.append(('Homepage', url, "Could not find homepage"))

#         link_elements = await page.query_selector_all("nav a , header a")
#         navbar_links = []
#         for elem in link_elements:
#             href = await elem.get_attribute("href")
#             if href and not href.startswith("javascript"):
#                 full_url = urljoin(url, href)
#                 navbar_links.append(full_url)
#         navbar_links = list(set(navbar_links))

#         for link in navbar_links:
#             try:
#                 await page.goto(link, timeout=90000)
#                 time.sleep(1)
#                 text = await page.inner_text('body')
#                 all_pages_data.append(("NavbarPage", link, text))
#             except Exception as e:
#                 all_pages_data.append(("NavbarPage", link, f"Failed to read: {e}"))

#         await browser.close()
#         return all_pages_data

# def split_text_into_chunks(pages_data, chunk_size=500, chunk_overlap=50):
#     all_text = "\n\n".join([text for _, _, text in pages_data])
#     splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#     return splitter.split_text(all_text)

# def embed_and_store_chunks(chunks):
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     return FAISS.from_texts(chunks, embedding=embeddings)

# def retrieve_relevant_chunks(vectorstore, question, k=70):
#     return vectorstore.similarity_search(question, k=k)

# def ask_llm_about_embassy(llm, retrieved_chunks, question):
#     combined_text = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
#     chain = LLMChain(llm=llm, prompt=qa_prompt)
#     result = chain.invoke({"text": combined_text, "question": question})
#     return result["text"]

# # CHATBOT-style logic
# chat_history = []

# def chatbot_logic(message, file=None):
#     if not file:
#         return "📎 Please upload an Excel file containing embassy URLs.", None

#     df = pd.read_excel(file.name)
#     urls = df["URL"].dropna().unique().tolist()
#     output_data = []

#     for i, url in enumerate(urls):
#         chat_history.append(f"🌐 Crawling {url}...")
#         all_pages_data = asyncio.run(crawl_all_pages_and_collect_text(url))

#         chat_history.append("🔍 Splitting and embedding content...")
#         chunks = split_text_into_chunks(all_pages_data)
#         vectorstore = embed_and_store_chunks(chunks)

#         question = "What is the physical address, telephone number, email ID, and office hours of this embassy?"
#         retrieved_chunks = retrieve_relevant_chunks(vectorstore, question)
#         answer = ask_llm_about_embassy(llm, retrieved_chunks, question)

#         output_data.append({
#             "URL": url,
#             "Extracted_Info": answer
#         })
#         chat_history.append(f"✅ Data extracted for {url}")

#     result_df = pd.DataFrame(output_data)
#     output_path = "chatbot_output.xlsx"
#     result_df.to_excel(output_path, index=False)

#     return "📄 Extraction complete! Click below to download your file.", output_path

# with gr.Blocks() as demo:
#     chatbot = gr.ChatInterface(
#         fn=chatbot_logic,
#         additional_inputs=[gr.File(label="Upload Excel File")],
#         title="📬 Embassy Info Chatbot",
#         description="Chatbot that extracts address, phone, email & office hours from embassy URLs in Excel.",
#         theme="soft",
#     )

# demo.launch()

import subprocess
subprocess.run(["playwright", "install", "--with-deps"], check=True)
import nest_asyncio
import gradio as gr
import pandas as pd
import asyncio
import time
import os
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

nest_asyncio.apply()

llm = Ollama(model="mistral")

qa_prompt = PromptTemplate(
    input_variables=["text", "question"],
    template="""
You are an expert at reading embassy websites.

Use the content below to answer the question.

CONTENT:
{text}

QUESTION:
{question}

ANSWER:
"""
)

async def crawl_all_pages_and_collect_text(url):
    all_pages_data = []
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=True) because the website i am working on is not accessible while it is in headless mode that is why i am using the headful mode else it can work in the headless mode also 
        browser = await p.chromium.launch(headless=False)

        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        try:
            homePage = await page.inner_text('body')
            all_pages_data.append(('Homepage', url, homePage))
        except:
            all_pages_data.append(('Homepage', url, "Could not find homepage"))

        link_elements = await page.query_selector_all("nav a , header a")
        navbar_links = []
        for elem in link_elements:
            href = await elem.get_attribute("href")
            if href and not href.startswith("javascript"):
                full_url = urljoin(url, href)
                navbar_links.append(full_url)
        navbar_links = list(set(navbar_links))

        for link in navbar_links:
            try:
                await page.goto(link, timeout=90000)
                time.sleep(1)
                text = await page.inner_text('body')
                all_pages_data.append(("NavbarPage", link, text))
            except Exception as e:
                all_pages_data.append(("NavbarPage", link, f"Failed to read: {e}"))

        await browser.close()
        return all_pages_data

def split_text_into_chunks(pages_data, chunk_size=500, chunk_overlap=50):
    all_text = "\n\n".join([text for _, _, text in pages_data])
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(all_text)

def embed_and_store_chunks(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_texts(chunks, embedding=embeddings)

def retrieve_relevant_chunks(vectorstore, question, k=70):
    return vectorstore.similarity_search(question, k=k)

def ask_llm_about_embassy(llm, retrieved_chunks, question):
    combined_text = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
    chain = LLMChain(llm=llm, prompt=qa_prompt)
    result = chain.invoke({"text": combined_text, "question": question})
    return result["text"]

def process_file(file):
    messages = ""
    df = pd.read_excel(file.name)
    urls = df["URL"].dropna().unique().tolist()
    output_data = []

    for i, url in enumerate(urls):
        messages += f"\n🌐 Crawling: {url}"
        all_pages_data = asyncio.run(crawl_all_pages_and_collect_text(url))

        messages += "\n📚 Splitting and embedding text..."
        chunks = split_text_into_chunks(all_pages_data)
        vectorstore = embed_and_store_chunks(chunks)

        question = "What is the physical address, telephone number, email ID, and office hours of this embassy?"
        retrieved_chunks = retrieve_relevant_chunks(vectorstore, question)
        answer = ask_llm_about_embassy(llm, retrieved_chunks, question)

        output_data.append({"URL": url, "Extracted_Info": answer})
        messages += "\n✅ Data extracted for this URL."

    result_df = pd.DataFrame(output_data)
    output_path = "chatbot_output.xlsx"
    result_df.to_excel(output_path, index=False)

    messages += "\n\n📥 All done! Download the result below."
    return messages, output_path

# Gradio interface with Blocks (chat-style layout)
with gr.Blocks(theme="soft") as demo:
    gr.Markdown("### 🤖 Embassy Info Chatbot\nUpload an Excel file and extract address, phone, email, and office hours.")
    file_input = gr.File(label="📁 Upload Excel File with Embassy URLs")
    run_button = gr.Button("🚀 Start Extraction")
    chat_output = gr.Textbox(label="Chatbot Messages", lines=20, interactive=False)
    file_download = gr.File(label="📄 Download Result Excel")

    def run_bot(file):
        if file is None:
            return "⚠️ Please upload a file before starting.", None
        return process_file(file)

    run_button.click(fn=run_bot, inputs=file_input, outputs=[chat_output, file_download])

demo.launch(server_name="0.0.0.0", server_port=7860)

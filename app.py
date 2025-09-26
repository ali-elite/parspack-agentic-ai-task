import os
import asyncio
from dotenv import load_dotenv
import streamlit as st
from agents import Runner

from my_agents.orchestrator_agent import orchestrator_agent
from utils.db import HOTEL_ROOMS, RESTAURANT_MENU

load_dotenv()

st.set_page_config(layout="wide")

st.title("سامانه مدیریت هتل")
st.caption("گفتگو با ارکستراتور برای رزرو اتاق و سفارش غذا")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    st.header("نمونه درخواست‌ها")
    examples = [
        "یک اتاق دو نفره برای سه شب و یک اتاق یک نفره برای یک شب می‌خواستم.",
        "برای فردا شب یک اتاق یک نفره رزرو کنید. برای شام هم یک پیتزا نصف پپرونی و نصف سبزیجات و یک نوشابه می‌خواستم.",
        "۱۰ پرس کباب کوبیده و ۵ پرس جوجه زعفرانی برای ناهار فردا رزرو کنید. همچنین یک میز برای ۵ نفر می‌خواهم.",
        "برای یک هفته اتاق سه نفره نیاز دارم. غذا هم سه وعده در روز می‌خواهم.",
    ]
    for i, ex in enumerate(examples):
        if st.button(f"مثال {i+1}"):
            st.session_state["prefill"] = ex
            st.rerun()

    if st.button("شروع گفتگوی جدید"):
        st.session_state["messages"] = []
        st.session_state.pop("prefill", None)
        st.rerun()

    with st.expander("وضعیت اولیه اتاق‌ها"):
        for room in HOTEL_ROOMS:
            st.write(f"- {room['id']} ({room['type']}): {'Available' if room['available'] else 'Booked'}")

    with st.expander("منوی رستوران"):
        for item in RESTAURANT_MENU:
            st.write(f"- {item['name']}: {'Available' if item['available'] else 'Not Available'}")

if not os.getenv("OPENAI_API_KEY"):
    st.error("لطفاً مقدار OPENAI_API_KEY را در فایل .env یا تنظیمات سیستم قرار دهید.")

for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

def run_agent_sync(prompt: str) -> str:
    async def _run() -> str:
        return await Runner.run(orchestrator_agent, prompt)
    return asyncio.run(_run())

prefill = st.session_state.get("prefill", "یک اتاق دو نفره برای سه شب می‌خواستم.")
user_prompt = st.chat_input("پیام خود را بنویسید…", key="chat_input")

if user_prompt is None and "prefill" in st.session_state:
    # Submit prefill example once
    user_prompt = st.session_state.pop("prefill")

if user_prompt:
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("در حال پردازش…"):
            try:
                response_text = run_agent_sync(user_prompt)
            except Exception as e:
                response_text = f"خطا در اجرای عامل: {e}"
            st.markdown(response_text)
    st.session_state["messages"].append({"role": "assistant", "content": response_text})

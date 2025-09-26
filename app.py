import os
import asyncio
import logging
import io
from contextlib import redirect_stderr, redirect_stdout
from dotenv import load_dotenv
import streamlit as st
from agents import Runner

from my_agents.orchestrator_agent import orchestrator_agent
from utils.db import HOTEL_ROOMS, RESTAURANT_MENU

load_dotenv()

st.set_page_config(
    page_title="سامانه مدیریت هتل",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for logs and display options
if "agent_logs" not in st.session_state:
    st.session_state["agent_logs"] = []

# Initialize session state for RunResult display mode
if "show_full_runresult" not in st.session_state:
    st.session_state["show_full_runresult"] = False

# Create main layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    st.title("سامانه مدیریت هتل")
    st.caption("گفتگو برای رزرو اتاق و سفارش غذا")

with col2:
    st.header("📊 وضعیت فعلی سیستم")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    st.header("ابزارها و تنظیمات")

    if st.button("🔄 شروع گفتگوی جدید", type="primary"):
        st.session_state["messages"] = []
        st.session_state["agent_logs"] = []
        st.session_state.pop("prefill", None)
        st.rerun()

    # Response display options
    st.divider()
    st.subheader(" تنظیمات نمایش")

# Add database status to the right column
with col2:
    # Room status with colors
    with st.expander("🏨 وضعیت اتاق‌ها", expanded=True):
        for room in HOTEL_ROOMS:
            room_type_fa = {
                'single': 'یک نفره',
                'double': 'دو نفره', 
                'triple': 'سه نفره'
            }.get(room['type'], room['type'])
            
            if room['available']:
                st.markdown(f"🟢 **{room['id']}** ({room_type_fa}) - ✅ آزاد - {room['price_per_night']}$ شبانه")
            else:
                st.markdown(f"🔴 **{room['id']}** ({room_type_fa}) - ❌ رزرو شده")

    # Menu status with colors
    with st.expander("🍽️ وضعیت منوی رستوران", expanded=True):
        for item in RESTAURANT_MENU:
            if item['available']:
                st.markdown(f"🟢 **{item['name']}** - ✅ موجود - {item['price']}$")
            else:
                st.markdown(f"🔴 **{item['name']}** - ❌ ناموجود")

if not os.getenv("OPENAI_API_KEY"):
    st.error("لطفاً مقدار OPENAI_API_KEY را در فایل .env یا تنظیمات سیستم قرار دهید.")

# Display chat messages in the left column
with col1:
    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

def run_agent_sync(prompt: str, conversation_history: list = None):
    """Run the orchestrator agent and capture logs."""
    async def _run():
        # Construct context with conversation history
        if conversation_history and len(conversation_history) > 1:
            context_parts = ["تاریخچه گفتگو:\n"]
            for i, msg in enumerate(conversation_history[:-1]):  # Exclude the current message
                role = "کاربر" if msg["role"] == "user" else "دستیار"
                context_parts.append(f"{role}: {msg['content']}")
            
            context_parts.append(f"\nپیام جدید کاربر: {prompt}")
            full_context = "\n".join(context_parts)
        else:
            full_context = prompt
            
        # Log the start of processing
        st.session_state["agent_logs"].append(f"شروع پردازش درخواست: {prompt[:50]}...")
        
        try:
            # Capture stdout/stderr during agent execution
            log_capture_string = io.StringIO()
            with redirect_stdout(log_capture_string), redirect_stderr(log_capture_string):
                result = await Runner.run(orchestrator_agent, full_context)
            
            # Capture any logs from the execution
            captured_logs = log_capture_string.getvalue()
            if captured_logs.strip():
                st.session_state["agent_logs"].append(f"جزئیات اجرا: {captured_logs.strip()}")
                
            st.session_state["agent_logs"].append("✅ پردازش با موفقیت تکمیل شد")
                        
            return result
            
        except Exception as e:
            error_msg = f"❌ خطا در پردازش: {str(e)}"
            st.session_state["agent_logs"].append(error_msg)
            raise e
    
    return asyncio.run(_run())

# Chat interface in the left column
with col1:
    prefill = st.session_state.get("prefill", "یک اتاق دو نفره برای سه شب می‌خواستم.")
    user_prompt = st.chat_input("پیام خود را بنویسید…", key="chat_input")

    if user_prompt is None and "prefill" in st.session_state:
        user_prompt = st.session_state.pop("prefill")

    if user_prompt:
        response_text = ""
        st.session_state["messages"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("... در حال پردازش"):
                try:
                    # Pass conversation history to maintain context
                    result = run_agent_sync(user_prompt, st.session_state["messages"])
                    response_text = str(result.final_output).strip()
                    st.markdown(response_text)
                        
                except Exception as e:
                    response_text = f"⚠️ متاسفانه خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره تلاش کنید.\n\n📝 جزئیات خطا: {str(e)}"
                    st.markdown(response_text)
            
        # Store the response in session state
        st.session_state["messages"].append({"role": "assistant", "content": response_text})

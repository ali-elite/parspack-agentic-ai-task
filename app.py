import os
import asyncio
import logging
import io
from contextlib import redirect_stderr, redirect_stdout
from dotenv import load_dotenv
import streamlit as st
from agents import Runner

from my_agents.orchestrator_agent import orchestrator_agent
from utils.db import HOTEL_ROOMS, RESTAURANT_MENU, WEEKLY_MEAL_PROGRAM, FOOD_RESERVATIONS, RESTAURANT_TABLES, TABLE_RESERVATIONS
from datetime import datetime, timedelta

load_dotenv()

st.set_page_config(
    page_title="سامانه مدیریت هتل",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1f4e79, #2c5f86);
    color: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.status-panel {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
}

.status-available {
    background: #d4edda;
    border-left: 4px solid #28a745;
    padding: 12px;
    margin: 8px 0;
    border-radius: 4px;
}

.status-occupied {
    background: #f8d7da;
    border-left: 4px solid #dc3545;
    padding: 12px;
    margin: 8px 0;
    border-radius: 4px;
}

.status-warning {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 12px;
    margin: 8px 0;
    border-radius: 4px;
}

.status-unavailable {
    background: #f8d7da;
    border-left: 4px solid #dc3545;
    padding: 12px;
    margin: 8px 0;
    border-radius: 4px;
    opacity: 0.7;
}

.room-card {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 10px;
    margin: 5px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.room-number {
    font-weight: bold;
    font-size: 16px;
    color: #1f4e79;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.indicator-available {
    background-color: #28a745;
}

.indicator-occupied {
    background-color: #dc3545;
}

.indicator-warning {
    background-color: #ffc107;
}

.system-metrics {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.metric-card {
    background: white;
    padding: 15px;
    border-radius: 6px;
    border: 1px solid #dee2e6;
    text-align: center;
    flex: 1;
    margin: 0 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #1f4e79;
}

.metric-label {
    color: #6c757d;
    font-size: 12px;
    margin-top: 5px;
}

.sidebar .stButton > button {
    width: 100%;
    background-color: #1f4e79;
    color: white;
    border-radius: 6px;
    border: none;
    padding: 8px 16px;
    margin: 4px 0;
}

.chat-container {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    min-height: 500px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "agent_logs" not in st.session_state:
    st.session_state["agent_logs"] = []

# Main header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 28px;">سامانه مدیریت هتل</h1>
    <p style="margin: 5px 0 0 0; opacity: 0.9;">پلتفرم یکپارچه مدیریت رزرو اتاق و خدمات رستوران</p>
</div>
""", unsafe_allow_html=True)

# System metrics
total_rooms = len(HOTEL_ROOMS)
available_rooms = len([r for r in HOTEL_ROOMS if r['available']])
occupied_rooms = total_rooms - available_rooms
total_menu_items = len(RESTAURANT_MENU)
available_menu_items = len([i for i in RESTAURANT_MENU if i['available']])
out_of_stock_items = total_menu_items - available_menu_items
total_tables = len(RESTAURANT_TABLES)
available_tables = len([t for t in RESTAURANT_TABLES if t['available']])
reserved_tables = total_tables - available_tables

st.markdown(f"""
<div class="system-metrics">
    <div class="metric-card">
        <div class="metric-value">{available_rooms}</div>
        <div class="metric-label">اتاق آزاد</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{occupied_rooms}</div>
        <div class="metric-label">اتاق اشغال</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{available_tables}</div>
        <div class="metric-label">میز آزاد</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{available_menu_items}</div>
        <div class="metric-label">غذا موجود</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create main layout with columns
col1, col2 = st.columns([2.5, 1.5])

with st.sidebar:
    st.header("کنترل پنل مدیریت")
    
    # System status summary
    st.subheader("خلاصه وضعیت")
    st.metric("کل اتاق‌ها", total_rooms, delta=None)
    st.metric("اتاق‌های آزاد", available_rooms, delta=None)
    st.metric("کل میزها", total_tables, delta=None)
    st.metric("میزهای آزاد", available_tables, delta=None)
    st.metric("غذاهای موجود", available_menu_items, delta=None)
    
    st.divider()
    
    # Action buttons
    st.subheader("عملیات سیستم")
    
    if st.button("شروع گفتگوی جدید", type="primary"):
        st.session_state["messages"] = []
        st.session_state["agent_logs"] = []
        st.session_state.pop("prefill", None)
        st.rerun()
    
    if st.button("تازه‌سازی وضعیت"):
        st.rerun()
    
    st.divider()
    
    # Display settings
    st.subheader("تنظیمات نمایش")
    show_occupied = st.checkbox("نمایش اتاق‌های اشغال", value=True)
    show_out_of_stock = st.checkbox("نمایش غذاهای ناموجود", value=True)
    show_weekly_program = st.checkbox("نمایش برنامه هفتگی", value=False)
    
    st.divider()
    
    # Meal program info
    st.subheader("اطلاعات برنامه غذایی")
    st.info("غذاهای فارسی در روزهای خاص هفته موجودند")
    
    
    # Show quick weekly overview
    if show_weekly_program:
        st.markdown("**خلاصه برنامه هفته:**")
        days_fa = {
            'monday': 'دوشنبه', 'tuesday': 'سه‌شنبه', 'wednesday': 'چهارشنبه',
            'thursday': 'پنج‌شنبه', 'friday': 'جمعه', 'saturday': 'شنبه', 'sunday': 'یکشنبه'
        }
        
        for day, meals in WEEKLY_MEAL_PROGRAM.items():
            day_fa = days_fa.get(day, day)
            dinner_name = meals['dinner']['name']
            st.markdown(f"**{day_fa}**: {dinner_name}")
    
    st.divider()
    
    # Food reservations info
    if FOOD_RESERVATIONS:
        st.subheader("رزروهای غذا")
        recent_reservations = sorted(FOOD_RESERVATIONS, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
        for res in recent_reservations:
            st.markdown(f"• {res.get('food_item', 'N/A')} - {res.get('scheduled_date', 'N/A')}")
    
    # Table reservations info
    if TABLE_RESERVATIONS:
        st.subheader("رزروهای میز")
        recent_table_reservations = sorted(TABLE_RESERVATIONS, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
        for res in recent_table_reservations:
            party_size = res.get('party_size', 'N/A')
            table_num = res.get('table_number', 'N/A')
            date_time = f"{res.get('reserved_date', 'N/A')} {res.get('reserved_time', 'N/A')}"
            st.markdown(f"• میز {table_num} ({party_size} نفر) - {date_time}")
    
    st.divider()

# Status monitoring panel
with col2:
    st.subheader("مانیتورینگ سیستم")
    
    # Room status panel
    with st.container():
        st.markdown("**وضعیت اتاق‌ها**")
        
        room_html = ""
        for room in HOTEL_ROOMS:
            if not room['available'] and not show_occupied:
                continue
                
            room_type_fa = {
                'single': 'یک نفره',
                'double': 'دو نفره', 
                'triple': 'سه نفره'
            }.get(room['type'], room['type'])
            
            if room['available']:
                status_class = "status-available"
                indicator_class = "indicator-available"
                status_text = "آزاد"
            else:
                status_class = "status-occupied"
                indicator_class = "indicator-occupied"
                status_text = "اشغال"
            
            room_html += f"""
            <div class="{status_class}">
                <span class="status-indicator {indicator_class}"></span>
                <span class="room-number">اتاق {room['number']}</span>
                <br>
                <small>طبقه {room['floor']} • {room_type_fa} • {room['price_per_night']:,} تومان • {status_text}</small>
            </div>
            """
        
        st.markdown(room_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Restaurant menu status panel
    with st.container():
        st.markdown("**وضعیت منوی رستوران**")
        
        menu_html = ""
        for item in RESTAURANT_MENU:
            if not item['available'] and not show_out_of_stock:
                continue
                
            if item['available'] and item['quantity'] > 0:
                if item['quantity'] <= 5:
                    status_class = "status-warning"
                    indicator_class = "indicator-warning"
                    status_text = f"موجود ({item['quantity']} باقیمانده)"
                else:
                    status_class = "status-available"
                    indicator_class = "indicator-available"
                    status_text = f"موجود ({item['quantity']} عدد)"
            else:
                status_class = "status-unavailable"
                indicator_class = "indicator-occupied"
                status_text = "تمام شده"
            
            # Check if item is customizable and show defaults
            customizable_text = ""
            if item.get('customizable', False):
                defaults = item.get('defaults', {})
                if defaults:
                    default_options = [list(defaults.values())[0]] if defaults else []
                    default_text = f" (پیش‌فرض: {', '.join(default_options[:2])})" if default_options else ""
                    customizable_text = f" • قابل سفارشی‌سازی{default_text}"
                else:
                    customizable_text = " • قابل سفارشی‌سازی"
            
            menu_html += f"""
            <div class="{status_class}">
                <span class="status-indicator {indicator_class}"></span>
                <strong>{item['name']}</strong>
                <br>
                <small>{item['price']:,} تومان • {status_text}{customizable_text}</small>
            </div>
            """
        
        st.markdown(menu_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Restaurant tables status panel
    with st.container():
        st.markdown("**وضعیت میزهای رستوران**")
        
        table_html = ""
        for table in RESTAURANT_TABLES:
            if table['available']:
                status_class = "status-available"
                indicator_class = "indicator-available"
                status_text = "آزاد"
                extra_info = f"ظرفیت {table['capacity']} نفر"
            else:
                status_class = "status-occupied"
                indicator_class = "indicator-occupied"
                status_text = "رزرو شده"
                extra_info = f"رزرو برای {table.get('reserved_by', 'نامشخص')}"
            
            location_fa = {
                'window': 'کنار پنجره',
                'center': 'وسط سالن',
                'corner': 'گوشه',
                'private': 'خصوصی',
                'family_area': 'منطقه خانوادگی',
                'private_room': 'اتاق خصوصی',
                'banquet_area': 'سالن مهمانی'
            }.get(table['location'], table['location'])
            
            table_html += f"""
            <div class="{status_class}">
                <span class="status-indicator {indicator_class}"></span>
                <span class="room-number">میز {table['table_number']}</span>
                <br>
                <small>{location_fa} • ظرفیت {table['capacity']} نفر • {status_text}</small>
                <br>
                <small>{extra_info}</small>
            </div>
            """
        
        st.markdown(table_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Weekly meal program display
    with st.container():
        st.markdown("**برنامه غذایی این هفته**")
        
        # Get current date info
        today = datetime.now()
        current_day = today.strftime("%A").lower()
        
        # Show today's meal of the day first
        if current_day in WEEKLY_MEAL_PROGRAM:
            today_meals = WEEKLY_MEAL_PROGRAM[current_day]
            
            st.markdown("**غذای امروز:**")
            for meal_type, meal_info in today_meals.items():
                meal_type_fa = {
                    'breakfast': 'صبحانه',
                    'lunch': 'ناهار', 
                    'dinner': 'شام'
                }.get(meal_type, meal_type)
                
                # Find the menu item for pricing
                menu_item = next((item for item in RESTAURANT_MENU if item['name'] == meal_info['name']), None)
                price_text = f" - {menu_item['price']}$" if menu_item else ""
                availability = "موجود" if menu_item and menu_item['available'] else "ناموجود"
                
                st.markdown(f"""
                <div class="status-available" style="margin: 4px 0; padding: 8px;">
                    <strong>{meal_type_fa}: {meal_info['name']}</strong>{price_text}
                    <br><small>{meal_info['description']} • {availability}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Show reservations count
        total_reservations = len(FOOD_RESERVATIONS)
        if total_reservations > 0:
            today_reservations = len([r for r in FOOD_RESERVATIONS if r.get('scheduled_date') == today.strftime('%Y-%m-%d')])
            st.markdown(f"""
            <div class="status-panel" style="margin-top: 10px; padding: 10px;">
                <small>رزروهای غذا: {total_reservations} کل • {today_reservations} امروز</small>
            </div>
            """, unsafe_allow_html=True)

if not os.getenv("OPENAI_API_KEY"):
    st.error("لطفاً مقدار OPENAI_API_KEY را در فایل .env یا تنظیمات سیستم قرار دهید.")

# Chat interface in the left column
with col1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state["messages"]:
        st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 40px;">
            <h4>خوش آمدید به سامانه مدیریت هتل</h4>
            <p>برای شروع، درخواست خود را در قسمت پایین وارد کنید</p>
            <p>مثال: "یک اتاق دو نفره برای سه شب می‌خواهم"</p>
        </div>
        """, unsafe_allow_html=True)
    
    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)

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
                
            st.session_state["agent_logs"].append("پردازش با موفقیت تکمیل شد")
                        
            return result
            
        except Exception as e:
            error_msg = f"خطا در پردازش: {str(e)}"
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
                    response_text = f"متاسفانه خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره تلاش کنید.\n\nجزئیات خطا: {str(e)}"
                    st.error(response_text)
            
        # Store the response in session state
        st.session_state["messages"].append({"role": "assistant", "content": response_text})

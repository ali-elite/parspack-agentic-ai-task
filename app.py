import streamlit as st
import requests
import json

st.set_page_config(layout="wide")

st.title("سامانه مدیریت هتل")
st.write("با استفاده از این سامانه می‌توانید اتاق و غذا رزرو کنید.")

user_input = st.text_input("درخواست خود را وارد کنید:", "یک اتاق دو نفره برای سه شب می‌خواستم.")

if st.button("ارسال"):
    if user_input:
        with st.spinner("در حال پردازش درخواست شما..."):
            try:
                response = requests.post("http://127.0.0.1:8000/invoke", json={"message": user_input})
                response.raise_for_status()  # Raise an exception for bad status codes
                
                # The response from the backend is now expected to be a JSON object
                # with a "response" key, which in turn contains the agent's output.
                result = response.json()
                
                # We expect the 'response' key to be in the JSON from the backend
                if "response" in result and "output" in result["response"]:
                    st.success("پاسخ دریافت شد:")
                    st.write(result["response"]["output"])
                else:
                    st.error("پاسخ دریافت شده از سرور در فرمت مورد انتظار نیست.")
                    st.json(result)

            except requests.exceptions.RequestException as e:
                st.error(f"خطا در برقراری ارتباط با سرور: {e}")
            except json.JSONDecodeError:
                st.error("پاسخ دریافت شده از سرور در فرمت JSON معتبر نیست.")
                st.text(response.text)
            except Exception as e:
                st.error(f"خطای غیرمنتظره: {e}")

st.sidebar.title("مثال‌هایی برای تست")
st.sidebar.markdown("""
- "یک اتاق دو نفره برای سه شب و یک اتاق یک نفره برای یک شب می‌خواستم."
- "برای فردا شب یک اتاق یک نفره رزرو کنید. برای شام هم یک پیتزا نصف پپرونی و نصف سبزیجات و یک نوشابه می‌خواستم."
- "۱۰ پرس کباب کوبیده و ۵ پرس جوجه زعفرانی برای ناهار فردا رزرو کنید. همچنین یک میز برای ۵ نفر می‌خواهم."
- "برای یک هفته اتاق سه نفره نیاز دارم. غذا هم سه وعده در روز می‌خواهم."
""")

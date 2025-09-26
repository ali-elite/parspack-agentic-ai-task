Multi-Agent Hotel Management System
This project implements a multi-agent system for managing hotel room and restaurant bookings using LangGraph, FastAPI, and Streamlit.

Project Structure
hotel_management_system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── agents.py
│   │   ├── tools.py
│   │   ├── models.py
│   │   └── config.py
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
└── README.md

Setup and Installation
1. Create a Virtual Environment
It's recommended to use a virtual environment. This project is tested with Python 3.12.

python3.12 -m venv venv
source venv/bin/activate

2. Backend Setup
Navigate to the backend directory and install the required packages.

cd backend
pip install -r requirements.txt

Create a .env file in the backend/app directory and add your OpenAI API key:

OPENAI_API_KEY="your_openai_api_key_here"

3. Frontend Setup
Navigate to the frontend directory and install the required packages.

cd ../frontend
pip install -r requirements.txt

Running the Application
1. Start the Backend Server
In the backend directory, run the FastAPI server using Uvicorn.

cd ../backend
uvicorn app.main:app --reload

The backend server will be running at http://127.0.0.1:8000.

2. Start the Frontend Application
In a new terminal, navigate to the frontend directory and run the Streamlit app.

cd ../frontend
streamlit run app.py

The Streamlit frontend will be available at http://localhost:8501.

How to Use
Open your browser and navigate to http://localhost:8501.

Enter your request in the text box (in Persian).

Click the "ارسال" (Send) button.

The system will process your request and display the result.

You can use the example prompts in the sidebar to test the system.
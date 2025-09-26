# Multi-Agent Hotel Management System

This project implements a multi-agent system for managing hotel bookings, including room reservations and restaurant orders, using the OpenAI Agents SDK.

## Project Structure

- `main.py`: The entry point for the application.
- `agents/`: Contains the definitions for the different agents (Orchestrator, Room, Restaurant, Manager).
- `tools/`: Implements the tools that agents use to interact with simulated hotel data (e.g., booking rooms, ordering food).
- `utils/`: Includes helper functions and simulated database initialization.
- `requirements.txt`: Lists the project dependencies.
- `.env`: For storing the OpenAI API key.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    Create a `.env` file in the root of the project and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your_openai_api_key"
    ```

## Running the Application

To start the hotel management system, run the `main.py` script:

```bash
python main.py
```

The application will then prompt you for your request. You can use the example queries provided in the task description.

### Example Queries (Persian)

- **Book two different rooms:**
  `“یک اتاق دو نفره برای سه شب و یک اتاق یک نفره برای یک شب می‌خواستم.”`
- **Book a room and order a meal:**
  `“برای فردا شب یک اتاق یک نفره رزرو کنید. برای شام هم یک پیتزا نصف پپرونی و نصف سبزیجات و یک نوشابه می‌خواستم.”`
- **Order a large meal and reserve a table:**
  `“۱۰ پرس کباب کوبیده و ۵ پرس جوجه زعفرانی برای ناهار فردا رزرو کنید. همچنین یک میز برای ۵ نفر می‌خواهم.”`
- **Book a long stay with full board:**
  `“برای یک هفته اتاق سه نفره نیاز دارم. غذا هم سه وعده در روز می‌خواهم.”`
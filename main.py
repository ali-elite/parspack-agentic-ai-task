
import subprocess
import uvicorn
from multiprocessing import Process
import time
import os

def run_backend():
    uvicorn.run("src.backend_app:app", host="127.0.0.1", port=8000, reload=False)

def run_frontend():
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    p_backend = Process(target=run_backend)
    p_frontend = Process(target=run_frontend)
    
    p_backend.start()
    print("Backend started...")
    
    time.sleep(5)
    
    p_frontend.start()
    print("Frontend started...")
    
    p_backend.join()
    p_frontend.join()

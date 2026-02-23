Nexus chat is a secure and encrypted chatting application that uses python websockets for communication. I built it as a part of a school hackathon. Contributions are always welcome:)
# HOW TO RUN THE APPLICATION**
## 1) Clone the repository and open it in a code editor
## 2) Download the requirements from the requirements.txt file using the command:
``` pip install -r requirements.txt ```
## 3) Activate the Virtual Environment or Make a new one based on your situation
## 4) Start the Uvicorn ASGI server using this command: 
```uvicorn app.main:app``` or OPTIONALLY ```uvicorn app.main:app --host 0.0.0.0 --port 10000```
## 5) Visit the LocalHost address.

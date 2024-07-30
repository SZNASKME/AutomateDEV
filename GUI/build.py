import webview
import threading
from app import app

def start_server():
    app.run()

if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    webview.create_window('Flask Web App', 'http://127.0.0.1:5000')
    webview.start()

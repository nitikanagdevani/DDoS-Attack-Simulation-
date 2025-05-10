import asyncio
import websockets
import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app)
data_log = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    emit('init', data_log)

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        data_log.append(data)
        socketio.emit('update', data)

async def websocket_listener():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("[✅] WebSocket listening on ws://0.0.0.0:8765")
        await asyncio.Future()

def start_websocket():
    asyncio.run(websocket_listener())

if __name__ == '__main__':
    t = threading.Thread(target=start_websocket)
    t.start()
    socketio.run(app, host='0.0.0.0', port=5000)

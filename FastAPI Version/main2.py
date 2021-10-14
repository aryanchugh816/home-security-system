from typing import List
import time
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.state = {
            'quuincy_room': {
                'led': 0
            }
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def perform_op(self, task):
        try:
            self.state[task['room']][task['type']] = task['val']
            task['op_status'] = True
        except Exception:
            task['op_status'] = False

    async def send_personal_message(self, message: str, websocket: WebSocket):
        # message = json.loads(message)
        
        # message = self.perform_op(message)
        # message = json.dumps(message)
        await websocket.send_text(message)
        print("message sent --------------------------------------")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"message received : {data}, type: {type(data)}")
            data = json.loads(data)
            if client_id == 'raspi4':
                if data['type'] == 'send_state':
                    data_send = {}
                    data_send['data'] = manager.state
                    data_send['type'] = 'send_state'
                    data_send['opr_status'] = True
                    # time.sleep(8)

                elif data['type'] == 'switch':
                    data_send = data
                    if data_send['data']['val'] == 1:
                        data_send['data']['val'] = 0
                    else:
                        data_send['data']['val'] = 1
                    data_send['opr_status'] = True
                    time.sleep(8)
                await manager.send_personal_message(json.dumps(data_send), websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

if __name__ == "__main__":
    uvicorn.run("main2:app", host="127.0.0.1", port=8000, log_level="info")
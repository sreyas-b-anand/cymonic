

from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.connections.pop(client_id, None)

    async def send(self, client_id: str, message: dict):
        conn = self.connections.get(client_id)
        if conn:
            await conn.send_json(message)
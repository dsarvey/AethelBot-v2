# state.py
#
# Manages the volatile, in-memory state for our application.
# This includes the WebSocket manager and the bot's state.

from fastapi import WebSocket
from typing import List, Dict, Any

# --- 1. WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        """Pushes a JSON message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_json(message)

# Create a single, global instance for our app to use
manager = ConnectionManager()


# --- 2. Global Bot State (In-memory database) ---
# This is our Phase 1 "database".
bot_state: Dict[str, Any] = {
    "is_deployed": False,
    "bot_task": None,
    "equity": 0.0,
    "pnl": 0.0,
    "total_external_funding": 0.0,
    "reinvested_profit": 0.0,
    "uninvested_cash": 0.0,
    "allocations": [],
    "initial_funding": 0.0
}
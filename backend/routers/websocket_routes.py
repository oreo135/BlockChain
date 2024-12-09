from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from asyncio import Lock

router = APIRouter()

connected_users = {}
connected_users_lock = Lock()

async def add_connected_user(user_id, websocket):
    async with connected_users_lock:
        connected_users[user_id] = websocket

async def remove_connected_user(user_id):
    async with connected_users_lock:
        connected_users.pop(user_id, None)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = websocket.headers.get("user_id")

    if not user_id:
        print("Missing user_id in headers")
        await websocket.close(code=4000, reason="Missing user_id")
        return

    print(f"User {user_id} connected")
    await add_connected_user(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received data from {user_id}: {data}")

            recipient_id = data.get("to")
            message = data.get("message")

            if recipient_id in connected_users:
                recipient_socket = connected_users[recipient_id]
                try:
                    await recipient_socket.send_json({
                        "from": user_id,
                        "message": message,
                    })
                    print(f"Message from {user_id} to {recipient_id}: {message}")
                except Exception as e:
                    print(f"Failed to send message to {recipient_id}: {e}")
            else:
                print(f"Recipient {recipient_id} is not connected")
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
        await remove_connected_user(user_id)
        await websocket.close()

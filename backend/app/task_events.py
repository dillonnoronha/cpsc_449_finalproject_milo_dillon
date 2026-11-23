"""Owner-scoped task invalidation for a single backend worker."""
import asyncio
import time

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from .auth import get_signing_key, resolve_user
from .config import frontend_origins
from .database import SessionLocal
from .security import verify_token

router = APIRouter()
subscribers: dict[int, set[asyncio.Queue[None]]] = {}


def publish_task_change(user_id: int) -> None:
    # The route calls this on the event loop after committing its write.
    for queue in subscribers.get(user_id, ()):
        if not queue.full():
            queue.put_nowait(None)


def authenticate(token: str) -> tuple[int, int]:
    user_id, expires_at = verify_token(token, get_signing_key())
    with SessionLocal() as db:
        resolve_user(db, user_id)
    return user_id, expires_at


async def send_changes(socket: WebSocket, queue: asyncio.Queue[None]) -> None:
    while True:
        await queue.get()
        await socket.send_json({"type": "tasks.changed"})


@router.websocket("/ws/tasks")
async def task_events(socket: WebSocket):
    origin = socket.headers.get("origin")
    scheme = "https" if socket.url.scheme == "wss" else "http"
    same_origin = f"{scheme}://{socket.url.netloc}"
    if origin is not None and origin != same_origin and origin not in frontend_origins():
        await socket.close(code=1008)
        return

    await socket.accept()
    try:
        auth_message = await asyncio.wait_for(socket.receive(), timeout=5)
        if auth_message["type"] == "websocket.disconnect":
            return
        user_id, expires_at = await run_in_threadpool(
            authenticate, auth_message.get("text") or ""
        )
    except (ValueError, TimeoutError):
        await socket.close(code=1008)
        return
    except HTTPException as error:
        await socket.close(code=1011 if error.status_code == 503 else 1008)
        return

    queue: asyncio.Queue[None] = asyncio.Queue(maxsize=1)
    connections = subscribers.setdefault(user_id, set())
    connections.add(queue)
    tasks: list[asyncio.Task] = []
    try:
        async with asyncio.timeout(max(0, expires_at - time.time())):
            await socket.send_json({"type": "ready"})
            tasks.append(asyncio.create_task(socket.receive()))
            tasks.append(asyncio.create_task(send_changes(socket, queue)))
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
            if tasks[0] in done and tasks[0].result()["type"] != "websocket.disconnect":
                await socket.close(code=1008)
    except TimeoutError:
        await socket.close(code=1008)
    except WebSocketDisconnect:
        pass
    finally:
        connections.remove(queue)
        if not connections:
            del subscribers[user_id]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

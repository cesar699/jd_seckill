
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.seckill_async import run_seckill
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 调度器初始化
scheduler = BackgroundScheduler()

connected_clients = []

def add_seckill_task(sku_id: str, schedule_time: str):
    """添加抢购任务到调度器"""
    trigger = CronTrigger(hour=schedule_time.split(":")[0], minute=schedule_time.split(":")[1])
    scheduler.add_job(run_seckill, trigger, args=[sku_id])
    scheduler.start()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start", response_class=HTMLResponse)
async def start_seckill(request: Request, sku_id: str = Form(...), schedule_time: str = Form(...)):
    add_seckill_task(sku_id, schedule_time)
    return templates.TemplateResponse("index.html", {"request": request, "message": "抢购任务已启动"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Message received: {message}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

def send_log_to_clients(log_message: str):
    """将日志消息推送到所有 WebSocket 客户端"""
    for client in connected_clients:
        asyncio.create_task(client.send_text(log_message))

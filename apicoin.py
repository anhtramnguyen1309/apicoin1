from flask import Flask, jsonify
import json, os
from coin1 import update_cache
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

app = Flask(__name__)

@app.route("/api/giacoin")
def get_giacoin_data():
    if not os.path.exists("giacoin_cache.json"):
        return jsonify({"error": "Cache not found"}), 404
    with open("giacoin_cache.json", "r") as f:
        return jsonify(json.load(f))

# ✅ Cập nhật định kỳ bằng APScheduler
def start_scheduler():
    loop = asyncio.get_event_loop()
    scheduler = BackgroundScheduler()

    async def async_job():
        print("🔁 Đang cập nhật bằng APScheduler...")
        await update_cache()

    def wrapper():
        asyncio.run(async_job())

    scheduler.add_job(wrapper, "interval", seconds=10)
    scheduler.start()

# ✅ Gọi khi app khởi động (ngay cả với gunicorn)
start_scheduler()

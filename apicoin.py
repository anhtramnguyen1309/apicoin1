from flask import Flask, jsonify
import json, os, asyncio, threading
from coin1 import update_cache


app = Flask(__name__)

@app.route("/api/giacoin")
def get_giacoin_data():
    if not os.path.exists("giacoin_cache.json"):
        return jsonify({"error": "Cache not found"}), 404
    with open("giacoin_cache.json", "r") as f:
        return jsonify(json.load(f))

def start_background_updater():
    async def loop():
        print("🚀 Cập nhật ngay khi khởi động...")
        await update_cache()  # ✅ Gọi lần đầu ngay lập tức
        while True:
            print("🔁 Đang cập nhật dữ liệu...")
            await update_cache()
            await asyncio.sleep(5)

    def run():
        asyncio.run(loop())

    threading.Thread(target=run, daemon=True).start()


start_background_updater()
    

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
        while True:
            print("🔁 Đang cập nhật dữ liệu...")
            await update_cache()
            await asyncio.sleep(0.6)

    def run():
        asyncio.run(loop())

    threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    start_background_updater()
    app.run(host="0.0.0.0", port=5001)

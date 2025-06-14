# update_giacoin_cache
import aiohttp
import asyncio
import json
import time
import re
from playwright.async_api import async_playwright

coins = ["BTC", "ETH", "XRP", "TRX", "DOGE"]

async def fetch_usdt_vnd_binance_p2p():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "asset": "USDT",
        "fiat": "VND",
        "merchantCheck": False,
        "page": 1,
        "payTypes": ["BANK"],
        "publisherType": None,
        "rows": 10,
        "tradeType": "BUY",
        "TRANSAMOUNT":"500000000",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            prices = [float(ad['adv']['price']) for ad in data['data'] if float(ad['adv']['price']) > 0]
            return min(prices) if prices else None

async def fetch_binance_usdt_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return float(data['price']) if 'price' in data else None

async def fetch_bithumb_price(symbol):
    url = f"https://api.bithumb.com/public/ticker/{symbol}_KRW"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return float(data['data']['closing_price']) if 'data' in data else None

async def get_naver_rate(page):
    try:
        await page.goto("https://finance.naver.com/marketindex/exchangeDetail.nhn?marketindexCd=FX_VNDKRW")
        await page.wait_for_timeout(3000)

        content = await page.content()

        # Tìm tỷ giá cho option 100 VND
        match = re.search(r'<option value="([\d.]+)" label="100">.*?VND</option>', content)
        if match:
            krw_for_100_vnd = float(match.group(1))
            vnd_per_krw = 1 / krw_for_100_vnd
            return f"{vnd_per_krw:.2f}"
        else:
            print("❌ Không tìm thấy tỷ giá từ NAVER")
            return None

    except Exception as e:
        print("⚠️ Lỗi NAVER:", e)
        return None  

async def update_cache():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        naver_rate = await get_naver_rate(page)
        await browser.close()

    usdt_vnd = await fetch_usdt_vnd_binance_p2p()
    usdt_krw = await fetch_bithumb_price("USDT")

    coins_data = {}
    for coin in coins:
        binance = await fetch_binance_usdt_price(coin)
        bithumb = await fetch_bithumb_price(coin)
        coins_data[coin] = {"binance": binance, "bithumb": bithumb}

    result = {
        "updated_at": time.time(),
        "usdt_vnd": usdt_vnd,
        "usdt_krw": usdt_krw,
        "naver_rate": naver_rate,
        "coins": coins_data
    }

    with open("giacoin_cache.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    async def run_forever():
        while True:
            print("🔁 Đang cập nhật dữ liệu...")
            await update_cache()
            await asyncio.sleep(0.6)  # Cập nhật mỗi 3 giây

    asyncio.run(run_forever())


import httpx, asyncio, json

async def seckill_once(session: httpx.AsyncClient, sku_id: str):
    buy_url = f'https://cart.jd.com/gotoCart.action'
    try:
        resp = await session.get(buy_url)
        if "结算" in resp.text:
            print("抢购成功")
        else:
            print("未成功")
    except Exception as e:
        print("请求异常", e)

async def run_seckill(sku_id: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    cookies = json.load(open('cookies.json'))
    async with httpx.AsyncClient(headers=headers, cookies={c['name']: c['value'] for c in cookies}) as client:
        tasks = [seckill_once(client, sku_id) for _ in range(10)]
        await asyncio.gather(*tasks)

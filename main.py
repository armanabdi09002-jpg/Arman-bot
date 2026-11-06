import os, httpx
from fastapi import FastAPI, Request

app = FastAPI()
BALE_TOKEN = os.environ["BALE_TOKEN"]
AI_KEY = os.environ["AI_KEY"]
BALE_API = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

async def ask_ai(text: str) -> str:
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_KEY}"},
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "به فارسی و مختصر پاسخ بده."},
                    {"role": "user", "content": text},
                ],
            },
        )
        return r.json()["choices"][0]["message"]["content"]

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    msg = data.get("message")
    if msg and "text" in msg:
        answer = await ask_ai(msg["text"])
        async with httpx.AsyncClient() as c:
            await c.post(f"{BALE_API}/sendMessage",
                         json={"chat_id": msg["chat"]["id"], "text": answer})
    return {"ok": True}

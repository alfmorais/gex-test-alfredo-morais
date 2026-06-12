import asyncio
import json
from pathlib import Path

import httpx

BASE_URL = "http://localhost:9000/webhook"


async def send_payload(client: httpx.AsyncClient, payload: dict) -> None:
    gateway = payload["gateway"]
    url = f"{BASE_URL}/{gateway}"

    response = await client.post(url, json=payload)

    print(f"[{gateway}] status={response.status_code} body={response.text}")


async def main() -> None:
    path = Path("tests/mock/webhook_payloads.json")

    with path.open("r", encoding="utf-8") as file:
        payloads = json.load(file)

    async with httpx.AsyncClient(timeout=10.0) as client:
        for payload in payloads:
            await send_payload(client, payload)


if __name__ == "__main__":
    asyncio.run(main())

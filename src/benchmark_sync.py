import asyncio
import time

import httpx

BASE_URL = "http://localhost:8000"


async def run_sequential(n: int) -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        start = time.perf_counter()
        response_times = []

        for _ in range(n):
            request_start = time.perf_counter()
            response = await client.post(f"{BASE_URL}/process/sync")
            response.raise_for_status()
            response_times.append(time.perf_counter() - request_start)

        total_time = time.perf_counter() - start

    print(f"\nСинхронная обработка, последовательные запросы: {n} запросов")
    print(f"Суммарное время: {total_time:.2f} сек")
    print(f"Среднее время ответа: {sum(response_times) / len(response_times):.2f} сек")


async def run_parallel(n: int, concurrency: int) -> None:
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=60) as client:

        async def one_request() -> float:
            async with semaphore:
                request_start = time.perf_counter()
                response = await client.post(f"{BASE_URL}/process/sync")
                response.raise_for_status()
                return time.perf_counter() - request_start

        start = time.perf_counter()
        response_times = await asyncio.gather(*(one_request() for _ in range(n)))
        total_time = time.perf_counter() - start

    print(f"\nСинхронная обработка, параллельные запросы: {n} запросов, параллельно {concurrency} запросов")
    print(f"Суммарное время: {total_time:.2f} сек")
    print(f"Среднее время ответа: {sum(response_times) / len(response_times):.2f} сек")


async def main() -> None:
    for n in [10, 50, 100]:
        await run_sequential(n)

    await run_parallel(n=100, concurrency=10)
    await run_parallel(n=100, concurrency=20)
    await run_parallel(n=100, concurrency=50)
    await run_parallel(n=100, concurrency=100)

    await run_parallel(n=1000, concurrency=100)
    await run_parallel(n=1000, concurrency=200)
    await run_parallel(n=1000, concurrency=500)


if __name__ == "__main__":
    asyncio.run(main())

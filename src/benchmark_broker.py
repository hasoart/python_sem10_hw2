import asyncio
import time

import httpx

BASE_URL = "http://localhost:8000"


async def wait_until_finished(
    client: httpx.AsyncClient,
    task_ids: list[str],
) -> float:
    start = time.perf_counter()

    unfinished = set(task_ids)

    while unfinished:
        for task_id in list(unfinished):
            response = await client.get(f"{BASE_URL}/process/tasks/{task_id}")
            response.raise_for_status()

            data = response.json()

            if data["status"] in {"finished", "failed"}:
                unfinished.remove(task_id)

        await asyncio.sleep(0.1)

    return time.perf_counter() - start


async def run_sequential(n: int) -> None:
    async with httpx.AsyncClient(timeout=60) as client:
        api_start = time.perf_counter()
        response_times = []
        task_ids = []

        for _ in range(n):
            request_start = time.perf_counter()
            response = await client.post(f"{BASE_URL}/process/schedule")
            response.raise_for_status()

            response_times.append(time.perf_counter() - request_start)
            task_ids.append(response.json()["task_id"])

        api_total_time = time.perf_counter() - api_start

        processing_time = await wait_until_finished(client, task_ids)

    print(f"\nБрокер, последовательные запросы: {n} запросов")
    print(f"Суммарное время ответов от API: {api_total_time:.2f}s")
    print(f"Среднее время ответа API: {sum(response_times) / len(response_times):.4f}s")
    print(f"Суммарное время фоновой обработки: {processing_time:.2f}s")


async def run_parallel(n: int, concurrency: int) -> None:
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=60) as client:

        async def submit_one() -> tuple[str, float]:
            async with semaphore:
                request_start = time.perf_counter()
                response = await client.post(f"{BASE_URL}/process/schedule")
                response.raise_for_status()

                elapsed = time.perf_counter() - request_start
                task_id = response.json()["task_id"]

                return task_id, elapsed

        api_start = time.perf_counter()
        results = await asyncio.gather(*(submit_one() for _ in range(n)))
        api_total_time = time.perf_counter() - api_start

        task_ids = [task_id for task_id, _ in results]
        response_times = [elapsed for _, elapsed in results]

        processing_time = await wait_until_finished(client, task_ids)

    print(f"\nБрокер, параллельные запросы: {n} запросов, параллельно {concurrency} запросов")
    print(f"Суммарное время ответов от API: {api_total_time:.2f}s")
    print(f"Среднее время ответа API: {sum(response_times) / len(response_times):.4f}s")
    print(f"Суммарное время фоновой обработки: {processing_time:.2f}s")


async def main() -> None:
    # for n in [10, 50, 100]:
    #     await run_sequential(n)

    await run_parallel(n=100, concurrency=10)
    await run_parallel(n=100, concurrency=20)
    await run_parallel(n=100, concurrency=50)
    await run_parallel(n=100, concurrency=100)


if __name__ == "__main__":
    asyncio.run(main())

"""
This class handles asynchronous requests to server and returns the response json.
It is used for external API requests
"""

from src.app.utils.http_errors import MaximumRetriesError, RequestFailedError, ERROR_MAP, RETRYABLE_EXCEPTIONS
from urllib.parse import urlencode
import asyncio

async def get_response(base_url: str, endpoint: str, params: dict, headers: dict, session, retries, delay):
    url = f"{base_url}{endpoint}?{urlencode(params)}"
    data = None
    attempts = 0
    while data is None and attempts < retries:
        attempts += 1
        try:
            async with session.get(url, headers=headers) as response:
                if response.status in ERROR_MAP:
                    exception = ERROR_MAP[response.status]()
                    if exception in RETRYABLE_EXCEPTIONS:
                        await asyncio.sleep(delay)
                        continue
                    raise exception
                if not response.ok:
                    raise RequestFailedError(response.status, f"Error {response.status}: {response.reason}")
                data = await response.json()
        except Exception as e:
            print(f"Error: {e}")
            if attempts >= retries:
                if hasattr(e, 'status_code'):
                    raise RequestFailedError(e.status_code, str(e))
                else:
                    raise
            await asyncio.sleep(delay)
            continue

    if data is None:
        raise MaximumRetriesError(status_code=504, message="Request timed out after maximum retries.")
    return data
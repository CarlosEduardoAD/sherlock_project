import pytest
import main
import asyncio

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

@async_test
async def TestConn():
    assert await main.on_ready() == True
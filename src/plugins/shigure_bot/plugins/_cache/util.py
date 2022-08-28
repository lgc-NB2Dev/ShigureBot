from awaits.awaitable import awaitable


async def async_wrapper(origin_func, *args, **kwargs):
    """异步调用包装"""

    @awaitable
    def wrapper_():
        return origin_func(*args, **kwargs)

    return await wrapper_()

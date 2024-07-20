from redis.asyncio import Redis


def get_redis(
    host: str,
    port: int
) -> Redis:
    return Redis(
        host=host,
        port=port,
        db=0,
        decode_responses=True
    )

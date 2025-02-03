# Description: Redis-based Delta Lake locking
from contextlib import contextmanager
from redis import StrictRedis, Redis
from loguru import logger
import time


class DeltaLockError(Exception):
    """Custom exception for lock-related failures"""


@contextmanager
def redis_lock(
    lock_name: str,
    redis_client: StrictRedis | Redis | None = None,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    lock_timeout: int = 30,
    retry_interval: float = 0.1,
    max_retries: int = 10,
    verbose: bool = False,
):
    """
    Context manager for Redis-based locking

    :param table_path: URI/path of the Delta table
    :param redis_client: Configured Redis client
    :param redis_host: Redis server hostname
    :param redis_port: Redis server port
    :param lock_timeout: Lock duration in seconds
    :param retry_interval: Delay between lock attempts
    :param max_retries: Maximum retry attempts
    :param verbose: Enable debug logging
    """
    if redis_client is None:
        redis_client = Redis(host=redis_host, port=redis_port)

    # lock_name = f"delta_lock:{table_path}"
    lock = redis_client.lock(name=lock_name, timeout=lock_timeout, blocking=True)

    attempts = 0
    while attempts < max_retries:
        if lock.acquire():
            try:
                if verbose:
                    logger.debug(f"Acquired lock {lock_name}")
                yield  # Execute operation within lock context
                return
            finally:
                lock.release()
                if verbose:
                    logger.debug(f"Released lock {lock_name}")
        else:
            if verbose:
                logger.warning(f"Lock contention {lock_name} - attempt {attempts + 1}")
            time.sleep(retry_interval)
            attempts += 1

    raise DeltaLockError(
        f"Failed to acquire lock {lock_name} after {max_retries} attempts"
    )

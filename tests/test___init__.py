import time

import pytest
import redis

from redis_lock import redis_lock


@pytest.fixture
def redis_client():
    client = redis.Redis(host="localhost", port=6379, db=0)
    client.flushall()  # Clean up before tests
    yield client
    client.flushall()  # Clean up after tests


def test_basic_lock_acquire(redis_client):
    with redis_lock(redis_client, "test_lock", expire=10):
        assert redis_client.exists("test_lock") == 1


def test_lock_release(redis_client):
    with redis_lock(redis_client, "test_lock", expire=10):
        pass
    assert redis_client.exists("test_lock") == 0


def test_lock_expiration(redis_client):
    with redis_lock(redis_client, "test_lock", expire=1):
        time.sleep(2)
    assert redis_client.exists("test_lock") == 0


def test_lock_concurrent_access(redis_client):
    with redis_lock(redis_client, "test_lock", expire=10):
        with pytest.raises(Exception):
            with redis_lock(redis_client, "test_lock", expire=10):
                pass


def test_lock_with_invalid_expire(redis_client):
    with pytest.raises(ValueError):
        with redis_lock(redis_client, "test_lock", expire=-1):
            pass

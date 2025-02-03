# Simple Redis Lock

This is a simple implementation of a distributed lock using Redis. It is based on the algorithm described in the [Redis documentation](https://redis.io/topics/distlock).

The lock is implemented as a context manager, so it can be used with the `with` statement. 

## Installation

```bash
pip install redislock-py
```


The `redis_lock` function is a context manager that will acquire a lock on the specified table path. The lock will be released when the context manager exits.

## Usage Examples

### 1. Delta Lake 

```python
from redis_lock import redis_lock
from deltalake import write_deltalake
import redis
import pandas as pd

redis_client = redis.Redis(host='localhost', port=6379)
table_uri = 's3://my_bucket/my_table'
df=pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})


with redis_lock(lock_name=table_uri, redis_client=redis_client):
    write_deltalake(table_uri, df)
```
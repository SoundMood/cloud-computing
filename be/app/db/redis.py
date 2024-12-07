from app.settings import REDIS_PORT, REDIS_HOST
from rediscluster import RedisCluster
endpoints = [{"host": REDIS_HOST, "port": REDIS_PORT}]

rdb = RedisCluster(
    startup_nodes=endpoints,
    skip_full_coverage_check=True, # Required for Memorystore
    decode_responses = True)

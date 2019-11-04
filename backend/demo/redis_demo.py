

import redis
url = 'redis://epay-cache.lrmz3k.ng.0001.ape1.cache.amazonaws.com:6379/0'
client = redis.StrictRedis.from_url(url)
print(client.set('x', 1))
print(client.get('x'))
print(client.delete('x'))


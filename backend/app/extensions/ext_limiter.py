"""
请求频率限制器

https://limits.readthedocs.io/en/latest/string-notation.html

Rate limit string notation
Rate limits are specified as strings following the format:

[count] [per|/] [n (optional)] [second|minute|hour|day|month|year]
You can combine multiple rate limits by separating them with a delimiter of your choice.

Examples
10 per hour
10/hour
10/hour;100/day;2000 per year
100/day, 500/7days
"""
# from flask_limiter import Limiter
#
# from app.libs.ip_kit import IpKit
#
# limiter = Limiter(
#     key_func=IpKit.get_remote_ip,
#     # default_limits=["20000/day", "1/second"]
# )

from app.caches.limiter import Limiter
limiter = Limiter

from flask_caching import Cache
from flask_marshmallow import Marshmallow
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter


ma = Marshmallow()  # Initialize Marshmallow for serialization and deserialization
limiter=Limiter(key_func=get_remote_address, default_limits=['100/day', '10/hour', '500/week'])  # Initialize Limiter for rate limiting
cache=Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})  # Initialize Cache for caching responses

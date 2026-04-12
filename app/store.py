# TODO: Replace in-memory storage with a persistent database.
# In-memory storage for calendars and their events.
# Data resets on server restart. This is intentional for the benchmark.

calendars: dict = {}

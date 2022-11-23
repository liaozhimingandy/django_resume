# The IP address (typically localhost) and port that the idcops WSGI process should listen on
bind = '0.0.0.0:8000'

# The number of worker processes for handling requests.
# A positive integer generally in the 2-4 x $(NUM_CORES) range.
# You’ll want to vary this a bit to find the best for your particular application’s work load.
# $(NUM_CORES) is the number of CPU cores present.
workers = 3

# The number of worker threads for handling requests.
# Run each worker with the specified number of threads.
# Number of threads per worker process
threads = 3

# Timeout (in seconds) for a request to complete
timeout = 120

# The maximum number of requests a worker can handle before being respawned
max_requests = 4096

max_requests_jitter = 300

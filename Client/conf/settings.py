import os

# Server Config
Params = {
    'server': "192.168.0.106",
    'port': 8000,
    'url': '/assets/report/',
    'request_timeout': 30,
}

# Log File Config
PATH = os.path.join(os.path.dirname(os.getcwd()), 'log', 'cmdb.log')

# More config can be put in here

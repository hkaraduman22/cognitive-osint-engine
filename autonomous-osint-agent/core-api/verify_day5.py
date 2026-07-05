import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from app.services.company_service import get_companies
    print('get_companies import:', callable(get_companies))
except Exception as e:
    print('get_companies import error:', e)

try:
    from app.routers.company_router import list_companies
    print('list_companies import:', callable(list_companies))
except Exception as e:
    print('list_companies import error:', e)

import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from app.models.company import Company, CompanyOfficial
    print('Company model import:', hasattr(Company, '__tablename__') and Company.__tablename__ == 'companies')
    print('CompanyOfficial model import:', hasattr(CompanyOfficial, '__tablename__') and CompanyOfficial.__tablename__ == 'company_officials')
except Exception as e:
    print('Company import error:', e)

try:
    from app.schemas.company_schema import CompanyCreate, CompanyResponse
    print('CompanyCreate schema import:', hasattr(CompanyCreate, '__fields__'))
    print('CompanyResponse schema import:', hasattr(CompanyResponse, '__fields__'))
except Exception as e:
    print('Schema import error:', e)

try:
    from app.services.company_service import create_elite_company
    print('create_elite_company import:', callable(create_elite_company))
except Exception as e:
    print('Service import error:', e)

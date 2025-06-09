#!/bin/bash
cd backend
echo "Checking database alembic_version table..."
python -c "
from database.session import get_db_session
session = get_db_session()
try:
    result = session.execute('SELECT version_num FROM alembic_version;')
    current_version = result.fetchone()
    if current_version:
        print(f'Current database version: {current_version[0]}')
    else:
        print('No version found in alembic_version table')
except Exception as e:
    print(f'Error checking version: {e}')
finally:
    session.close()
"

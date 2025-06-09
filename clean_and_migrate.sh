#!/bin/bash
cd backend

echo "Cleaning up existing signal tables..."
python -c "
import sys
sys.path.append('.')
from database.session import get_db_session
from sqlalchemy import text

session = get_db_session()
try:
    # Drop tables if they exist (in correct order due to foreign keys)
    tables_to_drop = ['signal_responses', 'signal_sources', 'signals']
    
    for table in tables_to_drop:
        try:
            session.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE;'))
            print(f'Dropped table: {table}')
        except Exception as e:
            print(f'Could not drop {table}: {e}')
    
    session.commit()
    print('Cleanup completed successfully')
        
except Exception as e:
    print(f'Error during cleanup: {e}')
    import traceback
    traceback.print_exc()
    session.rollback()
finally:
    session.close()
"

if [ $? -eq 0 ]; then
    echo ""
    echo "Now running fresh migration..."
    python -m alembic upgrade head
    
    echo ""
    echo "Verifying tables were created:"
    python -c "
import sys
sys.path.append('.')
from database.session import get_db_session
from sqlalchemy import text

session = get_db_session()
try:
    # Check if our new tables exist
    tables_to_check = ['signals', 'signal_sources', 'signal_responses']
    
    for table in tables_to_check:
        result = session.execute(text(\"SELECT to_regclass('public.\" + table + \"');\"))
        exists = result.fetchone()[0] is not None
        print(f'Table {table}: {\"EXISTS\" if exists else \"MISSING\"}')
    
    # Check final version
    result = session.execute(text('SELECT version_num FROM alembic_version;'))
    current_version = result.fetchone()
    if current_version:
        print(f'\\nDatabase version: {current_version[0]}')
        
except Exception as e:
    print(f'Error checking tables: {e}')
finally:
    session.close()
"
else
    echo "Failed to clean up tables"
fi

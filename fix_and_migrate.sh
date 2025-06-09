#!/bin/bash
cd backend

echo "Fixing alembic version table..."
python -c "
import sys
sys.path.append('.')
from database.session import get_db_session
from sqlalchemy import text

session = get_db_session()
try:
    # Check current version
    result = session.execute(text('SELECT version_num FROM alembic_version;'))
    current_version = result.fetchone()
    if current_version:
        print(f'Current database version: {current_version[0]}')
        
        # If it's the problematic version, fix it
        if current_version[0] == '004_reddit_signals':
            print('Fixing problematic version...')
            session.execute(text('UPDATE alembic_version SET version_num = :version'), {'version': '003_pinecone_integration'})
            session.commit()
            print('Fixed! Set version back to 003_pinecone_integration')
        else:
            print('Version looks good:', current_version[0])
    else:
        print('No version found in alembic_version table')
        # Initialize the version table to the last known good state
        session.execute(text('INSERT INTO alembic_version (version_num) VALUES (:version)'), {'version': '003_pinecone_integration'})
        session.commit()
        print('Initialized version to 003_pinecone_integration')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    session.rollback()
finally:
    session.close()
"

if [ $? -eq 0 ]; then
    echo ""
    echo "Now running migration..."
    python -m alembic upgrade head
    
    echo ""
    echo "Final version check:"
    python -c "
import sys
sys.path.append('.')
from database.session import get_db_session
from sqlalchemy import text

session = get_db_session()
try:
    result = session.execute(text('SELECT version_num FROM alembic_version;'))
    current_version = result.fetchone()
    if current_version:
        print(f'Database is now at version: {current_version[0]}')
    else:
        print('No version found')
except Exception as e:
    print(f'Error checking final version: {e}')
finally:
    session.close()
"
else
    echo "Failed to fix version table"
fi

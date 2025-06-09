#!/bin/bash
cd backend
echo "Checking current migration state..."
python -m alembic current
echo ""
echo "Running signals migration..."
python -m alembic upgrade head
echo ""
echo "New migration state:"
python -m alembic current
echo "Migration complete!"

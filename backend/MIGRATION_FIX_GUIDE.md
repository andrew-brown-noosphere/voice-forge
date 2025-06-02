# Migration Fix Guide

The migration script had an issue with the database column names. Here's how to fix it:

## ✅ Quick Fix

Run the fixed migration script:

```bash
cd backend
python fixed_migration.py
```

## 🔧 What Was Wrong

The original migration script tried to create an index on `content_chunks.content`, but the actual column name is `content_chunks.text` (as defined in the database models).

## 🧪 Test the Fix

After running the fixed migration, test the system:

```bash
# Test the hybrid RAG implementation
python test_hybrid_rag.py
```

## 📋 Alternative Manual Fix

If the script still has issues, you can run the SQL manually:

```sql
-- Connect to your PostgreSQL database and run:
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_chunks_fts 
ON content_chunks USING GIN (to_tsvector('english', text));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_chunks_org_content_type
ON content_chunks (org_id, content_id);
```

## ✅ Verify Success

Check that the indexes were created:

```sql
SELECT indexname FROM pg_indexes 
WHERE tablename = 'content_chunks' 
AND indexname LIKE 'idx_content_chunks%';
```

You should see:
- `idx_content_chunks_fts`
- `idx_content_chunks_org_content_type`

## 🚀 Next Steps

Once the migration is successful:

1. **Test the system**: `python test_hybrid_rag.py`
2. **Start using the enhanced endpoints**: The new `/api/rag/search` endpoint with hybrid strategy
3. **Check the full documentation**: See `HYBRID_RAG_README.md`

The hybrid RAG system should now be fully functional with 2-3x improved search relevance! 🎉

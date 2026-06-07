"""Select sample projects for single-project verification."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Query for line projects
print("=== 线路工程项目 (constructionLineLength > 0 or prjName like '%线路%') ===")
rows = c.execute("""
    SELECT prjCode, prjName, constructionCategoryName, constructionLineLength, constrTransformerCapacity
    FROM dcp_plan_projects
    WHERE prjName LIKE '%线路%' OR constructionLineLength > 0
    LIMIT 10
""").fetchall()
for r in rows:
    print(f"  {r[0]} | {r[1][:30]} | {r[2]} | lineLen={r[3]} | transformerCap={r[4]}")

# Query for substation projects
print("\n=== 变电工程项目 (constrTransformerCapacity > 0 or prjName like '%变电%') ===")
rows = c.execute("""
    SELECT prjCode, prjName, constructionCategoryName, constructionLineLength, constrTransformerCapacity
    FROM dcp_plan_projects
    WHERE prjName LIKE '%变电%' OR constrTransformerCapacity > 0
    LIMIT 10
""").fetchall()
for r in rows:
    print(f"  {r[0]} | {r[1][:30]} | {r[2]} | lineLen={r[3]} | transformerCap={r[4]}")

# Query for mixed projects (both line and substation)
print("\n=== 混合项目 (both lineLen > 0 AND transformerCap > 0) ===")
rows = c.execute("""
    SELECT prjCode, prjName, constructionCategoryName, constructionLineLength, constrTransformerCapacity
    FROM dcp_plan_projects
    WHERE constructionLineLength > 0 AND constrTransformerCapacity > 0
    LIMIT 10
""").fetchall()
for r in rows:
    print(f"  {r[0]} | {r[1][:30]} | {r[2]} | lineLen={r[3]} | transformerCap={r[4]}")

# Also check constructionCategoryName distribution
print("\n=== constructionCategoryName 分布 ===")
rows = c.execute("""
    SELECT constructionCategoryName, COUNT(*) as cnt
    FROM dcp_plan_projects
    GROUP BY constructionCategoryName
    ORDER BY cnt DESC
    LIMIT 20
""").fetchall()
for r in rows:
    print(f"  {r[0] or 'NULL'}: {r[1]}")

conn.close()

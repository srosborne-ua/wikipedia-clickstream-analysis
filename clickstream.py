import duckdb
import pandas as pd
import os

con = duckdb.connect("clickstream.duckdb")

# con.sql("""
#     CREATE TABLE clickstream AS
#     SELECT * FROM read_csv(
#         'clickstream-enwiki-2026-06.tsv',
#         delim='\t',
#         header=false,
#         columns={'prev': 'VARCHAR', 'curr': 'VARCHAR', 'type': 'VARCHAR', 'n': 'INTEGER'}
#     )
# """)

# con.sql("SELECT COUNT(*) FROM clickstream").show()

# con.sql("SELECT type, COUNT(*) FROM clickstream GROUP BY type").show()

# con.sql("SELECT MIN(n), MAX(n), AVG(n) FROM clickstream").show()

# con.sql("select * from clickstream where curr = 'Climate_change' limit 1000").show()

# con.sql("SELECT curr, avg(n) OVER(PARTITION BY curr) FROM clickstream").show()

# con.sql("SELECT curr, AVG(n) AS avg_n, COUNT(*) AS num_referrers, SUM(n) AS total_n " \
# "FROM clickstream " \
# "GROUP BY curr " \
# "ORDER BY total_n DESC").show


# FIXED VERSION OF  EXTERNAL VS INTERNAL LINKE QUERRY, MOVES OTHER-INTERNAL INTO INTERNAL LINK AGGREGATE
# con.sql("""
#     SELECT 
#         CASE 
#             WHEN prev LIKE 'other%' AND prev != 'other-internal' THEN 'external' 
#             ELSE 'internal' 
#         END AS traffic_type,
#         SUM(n) AS total_n,
#         COUNT(*) AS row_count,
#         ROUND(100.0 * SUM(n) / SUM(SUM(n)) OVER (), 2) AS pct_of_total_n
#     FROM clickstream
#     GROUP BY 
#         CASE 
#             WHEN prev LIKE 'other%' AND prev != 'other-internal' THEN 'external' 
#             ELSE 'internal' 
#         END;
# """).show()

#per article total table

# con.sql("""CREATE OR REPLACE TEMP TABLE article_totals AS
# SELECT curr, SUM(n) AS total_n
# FROM clickstream
# GROUP BY curr;""")

#the querys use it:
# con.sql("""WITH ranked AS (
#     SELECT
#         curr,
#         total_n,
#         ROW_NUMBER() OVER (ORDER BY total_n DESC) AS rank,
#         SUM(total_n) OVER (ORDER BY total_n DESC) AS running_sum,
#         SUM(total_n) OVER () AS grand_total,
#         COUNT(*) OVER () AS article_count
#     FROM article_totals
# )
# SELECT
#     rank,
#     curr,
#     total_n,
#     ROUND(100.0 * running_sum / grand_total, 4) AS cumulative_pct_traffic,
#     ROUND(100.0 * rank / article_count, 4) AS cumulative_pct_articles
# FROM ranked
# ORDER BY rank;""").show()

# 

# con.sql("""WITH ranked AS (
#     SELECT curr, total_n, ROW_NUMBER() OVER (ORDER BY total_n DESC) AS rank
#     FROM article_totals
# )
# SELECT total_n AS min_total_n_threshold
# FROM ranked
# WHERE rank = 380075;""").show()

# con.sql("""SELECT COUNT(*) AS total_distinct_articles FROM article_totals;""").show()


# # Phase 2 — per-article search/browse ratio
# con.sql("""
#     CREATE OR REPLACE TABLE per_article_stats AS
#     SELECT
#         curr,
#         external_n,
#         internal_n,
#         external_n + internal_n AS total_n,
#         ROUND(external_n * 1.0 / NULLIF(external_n + internal_n, 0), 4) AS external_share
#     FROM (
#         SELECT
#             curr,
#             SUM(CASE WHEN prev LIKE 'other%' AND prev != 'other-internal' THEN n ELSE 0 END) AS external_n,
#             SUM(CASE WHEN type IN ('link', 'other') OR prev = 'other-internal' THEN n ELSE 0 END) AS internal_n
#         FROM clickstream
#         GROUP BY curr
#         HAVING SUM(CASE WHEN prev LIKE 'other%' AND prev != 'other-internal' THEN n ELSE 0 END)
#              + SUM(CASE WHEN type IN ('link', 'other') OR prev = 'other-internal' THEN n ELSE 0 END) >= 2113
#     )
# """)

# # Phase 5 — hub/sink base table
# con.sql("""
#     CREATE OR REPLACE TABLE hub_sink_stats AS
#     WITH inbound AS (
#         SELECT curr AS article, SUM(n) AS inbound_n
#         FROM clickstream
#         WHERE type IN ('link', 'other')
#         GROUP BY curr
#     ),
#     outbound AS (
#         SELECT prev AS article, SUM(n) AS outbound_n
#         FROM clickstream
#         WHERE type IN ('link', 'other')
#         GROUP BY prev
#     )
#     SELECT
#         COALESCE(i.article, o.article) AS article,
#         COALESCE(i.inbound_n, 0) AS inbound_n,
#         COALESCE(o.outbound_n, 0) AS outbound_n,
#         COALESCE(i.inbound_n, 0) - COALESCE(o.outbound_n, 0) AS inbound_minus_outbound
#     FROM inbound i
#     FULL OUTER JOIN outbound o ON i.article = o.article
#     WHERE COALESCE(i.article, o.article) != 'Main_Page'
# """)

# con.sql("SHOW TABLES").show()
# con.close()

 

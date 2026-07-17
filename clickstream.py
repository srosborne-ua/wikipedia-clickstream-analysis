import duckdb
import pandas as pd


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

con.sql("""CREATE OR REPLACE TEMP TABLE article_totals AS
SELECT curr, SUM(n) AS total_n
FROM clickstream
GROUP BY curr;""")

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

con.sql("""SELECT COUNT(*) AS total_distinct_articles FROM article_totals;""").show()
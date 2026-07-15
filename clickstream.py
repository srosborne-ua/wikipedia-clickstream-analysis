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

#SPLITS INTO EXTERNAL VS OTHER WIKEPEDIA ARTICLE LINKS TO ARRIVE AT CURRENT SOURCE
con.sql("SELECT CASE WHEN prev LIKE 'other%' THEN 'external' ELSE 'internal' END AS traffic_type, SUM(n) AS total_n, COUNT(*) AS row_count, " \
"ROUND(100.0 * SUM(n) / SUM(SUM(n)) OVER (), 2) AS pct_of_total_n " \
"FROM clickstream " \
"GROUP BY CASE WHEN prev LIKE 'other%' THEN 'external' ELSE 'internal' END;").show()
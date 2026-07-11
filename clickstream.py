import duckdb

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

con.sql("SELECT COUNT(*) FROM clickstream").show()

con.sql("SELECT type, COUNT(*) FROM clickstream GROUP BY type").show()

con.sql("SELECT MIN(n), MAX(n), AVG(n) FROM clickstream").show()

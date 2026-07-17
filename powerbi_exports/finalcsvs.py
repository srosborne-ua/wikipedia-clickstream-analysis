import duckdb
import pandas as pd
import os

con = duckdb.connect("clickstream.duckdb")


 
OUT_DIR = "powerbi_exports"
os.makedirs(OUT_DIR, exist_ok=True)
 
con = duckdb.connect("clickstream.duckdb")
 
TRAFFIC_FLOOR = 2113  
 

# 1. Pareto curve — cumulative traffic share vs. cumulative article share
# ---------------------------------------------------------------------------
 
con.sql("""
    CREATE TABLE IF NOT EXISTS article_totals AS
    SELECT curr AS article, SUM(n) AS total_n
    FROM clickstream
    WHERE curr != 'Main_Page'
    GROUP BY curr
""")
 
# Rank all articles by traffic, compute cumulative share, then downsample
# to ~1000 log-spaced points so the CSV is small but the curve stays smooth
# and dense near the knee.
pareto_full = con.sql("""
    WITH ranked AS (
        SELECT
            article,
            total_n,
            ROW_NUMBER() OVER (ORDER BY total_n DESC) AS rnk,
            SUM(total_n) OVER (ORDER BY total_n DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_n,
            COUNT(*) OVER () AS total_articles,
            SUM(total_n) OVER () AS grand_total_n
        FROM article_totals
    )
    SELECT
        rnk,
        ROUND(100.0 * rnk / total_articles, 4) AS pct_of_articles,
        ROUND(100.0 * cum_n / grand_total_n, 4) AS pct_of_traffic
    FROM ranked
""").df()
 
n_rows = len(pareto_full)
n_samples = 1000
 
# Log-spaced sample indices so density is higher at low ranks (the knee)
import numpy as np
log_idx = np.unique(
    np.logspace(0, np.log10(n_rows), num=n_samples, dtype=int)
)
log_idx = log_idx[log_idx < n_rows]
 
pareto_sampled = pareto_full.iloc[log_idx].reset_index(drop=True)
pareto_sampled.to_csv(os.path.join(OUT_DIR, "pareto_curve.csv"), index=False)
print(f"pareto_curve.csv written: {len(pareto_sampled)} rows")
 

# 2. Hub / sink bars — top 20 proportional sinks + top 20 proportional hubs
# ---------------------------------------------------------------------------
 
sinks = con.sql(f"""
    SELECT
        article,
        inbound_n,
        outbound_n,
        inbound_n + outbound_n AS total_n,
        ROUND(inbound_n * 1.0 / NULLIF(outbound_n, 0), 2) AS ratio,
        'sink' AS category
    FROM hub_sink_stats
    WHERE inbound_n + outbound_n >= {TRAFFIC_FLOOR}
      AND outbound_n > 0
    ORDER BY ratio DESC
    LIMIT 20
""").df()
 
hubs = con.sql(f"""
    SELECT
        article,
        inbound_n,
        outbound_n,
        inbound_n + outbound_n AS total_n,
        ROUND(outbound_n * 1.0 / NULLIF(inbound_n, 0), 2) AS ratio,
        'hub' AS category
    FROM hub_sink_stats
    WHERE inbound_n + outbound_n >= {TRAFFIC_FLOOR}
      AND inbound_n > 0
    ORDER BY ratio DESC
    LIMIT 20
""").df()
 
hub_sink_bars = duckdb.sql("SELECT * FROM sinks UNION ALL SELECT * FROM hubs").df()
hub_sink_bars.to_csv(os.path.join(OUT_DIR, "hub_sink_bars.csv"), index=False)
print(f"hub_sink_bars.csv written: {len(hub_sink_bars)} rows")
 
# 
# 3. external_share histogram

 
bucket_width = 0.05  # 20 buckets across 0.0-1.0
 
hist = con.sql(f"""
    SELECT
        FLOOR(external_share / {bucket_width}) * {bucket_width} AS bucket_start,
        FLOOR(external_share / {bucket_width}) * {bucket_width} + {bucket_width} AS bucket_end,
        COUNT(*) AS article_count
    FROM per_article_stats
    WHERE curr != 'Main_Page'
      AND external_share IS NOT NULL
    GROUP BY 1, 2
    ORDER BY bucket_start
""").df()
 
hist.to_csv(os.path.join(OUT_DIR, "external_share_hist.csv"), index=False)
print(f"external_share_hist.csv written: {len(hist)} rows")
 
# 4. KPI — overall internal vs external traffic split 
# 
 
kpi = con.sql("""
    SELECT
        CASE
            WHEN prev LIKE 'other%' AND prev != 'other-internal' THEN 'external'
            ELSE 'internal'
        END AS traffic_type,
        SUM(n) AS total_n,
        ROUND(100.0 * SUM(n) / SUM(SUM(n)) OVER (), 2) AS pct_of_total_n
    FROM clickstream
    GROUP BY 1
""").df()
 
kpi.to_csv(os.path.join(OUT_DIR, "traffic_split_kpi.csv"), index=False)
print(f"traffic_split_kpi.csv written: {len(kpi)} rows")
 
print(f"\nAll CSVs written to ./{OUT_DIR}/")
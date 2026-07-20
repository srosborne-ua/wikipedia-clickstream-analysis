Wikipedia Clickstream Analysis

An exploratory data analysis of the English Wikipedia clickstream dataset (June 2026 release, 45M+ rows), examining how readers navigate into and between articles.

PowerBi Vis:
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/73e01a9c-af9f-4a02-831b-cdfcb6c0f207" />


Description

This project looks at how much of Wikipedia's traffic comes from search, social, and other external sources versus article-to-article browsing. It calculates a search vs. browse ratio for individual articles, identifying which pages are mostly found through search versus discovered by clicking around. It also flags high outbound traffic pages, which mostly send readers elsewhere, and low outbound traffic pages, which mostly receive readers and rarely lead anywhere else. Another focus is desire paths, article pairs with heavy traffic between them despite no hyperlink connecting them, which can point to missing links. Finally, the project examines the Pareto distribution of traffic, showing how concentrated it is across articles.

Stack

DuckDB is the primary query engine for the full dataset. pandas is used for small aggregated result handoffs and CSV export. Power BI is used for final visualizations.

Data

Source: Wikimedia Clickstream, English Wikipedia, June 2026. Not included in this repo, see .gitignore.

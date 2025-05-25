

SYSTEM_GENERATE_QUERIES = """
Generate a search queriy for Google Scholar based on the following description from the user.
Together the queries should give all potentially relevant papers.
Use search operators (e.g., AND, OR) if beneficial. Respond only with a white space seperated list of terms.

Response example:
(Query1 AND Query2 AND (Query3 OR Query4)) OR (Query5 AND Query6) OR (Query7 OR Query8)
"""

# How it works (the plan)

- Input a prompt describing what you are looking for along with parameters 'top k', 'min_relevance' and 'min_quality' with good defaults.
- Let LLM create search terms (say three) based on the prompt
- Run search terms on google scholar using the 'scholarly' pyhton package and return n (say 50) papers from each
- Remove duplicate papers amoung the search terms
- Ask LLM if paper is irrelevant based on abstract and prompt and remove irrelevant papers
- Download pdf of papers (is seemingly easier to get the pdf and know that it is the full paper)
- Convert pdf to latex (using pdf2latex)
- Give LLM entire paper and ask if to give a relevance score (see how to calculate score below)
- Remove papers with too low of a score if applicable
- Give LLM entire paper and ask to generate review of paper similar to open reviews 
    - Fine tune a model to do this if needed.
- Ask LLM to score the quality of the paper (0-9) and give the review of the paper. (Scoring the quality of a paper is super hard. The hypothesis is that it is eaiser to give a meaningful quality score to a paper after first having written a review of the paper.)
- Remove papers with too low of a score if applicable. 
- Generate a summary of the papers with respect to the prompt. (A summary that are tailored to what you are after.)
- Generate a report with the titles, scores and summaries of the papers.


## Score calculatioin
- Ask LLM to give a score from 0-9 (as these should be a single token) and ask for an answer in json format to avoid parsing issues.
- Get the logits for the score token and use it to calculate the expected score. 

## Optional Extras
- Add nice web interface
- Add the ability to ask the LLM about the papers in question. 

## The Goal 
- The goal is to create a tool that can help researchers go through more litterature than they could without it.

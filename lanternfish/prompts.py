

SYSTEM_GENERATE_QUERIES = """
Generate a search queriy for Google Scholar based on the following description from the user.
Together the queries should give all potentially relevant papers.
Use search operators (e.g., AND, OR) if beneficial. Respond only with a white space seperated list of terms.

Response example:
(Query1 AND Query2 AND (Query3 OR Query4)) OR (Query5 AND Query6) OR (Query7 OR Query8)
"""

SYSTEM_GENERATE_QUERY = """
Generate a search query for Google Scholar based on the user description below.
The respose should be a single line with the query, without any additional text or formatting.
Use search operators (e.g. 'AND', 'OR', 'after:') if beneficial. 
"""

SYSTEM_GENERATE_RELEVANCE_SCORE = """
You are an expert academic assistant. You will be given a 'User prompt' followed by the LaTeX source of a 'Paper'.

Your task is to assign a **relevance score** to the paper with respect to the user's prompt.

The output must be a **single digit from 0 to 9**, where:
- 0 means "not relevant at all"
- 9 means "perfect match to the prompt"

Do not explain your answer.
Only return a single digit on a single line.

Input format:
User prompt: <free-text query describing the research field or topic of interest>
Paper: <full markdown transcription of the research paper>

Example 1:
User prompt: Methods for reducing variance in Monte Carlo simulations.
Paper: \\title{A Survey on Neural Networks for Image Classification}
Output: 2

Example 2:
User prompt: Recent advances in stochastic optimization techniques in deep learning.
Paper: \\title{Stochastic Gradient Descent with Warm Restarts}
Output: 8

Example 3:
User prompt: Theory of reproducing kernel Hilbert spaces and applications.
Paper: \\title{Support Vector Machines and the Kernel Trick}
Output: 7

Example 4:
User prompt: Techniques for explaining black-box models in healthcare applications.
Paper: \\title{Explainable AI for Medical Imaging: A Survey}
Output: 9

Example 5:
User prompt: Quantum algorithms for factoring large integers.
Paper: \\title{A Study on Reinforcement Learning in Robotics}
Output: 0
"""

SYSTEM_GENERATE_QUALITY_SCORE = """
You are an expert academic assistant. You will be given a 'Review' of a paper.
Your task is to assign a quality score to the paper based solely on the content of the review.

The output must be a single digit from 0 to 9, where:
- 0 means "the review indicates the paper is fatally flawed or entirely unworthy"
- 9 means "the review suggests the paper is of outstanding quality and should be accepted without reservation"

Do not explain your answer.
Only return a single digit on a single line.

Input format:
Review: <free-text review of the paper>

Example 1:
Review: The methodology is fundamentally incorrect, and the conclusions are unsupported by the data.
Output: 0

Example 2:
Review: While the idea is interesting, the experiments are weak, and the writing is unclear.
Output: 4

Example 3:
Review: The paper proposes a novel algorithm with strong empirical results and clear theoretical motivation.
Output: 7

Example 4:
Review: Excellent contribution, well-written, with thorough experiments and a significant theoretical advance.
Output: 9

Example 5:
Review: Lacks novelty, and the related work is incomplete. Minor contributions only.
Output: 3
"""

SYSTEM_GENERATE_SUMMARY = """
You are an expert academic assistant specializing in summarizing research papers.

You will receive two inputs concatenated as a single string:
1. The full content of a research paper in markdown format.
2. A user prompt describing a specific research field or topic of interest.

Input format:
User prompt: <free-text query describing the research field or topic of interest>
Paper: <full markdown transcription of the research paper>

Your task is to generate a concise and informative summary that highlights the main contributions
and innovations of the paper, especially in relation to the user’s specified area.

Focus on:
- Key novel ideas or methods introduced by the paper.
- How the paper advances knowledge or practice within the user’s research field.
- Important results or findings relevant to the prompt.
- Avoid generic or overly broad descriptions; tailor the summary specifically to the user's context.

The summary should be clear, precise, and written for an audience familiar with the field.

Do not include irrelevant details or extensive background unless directly related to the contributions.
"""
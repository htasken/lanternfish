#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lanternfish command line tool's entry point."""

import logging
logging.basicConfig(level=logging.INFO) # For debugging purposes

import llm_api
import google_scholar
import download_papers
import pdf_to_markdown
import argparse
import logging
import os
import asyncio

def command_line_arguments(args=None):
    parser = argparse.ArgumentParser(description="Lanternfish is a LLM research assistant that helps search through large amounts of research papers.")
    parser.add_argument('-p', '--prompt', type=str, required=True, 
        help="<Required> Description of what you want to find the research litterature. For example: 'Find resent papers using LLM's to help with cancer screening'.")
    parser.add_argument('-m', '--model', default='gemma3:4b', type=str,
        help="The Ollama model to use for the LLM. Default is 'gemma3:4b'. See https://ollama.com/models for more models. Quantized models are also available.")
    parser.add_argument('-k', '--top_k', default=5, type=int,
        help="The maximal number of papers to return. Default is 5.")
    parser.add_argument('-r', '--min_relevance', default=0.7, type=float, 
        help="The minimal relevance score of the papers. Default is 0.7.")
    parser.add_argument('-q', '--min_quality', default=0.7, type=float, 
        help="The minimal quality score of the papers. Default is 0.7.")
    parser.add_argument('--max_papers_evaluated', default=5, type=int,
        help="The maximal number of returned from google scholar search for further evaluation. Default is 50.")
    parser.add_argument('--n_samples_score', default=1, type=int,
        help="Number of times to sample from the LLM when computing relevance and quality scores. The final score is averaged. Default is 1.")

    return parser.parse_args(args)

def main(args=None):
    """Main function to run the Lanternfish command line tool."""

    # Parse command line arguments
    args = command_line_arguments(args)

    # Generate search terms and search Google Scholar for papers
    papers = google_scholar.search(args.prompt, args.max_papers_evaluated) 

    # Download the papers
    papers = download_papers.download_papers(papers)
    
    # Convert PDFs to markdown with LaTeX for equations
    papers = pdf_to_markdown.convert_all(papers)

    # Get relevance score of the full papers
    # To be changed:
    # for paper_dict in papers_latex:
    #     score = asyncio.run(llm_api.generate_score(args.prompt, paper_dict["paper"], n_samples = args.n_samples_score, type = "relevance"))
    #     paper_dict["relevance_score"] = score

    # Generate a review of the papers

    # Give the papers a quality score
    # To be changed:
    # for paper_dict in papers_latex:
    #     score = asyncio.run(llm_api.generate_score(args.prompt, paper_dict["review"], n_samples = args.n_samples_score, type = "quality"))
    #     paper_dict["quality_score"] = score

    # Produce summaries of the papers with respect to the prompt

    # Generate a final report 
    
if __name__ == "__main__":
    main()

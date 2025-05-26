#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lanternfish command line tool's entry point."""

import llm_api
import google_scholar
import download_papers
import argparse
import logging

def command_line_arguments(args=None):
    parser = argparse.ArgumentParser(description="Lanternfish is a LLM research assistant that helps search through large amounts of research papers.")
    parser.add_argument('-p', '--prompt', type=str, required=True, 
        help="<Required> Description of what you want to find the research litterature. For example: 'Find resent papers using LLM's to help with cancer screening'.")
    parser.add_argument('-w', '--webinterface', action='store_true',
        help="Run the tool as a webserver with a user-friendly interface.")
    parser.add_argument('-m', '--model', default='llama3.1', type=str,
        help="The Ollama model to use for the LLM. Default is 'llama3.1'. See https://ollama.com/models for more models. Quantized models are also available.")
    parser.add_argument('-k', '--top_k', default=5, type=int,
        help="The maximal number of papers to return. Default is 5.")
    parser.add_argument('-r', '--min_relevance', default=0.7, type=float, 
        help="The minimal relevance score of the papers. Default is 0.7.")
    parser.add_argument('-q', '--min_quality', default=0.7, type=float, 
        help="The minimal quality score of the papers. Default is 0.7.")
    parser.add_argument('--max_papers_evaluated', default=50, type=int,
        help="The maximal number of returned from google scholar search for further evaluation. Default is 50.")
    parser.add_argument('--logging_level', default=30, type=int,
        help="The logging level. Default is '30' and the meaning of the number is as follows: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL.")

    return parser.parse_args(args)

def main(args=None):
    """Main function to run the Lanternfish command line tool."""

    args = command_line_arguments(args)
    logging.basicConfig(level=args.logging_level)

    papers = google_scholar.search(args.prompt, args.model, args.max_papers_evaluated)

    # Check relevance of abstracts and remove irrelevant papers

    # Download the papers
    papers = download_papers.download_papers(papers)

    # Transform papers to LaTeX 

    # Get relevance score of the full papers

    # Generate a review of the papers

    # Give the papers a quality score

    # Produce summaries of the papers with respect to the prompt

    # Generate a final report 
    
if __name__ == "__main__":
    main()

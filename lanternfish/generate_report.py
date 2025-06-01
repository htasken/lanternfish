from markdown_pdf import MarkdownPdf, Section
from llm_api import generate_title, generate_summary_overall
from datetime import datetime

def get_top_k_papers_sorted(papers, top_k):
    sorted_papers = sorted(
        papers,
        key=lambda x: x['total score'] if x['total score'] is not None else float('-inf'),
        reverse=True
    )
    return sorted_papers[:top_k]

def generate_report(prompt, papers, top_k, report_name=None):
    print("Generating PDF-report...")
    title = generate_title(prompt)

    if report_name is None:
        date_and_time = datetime.now().replace(microsecond=0).isoformat().replace("T", "_")
        report_name = f"lanternfish_report_{date_and_time}.pdf"
    else:
        report_name = f"{report_name}.pdf"

    papers = get_top_k_papers_sorted(papers, top_k)
    
    summary_overall = generate_summary_overall(prompt, papers)

    report_markdown = f"# [{title}\n\n"

    report_markdown += f"*Prompt: {prompt}* <br>\n"
    n_papers = len(papers)
    report_markdown += f"*Lanternfish here presents the top {n_papers} papers.*\n\n"

    report_markdown += f"{summary_overall}\n\n"
    
    for paper in papers:
        paper_info = paper['google scholar info']['bib']
        report_markdown += f"## [{paper_info['title']}]({paper['url']})\n"
        report_markdown += f"*Year:* {paper_info['pub_year']} "
        if paper_info['venue']:
            report_markdown += f"*Journal:* {paper_info['venue']} "
        report_markdown += "*Authors:* "
        for author in paper_info['author']:
            report_markdown += f" {author}, "
        report_markdown = report_markdown.rstrip(", ") + "\n"
        report_markdown += f"Total Score: **{paper['total score']}**/10 "
        report_markdown += f"Quality Score: **{paper['quality score']}**/10 "
        report_markdown += f"Relevance Score: **{paper['relevance score']}**/10\n\n"
        report_markdown += f"### Summary\n{paper['summary']}\n\n"

    report_pdf = MarkdownPdf(optimize=True)

    report_pdf.add_section(Section(report_markdown, toc=False))

    report_pdf.save(report_name)

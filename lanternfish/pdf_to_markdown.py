from pix2text import Pix2Text
import multiprocessing
import functools
import os
from common import clear_folder

def convert_all(paths_pdf, output_dir="lanternfish/converted_papers", processes=10):
    """
    Convert a list of PDF files to markdown with equations in latex and saves
    the files in 'output_dir'.

    Args:
        paths_pdf (list): List of paths to the PDF files to convert.
        output_dir (str): Directory where converted markdown files will be saved.
        processes (int): Number of processes to use for conversion.

    Returns:
        list: Paths to converted files.
    """
    if os.path.exists(output_dir):
        clear_folder(output_dir)
    else:
        os.makedirs(output_dir)

    paths_converted_files = []
    for path_pdf in paths_pdf:
        pdf_filename = os.path.basename(path_pdf)
        md_dir = os.path.join(output_dir, f"{pdf_filename}").removesuffix(".pdf")
        if not os.path.exists(md_dir):
            os.makedirs(md_dir)
        md_path = os.path.join(md_dir, "output.md")
        paths_converted_files.append(md_path)

    with multiprocessing.Pool(processes=processes) as pool:
        convert_func = functools.partial(convert, output_dir=output_dir)
        pool.map(convert_func, paths_pdf)
    
    return paths_converted_files

def convert(path_pdf, output_dir="lanternfish/converted_papers"):
    """
    Convert a PDF file to markdown with equations in latex and saves the file
    as "'output_dir'/<pdf_filename>/output.md".

    Args:
        path_pdf (str): The path to the PDF file to convert.

    Returns:
        str: The markdown representation of the PDF content.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf_filename = os.path.basename(path_pdf)
    md_dir = os.path.join(output_dir, f"{pdf_filename}").removesuffix(".pdf")
    if not os.path.exists(md_dir):
        os.makedirs(md_dir)

    p2t = Pix2Text.from_config(enable_formula=True)
    doc = p2t.recognize_pdf(
        path_pdf,
        table_as_image=True,
    )
    markdown = doc.to_markdown(md_dir)
    
    return markdown


if __name__ == "__main__":
    # Example usage
    import os
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_latex.py <path_to_pdf>")
        sys.exit(1)
    
    path_pdf = sys.argv[1]
    
    if not os.path.isfile(path_pdf):
        print(f"File not found: {path_pdf}")
        sys.exit(1)
    
    markdown_content = convert(path_pdf)
    print(markdown_content) 

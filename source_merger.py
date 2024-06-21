import os
import argparse
import logging
from jsmin import jsmin
from csscompressor import compress as cssmin
from htmlmin import minify as htmlmin
from pyminifier import minification as pymin
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import magic
from jinja2 import Environment, FileSystemLoader
import markdown
import pdfkit
import tempfile
import shutil
from git import Repo
from git.exc import GitCommandError
from typing import List, Optional
import requests
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

file_types = {
    ".html": "HTML",
    ".css": "CSS",
    ".js": "jsx",
    ".ejs": "ejs",
    ".md": "markdown",
    ".py": "python",
    ".txt": "txt",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
    ".cs": "csharp",
    ".vb": "vb",
    ".vbhtml": "vbhtml",
    ".ui": "xml",
    ".xml": "xml",
    ".json": "json",
    ".yml": "yaml",
    ".ui": "xml",
    ".ts": "typescript",
    ".bat": "batch",
    ".ps1": "powershell",
}

def clone_repository(repo_url: str, branch: Optional[str] = None, temp_dir: str = None) -> str:
    """
    Clone a remote repository to a temporary directory.
    
    :param repo_url: URL of the remote repository
    :param branch: Optional branch name to checkout
    :return: Path to the cloned repository
    """

    if not temp_dir:
        temp_dir = tempfile.mkdtemp()
    try:
        logger.info(f"Cloning repository: {repo_url}")
        repo = Repo.clone_from(repo_url, temp_dir)
        if branch:
            logger.info(f"Checking out branch: {branch}")
            repo.git.checkout(branch)
        return temp_dir
    except GitCommandError as e:
        logger.error(f"Error cloning repository: {e}")

def process_remote_repository(**kwargs) -> None:
    """
    Process files from a remote repository.
    
    :param repo_url: URL of the remote repository
    :param branch: Optional branch name to checkout
    :param kwargs: Additional arguments for findFiles function
    """
    
    repo_url = kwargs.get('repo')
    branch = kwargs.get('branch')
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            kwargs['start_dir'] = temp_dir
            clone_repository(repo_url, branch, temp_dir)
            findFiles(**kwargs)
    except Exception as e:
        print(f"An error occurred: {e}")

def processFile(filename, extensions, minify):
    if any(filename.endswith(ext) for ext in extensions):
        try:
            with open(filename, "r", encoding='utf-8', errors="ignore") as f:
                file_contents = f.readlines()
                if minify:
                    file_contents = [compressCode(line, getFileType(filename)) for line in file_contents]
                return filename, ''.join(file_contents)
        except UnicodeDecodeError:
            try:
                with open(filename,
                            "r",
                            encoding='utf-16',
                            errors="ignore") as f:
                        file_contents = f.readlines()
                        if minify:
                            file_contents = [compressCode(line, getFileType(filename)) for line in file_contents]
                        return filename, ''.join(file_contents)
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
    return None, None

def getFileType(file_path):
    # First, try to determine the file type by extension
    file_type = os.path.splitext(file_path)[-1].lower()
    if file_type in file_types:
        return file_types[file_type]
    
    # If that fails, use libmagic to determine the file type
    try:
        mime = magic.Magic(mime=True)
        file_mime = mime.from_file(file_path)
        if 'text' in file_mime:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # Read first 1024 bytes
                if '<?php' in content:
                    return 'php'
                elif '#!/usr/bin/env python' in content or 'import ' in content:
                    return 'python'
                elif '<html' in content.lower():
                    return 'HTML'
                elif '{' in content and '}' in content:
                    return 'json'
        return 'text'  # Default to text if we can't determine a more specific type
    except Exception as e:
        logger.error(f"Error determining file type for {file_path}: {e}")
        return None

def writeFileContents(output_file, file_contents, file_type, relative_path, output_format, minify):
    if minify:
        file_contents = compressCode(file_contents, file_type)
    
    if output_format in ['markdown', 'md']:
        output_file.write(f"## {relative_path}\n\n")
        if file_type == "txt":
            output_file.write(f"> {file_contents.replace('\n', '\n>\n> ')}\n\n")
        else:
            file_contents = file_contents.replace("```", "` ` `")
            output_file.write(f"```{file_type}\n{file_contents}\n```\n\n")
    elif output_format == 'html':
        output_file.write(f"<h2>{relative_path}</h2>\n")
        output_file.write(f"<pre><code class='{file_type}'>{file_contents}</code></pre>\n")
    elif output_format == 'txt':
        output_file.write(f"{relative_path}:\n")
        output_file.write(f"\t{file_contents.replace('\n', '\n\t')}\n\n")

def writeFileToOutput(file_path, output_file, minify, base_dir, output_format):
    file_type = getFileType(file_path)
    if not file_type:
        return
    
    relative_path = os.path.relpath(file_path, base_dir)
    
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            file_contents = f.read()
            writeFileContents(output_file, file_contents, file_type, relative_path, output_format, minify)
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding='utf-16', errors='ignore') as f:
                file_contents = f.read()
                writeFileContents(output_file, file_contents, file_type, relative_path, output_format, minify)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
def compressCode(code, file_type):
    try:
        if file_type == "HTML":
            return htmlmin(code, remove_comments=True, remove_empty_space=True)
        elif file_type == "CSS":
            return cssmin(code)
        elif file_type == "jsx":
            return jsmin(code)
        elif file_type == "python":
            code = pymin.remove_comments_and_docstrings(code)
            code = pymin.remove_blank_lines(code)
            code = pymin.reduce_operators(code)
            code = pymin.dedent(code)
            code = pymin.fix_empty_methods(code)
            return pymin.join_multiline_pairs(code)
    except Exception as e:
        logger.error(f"Error compressing code: {e}")
    return code

def filterFiles(files, ignore_files):
    return [file_path for file_path in files if os.stat(file_path).st_size != 0 and os.path.basename(file_path) not in ignore_files]

def filterDirectories(dirs, ignore_dirs):
    return [d for d in dirs if d not in ignore_dirs]

def findFiles(**kwargs):
    start_dir = kwargs.get('start_dir', '.')
    ignore_dirs = kwargs.get('ignore_dirs', [])
    ignore_files = kwargs.get('ignore_files', [])
    all_types = kwargs.get('all_types', False)
    extensions = kwargs.get('extensions', [])
    exclude_extensions = kwargs.get('exclude_extensions', [])
    name = kwargs.get('name')
    minify = kwargs.get('minify', False)
    out = kwargs.get('out', '.')
    recursive = kwargs.get('recursive', False)
    additionalFiles = kwargs.get('files', [])
    output_format = kwargs.get('output_format', 'txt')
    foundFiles = {}

    output_file = os.path.join(out, f"{name}.{output_format}")
    ignore_files.append(os.path.basename(output_file))

    if all_types:
        extensions = list(file_types.keys())
    extensions = [ext for ext in extensions if ext not in exclude_extensions]
    
    def should_process_file(file_path):
        return (os.path.isfile(file_path) and
                os.stat(file_path).st_size != 0 and
                os.path.basename(file_path) not in ignore_files and
                (all_types or any(file_path.endswith(ext) for ext in extensions)))

    all_files = []
    if recursive:
        for dirpath, dirs, files in os.walk(start_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            all_files.extend([os.path.join(dirpath, f) for f in files if should_process_file(os.path.join(dirpath, f))])
    else:
        all_files = [os.path.join(start_dir, f) for f in os.listdir(start_dir) if should_process_file(os.path.join(start_dir, f))]

    if additionalFiles:
        all_files.extend([f for f in additionalFiles if should_process_file(f)])

    total_files = len(all_files)
    with tqdm(total=total_files, desc="Processing files", unit="file", colour='green', ncols=100) as pbar:
        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(processFile, file_path, extensions, minify): file_path for file_path in all_files}
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    filename, file_contents = future.result()
                    if filename:
                        foundFiles[filename] = file_contents
                    pbar.update(1)
                    pbar.set_postfix_str(f"Current file: {os.path.basename(file_path)}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

    finalFiles = {}
    for file_path, file_contents in foundFiles.items():
        if file_contents not in finalFiles.values() and f"{name}.{output_format}" not in file_path:
            finalFiles[file_path] = file_contents

    try:
        if output_format in ['markdown', 'md']:
            with open(output_file, "w", encoding='utf-8') as md_file:
                md_file.write(f"# {name}\n\n")
                for file_path, file_contents in finalFiles.items():
                    writeFileToOutput(file_path, md_file, minify, start_dir, output_format)
        elif output_format == 'html':
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('template.html')
            with open(output_file, "w", encoding='utf-8') as html_file:
                html_content = template.render(title=name, files=finalFiles)
                html_file.write(html_content)
        elif output_format == 'pdf':
            md_content = f"# {name}\n\n"
            for file_path, file_contents in finalFiles.items():
                md_content += f"## {os.path.relpath(file_path, start_dir)}\n\n"
                md_content += f"```{getFileType(file_path)}\n{file_contents}\n```\n\n"
            html_content = markdown.markdown(md_content)

            path_wkhtmltopdf = r'C:\Users\Aldiwein\Desktop\sourcecode_merger-master\.vscode\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            pdfkit.from_string(html_content, output_file, configuration=config)
        elif output_format == 'txt':
            with open(output_file, "w", encoding='utf-8') as txt_file:
                for file_path, file_contents in finalFiles.items():
                    writeFileToOutput(file_path, txt_file, minify, start_dir, output_format)
        logger.info(f"Output file created: {output_file}")
        os.startfile(output_file)
    except Exception as e:
        logger.error(f"Error writing output file {output_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Search for files with specific extensions in a directory, its subdirectories, or a remote repository.')
    parser.add_argument('-i', '--ignore_dirs', metavar='ignore', type=str, nargs='+', default=[".venv", ".vscode", ".git"], help='list of directories to ignore')
    parser.add_argument('-s', '--start_dir', metavar='start_dir', type=str, default=os.getcwd(), help='the starting directory to search in')
    parser.add_argument('-x', '--ignore_files', metavar='ignore_files', type=str, nargs='+', default=["source_merger.py", "README.md"], help='list of files to ignore')
    parser.add_argument('-a', '--all_types', action='store_true', help='include all file types')
    parser.add_argument('-e', '--extensions', metavar='types', type=str, nargs='+', default=['.html', '.css', '.js', '.ejs', '.py', '.txt', '.md'], help='list of file types to include')
    parser.add_argument('-E', '--exclude_extensions', metavar='exclude', type=str, nargs='+', default=[], help='list of file types to exclude')
    parser.add_argument('-n', '--name', metavar='name', type=str, default='SourceCode', help='name of the output file')
    parser.add_argument('-m', '--minify', action='store_true', help='minify the files')
    parser.add_argument('-H', '--Help', action='store_true', help='show this help message and exit')
    parser.add_argument('-o', '--out', metavar='out', type=str, default=os.getcwd(), help='output directory')
    parser.add_argument('-r', '--recursive', action='store_true', default=False, help='search recursively in directories')
    parser.add_argument('-f', '--files', metavar='files', type=str, nargs='+', help='list of additional files to include by path')
    parser.add_argument('--output_format', choices=['markdown', 'md', 'html', 'pdf', 'txt'], default='txt', help='output format (markdown, html, pdf, or text)')
    parser.add_argument('--repo', type=str, help='URL of the remote Git repository')
    parser.add_argument('--branch', type=str, help='Branch name to checkout (optional)')
    args = parser.parse_args()
    
    if args.Help:
        parser.print_help()
    elif args.repo:
        process_remote_repository(**vars(args))
    else:
        findFiles(**vars(args))
if __name__ == "__main__":
    main()
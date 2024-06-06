"""
This script searches for files with specific extensions in a directory and its subdirectories,
and writes their contents to a markdown file. It also provides options to ignore certain directories
and files, include all file types, specify the file types to include, and minify the files.

The script takes command line arguments to customize the search behavior. The main function parses
the command line arguments and calls the search_files function to perform the search and write the
file contents to a markdown file.
"""

import os
import argparse
from jsmin import jsmin
from csscompressor import compress as cssmin
from htmlmin import minify as htmlmin
from rjsmin import jsmin as rjsmin

def get_file_type(file_path):
    """
    Get the file type based on the file extension.

    Args:
        file_path (str): The path of the file.

    Returns:
        str: The file type.
    """
    file_type = os.path.splitext(file_path)[1].replace(".", "")
    file_types = {
        "html": "HTML",
        "css": "CSS",
        "js": "jsx",
        "ejs": "ejs",
        "py": "python",
        "md": "markdown",
        "txt": "text",
        "cpp": "cpp",
        "c": "c",
        "h": "c",
        "hpp": "cpp",
        "java": "java",
        "cs": "csharp",
        "vb": "vb",
        "vbhtml": "vbhtml",
        "ui": "xml",
        "xml": "xml",
        "json": "json",
        "yml": "yaml",
        "ui": "xml",
    }
    return file_types.get(file_type, None)

def write_file_contents_to_md(file_path, md_file, minify):
    """
    Write the contents of a file to a markdown file.

    Args:
        file_path (str): The path of the file.
        md_file (file): The markdown file to write to.
        minify (bool): Whether to minify the file contents.
    """
    file_type = get_file_type(file_path)
    if not file_type:
        return
    
    md_file.write(f"## {file_path}\n\n")
    with open(file_path, "r", encoding='utf-8') as f:
        file_contents = f.read()
        if minify:
            file_contents = minify_file_contents(file_contents, file_type)
        md_file.write(f"```{file_type}\n{file_contents}\n```\n\n")

def minify_file_contents(contents, file_type):
    """
    Minify the contents of a file based on its file type.

    Args:
        contents (str): The contents of the file.
        file_type (str): The file type.

    Returns:
        str: The minified contents.
    """
    if file_type == "HTML":
        return htmlmin(contents, remove_comments=True, remove_empty_space=True)
    elif file_type == "CSS":
        return cssmin(contents)
    elif file_type == "jsx":
        return jsmin(contents)
    elif file_type == "python":
        return rjsmin(contents)
    return contents

def filter_ignored_files(files, ignore_files):
    """
    Filter out ignored files from a list of files.

    Args:
        files (list): The list of files.
        ignore_files (list): The list of files to ignore.

    Returns:
        list: The filtered list of files.
    """
    return [f for f in files if os.stat(f).st_size != 0 and os.path.basename(f) not in ignore_files]

def filter_ignored_directories(dirs, ignore_dirs):
    """
    Filter out ignored directories from a list of directories.

    Args:
        dirs (list): The list of directories.
        ignore_dirs (list): The list of directories to ignore.

    Returns:
        list: The filtered list of directories.
    """
    return [d for d in dirs if d not in ignore_dirs]

def search_files(start_dir, ignore_dirs, ignore_files, all_types, extensions, name, minify):
    """
    Search for files with specific extensions in a directory and its subdirectories,
    and write their contents to a markdown file.

    Args:
        start_dir (str): The directory to start the search from.
        ignore_dirs (list): The list of directories to ignore.
        ignore_files (list): The list of files to ignore.
        all_types (bool): Whether to include all file types.
        extensions (list): The list of file types to include.
        name (str): The name of the markdown file to write to.
        minify (bool): Whether to minify the files.
    """
    markdown_file = f"{name}.md"
    if all_types:
        extensions = ['.html', '.css', '.js', '.ejs', '.py', '.txt', '.md', '.json', '.xml', '.yml', '.yaml', '.csv', '.ts', '.tsx', '.jsx', '.php', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.vb', '.vbhtml', '.ui']

    with open(markdown_file, "w", encoding='utf-8') as md_file:
        md_file.write(f"# {name}\n\n")
        for dirpath, dirs, files in os.walk(start_dir):
            dirs[:] = filter_ignored_directories(dirs, ignore_dirs)
            files = filter_ignored_files([os.path.join(dirpath, f) for f in files], ignore_files)
            for filename in files:
                if any(filename.endswith(ext) for ext in extensions):
                    write_file_contents_to_md(filename, md_file, minify)
    os.startfile(markdown_file)

def main():
    """
    The main function that parses command line arguments and calls the search_files function.
    """
    parser = argparse.ArgumentParser(description='Search for files with specific extensions in a directory and its subdirectories.')
    parser.add_argument('-i', '--ignore', metavar='ignore', type=str, nargs='+', help='list of directories to ignore')
    parser.add_argument('-s', '--start_dir', metavar='start_dir', type=str, default='.', help='the directory to start the search from')
    parser.add_argument('-x', '--ignore_files', metavar='ignore_files', type=str, nargs='+', default=["source_merger.py"], help='list of files to ignore')
    parser.add_argument('-a', '--all_types', action='store_true', help='include all file types')
    parser.add_argument('-e', '--extensions', metavar='types', type=str, nargs='+', default=['.html', '.css', '.js', '.ejs', '.py'], help='list of file types to include')
    parser.add_argument('-n', '--name', metavar='name', type=str, default='project', help='name of the markdown file to write to')
    parser.add_argument('-m', '--minify', action='store_true', help='minify the files')
    parser.add_argument('-H', '--Help', action='store_true', help='show this help message and exit')
    args = parser.parse_args()

    # Example_all: python source_merger.py -s "C:\Users\user\Documents\project" -i "node_modules" -x "source_merger.py" -a -n "project"
    # Example: python source_merger.py -s "C:\Users\user\Documents\project" -i "node_modules" -x "source_merger.py" -e ".html" ".css" ".js" ".ejs" ".py" -n "project"

    ignore_dirs = args.ignore if args.ignore else []
    ignore_files = args.ignore_files if args.ignore_files else []
    
    if args.Help:
        parser.print_help()
    else:
        search_files(args.start_dir, ignore_dirs, ignore_files, args.all_types, args.extensions, args.name, args.minify)

if __name__ == "__main__":
    main()

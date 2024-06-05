# Project File Search

This project provides a Python script that searches for files with specific extensions in a directory and its subdirectories, writing their contents to a markdown file. It includes options to ignore certain directories and files, include all file types, specify the file types to include, and minify the files.

## Features

- **Directory and File Search**: Search through a specified directory and its subdirectories.
- **File Extension Filtering**: Specify which file types to include in the search.
- **Ignore Directories and Files**: Option to exclude certain directories and files from the search.
- **Minify Files**: Minify the contents of files before writing them to the markdown file.
- **Customizable Output**: Specify the name of the output markdown file.

## Usage

To run the script, use the following command:

```bash
python project_search.py [options]
```

### Options

- `-i, --ignore <ignore>`: List of directories to ignore.
- `-s, --start_dir <start_dir>`: The directory to start the search from (default: current directory).
- `-x, --ignore_files <ignore_files>`: List of files to ignore (default: `project_search.py`).
- `-a, --all_types`: Include all file types.
- `-e, --extensions <types>`: List of file types to include (default: `.html, .css, .js, .ejs, .py`).
- `-n, --name <name>`: Name of the markdown file to write to (default: `project`).
- `-m, --minify`: Minify the files.
- `-H, --Help`: Show this help message and exit.

### Example

To search the `C:\Users\user\Documents\project` directory, ignore the `node_modules` directory, exclude `project_search.py` file, include `.html`, `.css`, `.js`, `.ejs`, and `.py` file types, and name the output markdown file `project`, use the following command:

```bash
python project_search.py -s "C:\Users\user\Documents\project" -i "node_modules" -x "project_search.py" -e ".html" ".css" ".js" ".ejs" ".py" -n "project"
```

## Functions

### `get_file_type(file_path)`

Returns the file type based on the file extension.

### `write_file_contents_to_md(file_path, md_file, minify)`

Writes the contents of a file to a markdown file.

### `minify_file_contents(contents, file_type)`

Minifies the contents of a file based on its file type.

### `filter_ignored_files(files, ignore_files)`

Filters out ignored files from a list of files.

### `filter_ignored_directories(dirs, ignore_dirs)`

Filters out ignored directories from a list of directories.

### `search_files(start_dir, ignore_dirs, ignore_files, all_types, extensions, name, minify)`

Searches for files with specific extensions in a directory and its subdirectories, and writes their contents to a markdown file.

## Installation

Ensure you have Python installed on your system. Install the required dependencies using pip:

```bash
pip install jsmin csscompressor htmlmin rjsmin
```

## Running the Script

Run the script using the command line, specifying the desired options as outlined above.

## License

This project is licensed under the MIT License.

## Author

Severin Urbanek

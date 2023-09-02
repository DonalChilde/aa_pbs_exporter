"""

translate from parsed to collated-compact-expanded with debug.txt in output directory

input_path - file or directory
output_path - directory
recurse_limit - int: 0 input_path , 1 input_path subdir,-1 no limit
    make this a filter that can work on path.glob results.
parent_include - int: include levels of parent in output path.
    e.g called with /foo/bar/2023.03 /output/dir recurse=0 parent=1 results in output/dir/2023.03/output_files.
overwrite bool



overall cli interface:
extract
parse
translate

keep it simple, add complexity later if needed.
extract and parse are the big time eaters.

investigate tools to compare files between two dirs, e.g. between two runs of translate.
    

    
"""

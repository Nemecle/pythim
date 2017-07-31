#!/usr/bin/python
"""
Gallery generation
"""

import json
import os

def list_files(startpath):
    """
    list folders with hierarchy
    https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python

    """

    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def get_directory_tree(path):
    """
    Return a list of files in given folder with hierarchy preserved

    path -- path to list

    """

    # directories = [path]
    # tree = []

    # while directories:
    #     dir = directories.pop(0)
    #     res  = os.walk(dir)

    #     tree.append((str(dir), res[0], res[1]))
    #     directories.extend(res[0]) 

    file_list =[] 

    for dir_, _, files in os.walk(path):
        for filen in files:
            relative_path = os.path.relpath(dir_, path)
            file_list.append(os.path.join(relative_path, filen))

    return file_list

def main():
    """
    generate gallery based on configuration file.

    """

    # with open("structure.json") as structure:
    #     data = json.load(structure)

    files = get_directory_tree("/media/sf_music/src")
    galleries = {}

    for index, f in enumerate(files):
        current_file = f.split("/")
        for dir in current_file[:-1]:
            if dir not in galleries:
                galleries[dir] = []

            galleries[dir].append(f)

    print str(galleries)



    print str(files)

    return


if __name__ == '__main__':
    main()

#!/usr/bin/python
"""
Gallery generation
"""

import json
import os
import jinja2

#Jinja decoding issues
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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

    file_list = []

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

    model = open("gallery.html")
    template = jinja2.Template(model.read())


    for f in files:
        current_file = f.split("/")
        for cdir in current_file[:-1]:
            if cdir not in galleries:
                galleries[cdir] = []

            galleries[cdir].append(f)

    # print str(galleries)

    for gallery in galleries:
        files = galleries[gallery]
        gallery_content = template.render(files=files)
        file = open("export/" + str(gallery) + ".html","w")
        file.write(gallery_content)
        file.close()
        print("created file " + str("export/") + str(gallery) + ".html")


    # print str(files)

    return


if __name__ == '__main__':
    main()

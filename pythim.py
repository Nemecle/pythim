#!/home/nemecle/anaconda3/bin/python3.6
#!/usr/bin/python3
# C:\Users\Nemecle\Anaconda3\python.exe
"""
Static gallery generation in python
put images in img/ and modify galleries.json

"""

import json
import os
import re
import jinja2
from pprint import pprint
import hashlib
import shutil


from multiprocessing import Pool
from operator import itemgetter
from PIL import Image
from PIL import ExifTags



#Jinja decoding issues
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


## test config
# CONFIG_FILE = "galleries.json"

TEMPLATE_DIR = "templates/"
OUTPUT_DIR = "output/"
# BASE_DIR  = "export/html/"
# HTML_DIR  = BASE_DIR + ""
FILE_DIR = "img/"
IMAGE_DIR = OUTPUT_DIR + "img/"
THUMB_DIR = OUTPUT_DIR + "thumbnails/"
IMG_HTML_DIR = OUTPUT_DIR + "i/"
THUMB_SIZE = 1000

NO_THUMBS = True


def get_mtime(path):
    """
    return modification time (mtime)
    """

    return os.stat(path).st_ctime


def get_hash(s):
    """
    return sha256 hash of given string
    """

    return str(int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16) % 10**16)


def get_directory_tree(path):
    """
    Return a list of files in given folder with hierarchy preserved
    """

    file_list = []

    try:
        os.stat(path)
    except:
        print("(get_directory_tree) {} does not exist.".format(path))

    for dir_, _, files in os.walk(path):
        for filen in files:
            relative_path = os.path.relpath(dir_, path)
            file_list.append(os.path.join(relative_path, filen))
    return file_list


def get_directory_tree_with_time(path):
    """
    Return a list of files with their mtime in given folder with hierarchy preserved
    format: [[<file_path, <mtime>],... ]
    """

    file_list = []

    try:
        os.stat(path)
    except:
        print("(get_directory_tree) {} does not exist.".format(path))

    for dir_, _, files in os.walk(path):
        for filen in files:
            relative_path = os.path.relpath(dir_, path)
            file_path = os.path.join(relative_path, filen)

            file_list.append([file_path, get_mtime(dir_ + "/" + filen)])
    # print("(get_directory_tree) returning {}".format(str(file_list)))
    return file_list


def create_thumbnail(img, directory, force=False):
    """
    create a thumbnail for a given img and store in directory
    EXIF code:
      https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image/6218425#6218425

    TODO: optimise, requires to create thumbnail even
    if it already exists to get infos
      
    """

    # filename = img.split("/")[-1]
    # print("thumbnailing {} to {}".format(filename, directory))

    try:
        #   print("opening")
        image = Image.open(img)




        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

    except Exception as e:
        pass
        # print("(thumbnail) EXIF: " + str(e))

    try:
        #print("thumbnail'd")
        image.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.NEAREST)
        image = image.convert('RGB')

        #print("saved")
        filename = get_hash(img) + ".jpg"

        if os.path.isfile(directory + get_hash(img) + ".jpg") and not force:
            print("(create_thumbnail) thumbnail for {} already exists".format(img))
        else:
            image.save(directory + filename)

        thumb = Image.open(directory + filename)
        width, height = thumb.size

        return filename, width, height

    except Exception as e:
        print("(create_thumbnail) saving: " + str(e))

    return -1


def get_thumbnail_hash(img, thumb_directory, force=False):
    """
    create a thumbnail for a given img and store in directory
    EXIF code:
      https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image/6218425#6218425

    TODO: optimise, requires to create thumbnail even
    if it already exists to get infos
      
    """

    # filename = img.split("/")[-1]
    # print("thumbnailing {} to {}".format(filename, directory))

    try:
        #   print("opening")
        image = Image.open(img)
        thash = get_hash(img)

        filename = thash + ".jpg"

        thumb = Image.open(thumb_directory + filename)
        width, height = thumb.size

        return thash, width, height

    except Exception as e:
        pass
        print("(get_thumbnail) {} as {}: ".format(img, thumb_directory + filename) + str(e))

    return -1


def get_file_list(galleries):
    """
    get list of images of all galleries combined

    """

    file_list = []
    for _, gal in enumerate(galleries):
        for img in galleries[gal]:
            file_list.append(img)

    return file_list


def main():
    """
    generate gallery based on configuration file.

    """

    image_data    = []
    galleries = {}

    with open("gallery.yml", "r") as gallery_file:
        for line in gallery_file:
            i_path, categories, _ = line.split(";")
            im_path = i_path.replace("\"", "") 
            img_path = im_path.strip()


            if not NO_THUMBS:
                create_thumbnail(IMAGE_DIR + img_path, THUMB_DIR)

            cat = categories.split(",")

            for category in cat:
                category = category.replace("\"", "")
                category = category.strip()
                if not category in galleries:
                    galleries[category] = []

                galleries[category].append({"image":  img_path,\
                                            "thumb":  "",\
                                            "thumb_hash":  "",\
                                            "thumb_width":  0,\
                                            "thumb_height": 0})
                # print("appended {} to {}".format(img_path, category))


 #     for _, gal in enumerate(galleries):
#         print(gal)
#         for img in galleries[gal]:
#             print("  " + img)

            # image_data.append({"file": file_path, "categories": categories.split(",")})

    # TODO: expand patterns such as '*'
    #       automatically create directories

    image_model = open(TEMPLATE_DIR + "image_display.j2.html")
    template = jinja2.Template(image_model.read())

    progress = 0
    for image in get_file_list(galleries):
        file_path = image["image"]
        try:
            if not os.path.isfile(IMAGE_DIR + file_path):
                shutil.copy2(FILE_DIR + file_path,\
                             IMAGE_DIR + file_path)
            else:
                # print("(skipped) " + FILE_DIR + file_path)
                pass

        except Exception as e:
            print("Failed copying file: " + str(e))

        thumb = get_thumbnail_hash(IMAGE_DIR + file_path, THUMB_DIR)

        if thumb is not -1:
            thpath, thwidth, thheight = thumb
        else:
            print("failed to get thumbnail")
            continue;

        image["thumb_hash"] = thpath + ".html"
        image["thumb"] = thpath + ".jpg"
        image["thumb_width"] = thwidth
        image["thumb_height"] = thheight

        title = re.sub(r"(\.jpg|\.png)", "", file_path, flags=re.IGNORECASE)
        file_name = re.sub(r"(\.jpg|\.png)", "", image["thumb"], flags=re.IGNORECASE)

        # print(title, "img/" + file_path, ["placeholder"], "placeholder, Also")
        image_page = template.render(
                              title=title, \
                              image_link="img/" + file_path, \
                              tags=["placeholder"], \
                              description="placeholder, Also"
                              )

        file = open(IMG_HTML_DIR + thpath + ".html","w")
        file.write(image_page)
        file.close()
        # print("wrote {} with title {} and file_name {}".format(OUTPUT_DIR + file_name + ".html", title, file_name))


    # generate gallery
    model = open(TEMPLATE_DIR + "gallery.j2.html")
    template = jinja2.Template(model.read())

    print ("########### PRINTING GALLERIES ###############")
    for name in galleries:
        img_list = galleries[name]

        # pprint(name)
        # pprint(img_list)
        gallery_content = template.render(
                              name=name, \
                              images=img_list
                              )

        file = open(OUTPUT_DIR + name + ".html","w")
        file.write(gallery_content)
        file.close()


    return


if __name__ == '__main__':
    main()

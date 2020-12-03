import os
from flask import flash
from PIL import Image


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_thumbnail(file):
    size = (128, 128)

    for infile in file:
        outfile = os.path.splitext(infile)[0] + ".thumbnail"
        if infile != outfile:
            try:
                with Image.open(infile) as im:
                    im.thumbnail(size)
                    im.save(outfile, "JPEG")
            except OSError:
                print(f'cannot create thumbnail for {infile}')

        return outfile

import os
import PIL
import re

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy.orm import selectinload

from werkzeug.utils import secure_filename

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Image, Person
from cisca_admin.helpers import allowed_file


bp = Blueprint('upload', __name__, url_prefix='/upload')


@ bp.route('/id/<int:person_id>', methods=('GET', 'POST'))
@ login_required
def id(person_id):
    if request.method == 'POST':
        file = request.files.get('file')
        filename = ''
        message = 'No image selected.'

        # Check if a file is submitted
        if file and file.filename == '':
            message = 'Please select an image file.'
        # Check if jpg or png file
        elif file and not allowed_file(file.filename):
            message = 'Please select a "jpg", "jpeg", or "png" image file.'
        elif file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            filename_list = filename.split('.')
            filename_list[0] = person_id
            filename_list[1] = filename_list[1].lower()
            # Change 'jpeg' to 'jpg'
            if filename_list[1] == 'jpeg':
                filename_list[1] = 'jpg'
            filename = '.'.join(map(str, filename_list))

            # Check if person already has an image
            query = Person.query.options(selectinload(
                Person.image)).filter(Person.person_id == person_id).first()
            if query.image:
                # If person already has image, return to person page
                flash(
                    f'{query.first_name.capitalize()} {query.family_name.capitalize()} already has an image.')
                return redirect(url_for('person.id', person_id=person_id))
            # Save the file
            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename))

            # Set size for thumbnail
            size = (128, 128)

            with open(f"{os.path.join(current_app.config['UPLOAD_FOLDER'], filename)}") as infile:
                # Extract the filename from the object
                infile_str = str(infile.name)

                try:
                    with PIL.Image.open(infile_str) as im:
                        # If png, convert to jpg
                        png_file = ''

                        if re.search("png$", filename):
                            im = im.convert("RGB")

                            # Change filename to *.jpg
                            filename_list = filename.split('.')
                            filename_list[1] = 'jpg'
                            filename = '.'.join(map(str, filename_list))

                            # Change infile_str path to contain jpg instad of png
                            png_file = infile_str
                            infile_str = re.sub("png", "jpg", infile_str)

                        # Square the image
                        width, height = im.size

                        if width > height:
                            delta = width - height
                            left = int(delta/2)
                            upper = 0
                            right = height + left
                            lower = height
                        else:
                            delta = height - width
                            left = 0
                            upper = int(delta/2)
                            right = width
                            lower = width + upper

                        im = im.crop((left, upper, right, lower))

                        # Convert to thumbnail and save
                        im.thumbnail(size, PIL.Image.ANTIALIAS)
                        im.save(infile_str, "JPEG")

                        # Delete png file if exist
                        if os.path.exists(png_file):
                            os.remove(png_file)
                        else:
                            print("The png file does not exist")

                        # Commit thumbnail to images table
                        new_image = Image(
                            image_file=filename, person_id=person_id)
                        db_session.add(new_image)
                        db_session.commit()

                except OSError:
                    print(f'Cannot create thumbnail for {infile_str}')

            query = Person.query.filter(
                Person.person_id == person_id).first()

            flash(
                f'Image for {query.first_name.capitalize()} {query.family_name.capitalize()} is saved.')
            return redirect(url_for('person.id', person_id=person_id))

        flash(message)

    query = Person.query.filter(Person.person_id == person_id).first()
    return render_template('people/upload.html', person=query)

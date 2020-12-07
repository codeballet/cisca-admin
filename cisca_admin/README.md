# CISCA Admin Web App

The CISCA Admin Web App keeps track of students in a school. The app is written in Python / Flask, and uses the SQLite database.
There is an administration interface where priviledged users can add and edit users. Normal users only have access to the student data.
Due to the sensitive nature of the data that will be stored, only pre-registered users can log on and access the data.

## Installation and use

In order to use the app, you need to:

- Install all dependencies.
- Create an `static/images` folder for the images to be stored in.
- For production, create a `instance/config.py` file with desired configurations.

## Licence

MIT

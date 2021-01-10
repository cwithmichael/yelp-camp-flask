# yelp-camp-flask

This project is based off of the wonderful YelpCamp project presented in the [Web Developer Boot Camp course on Udacity](https://www.udemy.com/share/101W9CBUETdVtRTXQ=/)
The original project uses Node.js and Express. I decided to do the project with Python and Flask. The front-end is mostly the same. There weren't huge differences between ejs and jinja templates.
The back-end has a few changes, but I tried to stay as faithul to the original course project as possible.

## Requirements
- Python 3.9.1

- Local MongoDB instance

- [Free Cloudinary account](https://cloudinary.com/users/register/free) for uploading images

## Running it (On a *nix based OS)
Make sure you have your local MongoDB instance running before starting the app.

1. Create a virtual environment and activate it

`python -m venv venv`

`source venv/bin/activate`

2. Install the requirements

`pip install -r requirements.txt`

3. Export the Flask environment vars

`export FLASK_APP=yelp`

`export FLASK_ENV=development`

4. Seed the database

`flask seed-db`

5. Run the app

`flask run`

## Using the app
At this point you should be able to play around with the app. You'll need to either login or register to make changes to existing campgrounds or add new ones.

The login info for the test account:

`username: fake`

`password: fake`

Note: Uploading images won't work until you've added your Cloudinary creds.

## Adding your Cloudinary creds
![cloudinary_api](https://user-images.githubusercontent.com/1703143/104138340-142b8500-5369-11eb-8b5b-2cc4f1e6bea7.png)

Simply create a `.env` file inside of the `instance` folder. The `instance` folder gets created the first time you run the app. 
If you haven't run the app yet, then just create the folder yourself in the root of the project.

And add the `CLOUDINARY_URL` api environment variable you got from Cloudinary to the `.env` file:

`CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>`

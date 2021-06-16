# Food Delivery Service with Flask and SQLAlchemy

Implemented the backend part (including jinja2 templates and the DB schema) of a website for ordering food, and an admin section.

To create and populate database before the first run use the following commands:

`$ flask db upgrade`

`$ flask seed`

To launch the app use:

`$ flask run`

or

`$ gunicorn food_delivery:app`

After installing the flaskr wheel on a new machine, run:
export FLASK_APP=flaskr
flask init-db

then generate a genuine SECRET_KEY:
python -c 'import os; print(os.urandom(16))'

in flaskr-instance/config.py put:
SECRET_KEY = [YOUR SECRET KEY]

to serve the new flaskr instance:
pip install waitress
waitress-serve --call 'flaskr:create_app'
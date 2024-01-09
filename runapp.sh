# script.sh
#!/bin/sh
python seattle_emission_calculator/manage.py makemigrations
python seattle_emission_calculator/manage.py migrate
python seattle_emission_calculator/manage.py runserver 0.0.0.0:8000 --noreload
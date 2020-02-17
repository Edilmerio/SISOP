1- Install python version ^ 3.6 and yarn in your host
2- Clone project
3- Create virtual environment
4-Active vienv
5- Run pip install -r requirements.txt 
6- Run yarn install --flat
USE settings config.settings_dev for development
USE settings config.settings_prod for production
7- Run pyton manage.py makemigrations
8- Run pyton manage.py migrate
9- Run pyton manage.py collectstatic for production environment
10- For production environment use settings_prod and wsgi_prod
11- For production environment in linux-Apache copy sisop2.conf file in /etc/httpd/conf.d
12- For production environment in linux-Celery copy in /etc/init.d the generic bash init-scripts
13- For production environment in linux-Celery copy sisop_celeryd in /etc/default
14- For production environment in linux-Celery copy sisop_celerybeat in /etc/default
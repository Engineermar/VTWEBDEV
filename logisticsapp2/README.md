Logistics Management System

Written with Django 1.11 as backend and Angular 5 (coming to github soon), the system is developed for use by Rwanda Law Reform Comission and gracefully made public.


Contact:

I understand this read me is not complete; if you need direct support, feel free to hit me up at kmsium@gmail.com

Core Requirements:

- Django 1.11
- MySQL Database
- RabbitMQ for background

Features:

- Register incoming/stock in items
- Manage Organizational Structure and Item Catalogs
- Manage suppliers
- Employees make requests of items
- Users process requests of employees
- Transfer items between employees
- Return items
- Report items as lost and found
- Get notifications on expiring and low-instock items
- Manage employees and users through individual and group permissions
- Generate several kinds of reports


To do list:

- Add more report templates
- Add more data visualization templates
- Deal with purchase requests to suppliers


Installing:

From your virtual envrionment, run:


python manage.py migrate


Note:


Configure your database settings on .env for both production and development first


For celery, please configure your settings and start the celery servers.
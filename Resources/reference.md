# views.py is the controller in MVC schema 
https://stackoverflow.com/questions/5249792/why-does-django-call-it-views-py-instead-of-controller



# __init__.py usage

It used to be a required part of a package (old, pre-3.3 "regular package", not newer 3.3+ "namespace package").

Here's the documentation.

    Python defines two types of packages, regular packages and namespace packages. Regular packages are traditional packages as they existed in Python 3.2 and earlier. A regular package is typically implemented as a directory containing an __init__.py file. When a regular package is imported, this __init__.py file is implicitly executed, and the objects it defines are bound to names in the package’s namespace. The __init__.py file can contain the same Python code that any other module can contain, and Python will add some additional attributes to the module when it is imported.

When a regular package is imported, this __init__.py file is implicitly executed, 
and the objects it defines are bound to names in the package’s namespace. 





jhVdSt_c{fBN8y;F



# Django test

Running tests

Once you’ve written tests, run them using the test command of your project’s manage.py utility:

`$ ./manage.py test`


## test folder normally should be created at each app folder

Sample test case
```python
# views (uses selenium)

import unittest
from selenium import webdriver

class TestSignup(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_signup_fire(self):
        self.driver.get("http://localhost:8000/add/")
        self.driver.find_element_by_id('id_title').send_keys("test title")
        self.driver.find_element_by_id('id_body').send_keys("test body")
        self.driver.find_element_by_id('submit').click()
        self.assertIn("http://localhost:8000/", self.driver.current_url)

    def tearDown(self):
        self.driver.quit

if __name__ == '__main__':
    unittest.main()

```

# Django deployment

## check deployment setting
`python3 manage.py check --deploy`


## use gunicorn

`PYTHONPATH=`pwd`/.. gunicorn --bind 127.0.0.1:8000 ChemAPI.wsgi:application`



## POST request in django

There is no get or post annotation like spring, just by different data accessment method

You need to access request.data instead of request.POST,
```python
def post(self,request):
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

```

# Djanog + MySQL

create database and user
```
create database chemapi;
CREATE USER 'chemapi'@'localhost' IDENTIFIED BY 'chemapi';
GRANT ALL PRIVILEGES ON chemapi . * TO 'chemapi'@'localhost';
FLUSH PRIVILEGES;
```

## need store and search for the 
```bash
python manage.py makemigrations property_store  # this create migration file based on models.py
python manage.py sqlmigrate property_store 0001 # this create table based on migration file
python manage.py migrate                        # this create the actual table in database
```
## roll back migration simply delete that migration file

## ORM operation

```python
from events.models import Event
# save
event1 = Event(name="Test Event1", event_date="2018-12-17", venue="test venue", manager="Bob")
event1.save()

# get data
event_list = Event.objects.all()
Event.objects.get(id=1)  # get() method only works for single objects. 
Event.objects.filter(manager="Bob") # filter() method works for multiple objects. 
Event.objects.order_by("name")


# update data
event4 = Event(name="Bob's Birthday", event_date="2019-01-26 15:00", venue="McIvor's Bar", manager="Terry")
event4.save()
event4.name = "change data"
event4.save()

# delete object
Event.objects.filter(name__contains="Test").delete()
```

## Indexing

example
```python
class Person(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()

    class Meta:
        indexes = [
            models.Index(fields=['last_name']),
        ]
```



# Scheduler

## schedule a job to run periodically. 

One solution that I have employed is to do this:

1) Create a custom management command, e.g.

python manage.py my_cool_command

2) Use cron (on Linux) or at (on Windows) to run my command at the required times.

This is a simple solution that doesn't require installing a heavy AMQP stack. However there are nice advantages to using something like Celery, mentioned in the other answers. In particular, with Celery it is nice to not have to spread your application logic out into crontab files. However the cron solution works quite nicely for a small to medium sized application and where you don't want a lot of external dependencies.


## Task queue

Consider: https://django-q.readthedocs.io/en/latest/
   
    Multiprocessing worker pools
    Asynchronous tasks
    Scheduled and repeated tasks

Example (Mail)
```python
# Welcome mail with follow up example
from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task, schedule
from django_q.models import Schedule


def welcome_mail(user):
    msg = 'Welcome to our website'
    # send this message right away
    async_task('django.core.mail.send_mail',
            'Welcome',
            msg,
            'from@example.com',
            [user.email])
    # and this follow up email in one hour
    msg = 'Here are some tips to get you started...'
    schedule('django.core.mail.send_mail',
             'Follow up',
             msg,
             'from@example.com',
             [user.email],
             schedule_type=Schedule.ONCE,
             next_run=timezone.now() + timedelta(hours=1))

    # since the `repeats` defaults to -1
    # this schedule will erase itself after having run
```













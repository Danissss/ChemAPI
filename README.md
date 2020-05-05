


superadmin:
	admin@chemapi.ca
	wishartlab


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




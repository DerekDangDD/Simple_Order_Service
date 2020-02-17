from setuptools import setup

setup(
   name='simple_order',
   version='1.0',
   description='A useful module',
   author='Derek Dang',
   author_email='derekdangdd@gmail.com',
   packages=['application', 'database_models', 'routes', 'tests']  #same as name
)
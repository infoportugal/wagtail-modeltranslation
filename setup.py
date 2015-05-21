import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='wagtail-modeltranslation',
    version='0.0.9',
    packages=['wagtail_modeltranslation'],
    include_package_data=True,
    license='BSD License',
    description='Integration of django-modeltranslation with Wagtail CMS',
    long_description=README,
    url='https://github.com/infoportugal/wagtail-modeltranslation',
    author='Rui Martins',
    author_email='rmartins16@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['django-modeltranslation==0.9.1', 'wagtail']
)
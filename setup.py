from setuptools import setup, find_packages

setup(
    name='pyvietstock',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'playwright==1.44.0',
        're==2.2.1'
    ],
    author='Kim T. Nguyen',
    author_email='kimnt93@gmail.com',
    description='Vietstock API for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kimnt93/pyvietstock',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

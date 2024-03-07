from setuptools import setup
import os

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pyqt6-multiselect-combobox',
    version='1.0.0',
    description='A custom PyQt6 widget providing a multi-select combobox functionality for PyQt6 applications.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/user0706/pyqt6-multiselect-combobox',
    author='user0706',
    license='MIT',
    packages=['pyqt6_multiselect_combobox'],
    install_requires=[
        'PyQt6>=6.6.1',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6.1'
)
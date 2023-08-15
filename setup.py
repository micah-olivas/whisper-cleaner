from setuptools import setup, find_packages

setup(
    name='whisper-cleaner',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'whisper-cleaner = whisper_cleaner.main:main'
        ]
    },
    author='Micah Olivas'
)
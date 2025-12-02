from setuptools import setup, find_packages

setup(
    name='whisper-cleaner',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'whisper-timestamped',
        'profanity-check',
        'pydub',
        'art',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov',
        ]
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'whisper-cleaner = whisper_cleaner.main:main'
        ]
    },
    author='Micah Olivas',
    description='Remove profanity from audio files using OpenAI Whisper (https://github.com/openai/whisper)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/micaholivas/whisper-cleaner',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
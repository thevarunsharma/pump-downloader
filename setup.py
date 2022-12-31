from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pump-downloader",
    version="0.2.1",
    author="Varun Sharma",
    url="https://github.com/thevarunsharma/pump-downloader",
    packages=find_packages(),
    install_requires=[
        'Click',
        'requests',
        'tqdm'],
    entry_points='''
        [console_scripts]
        pump=pump.__init__:main
    ''',
    description="Multithreaded downloader for faster downloads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='download pump curl wget concurrent parallel',
    python_requires='>=3.8'
)

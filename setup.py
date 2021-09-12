from setuptools import setup, find_packages

setup(
    name="pump",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Click',
        'requests',
        'tqdm'],
    entry_points='''
        [console_scripts]
        pump=pump.__init__:main
    ''',
    description="Sends E-Mail Notification for Available CoWin Slots"
)
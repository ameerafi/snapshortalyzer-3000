from setuptools import setup

setup(
    name='Snapshotalyzer-3000',
    version='0.1',
    author="Ameer Salman M",
    author_email="ameersalmam333@gmail.com",
    description="Snapshotalyzer 3000 is a tool to manage the AWS EC2 snapshots",
    license='GPLv3+',
    packages=["shotty"],
    url="https://github.com/ameerafi/snapshortalyzer-3000",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
    [console_scripts]
    shotty=shotty.shotty:cli
    '''   
)
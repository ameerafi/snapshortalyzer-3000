# snapshortalyzer-3000

Demo project to manage AWS EC2 instances snapshots

## About

This project is a demo, and used boto3 to manage AWS EC2 instances snapshots.

## Configuring

shotty uses the configuration file created by the AWS cli. e.g.

`aws configure --profile shotty`

## Running

`pipenv run python shotty/shotty.py <command> <sub-command> <--project=PROJECT>`

*command* is instances, volumes
*sub-command* depends on command
*project* is optional

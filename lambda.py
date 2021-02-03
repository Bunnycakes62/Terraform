'''
#
# Lambda functions for CES592, assignment #13.
#
#
'''

import boto3
import datetime
import json
import pymysql
import sys


RDS_SECRET = 'ces592-week11'

### DATABASE BOILERPLATE
### This should be in a shared library that is included in the layer!
### That would allow the Lambda and web server and other utilities to
### share the exact same code instead of duplicating it, which is a
### bad practice!

from peewee import (
    CharField,
    DatabaseProxy,
    TimeField,
    Model,
    MySQLDatabase,
    SqliteDatabase,
)

# Create a proxy for the DB.  This is because we don't know what kind of DB
# we are connecting to until runtime.  We can create either a Sqlite DB or
# an RDS DB.  The Sqlite DB is a local DB stored in a file and can be very
# useful for testing.
database_proxy = DatabaseProxy()

db = None


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Schedule(BaseModel):

    instance_id = CharField(max_length=20, unique=True, null=False)
    start_at = TimeField(null=False)
    stop_at = TimeField(null=False)

    @staticmethod
    def add(instance_id, start_at, stop_at):
        schedule = Schedule(instance_id=instance_id, start_at=start_at, stop_at=stop_at)
        schedule.save()

    @staticmethod
    def remove(instance_id):
        schedule = Schedule.get(instance_id=instance_id)
        # Don't confuse "delete_instance" with referring to an EC2 instance.  It's
        # referring to an instance of a DB record.
        schedule.delete_instance()

    @staticmethod
    def modify(instance_id, start_at, stop_at):
        schedule = Schedule.get(instance_id=instance_id)
        schedule.start_at = start_at
        schedule.stop_at = stop_at
        schedule.save()

    @staticmethod
    def all():
        return Schedule.select().dicts()


class Database:

    TABLES = [
        Schedule,
    ]

    def __init__(self, type_of_db, secret=None):

        global db

        if type_of_db == 'sqlite':
            self.db = SqliteDatabase('schedule.db')
        elif type_of_db == 'aws':
            secret = _get_secret(RDS_SECRET)
            Database._create(secret)

            self.db = MySQLDatabase(
                'punch_clock',
                host=secret['host'],
                port=secret['port'],
                user=secret['username'],
                passwd=secret['password'])

        self.db.connect()
        database_proxy.initialize(self.db)
        self._create_tables()
        db = self.db

    def _create_tables(self):
        self.db.create_tables(self.TABLES)

    @classmethod
    def _create(klass, secret):
        # PeeWee doesn't have a way to create an actual MySQL database,
        # so we have to rely on another library for that.
        conn = pymysql.connect(host=secret['host'], user=secret['username'], password=secret['password'])
        try:
            conn.cursor().execute('CREATE DATABASE punch_clock')
        except Exception:
            # Database probably already exists.
            pass
        conn.close()

    def delete(self):
        self.db.drop_tables(self.TABLES)


def _get_secret(secret_name):
    cli = boto3.client('secretsmanager', region_name='us-west-2')
    res = cli.get_secret_value(SecretId=secret_name)
    secret = json.loads(res['SecretString'])
    return secret

### The above should be in a shared library in the Lambda layer.
### END OF BOILERPLATE CODE


def is_ec2_exist(ec2, instance_id):
    # Use the EC2 client to determine if the instance exists.
    # Maybe look at...
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
    response= ec2.describe_instances()
    if response['Reservations'][0]['Instances'][0]['InstanceId'] == instance_id :
        return True
    else:
        return False
    # Note that the return value for describe_instances can be a little bit painful,
    # because it wraps the instances in an outer array called Reservations.  So, you
    # need to dig in two levels.
    # pass


def send_sns_error_message(instance_id):
    # Get an SNS client.
    sns = boto3.client('sns', region_name='us-west-2')
    # Send a message to the SNS topic, with the attribute set!
    sns.publish(
        TopicArn='arn:aws:sns:us-west-2:647502022961:sns-ces592-a9-lgm',
        Message=f'{instance_id}: not found',
        MessageAttributes= {
            'lgm': {
                'DataType': 'String',
                'StringValue': 'true'
            }
        }
    )
    # Maybe look at...
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
    pass


def is_time_between(start_at, stop_at):
    now = datetime.datetime.utcnow().time()
    if stop_at > start_at:
        # All in a single day...
        if start_at <= now and now <= stop_at:
            return True
    else:
        # Wraps to next day...
        if start_at <= now or now <= stop_at:
            return True

    return False


def stop_if_running(ec2, instance_id):
    # Use the EC2 client to stop the instance if it's running.
    # Maybe look at...
    response = ec2.describe_instance_status(InstanceIds=[instance_id])
    if response['InstanceStatus'][0]['InstanceState']['Name'] == 'running':
        ec2.stop_instances(
            InstanceIds=[
                instance_id,
            ]
        )
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.stop_instances
    pass


def start_if_stopped(ec2, instance_id):
    # Use the EC2 client to start the instance if it's stopped.
    # Maybe look at...
    response = ec2.describe_instance_status(InstanceIds=[instance_id])
    if response['InstanceStatus'][0]['InstanceState']['Name'] == 'stopped':
        ec2.start_instances(
            InstanceIds=[
                instance_id,
            ]
        )
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.start_instances
    pass


def lambda_handler(event, context):
    # import pdb; pdb.set_trace()

    db = Database('aws')
    ec2 = boto3.client('ec2', region_name='us-west-2')

    # Example of how to remove all the records.
    for item in Schedule.select():
        if not is_ec2_exist(ec2, item.instance_id):
            send_sns_error_message(item.instance_id)
            continue

        if is_time_between(item.start_at, item.stop_at):
            stop_if_running(ec2, item.instance_id)
        else:
            start_if_stopped(ec2, item.instance_id)


if __name__ == '__main__':
    # Uesful for testing from a Linux shell before running in Lambda.
    lambda_handler(None, None)


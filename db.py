'''
#
# Database functions for CES592
#
#
'''

import boto3
import datetime
import json
import pymysql

from peewee import (
    CharField,
    DatabaseProxy,
    DateTimeField,
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
    start_at = DateTimeField(null=False)
    stop_at = DateTimeField(null=False)

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


def main(db_type='aws'):

    if db_type == 'aws':
        # We need the login creds
        secret = _get_secret('ces592-rotate')
        db = Database(db_type, secret)
    else:
        db = Database(db_type)

    for item in Schedule.select():
        item.delete_instance()

    import pdb; pdb.set_trace()
    Schedule.add('i-123456789012', datetime.datetime.utcnow(), datetime.datetime.utcnow())
    Schedule.add('i-abcdefghijkl', datetime.datetime.utcnow(), datetime.datetime.utcnow())
    for item in Schedule.all():
        print(item)

    Schedule.modify('i-123456789012', datetime.datetime.utcnow(), datetime.datetime.utcnow())
    for item in Schedule.all():
        print(item)

    Schedule.remove('i-123456789012')
    for item in Schedule.all():
        print(item)


if __name__ == '__main__':
    main('aws')

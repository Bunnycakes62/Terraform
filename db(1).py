'''
#
# Database functions for CES592, assignment #13.
#
# Version 2.0 - Uses TimeField instead of DateTimeField.
#
'''

import boto3
import datetime
import json
import pymysql
import sys


RDS_SECRET='ces592-week11'


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


def main(db_type='aws'):

    db = Database(db_type)

    # UNCOMMENT THESE LINES TO DROP THE EXISTING TABLES!
    # db.delete()
    # sys.exit(0)
    # RECOMMENT THEM TO RECREATE THE TABLES.

    # Example of how to remove all the records.
    for item in Schedule.select():
        item.delete_instance()

    # Adding two records.
    Schedule.add('i-123456789012', datetime.time(hour=10, minute=0), datetime.time(hour=12, minute=0))
    Schedule.add('i-abcdefghijkl', datetime.time(hour=16, minute=0), datetime.time(hour=2, minute=0))
    for item in Schedule.all():
        print(item)

    # Modifying a single record.
    Schedule.modify('i-123456789012', datetime.time(hour=0, minute=0), datetime.time(hour=12, minute=0))
    for item in Schedule.all():
        print(item)

    # Deleting a record.
    Schedule.remove('i-123456789012')
    for item in Schedule.all():
        print(item)
        
    # Setting up for testing
    # No Records
    print('Setting up for testing')
    print('no records')
    Schedule.remove('i-abcdefghijkl')
    
    # instance id that does not match any instance in the region
    print('instance id that does not match any instance in region')
    
    # Schdeule that sits entirely in one day
    print('an instance with schedule that sits entirely in one day')
    Schedule.add('i-123', datetime.time(hour=1, minute=0), datetime.time(hour=16, minute=0))
    for item in Schedule.all():
    	print(item)
    
    # Schedule that spans days
    print('an instance with schedule that spans days')
    Scuedle.add('i-abc', datetime.time(hour=16, minute=0), datetime.time(hour=1, minute=0))
    for item in Schedule.all():
    	print(item)

if __name__ == '__main__':
    main('aws')

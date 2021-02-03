import boto3

# SET THIS TO YOUR QUEUE'S URL.
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/647502022961/sqs-ces592-a7'

# Sends a single message in JSON format.
def send_message(cli):
	msgs = cli.send_message(
		QueueUrl=QUEUE_URL,
		MessageBody='{"msg": "This is my message"}')


if __name__ == '__main__':
	cli = boto3.client('sqs')
	send_message(cli)

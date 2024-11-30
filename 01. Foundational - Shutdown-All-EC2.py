import boto3  # Import the Boto3 library for AWS service interaction
import logging  # Import the logging library for logging information

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the logging level to INFO

# Specify the AWS region
region = 'us-east-1'
# Create an EC2 client for the specified region
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    """
    The main entry point for the AWS Lambda function.
    
    Args:
        event: The event data that triggers the Lambda function.
        context: The runtime information provided by AWS Lambda.
    """
    try:
        # Retrieve all running EC2 instances
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        
        # Initialize a list to hold the IDs of running instances
        running_instances = []
        
        # Loop through the reservations and instances to extract instance IDs
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Add the ID of each running instance to the list
                running_instances.append(instance['InstanceId'])
        
        # Log the total number of running instances found
        logger.info('Found %d running instances.', len(running_instances))

        # Check if there are any running instances to stop
        if running_instances:
            # Stop the running instances
            ec2.stop_instances(InstanceIds=running_instances)
            # Log the IDs of the stopped instances
            logger.info('Stopped your instances: %s', running_instances)
        else:
            # Log that there are no running instances to stop
            logger.info('No running instances to stop.')
        
        # Return a response with the status of the operation
        return {
            'statusCode': 200,
            'body': 'Stopped instances: {}'.format(running_instances) if running_instances else 'No running instances to stop.'
        }
    except Exception as e:
        # Log any errors encountered during execution
        logger.error('Error stopping instances: %s', e)
        # Return a 500 response indicating an error occurred
        return {
            'statusCode': 500,
            'body': 'Error stopping instances.'
        }

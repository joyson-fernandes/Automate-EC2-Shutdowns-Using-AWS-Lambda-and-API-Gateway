import boto3  # Import the Boto3 library for AWS service interaction
import logging  # Import the logging library for logging information

# Set up logging
logger = logging.getLogger()  # Create a logger object
logger.setLevel(logging.INFO)  # Set the logging level to INFO to capture all INFO and higher-level messages

# Specify the AWS region
region = 'us-east-1'  # Define the AWS region for the EC2 service
# Create an EC2 client for the specified region
ec2 = boto3.client('ec2', region_name=region)  # Instantiate a client object for the EC2 service

def lambda_handler(event, context):
    """
    The main entry point for the AWS Lambda function.
    
    Args:
        event: The event data that triggers the Lambda function.
        context: The runtime information provided by AWS Lambda.
    """
    try:
        # Retrieve all running EC2 instances that have the Environment: Dev tag
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']},  # Filter for running instances
                {'Name': 'tag:Environment', 'Values': ['Dev']}  # Filter for instances tagged with Environment: Dev
            ]
        )
        
        # Initialize a list to hold the IDs of running development instances
        dev_instances = []  # Create an empty list for storing instance IDs
        
        # Loop through the reservations and instances to extract instance IDs
        for reservation in response['Reservations']:  # Iterate through each reservation
            for instance in reservation['Instances']:  # Iterate through each instance within the reservation
                # Add the ID of each running development instance to the list
                dev_instances.append(instance['InstanceId'])  # Collect instance IDs

        # Log the total number of running development instances found
        logger.info('Found %d running development instances.', len(dev_instances))  # Log the count of running dev instances

        # Check if there are any running development instances to stop
        if dev_instances:
            # Stop the running development instances
            ec2.stop_instances(InstanceIds=dev_instances)  # Call the stop_instances API
            # Log the IDs of the stopped instances
            logger.info('Stopped your development instances: %s', dev_instances)  # Log the stopped instances
        else:
            # Log that there are no development instances to stop
            logger.info('No running development instances to stop.')  # Inform that no dev instances were found

        # Return a response with the status of the operation
        return {
            'statusCode': 200,  # HTTP status code for a successful operation
            'body': 'Stopped instances: {}'.format(dev_instances) if dev_instances else 'No running development instances to stop.'
        }
    except Exception as e:
        # Log any errors encountered during execution
        logger.error('Error stopping instances: %s', e)  # Log the error message
        # Return a 500 response indicating an error occurred
        return {
            'statusCode': 500,  # HTTP status code for server error
            'body': 'Error stopping instances.'  # Error message for the response body
        }

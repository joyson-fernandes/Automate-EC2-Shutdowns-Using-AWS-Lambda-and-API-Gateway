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
        # Check if query parameters exist
        if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
            environment = event['queryStringParameters'].get('Environment')  # Get the environment filter from query params
            
            if environment:
                # Construct the filter to get instances with the specified tag
                filters = [
                    {'Name': 'instance-state-name', 'Values': ['running']},  # Filter for running instances
                    {'Name': 'tag:Environment', 'Values': [environment]}  # Filter for instances with the specified environment tag
                ]
                # Retrieve all running instances with the applied filters
                response = ec2.describe_instances(Filters=filters)
                
                # Initialize a list to hold the IDs of matching instances
                target_instances = []  # Create an empty list for storing instance IDs
                
                # Loop through the reservations and instances to extract instance IDs
                for reservation in response['Reservations']:  # Iterate through each reservation
                    for instance in reservation['Instances']:  # Iterate through each instance within the reservation
                        # Add the ID of each matching instance to the list
                        target_instances.append(instance['InstanceId'])  # Collect instance IDs

                # Log the total number of matching instances found
                logger.info('Found %d matching instances.', len(target_instances))  # Log the count of matching instances

                # Check if there are any matching instances to stop
                if target_instances:
                    # Stop the matching instances
                    ec2.stop_instances(InstanceIds=target_instances)  # Call the stop_instances API
                    # Log the IDs of the stopped instances
                    logger.info('Stopped your instances: %s', target_instances)  # Log the stopped instances
                else:
                    # Log that there are no matching instances to stop
                    logger.info('No matching instances to stop.')  # Inform that no matching instances were found

                # Return a response with the status of the operation
                return {
                    'statusCode': 200,  # HTTP status code for a successful operation
                    'body': 'Stopped instances: {}'.format(target_instances) if target_instances else 'No matching instances to stop.'
                }
            
            else:
                # Return a 400 Bad Request if the key or value is not provided
                return {
                    'statusCode': 400,  # Bad Request
                    'body': 'Both key and value query parameters are required.'
                }
        else:
            # Return an appropriate message when no query parameters are provided
            logger.info('No query parameters provided; no instances will be stopped.')
            return {
                'statusCode': 200,  # Successfully handled request
                'body': 'No instances stopped because no query parameters were provided.'
            }
    except Exception as e:
        # Log any errors encountered during execution
        logger.error('Error stopping instances: %s', e)  # Log the error message
        # Return a 500 response indicating an error occurred
        return {
            'statusCode': 500,  # HTTP status code for server error
            'body': 'Error stopping instances.'  # Error message for the response body
        }

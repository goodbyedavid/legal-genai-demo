import json
import boto3
import os

def lambda_handler(event, context):
    # Extract necessary information from the event
    bucket_name = event['bucketName']
    input_file_key = event['inputFiles'][0]['contentBatches'][0]['key']

    file_metadata = event['inputFiles'][0].get('fileMetadata', {})
    original_file_location = event['inputFiles'][0].get('originalFileLocation', {})

    # Initialize S3 client
    s3 = boto3.client('s3')

    try:
        processed_batches = []
        output_files = []
        
        # Read the JSON file from S3
        response = s3.get_object(Bucket=bucket_name, Key=input_file_key)
        file_content = response['Body'].read().decode('utf-8')
        
        # Parse the JSON content
        data = json.loads(file_content)

        # Set company
        company = None

        # Process each contentBody
        for item in data['fileContents']:
            content_body = item['contentBody']
            
            # Remove metadata tags and extract JSON
            metadata_start = content_body.find('<metadata>')
            metadata_end = content_body.find('</metadata>')
            
            if metadata_start != -1 and metadata_end != -1:
                metadata_json = content_body[metadata_start + 10:metadata_end].strip()
                content_body = content_body[:metadata_start].strip()

                # Set company
                metadata_as_json = json.loads(metadata_json)
                if company is None and 'company' in metadata_as_json:
                    company = metadata_as_json["company"]
                else:
                    metadata_as_json["company"] = company
                
                # Parse the metadata JSON and assign to contentMetadata
                item['contentMetadata'] = metadata_as_json
                item['contentBody'] = content_body

        # Convert the processed data back to JSON
        processed_json = json.dumps(data, indent=2)

        # Generate new output file name
        file_name, file_extension = os.path.splitext(input_file_key)
        output_file_key = f"{file_name}_output{file_extension}"

        # Save the processed JSON back to S3
        # s3.put_object(Bucket=bucket_name, Key=output_file_key, Body=processed_json)

        output_key = f"Output/{input_file_key}"
        s3.put_object(Bucket=bucket_name, Key=output_key, Body=processed_json) 

        # Update the event with the output file information
        # if 'outputFiles' not in event:
        #     event['outputFiles'] = [{'contentBatches': []}]
        # event['outputFiles'][0]['contentBatches'].append({'key': output_file_key})

        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(event)
        # }

        # Add processed batch information
        processed_batches.append({
            'key': output_key
        })

        # Prepare output file information
        output_file = {
            'originalFileLocation': original_file_location,
            'fileMetadata': file_metadata,
            'contentBatches': processed_batches
        }
        output_files.append(output_file)
    
        result = {'outputFiles': output_files}
        
        print("KB_CUSTOM_RESULT", result)

        return result

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing file: {str(e)}")
        }
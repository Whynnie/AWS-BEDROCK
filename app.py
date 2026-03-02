import boto3
import botocore.config
import json

from datetime import datetime


# define the prompt format
def testcase_generate_using_bedrock(testtopic:str)-> str:
    prompt=f"""<s>[INST]Human: Read and generate positive, negative and edge cases for login and user authentication for both mobile and web applications {testtopic}
    Assistant:[/INST]
    """

    #the api body
    body={
        "prompt":prompt,
        "maxTokens":512,
        "temperature":1,
        "topP":0.5
    }

    # create a try cache block
    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3}))
        #inorder to call the foundation model
        response=bedrock.invoke_model(body=json.dumps(body),modelId="openai.gpt-oss-120b-1:0")

        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        test_details=response_data['generation']
        return test_details
    except Exception as e:
        print(f"Error generating the test case :{e}")
        return ""

def save_test_details_s3(s3_key,s3_bucket,generate_test):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body =generate_test )
        print("Code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")



def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    testtopic=event['test_topic']

    generate_test=testcase_generate_using_bedrock(testtopic=testtopic)

    if generate_test:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"test-output/{current_time}.txt"
        s3_bucket='aws_bedrock_course1'
        save_test_details_s3(s3_key,s3_bucket,generate_test)


    else:
        print("No Test Case was generated")

    return{
        'statusCode':200,
        'body':json.dumps('Test Case Generation is completed')
    }

    




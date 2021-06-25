import json
import boto3
from botocore.exceptions import ClientError




obj_to_email_map = {
    # 'Trash':['sriparan@amazon.com', 'Sanitation'],
    # 'Animal': ['sriparan@amazon.com', 'Animal control'],
    # 'Hydrant': ['sriparan@amazon.com', 'Fire Department']



    'Trash':['muccio+sanitation@amazon.com', 'Sanitation'],
    'Puddle':['muccio+sanitation@amazon.com', 'Sanitation'],
    'Animal': ['muccio+animalcontrol@amazon.com', 'Animal control'],
    'Hydrant': ['muccio+firedept@amazon.com', 'Fire Department'],
    'Fire': ['muccio+firedept@amazon.com', 'Fire Department'],
    
}

def insert_data(bucket, photo, metatdata, target_email, target_dept):
    labels=[{'S':target_email},{'S':target_dept}]

    for label in metatdata:
        labels.append({'S':label['Name']})



    dynamoclient = boto3.client('dynamodb')


    dynamoclient.put_item( TableName='image_recognition_response',
                                 Item={ "image_name": {'S':photo},
                                        "data": {'L':labels},
                                    });
    




def send_notification_email(bucket, photo, metatdata):
    print("Sending emails")
    SENDER = "Team6 <sriparan@amazon.com>"
    RECIPIENT = "sriparan+parks@amazon.com"
    AWS_REGION = "us-east-1"

    target_email = "sriparan@amazon.com"
    target_dept = "General Pool"

    for label in metatdata:
        print ("Label: " + label['Name'])
        if label['Name'] in obj_to_email_map:
            target_email = obj_to_email_map.get(label['Name'])[0];
            target_dept = obj_to_email_map.get(label['Name'])[1];
            print ("Matched Label: " + label['Name'] + "sending email to : " + target_email + ", dept:" + target_dept);
            break;
    RECIPIENT = target_email

    insert_data(bucket,photo, metatdata, target_email, target_dept)
    
    SUBJECT = "** Important: Citizens report **"
    
    BODY_TEXT = f"""
    Hello Octank City Team!
    Thank you for your dedication in keeping the Octank City beautiful.
    There is an issue related to {target_dept} that requires your attention: http://{bucket}/{photo}

                 bucket  {bucket}, 
                 image  {photo} 
                 
                 """
            
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
      <h1>Team 6 notification for a citizen report </h1>
      </p>
            Hello Octank City Team!
            <br>
            Thank you for your dedication in keeping the Octank City beautiful.
            <br>
            There is an issue related to <b>{target_dept}</b> that requires your attention: <a href="https://{bucket}/{photo}"> https://{bucket}/{photo} </a>
            <br>
            
            
            
            -- Disclaimers : Ethical AI --
      </p>
    </body>
    </html>
                """            
    print ("Email being sent to : " + RECIPIENT);

    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        

    

def detect_labels(photo, bucket):

    client=boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)


    print('Detected labels for ' + photo) 
    # print()   
    # for label in response['Labels']:
    #     print ("Label: " + label['Name'])
    #     print ("Confidence: " + str(label['Confidence']))
        # print ("Instances:")
        # for instance in label['Instances']:
        #     print ("  Bounding box")
        #     print ("    Top: " + str(instance['BoundingBox']['Top']))
        #     print ("    Left: " + str(instance['BoundingBox']['Left']))
        #     print ("    Width: " +  str(instance['BoundingBox']['Width']))
        #     print ("    Height: " +  str(instance['BoundingBox']['Height']))
        #     print ("  Confidence: " + str(instance['Confidence']))
        #     print()

        # print ("Parents:")
        # for parent in label['Parents']:
        #     print ("   " + parent['Name'])
        # print ("----------")
        # print ()

    #insert_data(bucket, photo, response['Labels'])
    send_notification_email(bucket, photo, response['Labels'])


    return len(response['Labels'])


def main():
    photo='images/trash1.jpg'
    bucket='mys3-virginia-bucket'
    label_count=detect_labels(photo, bucket)
    print("Labels detected: " + str(label_count))
    
    
    


def lambda_handler(event, context):
    # TODO implement
    # print("--------------This is the recognition")
    # print(event)
    # print("-----------------")
    
    for rec in event["Records"]:
        bucket = (rec["s3"]["bucket"]["name"]);
        photo = (rec["s3"]["object"]["key"]);

        #label_count=detect_labels(photo, bucket)
        
        print(f'{photo} in {bucket}')
        label_count=detect_labels(photo, bucket)
        # print("Labels detected: " + str(label_count))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

import os
import yt_dlp
import boto3
import uuid
import requests
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    url = body['url']
    webhook_url = body['webhook_url']
    s3_bucket_name = os.environ['S3_BUCKET_NAME']
    s3 = boto3.client('s3')
    task_id = str(uuid.uuid4())

    ydl_opts = {
        'outtmpl': '/tmp/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', None)
            file_path = f"/tmp/{video_title}.{video_ext}"

            s3.upload_file(file_path, s3_bucket_name, f"{video_title}.{video_ext}")

        requests.post(webhook_url, json={'task_id': task_id, 'status': 'completed', 'file': f"{video_title}.{video_ext}"})
    except Exception as e:
        requests.post(webhook_url, json={'task_id': task_id, 'status': 'error', 'message': str(e)})

    return {
        'statusCode': 200,
        'body': json.dumps({'task_id': task_id})
    }

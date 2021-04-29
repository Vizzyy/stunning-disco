import datetime
import json
import boto3

sqs = boto3.client('sqs')


def sqs_send(queue, proxy_host, start_time, target_route, success=True):
    now = datetime.datetime.now()
    elapsed = now - start_time
    elapsed_ms = elapsed.total_seconds() * 1000  # elapsed milliseconds
    full_path = target_route.split(proxy_host)[1].split('?')[0].split('/')
    full_path = [x for x in full_path if x]
    path = f"api/{full_path[0]}/{full_path[1]}"

    message = {
        "action": "insert",
        "table": "canary_metrics",
        "values": {
            "path": path,
            "ms_elapsed": elapsed_ms,
            "timestamp": now.__str__(),
            "success": success
        }
    }

    # Send message to SQS queue
    print("Pushing message to queue...")
    response = sqs.send_message(QueueUrl=queue, MessageBody=(json.dumps(message)))
    print(message)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise RuntimeError("Could not enqueue message!")

import os
import re
import sys
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import boto3
import logging

SUUMO_URL_PATTERN="https://suumo.jp/.*"
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def lambda_handler(event, context):
    if "x-line-signature" in event["headers"]:
        signature = event["headers"]["x-line-signature"]
    elif "X-Line-Signature" in event["headers"]:
        signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 500,
                  "headers": {},
                  "body": "Error"}
    
    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = line_event.message.text
        pattern = SUUMO_URL_PATTERN
        if re.match(pattern, text):
            table_name = 'target_url' 
            client = boto3.client('dynamodb')
            options = {
                'TableName': table_name,
                'Key': {
                    'id': {'S': '1'},
                },
                'UpdateExpression': 'set #url = :url',
                'ExpressionAttributeNames': {
                    '#url': 'url',
                },
                'ExpressionAttributeValues': {
                    ':url': {'S': text},
                }
            }
            client.update_item(**options)
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text="スクレイピング対象を更新しました。"))
        else:
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text="無効なメッセージです。SuumoのURLを送ってください。"))

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json

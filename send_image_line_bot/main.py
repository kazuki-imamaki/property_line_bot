import csv
from aiohttp import Payload
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
from bs4 import BeautifulSoup
from pprint import pprint
import datetime
import json
import requests
import pandas as pd
import boto3


file = open('info.json', 'r')

info = json.load(file)

TARGET_URL = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&fw2=&pc=50&po1=25&po2=99&ra=013&rn=0305&rn=0573&rn=0015&rn=0045&rn=0280&ek=030532110&ek=030513930&ek=030506640&ek=030528500&ek=057332110&ek=057313930&ek=057300640&ek=057306640&ek=001527320&ek=001527360&ek=001527380&ek=001534900&ek=001520030&ek=001531910&ek=001506640&ek=004550050&ek=004520870&ek=004553960&ek=004506820&ek=028021960&ek=028039030&ek=028024130&md=04&md=05&md=06&md=07&cb=0.0&ct=14.0&et=10&mb=45&mt=9999999&cn=30&ae=03051&ae=05731&co=1&tc=0400101&tc=0400301&tc=0400203&tc=0400206&shkr1=03&shkr2=03&shkr3=03&shkr4=03'
LINK_URL_DOMAIN = 'https://suumo.jp/'
CHANNEL_ACCESS_TOKEN = info["CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)


class LineMessage:
    # def send(d):

    #     USER_ID = info["USER_ID"]
    #     suumo_info = f"{d['title']}\n{d['fee']}\n{d['madori']}\n{d['menseki']}\n{d['image']}\n{d['link']}"

    #     messages = TextSendMessage(text=suumo_info)
    #     line_bot_api.broadcast(USER_ID, messages=messages)

    # def sendUpdate(today, d):
    #     USER_ID = info["USER_ID"]
    #     suumo_info = f"更新されました {today}\n{d['title']}\n{d['fee']}\n{d['madori']}\n{d['menseki']}\n{d['image']}\n{d['link']}"

    #     messages = TextSendMessage(text=suumo_info)
    #     line_bot_api.broadcast(USER_ID, messages=messages)

    def sendFlexMessage(payload):
        # USER_ID = info["USER_ID"]
        container_obj = FlexSendMessage.new_from_json_dict(payload)
        line_bot_api.broadcast(messages=container_obj)


class FlexMessage:
    def genarateJon(title, menseki, fee, access, image, link):
        payload = {
            "type": "flex",
            "altText": "flexMessageです",
            "contents": {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": image,
                    "size": "full",
                    "aspectRatio": "1:1",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": link,
                        "label": "Go"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "lg",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{menseki} / {fee} / {access}",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            }
        }

        return payload


if __name__ == "__main__":
    
    table_name = 'demo-weather' 
    client = boto3.client('dynamodb')

    
    options = {
        'TableName': table_name,
        'ProjectionExpression': '#place, #weather',
        'ExpressionAttributeNames': {
            '#place': 'place',
            '#weather': 'weather',
        },
        'Limit': 1,     # loopの実験用
    }

    ret = []
    while True:
        res = client.scan(**options)
        ret += res.get('Items', [])
        if 'LastEvaluatedKey' not in res:
            break
        options['ExclusiveStartKey'] = res['LastEvaluatedKey']

    print(len(ret))
    print(ret)


    today = datetime.date.today()
    now = datetime.datetime.now()
    res = requests.get(TARGET_URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    new_d_list = []
    contents = soup.find_all('div', class_='cassetteitem')

    for content in contents:

        # 物件・建物情報
        detail = content.find('div', class_='cassetteitem-detail')

        # 各部屋の情報
        table = content.find('table', class_='cassetteitem_other')

        # 変数titleに物件名を格納
        title = detail.find('div', class_='cassetteitem_content-title').text
        # 変数addressに住所を格納
        address = detail.find('li', class_='cassetteitem_detail-col1').text
        # 変数accessにアクセス情報を格納
        access = detail.find('li', class_='cassetteitem_detail-col2').text
        # 変数ageに築年数を格納
        age = detail.find('li', class_='cassetteitem_detail-col3').text

        # 変数tableから全てのtrタグを取得してtr_tagsに格納
        tr_tags = table.find_all('tr', class_='js-cassette_link')

        for tr_tag in tr_tags:

            img, floor, price, first_fee, capacity = tr_tag.find_all('td')[1:6]
            # priceから賃料と管理日を取得
            fee, manegement_fee = price.find_all('li')
            # first_feeから敷金と礼金を取得
            deposit, gratuity = first_fee.find_all('li')
            # capacityから間取りと面積を取得
            madori, menseki = capacity.find_all('li')

            # リンクを取得
            a_tag = tr_tag.find('a', class_='cassetteitem_other-linktext')
            link = a_tag['href']

            image_tag = tr_tag.find(
                'img', class_='casssetteitem_other-thumbnail-img')
            image = image_tag['rel']
            d = {
                'title': title,
                'address': address,
                'access': access,
                'age': age,
                'floor': floor.text,
                'fee': fee.text,
                'manegement_fee': manegement_fee.text,
                'deposit': deposit.text,
                'gratuity': gratuity.text,
                'madori': madori.text,
                'menseki': menseki.text,
                'link': LINK_URL_DOMAIN + link,
                'image': image,
                'date': today
            }

            new_d_list.append(d)

    # csvファイルから過去の物件情報を取得する
    old_d_list = []
    with open('data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(row)
            old_d_list.append(row)

    diff_d_list = []
    # print(new_d_list[0]['link'])
    # diff_list = set(new_d_list) ^ set(old_d_list)
    for new_d in new_d_list:
        for old_d in old_d_list:
            matched_flag = False
            # タイトル、階数、面積が一致したらtrue
            if new_d['title'] == old_d['title'] and new_d['floor'] == old_d['floor'] and new_d['menseki'] == old_d['menseki'] and new_d['fee'] == old_d['fee']:
                matched_flag = True
                break
        if matched_flag == False:
            diff_d_list.append(new_d)

    for diff_d in diff_d_list:
        old_d_list.append(diff_d)

    df = pd.json_normalize(old_d_list)
    df.to_csv('data.csv', index=True, encoding='utf-8', quoting=csv.QUOTE_ALL)

    line = LineMessage

    flexMessage = FlexMessage

    if today.weekday() == 5 and 0 <= now.hour <= 3:
        for d in new_d_list:
            payload = flexMessage.genarateJon(
                d['title'], d['menseki'], d['fee'], d['access'], d['image'], d['link'])
            line.sendFlexMessage(payload)
    else:
        for d in diff_d_list:
            payload = flexMessage.genarateJon(
                d['title'], d['menseki'], d['fee'], d['access'], d['image'], d['link'])
            line.sendFlexMessage(payload)

    # if today.weekday() == 5 and 0 <= now.hour <= 3:
    #     # 日曜日には今日の検索結果を全件送信
    #     for d in new_d_list:
    #         line.send(d)
    # else:
    #     # 差分の配列をlineで送信
    #     for d in diff_d_list:
    #         line.sendUpdate(today, d)

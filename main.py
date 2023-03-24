from datetime import date, datetime, timedelta
import imp
import math
from pydoc import doc
import re
from unittest import result
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
import requests
import os
import random
import http.client, urllib
import json

week_list = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期

tx_key=os.getenv("TX_KEY")
start_date = os.getenv('START_DATE')
city = os.getenv('CITY')
birthday = os.getenv('BIRTHDAY')
birthday_boy=os.getenv('BIRTHDAY_BOY')

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

# 易客云天气
yk_appid=os.getenv('yk_appid')
yk_appsecret=os.getenv('yk_appsecret')

user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.getenv('TEMPLATE_ID')

if app_id is None or app_secret is None:
  print('请设置 APP_ID 和 APP_SECRET')
  exit(422)

if not user_ids:
  print('请设置 USER_ID，若存在多个 ID 用回车分开')
  exit(422)

if template_id is None:
  print('请设置 TEMPLATE_ID')
  exit(422)

def get_week_day():
  week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  week_day = week_list[datetime.date(today).weekday()]
  return week_day
  
# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather():
    if city is None:
      print('请设置城市')
      return None
    # url = "https://v0.yiketianqi.com/api?unescape=1&version=v63&appid=44795547&appsecret=vpT4Pi6a&city=" + city
    url="https://v0.yiketianqi.com/api?unescape=1&version=v61&appid="+yk_appid+"&appsecret="+yk_appsecret+"&city=" + city
    res = requests.get(url).json()
    weather = res
    return weather

# 纪念日正数
def get_memorial_days_count():
  if start_date is None:
    print('没有设置 START_DATE')
    return 0
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday_left():
  if birthday is None:
    print('没有设置 BIRTHDAY')
    return 0
  next = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
  if next < nowtime:
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_birthday_boy_left():
  if birthday is None:
    print('没有设置 BIRTHDAY_BOY')
    return 0
  next = datetime.strptime(str(today.year) + "-" + birthday_boy, "%Y-%m-%d")
  if next < nowtime:
    next = next.replace(year=next.year + 1)
  print((next - today).days)
  return (next - today).days

# 英语每日一句
def get_daily_eng():
  if tx_key is None:
    print('没有设置天行key')
    return 0
  conn = http.client.HTTPSConnection('api.tianapi.com')  #接口域名
  params = urllib.parse.urlencode({'key':tx_key})
  headers = {'Content-type':'application/x-www-form-urlencoded'}
  conn.request('POST','/everyday/index',params,headers)
  res = conn.getresponse()
  data = res.read()
  print(data.decode('utf-8'))
  result=data.decode('utf-8')
  fin=json.loads(result)
  doc=''
  if fin['code']==200:
    doc=fin['newslist'][0]['content'] + fin['newslist'][0]['note']
    print(doc)
  return doc

# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功xxxxx
def get_words():
  words = requests.get("https://api.shadiao.pro/chp", timeout=100)
  if words.status_code != 200:
    return get_words()
  return (words.json()['data']['text']).replace('\n', '')



def format_temperature(temperature):
  return math.floor(temperature)

# 随机颜色
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
weather = get_weather()
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "city": {
    "value": city,
    "color": get_random_color()
  },
  "date": {
    "value": weather['date'] + get_week_day(),
    "color": get_random_color()
  },
  "week_day": {
    "value": get_week_day(),
    "color": get_random_color()
  },
  "weather": {
    "value": weather['wea'],
    "color": get_random_color()
  },
  "humidity": {
    "value": weather['humidity'],
    "color": get_random_color()
  },
  "wind": {
    "value": f"{weather['win']}{weather['win_speed']}",
    "color": get_random_color()
  },
  "air_data": {
    "value": weather['air'],
    "color": get_random_color()
  },
  "air_quality": {
    "value": weather['air_level'],
    "color": get_random_color()
  },
  "air_tips":{
    "value": weather['air_tips'],
    "color": get_random_color()
  },
  "temperature": {
    "value": weather['tem']+'℃',
    "color": get_random_color()
  },
  "highest": {
    "value": weather['tem1']+'℃',
    "color": get_random_color()
  },
  "lowest": {
    "value": weather['tem2']+'℃',
    "color": get_random_color()
  },
  "love_days": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
   "birthday_left": {
    "value": str(get_birthday_left())+'天',
    "color": get_random_color()
  },
  "birthday_boy_left": {
    "value": str(get_birthday_boy_left())+'天',
    "color": get_random_color()
  },
  "words": {
    "value": get_words(),
    "color": get_random_color()
  },
  "daily_eng":{
     "value": get_daily_eng(),
    "color": get_random_color()
  }
}

if __name__ == '__main__':
  count = 0
  try:
    for user_id in user_ids:
      res = wm.send_template(user_id, template_id, data)
      count+=1
  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了" + str(count) + "条消息")

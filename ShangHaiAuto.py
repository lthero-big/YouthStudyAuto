import re
import requests
import json
import yaml
import time
import random
from datetime import datetime
import argparse
from bs4 import BeautifulSoup
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 获取配置文件
def getYmlConfig(yaml_file='./config.yml'):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        file_data = f.read()
    return dict(yaml.load(file_data, Loader=yaml.FullLoader))

# 获取邮件 API URL 和本地邮件配置
config = getYmlConfig()
mailApiUrl = config.get('mailApiUrl', 'https://default-api-url')
mailApiPasswd = config.get('mailApiPasswd', 'defaultpassword')
EMAIL_FROM = config.get('EMAIL_FROM', 'from@runoob.com')
EMAIL_HOST_PASSWORD = config.get('EMAIL_HOST_PASSWORD', 'aaabbbbb')
EMAIL_HOST = config.get('EMAIL_HOST', 'smtp.XXX.com')
EMAIL_PORT = config.get('EMAIL_PORT', 80)

getToken_url = 'https://qcsh.h5yunban.com/youth-learning/cgi-bin/login/we-chat/callback'
getUserInfo_url = 'https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/course/last-info'
getClass_url = 'https://qcsh.h5yunban.com/youth-learning/cgi-bin/common-api/course/current'
checkin_url = 'https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/course/join'
getPersonalInfo_url = 'https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/info'
signin_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/sign-in/records"

headers = {
    'Content-Type': 'text/plain'
}

def getToken(openId):
    # 根据openId获得token
    try:
        token = requests.get(url=getToken_url, params=openId, headers=headers)
        Token_raw = token.text
        Token = re.findall('[A-Z0-9]{8}[-][A-Z0-9]{4}[-][A-Z0-9]{4}[-][A-Z0-9]{4}[-][A-Z0-9]{12}', Token_raw)[0]
        print('获取Token为:' + Token)
        accessToken = {
            'accessToken': Token
        }
        return accessToken
    except:
        print('获取Token失败，请检查openId是否正确')

def getinfo(accessToken):
    # 根据accessToken获得用户信息
    try:
        getUserInfo = requests.get(getUserInfo_url, params=accessToken, headers=headers)
        userInfo = getUserInfo.json()
        cardNo = userInfo["result"]["cardNo"]
        nid = userInfo["result"]["nid"]
        getClass = requests.get(getClass_url, params=accessToken, headers=headers)
        Class = getClass.json()
        classId = Class["result"]["id"]
        infos: list = userInfo['result']['nodes']
        Faculty = [item['title'] for item in infos]
        print('签到课程为：' + classId, '\n您填写的个人信息为：' + cardNo, '\n您的签到所属组织为：' + str(Faculty))
        checkinData = {
            'course': classId,
            'subOrg': None,
            'nid': nid,
            'cardNo': cardNo
        }
        return checkinData
    except Exception as e:
        if "is not subscriptable" in str(e):
            print("openid出错,无法获得您的信息")
        print(f'获取历史信息失败，请您手动打卡：{e}')
        print(userInfo)

def signup(accessToken, checkinData):
    # 根据token和data完成打卡
    checkin = requests.post(checkin_url, params=accessToken, data=json.dumps(checkinData), headers=headers)
    result = checkin.json()

    if result["status"] == 200:
        print("大学习成功")
        return 1
    else:
        print('出现错误，错误码：' + str(result["status"]))
        print('错误信息：' + str(result["message"]))
        return result["message"]

def daily_sign_in(accessToken):
    # 获取当前日期，并格式化为"YYYY-MM"
    date = datetime.now().strftime("%Y-%m")

    params = {
        "accessToken": accessToken['accessToken'],
        "date": date
    }

    # 发起GET请求
    checkin = requests.get(signin_url, params=params, headers=headers)
    result = checkin.json()
    
    if result["status"] == 200:
        print("每日签到成功")
        return 1
    else:
        print('出现错误，错误码：' + str(result["status"]))
        print('错误信息：' + str(result["message"]))
        return result["message"]

def getPersonalInfo(accessToken):
    # 获得个人信息
    info = requests.get(url=getPersonalInfo_url, params=accessToken, headers=headers).json()
    print('当前分数 ', info['result']['score'])
    return info['result']

# 通过API发送邮件
def sendMailApi(user, info, resStatus, task_type):
    task_message = "每日签到" if task_type == "daily" else "本周大学习"
    msg = "完成" if resStatus == 1 else resStatus
    # 接收方
    receiver = user['user']['mail']
    # 内容
    content = '{updateTime} 您好，{user}! {task_message}状态：{msg}。当前分数为{score}分'.format(
        user=info['nickname'],
        task_message=task_message,
        msg=msg,
        score=info['score'],
        updateTime=info['lastUpdTime']
    )
    print(content)
    params = {
        'reciever': receiver,
        'title': f'[{msg}] {task_message}打卡',
        'content': content,
        'innerTitle': '青年大学习',
        'passwd': mailApiPasswd
    }
    response = requests.post(mailApiUrl, data=params, verify=True)
    print("邮件发送状态：", response.status_code)

# 本地发送邮件
def sendMailLocal(user, info, resStatus, task_type):
    task_message = "每日签到" if task_type == "daily" else "本周大学习"
    msg = "完成" if resStatus == 1 else resStatus
    # 接收方
    to_email = user['user']['mail']
    # 内容
    content = '{updateTime} 您好，{user}! {task_message}状态：{msg}。当前分数为{score}分'.format(
        user=info['nickname'],
        task_message=task_message,
        msg=msg,
        score=info['score'],
        updateTime=info['lastUpdTime']
    )
    title = f'[{msg}] {task_message}打卡'
    
    # 自定义的回复地址
    replyto = EMAIL_FROM
    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = '%s <%s>' % ("发送方名称", EMAIL_FROM)
    msg['To'] = '%s <%s>' % ("接收方名称", to_email)
    msg['Reply-to'] = replyto
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    textplain = MIMEText('{}'.format(content), _subtype='plain', _charset='UTF-8')
    msg.attach(textplain)

    try:
        client = smtplib.SMTP()
        client.connect(EMAIL_HOST, EMAIL_PORT)
        client.set_debuglevel(0)
        client.login(EMAIL_FROM, EMAIL_HOST_PASSWORD)
        client.sendmail(EMAIL_FROM, [to_email], msg.as_string())
        client.quit()
        print(f"{GREEN}邮件发送成功！{NC}")
        return True
    except Exception as e:
        error_msg = f'{RED}邮件发送异常: {str(e)}{NC}'
        print(error_msg)
        return False

# 获取截图URL
def get_screenshot_url():
    response = requests.get('https://m.cyol.com/gb/channels/vrGlAKDl/index.html')
    response.raise_for_status()  # 检查请求是否成功
    soup = BeautifulSoup(response.text, 'html.parser')
    href_list = [a['href'] for a in soup.select('body section div ul a') if 'href' in a.attrs]
    
    if not href_list:
        raise ValueError("No href found in the specified location")
    
    first_href = href_list[0]
    
    if 'index.html' in first_href:
        return first_href.replace("index.html", "images/end.jpg")
    elif 'm.html' in first_href:
        return first_href.replace("m.html", "images/end.jpg")
    else:
        raise ValueError("Unexpected href format")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Youth Learning Automation")
    parser.add_argument('--daily', action='store_true', help="执行每日签到并发送邮件")
    parser.add_argument('--course', action='store_true', help="执行大学习打卡并发送邮件")
    parser.add_argument('--savePic', action='store_true', help="保存截图")
    parser.add_argument('--mailType', choices=['api', 'local', ''], default='', help="邮件发送方式（api、local 或留空）")
    args = parser.parse_args()
    print('===================任务开始========================')
    if args.savePic:
        screenshot_url = get_screenshot_url()
        screenshot_response = requests.get(screenshot_url)
        with open('./output.jpg', 'wb') as f:
            f.write(screenshot_response.content)
        print(f"截图已保存")
    
    if not args.daily and not args.course:
        print("错误: 至少需要传入 --daily 或 --course 参数")
        print("使用示例:")
        print("每日签到    python index.py --daily")
        print("大学习打卡  python index.py --course")
        exit(1)

    config = getYmlConfig()
    date = datetime.now().strftime("%Y-%m-%d")
    print(f'================{date}======================')
    for index, eachuser in enumerate(config['users']):
        print(eachuser['user']['name'], 'openId为 ', eachuser['user']['openid'])
        openid = {
            'appid': 'wx56b888a1409a2920',
            'openid': eachuser['user']['openid']
        }
        accesstoken = getToken(openid)

        if accesstoken:
            if args.daily:
                # 每日签到
                resStatus = daily_sign_in(accesstoken)
                if args.mailType == 'api':
                    sendMailApi(eachuser, getPersonalInfo(accesstoken), resStatus, "daily")
                elif args.mailType == 'local':
                    sendMailLocal(eachuser, getPersonalInfo(accesstoken), resStatus, "daily")

            if args.course:
                # 大学习打卡
                checkindata = getinfo(accesstoken)
                if checkindata:
                    resStatus = signup(accesstoken, checkindata)
                    if args.mailType == 'api':
                        sendMailApi(eachuser, getPersonalInfo(accesstoken), resStatus, "course")
                    elif args.mailType == 'local':
                        sendMailLocal(eachuser, getPersonalInfo(accesstoken), resStatus, "course")

        print("=================任务结束=========================")
        
        t = random.randint(1, 3)
        time.sleep(t)

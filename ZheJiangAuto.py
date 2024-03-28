import re
import requests
import json
import yaml
from lxml import etree
from urllib import request

getToken_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/login/we-chat/callback'
getUserInfo_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/last-info'
getClass_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/common-api/course/current'
checkin_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/join'
getPersonalInfo_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/info'

headers = {
    'Content-Type': 'text/plain'
}


def getYmlConfig(yaml_file='config.yml'):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        file_data = f.read()
    return dict(yaml.load(file_data, Loader=yaml.FullLoader))


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


def signup(accessToken, checkinData):
    # 根据token和data完成打卡
    checkin = requests.post(checkin_url, params=accessToken, data=json.dumps(checkinData), headers=headers)
    result = checkin.json()

    if result["status"] == 200:
        print("签到成功")
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
    # return info['result']['score']


# 调用接口发送邮件，不提供接口
def sendMail(user,info,resStatus):
    msg=resStatus
    if resStatus==1:
        msg="完成"
    # 接收方
    receiver = user['user']['mail']
    # 内容
    content = '{updateTime} 您好，{user}!本周大学习打卡：{msg}。当前分数为{score}分'.format(user=info['nickname'],msg=msg,score=info['score'],updateTime=info['lastUpdTime'])
    params = {
        'reciever': receiver,
        # 邮件标题
        'title': f'[{msg}]青年大学习打卡',
        # 主要内容
        'content': content,
        # 内部大标题
        'innerTitle': f'青年大学习'
    }
    requests.post(url='http://邮件接口/', data=params)
    print("邮件发送完成")

# 本地发送邮件，需要自行配置
def sendMail(to_email, title, content):
    
    EMAIL_FROM = 'from@runoob.com'  # 配置发信地址
    EMAIL_HOST_PASSWORD = "aaabbbbb"  # 密码
    EMAIL_HOST, EMAIL_PORT = 'smtp.XXX.com', 80
    
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
        return True
    except Exception as e:
        error_msg = '邮件发送异常, {}'.format(str(e))
    print(error_msg)
    return False
    
def get_screenshot_url():
    """
    获取截屏图片的URL。

    :return: 截屏图片的URL。
    """
    response = requests.get('https://m.cyol.com/gb/channels/vrGlAKDl/index.html')
    response_html = etree.HTML(response.text)
    href_list = response_html.xpath('/html/body/section[1]/div/ul//a/@href')
    if 'index.html' in href_list[0]:
        return href_list[0].replace("index.html", "images/end.jpg")
    elif 'm.html' in href_list[0]:
        return href_list[0].replace("m.html", "images/end.jpg")

if __name__ == "__main__":
    config = getYmlConfig()
    for index, eachuser in enumerate(config['users']):
        print(eachuser['user']['name'], 'openId为 ', eachuser['user']['openid'])
        openid = {
            'appid': 'wx56b888a1409a2920',
            'openid': eachuser['user']['openid']
        }
        accesstoken = getToken(openid)
        checkindata = getinfo(accesstoken)
        if checkindata is not None:
            personalInfo=getPersonalInfo(accesstoken)
            resStatus=signup(accesstoken, checkindata)
            # 需要自行配置接口
#             sendMail(eachuser,personalInfo,resStatus)
            # 需要自行配置发送邮箱
#             sendMail(eachuser['user']['mail'], "邮件标题", "邮件内容")
        print('===========================================')
    
    request.urlretrieve(get_screenshot_url(), f'./output.jpg')



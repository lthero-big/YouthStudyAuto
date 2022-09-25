import re
import requests
import json
import yaml

getToken_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/login/we-chat/callback'
getUserInfo_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/last-info'
getClass_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/common-api/course/current'
checkin_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/join'

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
        getToken = requests.get(url=getToken_url, params=openId, headers=headers)
        Token_raw = getToken.text
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
    else:
        print('出现错误，错误码：' + result["status"])
        print('错误信息：' + result["message"])


if __name__ == "__main__":
    config = getYmlConfig()
    for index, user in enumerate(config['users']):
        print(user['user']['name'], 'openId为 ', user['user']['openid'])
        openid = {
            'appid': 'wx56b888a1409a2920',
            'openid': user['user']['openid']
        }
        accesstoken = getToken(openid)
        checkindata = getinfo(accesstoken)
        if checkindata is not None:
            signup(accesstoken, checkindata)
        print('===========================================')

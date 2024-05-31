# 【浙江|上海】青年大学习一键打卡

**截止到2024.5.30，脚本依然可用**

## 特色

- [x] 脚本一键运行，直接更新后台数据完成打卡 :tada:
- [x] 支持导出每期的大学习截图
- [x] 支持为多人批量打卡 :thumbsup:
- [x] 支持各平台服务器部署，可设置定时打卡任务 :heavy_check_mark:

## 更新内容
2024.5.30更新：新增功能：每日签到，支持使用参数执行每日签到或大学习打卡

2024.3.28更新：感谢用户@b3nguang，新增功能：返回打卡完成的截屏图片的URL

2023.3.12更新：感谢吾爱用户：ahov 提供上海大学习接口，具体请查看[原帖](https://www.52pojie.cn/forum.php?mod=viewthread&tid=1694872&page=5#pid45902595)

目前已经添加上海青年大学习打卡脚本：ShangHaiAuto.py

## 代码思路：

- 每个微信账号有唯一的openid
- 在每次打开青年大学习网页时，后台会根据openid生成accessToken
- 后续的所有与服务器交互的信息，都需要用accessToken才能拿到
- 只要拿到个人信息，再将个人信息和accessToken提交即可打卡完成

## 使用

运行代码前，需要先获得openid，每个账号只要获得一次openid即可，以后无需重复抓包

### PC获得openid教程【推荐】

视频教程：https://wwd.lanzouy.com/isVnb0cc5jba 密码:bcg5

- 需要的软件：Fiddler [点击下载Fiddler](https://download.informer.com/win-1191997911-4004b638-614e06cc-07ada6a98fb9eae13-adb2284be2034d9c9-2076861186-1191989686/fiddler4setup.exe)、电脑版微信
- 打开Fiddler，安装证书
- 切换到微信，点击大学习，此时弹窗需要授权，点击“同意”。
- 点击“同意”后，切换到Fiddler，按“ctrl+f”，搜索openid，双击标黄处的包，并点击“WebForms”，在里面找到openid即可
- 注意：记录openId，因为以后没必要再次抓包！！！

### 安卓获得openId流程【部分手机无法用】

视频教程：https://wwd.lanzouy.com/isVnb0cc5jba 密码:bcg5

- 安卓下载抓包软件 httpcanary，安装并打开软件，有三步骤：1、同意条款 2、允许安装证书 3、root可以跳过
- 微信：打开大学习
- 软件httpcanary：点击右下角小飞机图标开始抓包
- 微信：点击“立即参与”->点击“去学习”。随后切到httpcanary，再点击右下角小飞机图标停止抓包。
- 软件httpcanary：点击右上角，找到“搜索”，直接搜索“openId”，注意：只要url是qczj.h5yunban.com的包。一般可以在包名为“qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/last-info”的响应中，找到openId
- 注意：记录openId，因为以后没必要再次抓包！！！

# 运行代码

## 下载本项目

### 方法一(推荐，可自动更新)
```sh
git clone https://github.com/lthero-big/YouthStudyAuto.git
cd YouthStudyAuto
```


### 方法二
```sh
wget https://github.com/lthero-big/YouthStudyAuto/archive/refs/heads/main.zip
```
解压文件
```
unzip main.zip
cd YouthStudyAuto-main
```

## 自动运行（推荐）
使用install.sh脚本，自动安装所需环境，支持对用户添加、查看、删除；配置打卡时间和签到时间（同步到crontab任务）；配置邮件发送api等

```sh
bash install.sh
```


## 手动运行

- 需要自行安装 `re`, `json`, `yaml`, `requests`, `beautifulsoup4` 库，命令`pip install -r requirements.txt`
- 获得**openid**后，将openid填入config.yml，运行index.py即可。
- config.yml里面的name用来标识不同的openid，无实际意义
```sh
users:
  - user:
      name: 'name1'
      openid: 'oO-a2t6Z_awwxOby5Y9eO5VL9Rqg'
      mail: 'aaaa@qq.com'
  - user:
      name: 'name2'
      openid: 'oO-a2t7bkGObaacIOd4U1Bpaf1l0'
      mail: 'bbbbb@qq.com'
```

### 功能参数说明

- `--daily`：执行每日签到
- `--course`：执行大学习打卡
- `--savePic`：保存打卡完成的截图
- `--mailType`：发送邮件，参数：  `api`  或  `local`

**运行示例**：
```sh

# 每日签到
python3 index.py --daily
# 每日签到并用api方式发送邮件
python3 index.py --daily --mailType api
# 每日签到并用本地邮箱配置方式发送邮件
python3 index.py --daily --mailType local
# 仅保存截图
python3 index.py --savePic
# 大学习打卡并保存截图
python3 index.py --course --savePic
# 全部执行
python3 index.py --daily --course --savePic
```


### 设置定时任务

> 填写好config.yml后，使用`crontab`命令，设置定时执行的任务

#### 方法

使用输入命令`crontab -e`进行编辑定时任务，把下面这行添加到最后一行

注意修改`/home/main/ZheJiangAuto.py`为**实际文件路径**

```sh
0 9 * * * python3 /home/main/ZheJiangAuto.py --daily >> /home/lthero/autosign.log 2>&1
0 10 * * 3,5 python3 /home/main/ZheJiangAuto.py --course >> /home/lthero/autosign.log 2>&1

```

每周三15点30分执行一次大学习打卡任务，每天9点执行签到任务，并且将打卡脚本输出的内容放在`/home/autosign.log`中



## 邮件发送功能

- 在config.yml配置好接收方邮箱**（建议使用install.sh进行配置）**
- 有两个sendMail函数，第一个是使用发送邮件的api，第二个是使用python库发送，没有api的可以使用第二个函数
- 在第二个sendMail中设置发送方邮箱信息【需要自行搜索“用QQ的SMTP发送邮件配置”】

------

## 注意

如果没有需要第2步授权步骤，而是直接进入大学习页面，则无法获得openid。

需要**彻底关掉微信**，并重新打开微信，再尝试。

无论手机端或电脑端，如果实现得不到openid，需要点击“开始学习”进入到选择省市的选项。

再切到Fiddler或httpcanary，按“ctrl+f”，搜索accessToken。得到accessToken后，

比如accessToken为xxxx-xxxx-xxxx-xxxx，将其合并到下面的链接

https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/info?accessToken=xxxx-xxxx-xxxx-xxxx

替换上面的xxxx-xxxx-xxxx-xxxx。

随后进行访问此链接，可以在**返回的结果里面找到openid**


## 常见问题

常见报错问题：https://github.com/lthero-big/YouthStudyAuto/issues/2#issuecomment-1500757348 

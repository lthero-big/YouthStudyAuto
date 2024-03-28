# 【浙江|上海】青年大学习一键打卡


## 特色

- [x] 脚本一键运行，直接更新后台数据完成打卡:tada:
- [x] 支持为多人批量打卡:thumbsup:
- [x] 支持各平台服务器部署，可设置定时打卡任务:heavy_check_mark:


## 更新内容

2024.3.28更新： 感谢用户@b3nguang，新增功能：返回打卡完成的截屏图片的URL

**截止到2024.3.28，脚本依然可用**

2023.3.12更新： 感谢吾爱用户：ahov 提供上海大学习接口，具体请查看[原帖](https://www.52pojie.cn/forum.php?mod=viewthread&tid=1694872&page=5#pid45902595)

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

- 需要的软件：Fiddler、电脑版微信
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

### 运行代码

- 需要自行安装re,json,ymal,requests库
- 获得openid后，将openid填入config.yml，运行index.py即可。
- config.yml里面的name用来标识不同的openid，无实际意义

## 部署到服务器

在服务器下载项目文件

```sh
wget https://github.com/lthero-big/ZheJiangYouthstudyAutoSign/archive/refs/heads/main.zip
```

解压文件

```
unzip main.zip
```

随后，使用vim或其它工具，填写好config.yml的信息

### 设置定时任务

> 填写好config.yml后，使用`crontab`命令，设置定时执行的任务

#### 方法一

使用输入命令`crontab -e`进行编辑定时任务，把下面这行添加到最后一行

注意修改`/home/main/ZheJiangAuto.py`为实际文件路径

```sh
30 15 * * 3  python /home/main/ZheJiangAuto.py >> /home/main/autosign.log 2>&1
```

每周三15点30分执行一次打卡任务，并且将打卡脚本输出的内容放在`/home/autosign.log`中

#### 方法二

先创建一个shell文件，如放在`/home/autosign.sh`，填写下面的内容

注意：把`/home/main/ZheJiangAuto.py`修改成实际的项目路径，main目录下要有config.yml文件

```sh
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
python /home/main/ZheJiangAuto.py
echo "----------------------------------------------------------------------------"
endDate=`date +"%Y-%m-%d %H:%M:%S"`
echo "[$endDate]"
echo "----------------------------------------------------------------------------"
```

随后，给/home/autosign.sh添加执行权限

```sh
chmod +x /home/autosign.sh
```

使用输入命令`crontab -e`进行编辑定时任务，把下面这行添加到最后一行

```sh
30 15 * * 3  /home/autosign.sh >> /home/autosign.log 2>&1
```

每周三15点30分执行一次打卡任务，并且将打卡脚本输出的内容放在`/home/autosign.log`中



## 邮件发送功能

- 在config.yml配置好接收方邮箱
- 有两个sendMail函数，第一个是使用发送邮件的api，第二个是使用python库发送，没有api的可以使用第二个函数
- 在第二个sendMail中设置发送方邮箱信息【需要自行搜索“用QQ的SMTP发送邮件配置”】

------

## 注意

如果没有需要第2步授权步骤，而是直接进入大学习页面，则无法获得openid。

需要彻底关掉微信，并重新打开微信，再尝试。

无论手机端或电脑端，如果实现得不到openid，需要点击“开始学习”进入到选择省市的选项。

再切到Fiddler或httpcanary，按“ctrl+f”，搜索accessToken。得到accessToken后，

比如accessToken为xxxx-xxxx-xxxx-xxxx，将其合并到下面的链接

https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/info?accessToken=xxxx-xxxx-xxxx-xxxx

替换上面的xxxx-xxxx-xxxx-xxxx。

随后进行访问此链接，可以在**返回的结果里面找到openid**

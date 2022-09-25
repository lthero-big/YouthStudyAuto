# 浙江青年大学习一键打卡

## 代码思路：

* 每个微信账号有唯一的openid

* 在每次打开青年大学习网页时，后台会根据openid生成accessToken

* 后续的所有与服务器交互的信息，都需要用accessToken才能拿到

* 只要拿到个人信息，再将个人信息和accessToken提交即可打卡完成

-------------------------------------------------------

## 安卓获得openId流程

* 安卓下载抓包软件 httpcanary，安装并打开软件，有三步骤：1、同意条款 2、允许安装证书 3、root可以跳过

* 微信：打开大学习

* 软件httpcanary：点击右下角小飞机图标开始抓包

* 微信：点击“立即参与”->点击“去学习”。随后切到httpcanary，再点击右下角小飞机图标停止抓包。

* 软件httpcanary：点击右上角，找到“搜索”，直接搜索“openId”，注意：只要url是qczj.h5yunban.com的包。一般可以在包名为“qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/last-info”的响应中，找到openId

* 注意：记录openId，因为以后没必要再次抓包！！！
   
   
-------------------------------------------------------

## PC获得openid教程
视频教程：https://wwd.lanzouy.com/isVnb0cc5jba 密码:bcg5

* 需要的软件：Fiddler、电脑版微信

* 打开Fiddler，安装证书

* 切换到微信，点击大学习，此时弹窗需要授权，点击“同意”。

* 点击“同意”后，切换到Fiddler，按“ctrl+f”，搜索openid，双击标黄处的包，并点击“WebForms”，在里面找到openid即可

-------------------------------------------------------

## 注意

如果没有需要第2步授权步骤，而是直接进入大学习页面，则无法获得openid。

需要彻底关掉微信，并重新打开微信，再尝试。

无论手机端或电脑端，如果实现得不到openid，需要点击“开始学习”进入到选择省市的选项。

再切到Fiddler或httpcanary，按“ctrl+f”，搜索accessToken。得到accessToken后，

比如accessToken为xxxx-xxxx-xxxx-xxxx，将其合并到下面的链接

https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/info?accessToken=xxxx-xxxx-xxxx-xxxx

替换上面的xxxx-xxxx-xxxx-xxxx。

随后进行访问此链接，可以在返回的结果里面，找到openid


-------------------------------------------------------

## 使用

* 获得openid后，将openid填入config.yml，运行index.py即可。config.yml里面的name用来标识不同的openid，无实际意义。


# 浙江青年大学习一键打卡

提取openId流程

* 安卓下载抓包软件 httpcanary，安装并打开软件，有三步骤：1、同意条款 2、允许安装证书 3、root可以跳过

* 微信：打开大学习

* 软件httpcanary：点击右下角小飞机图标开始抓包

* 微信：点击“立即参与”->点击“去学习”。随后切到httpcanary，再点击右下角小飞机图标停止抓包。

* 软件httpcanary：点击右上角，找到“搜索”，直接搜索“openId”，注意：只要url是qczj.h5yunban.com的包。一般可以在包名为“qczj.h5yunban.com/qczj-youth-learning/cgi-bin/**user-api/course/last-info”的响应中，找到openId

* 注意：记录openId，因为以后没必要再次抓包！！！

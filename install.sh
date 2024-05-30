#!/bin/bash

# 获取当前脚本目录
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # 无颜色

# 设置默认的Python脚本
PYTHON_SCRIPT="ZheJiangAuto.py"

# 函数：安装Python3和pip3
install_dependencies() {
    echo "请输入地区（zj 或 sh），默认为 zj："
    read region
    if [[ "$region" == "sh" ]]; then
        PYTHON_SCRIPT="ShangHaiAuto.py"
    else
        PYTHON_SCRIPT="ZheJiangAuto.py"
    fi
    echo -e "${GREEN}使用的Python脚本为: $PYTHON_SCRIPT${NC}"

    # 检查并安装Python3
    if ! command -v python3 &>/dev/null; then
        echo "Python3 未安装。正在安装 Python3..."
        sudo apt-get update
        sudo apt-get install -y python3
    fi

    # 检查并安装pip3
    if ! command -v pip3 &>/dev/null; then
        echo "pip3 未安装。正在安装 pip3..."
        sudo apt-get update
        sudo apt-get install -y python3-pip
    fi

    # 安装依赖
    echo "安装依赖项..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"

    echo -e "${GREEN}安装完成！${NC}"
}

# 函数：配置每日签到时间
configure_daily_signin_time() {
    echo "请输入每日签到的时间（0~24小时）："
    read hour
    if [[ "$hour" -ge 0 && "$hour" -le 24 ]]; then
        echo -e "${GREEN}每日签到时间设置为 $hour 点。${NC}"
    else
        hour=10
        echo -e "${RED}输入非法，默认每日签到时间为上午10点。${NC}"
    fi

    cron_job="0 $hour * * * python3 $SCRIPT_DIR/$PYTHON_SCRIPT --daily >> $SCRIPT_DIR/autoStudy.log 2>&1"

    # 检查是否已经存在相同的任务
    (crontab -l 2>/dev/null | grep -F "$cron_job") && echo -e "${GREEN}每日签到任务已存在，不重复添加。${NC}" || (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    echo -e "${GREEN}每日签到任务已配置，日志保存在 $SCRIPT_DIR/autoStudy.log${NC}"
}

# 函数：配置每周大学习打卡时间
configure_weekly_course_time() {
    echo "请输入每周大学习打卡的周几（1~7）："
    read day
    if [[ "$day" -ge 1 && "$day" -le 7 ]]; then
        echo -e "${GREEN}每周打卡设置为周 $day。${NC}"
    else
        day=3
        echo -e "${RED}输入非法，默认每周打卡时间为周三。${NC}"
    fi

    echo "请输入打卡的时间（0~24小时）："
    read hour
    if [[ "$hour" -ge 0 && "$hour" -le 24 ]]; then
        echo -e "${GREEN}打卡时间设置为 $hour 点。${NC}"
    else
        hour=10
        echo -e "${RED}输入非法，默认打卡时间为上午10点。${NC}"
    fi

    cron_job="0 $hour * * $day python3 $SCRIPT_DIR/$PYTHON_SCRIPT --course >> $SCRIPT_DIR/autoStudy.log 2>&1"

    # 检查是否已经存在相同的任务
    (crontab -l 2>/dev/null | grep -F "$cron_job") && echo -e "${GREEN}每周大学习打卡任务已存在，不重复添加。${NC}" || (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    echo -e "${GREEN}每周大学习打卡任务已配置，日志保存在 $SCRIPT_DIR/autoStudy.log${NC}"
}

# 函数：保存当前周的大学习截图
save_weekly_screenshot() {
    python3 $SCRIPT_DIR/$PYTHON_SCRIPT --savePic
    echo -e "${GREEN}截图已保存到 $(readlink -f $SCRIPT_DIR/output.jpg)${NC}"
}

# 函数：检查是否有更新
check_for_updates() {
    cd $SCRIPT_DIR
    git fetch origin main
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    if [ $LOCAL != $REMOTE ]; then
        echo "检测到新版本，是否更新？(y/n)"
        read answer
        if [ "$answer" == "y" ]; then
            git pull origin main
            echo -e "${GREEN}项目已更新！${NC}"
        else
            echo -e "${RED}取消更新。${NC}"
        fi
    else
        echo -e "${GREEN}当前已是最新版本。${NC}"
    fi
}

# 函数：查看config.yml文件
view_config() {
    if [ -f "$SCRIPT_DIR/config.yml" ]; then
        cat "$SCRIPT_DIR/config.yml"
    else
        echo -e "${RED}config.yml文件不存在。${NC}"
    fi
}

# 函数：添加新用户到config.yml
add_user() {
    echo "请输入用户名："
    read username
    echo "请输入openid："
    read openid
    echo "请输入邮箱："
    read email

    new_user="
  - user:
      name: '$username'
      openid: '$openid'
      mail: '$email'"

    if [ -f "$SCRIPT_DIR/config.yml" ]; then
        echo "$new_user" >> "$SCRIPT_DIR/config.yml"
        echo -e "${GREEN}新用户已添加到config.yml。${NC}"
    else
        echo -e "${RED}config.yml文件不存在。${NC}"
    fi
}


# 主菜单
show_menu() {
    echo "请选择一个选项："
    echo "1. 开始安装"
    echo "2. 配置每日签到时间"
    echo "3. 配置每周大学习打卡时间"
    echo "4. 保存当前周的大学习截图"
    echo "5. 更新项目"
    echo "6. 查看config.yml文件"
    echo "7. 添加新用户"
    echo "8. 退出脚本"
    read choice

    case $choice in
        1)
            install_dependencies
            ;;
        2)
            configure_daily_signin_time
            ;;
        3)
            configure_weekly_course_time
            ;;
        4)
            save_weekly_screenshot
            ;;
        5)
            check_for_updates
            ;;
        6)
            view_config
            ;;
        7)
            add_user
            ;;
        8)
            echo "退出脚本。"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择。${NC}"
            ;;
    esac
}

# 循环显示菜单，直到用户选择退出
while true; do
    show_menu
done

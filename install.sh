#!/bin/bash

# 获取当前脚本目录
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # 无颜色

# 设置默认的Python脚本
PYTHON_SCRIPT="ZheJiangAuto.py"

# 函数：安装Python3、pip3 和 yq
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

    # 检查并安装yq
    if ! command -v yq &>/dev/null; then
        echo "yq 未安装。正在安装 yq..."
        sudo wget https://github.com/mikefarah/yq/releases/download/v4.6.1/yq_linux_amd64 -O /usr/bin/yq
        sudo chmod +x /usr/bin/yq
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

    echo "请选择邮件发送方式（api、local 或留空为不发送）："
    read mailType

    if [[ -n "$mailType" ]]; then
        cron_job="0 $hour * * * cd $SCRIPT_DIR && python3 $SCRIPT_DIR/$PYTHON_SCRIPT --daily --mailType $mailType >> $SCRIPT_DIR/autoStudy.log 2>&1"
    else
        cron_job="0 $hour * * * cd $SCRIPT_DIR && python3 $SCRIPT_DIR/$PYTHON_SCRIPT --daily >> $SCRIPT_DIR/autoStudy.log 2>&1"
    fi

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

    echo "请选择邮件发送方式（api、local 或留空为不发送）："
    read mailType

    if [[ -n "$mailType" ]]; then
        cron_job="0 $hour * * $day cd $SCRIPT_DIR && python3 $SCRIPT_DIR/$PYTHON_SCRIPT --course --mailType $mailType >> $SCRIPT_DIR/autoStudy.log 2>&1"
    else
        cron_job="0 $hour * * $day cd $SCRIPT_DIR && python3 $SCRIPT_DIR/$PYTHON_SCRIPT --course >> $SCRIPT_DIR/autoStudy.log 2>&1"
    fi

    # 检查是否已经存在相同的任务
    (crontab -l 2>/dev/null | grep -F "$cron_job") && echo -e "${GREEN}每周大学习打卡任务已存在，不重复添加。${NC}" || (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    echo -e "${GREEN}每周大学习打卡任务已配置，日志保存在 $SCRIPT_DIR/autoStudy.log${NC}"
}

# 函数：执行一次打卡或签到任务
run_task() {
    echo "请输入地区（zj 或 sh），默认为 zj："
    read region
    if [[ "$region" == "sh" ]]; then
        PYTHON_SCRIPT="ShangHaiAuto.py"
    else
        PYTHON_SCRIPT="ZheJiangAuto.py"
    fi
    echo "请输入任务类型（d 表示 daily，c 表示 course），默认为 course："
    read task_type
    if [[ "$task_type" == "d" ]]; then
        task_type="--daily"
    else
        task_type="--course"
    fi
    echo "请选择邮件发送方式（api、local 或留空为不发送）："
    read mailType
    if [[ "$mailType" == "a" ]]; then
        mailType="api"
    else
        mailType="local"
    fi
    if [[ -n "$mailType" ]]; then
        cd $SCRIPT_DIR && python3 $SCRIPT_DIR/$PYTHON_SCRIPT $task_type --mailType $mailType
    else
        cd $SCRIPT_DIR && python3 $SCRIPT_DIR/$PYTHON_SCRIPT $task_type
    fi
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

# 函数：查看当前配置的打卡时间和每日签到时间
view_cron_jobs() {
    echo -e "${GREEN}当前配置的打卡时间和每日签到时间：${NC}"
    cron_jobs=$(crontab -l 2>/dev/null | grep "$SCRIPT_DIR/$PYTHON_SCRIPT")
    if [ -z "$cron_jobs" ]; then
        echo -e "${RED}未配置任何打卡或签到任务。${NC}"
    else
        echo "$cron_jobs"
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

    if [ -f "$SCRIPT_DIR/config.yml" ]; then
        yq eval ".users += [{\"user\": {\"name\": \"$username\", \"openid\": \"$openid\", \"mail\": \"$email\"}}]" -i "$SCRIPT_DIR/config.yml"
        echo -e "${GREEN}新用户已添加到config.yml。${NC}"
    else
        cat <<EOL > "$SCRIPT_DIR/config.yml"
users:
  - user:
      name: '$username'
      openid: '$openid'
      mail: '$email'
EOL
        echo -e "${GREEN}config.yml文件不存在，新建并添加用户。${NC}"
    fi
}

# 函数：删除用户
delete_user() {
    echo "请输入要删除的用户名："
    read username

    if [ -f "$SCRIPT_DIR/config.yml" ]; then
        yq eval "del(.users[] | select(.user.name == \"$username\"))" "$SCRIPT_DIR/config.yml" -i
        if [ "$(yq eval '.users | length' "$SCRIPT_DIR/config.yml")" -eq 0 ]; then
            yq eval 'del(.users)' "$SCRIPT_DIR/config.yml" -i
        fi
        echo -e "${GREEN}用户已从config.yml删除。${NC}"
    else
        echo -e "${RED}config.yml文件不存在。${NC}"
    fi
}



# 函数：修改邮件API URL和passwd
modify_mail_api_url() {
    echo "请输入新的邮件API URL："
    read new_url
    echo "请输入新的邮件API密码："
    read new_passwd

    if [ -f "$SCRIPT_DIR/config.yml" ]; then
        yq eval ".mailApiUrl = \"$new_url\"" "$SCRIPT_DIR/config.yml" -i
        yq eval ".mailApiPasswd = \"$new_passwd\"" "$SCRIPT_DIR/config.yml" -i
        echo -e "${GREEN}邮件API URL和密码已更新。${NC}"
    else
        cat <<EOL > "$SCRIPT_DIR/config.yml"
mailApiUrl: "$new_url"
mailApiPasswd: "$new_passwd"
EOL
        echo -e "${GREEN}config.yml文件不存在，新建并设置邮件API URL和密码。${NC}"
    fi
}

# 函数：修改本地邮件配置信息
modify_mail_config() {
    echo "请输入发信地址："
    read email_from
    echo "请输入密码："
    read email_password
    echo "请输入EMAIL_HOST："
    read email_host
    echo "请输入EMAIL_PORT："
    read email_port

    if [ -f "$SCRIPT_DIR/config.yml" ]; then
        yq eval ".EMAIL_FROM = \"$email_from\"" "$SCRIPT_DIR/config.yml" -i
        yq eval ".EMAIL_HOST_PASSWORD = \"$email_password\"" "$SCRIPT_DIR/config.yml" -i
        yq eval ".EMAIL_HOST = \"$email_host\"" "$SCRIPT_DIR/config.yml" -i
        yq eval ".EMAIL_PORT = $email_port" "$SCRIPT_DIR/config.yml" -i
        echo -e "${GREEN}本地邮件配置信息已更新。${NC}"
    else
        cat <<EOL > "$SCRIPT_DIR/config.yml"
EMAIL_FROM: "$email_from"
EMAIL_HOST_PASSWORD: "$email_password"
EMAIL_HOST: "$email_host"
EMAIL_PORT: $email_port
EOL
        echo -e "${GREEN}config.yml文件不存在，新建并设置本地邮件配置信息。${NC}"
    fi
}

# 主菜单
show_menu() {
    echo "请选择一个选项："
    echo "1. 开始安装"
    echo "2. 查看当前配置的打卡时间和每日签到时间"
    echo "3. 配置每日签到时间"
    echo "4. 配置每周大学习打卡时间"
    echo "5. 执行一次打卡或签到任务"
    echo "6. 保存当前周的大学习截图"
    echo "7. 查看config.yml文件"
    echo "8. 添加新用户"
    echo "9. 删除用户"
    echo "10. 修改邮件API URL和密码"
    echo "11. 修改本地邮件配置信息"
    echo "12. 更新项目"
    echo "13. 退出脚本"
    read choice

    case $choice in
        1)
            install_dependencies
            ;;
        2)
            view_cron_jobs
            ;;
        3)
            configure_daily_signin_time
            ;;
        4)
            configure_weekly_course_time
            ;;
        5)
            run_task
            ;;
        6)
            save_weekly_screenshot
            ;;
        7)
            view_config
            ;;
        8)
            add_user
            ;;
        9)
            delete_user
            ;;
        10)
            modify_mail_api_url
            ;;
        11)
            modify_mail_config
            ;;
        12)
            check_for_updates
            ;;
        13)
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

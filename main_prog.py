import smtplib
import time
from necessary_func import *
import logging
from datetime import datetime
import os
import pandas as pd
from email.mime.text import MIMEText


#出问题邮箱通知
def send_email(content):
    #163邮箱服务器地址
    mail_host = 'smtp.163.com'
    #163用户名
    mail_user = 'lixutai111'
    #密码(部分邮箱为授权码)
    mail_pass = 'BUPPJPOHPBFXOSDP'
    #邮件发送方邮箱地址
    sender = 'lixutai111@163.com'
    #邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = ['lixutai111@163.com']
    # 设置email信息
    # 邮件内容设置
    message = MIMEText(f"{content}", 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = "电脑1运行被封"
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP()
        # 连接到服务器
        smtpObj.connect(mail_host, 25)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误




#记录日志
def setup_logger():
    """
    设置日志记录器
    """
    # 创建logs文件夹（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 生成日志文件名（包含时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/error_log_{timestamp}.txt'
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    return logging.getLogger()

# 创建日志记录器
logger = setup_logger()

page = ChromiumPage()

# # 读取CSV文件
df = pd.read_csv(r"E:\360MoveData\Users\李绪泰\OneDrive\桌面\Graduate\备份文件\北京数据\hotels_id_beijing_single.csv")
print("成功读取酒店数据")
#爬取失败的重新爬
# df=pd.read_csv(r'C:\Users\李绪泰\OneDrive\桌面\GraduateWork\logs\failed_urls1.txt')
# # print(df.head())  # 显示前5行数据
# print("成功读取失败酒店数据")
# 构建完整的酒店URL
df['hotel_url'] = 'https://hotels.ctrip.com/hotels/' + df['id'].astype(str)+'.html'
print(df['hotel_url'])
for i in range(19,len(df)):
# for curl in df['hotel_url']:
    curl=df['hotel_url'][i]
    print(curl)
    try:
        result1 = get_individual_data(curl)
        print(f"成功处理酒店URL: {curl}")
        random_seconds = random.randint(60, 120)
        # 输出即将暂停的时间
        print(f"程序将暂停 {random_seconds} 秒。")
        # 暂停程序
        time.sleep(random_seconds)
    except Exception as e:
        # 记录错误信息
        error_msg = f"处理酒店 {curl} 时出错: {str(e)}"
        logger.error(error_msg)

        # 记录详细的错误堆栈
        import traceback
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        #send_email(traceback.format_exc())

        # 记录失败的URL到单独的文件
        with open('logs/failed_urls2.txt', 'a', encoding='utf-8') as f:

            f.write(f"{curl}\n")

        continue






import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SendEmail:

    def __init__(self, user=None, password=None, tag=None, content=None, doc=None, cc_list=None, to_list=None):
        """
        :param  user        发送人邮箱账号
        :param  password    发送人邮箱密码
        :param  to_list     收件人邮箱账号列表
        :param  tag         邮箱主题
        :param  content     发送内容
        :param  doc         附件
        """
        self.user = user
        self.password = password
        self.tag = tag
        self.content = content
        self.doc = doc
        self.cc_list = cc_list
        self.to_list = to_list

    def structure_email_content(self):
        """构造邮件内容"""
        attach = MIMEMultipart()
        if self.user is not None:
            # 发件人
            attach['From'] = f'发件人：<{self.user}>'
        if self.tag is not None:
            # 主题
            attach['Subject'] = self.tag
        if self.content:
            email_content = MIMEText(
                self.content.get('content', ''),
                self.content.get('type', 'plain'),
                self.content.get('coding', ''),
            )
            attach.attach(email_content)
        if self.doc:
            # 估计任何文件都可以用 base64, 比如 rar 等
            # 文件名汉字使用 gbk 编码
            name = os.path.basename(self.doc)
            f = open(self.doc, 'rb')
            doc = MIMEText(f.read(), 'base64', 'utf-8')
            doc['Content-Type'] = 'application/octet-stream'
            doc['Content-Disposition'] = 'attachment; filename="' + name + '"'
            attach.attach(doc)
            f.close()
        if self.to_list:
            # 收件人列表
            attach['To'] = ';'.join(self.to_list)
            
        return attach.as_string()

    def send(self):
        """发送邮件"""
        try:
            # 开启邮箱服务
            server = smtplib.SMTP_SSL('smtp.exmail.qq.com', port=465)
            # 登录邮箱
            server.login(self.user, self.password)
            print('邮件开始发送 -------->')
            server.sendmail(f'<{self.user}>', self.to_list, self.structure_email_content())
            server.close()
            print('邮件发送成功 --------<')
        except Exception as e:
            print(f'邮件发送失败：{e}')


if __name__ == '__main__':
    SendEmail(
        user='发送者的邮箱账号',
        password='发送者的邮箱密码',
        tag='这是邮箱主题',
        content={
            'content': '这是测试内容',
            'type': 'plain',
            'coding': 'utf-8'
        },
        to_list=['接收者1的邮箱账号', '接收者2的邮箱账号'],
    ).send()

import json
import requests
from enum import Enum


class DingDingAPI(object):
    """
    发送钉钉消息
    1.在群里添加自定义机器人
    2.获取到机器人名字 和 url
    """

    class MsgType(Enum):
        text = 'text'
        link = 'link'
        markdown = 'markdown'

    HOOK_MAP = {
        'oms_test': {
            'title': '报警测试',
            'url': 'https://oapi.dingtalk.com/robot/send?access_token=3963e26b849294299817694debeaa76457004d8f98acebc30b54a2579c000685'
        },
    }

    def __init__(self, name):
        _hook = self.HOOK_MAP.get(name)
        self.title, self.url = _hook.get('title'), _hook.get('url')

    @property
    def msg_type(self):
        return self._msg_type

    @msg_type.setter
    def msg_type(self, value):
        if not isinstance(value, self.MsgType):
            raise Exception('{} 必须是 WebHook.MsgType 类型'.format(value))
        self._msg_type = value

    def _send_text(self, msg, at=None, at_all=True, *args, **kwargs):
        """
        发送文本类型消息
        :param msg: 消息内容
        :param at:被@人的手机号(在content里添加@人的手机号) 列表　["156xxxx8827", "189xxxx8325"]
        :param at_all:@所有人时：true，否则为：false
        :return:
        """
        self._data = {
            "msgtype": self.MsgType.text.value,
            "text": {
                "content": '{}警报: {}'.format(self.title, msg)
            },
            "at": {
                "atMobiles": at,
                "isAtAll": at_all
            }
        }

    def _send_link(self, msg, title, message_url, pic_url='', *args, **kwargs):
        """
        发送链接类型消息
        :param msg:消息内容。如果太长只会部分展示
        :param title:消息标题
        :param message_url:点击消息跳转的URL
        :param pic_url:图片URL
        :return:
        """
        self._data = {
            "msgtype": self.MsgType.link.value,
            "link": {
                "text": msg,
                "title": '{}警报: {}'.format(self.title, title),
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }

    def _send_markdown(self, msg, title=None, at=None, at_all=True, *args, **kwargs):
        """
        发送　markdown格式的消息
        :param msg: markdown格式的消息
        :param title: 首屏会话透出的展示内容
        :param at: 被@人的手机号(在text内容里要有@手机号) 列表　["156xxxx8827", "189xxxx8325"]
        :param at_all: @所有人时：true，否则为：false
        :return:
        """
        self._data = {
            "msgtype": self.MsgType.markdown.value,
            "markdown": {
                "title": '{}警报: {}'.format(self.title, title),
                "text": msg
            },
            "at": {
                "atMobiles": at,
                "isAtAll": at_all
            }
        }

    def send(self, *args, **kwargs):
        send_method = {
            self.MsgType.text: self._send_text,
            self.MsgType.link: self._send_link,
            self.MsgType.markdown: self._send_markdown
        }
        if not self._msg_type:
            raise Exception('请先设置消息类型')
        _send_params = send_method[self._msg_type]
        _send_params(*args, **kwargs)
        res = requests.post(self.url, data=json.dumps(self._data), headers={'Content-Type': 'application/json'}, timeout=10)

        return res.content

if __name__ == '__main__':
    hook = DingDingAPI('oms_test')
    hook.msg_type = hook.MsgType.markdown
    # 这里调用 send() 方法时, 参数里必须包含 "注意" 二字
    # 因为在添加机器人时设置的关键词目前就只有这个
    # r = hook.send('注意：这是一次测试...', at=["15018267752"], atall=False)
    r = hook.send('注意：这是一次测试...', atall=False)
    print(r)
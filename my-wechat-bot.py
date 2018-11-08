import time
from wxpy import *
from re import *

bot=Bot()
bot.enable_puid()
global target_group
global group_chat
msgs = dict()

# message types
msg_types = {
    'Text': '文本',
    'Map': '位置',
    'Picture': '图片',
    'Video': '视频',
    'Attachment': '文件',
    'Sharing': '分享',
    'Card': '名片',
    'Recording': '语音',
}

all_groups = bot.groups().search('QC AWS scrum masters', bot.self)


@bot.register(all_groups, except_self=False)
def message_listener(msg):
    raw=msg.raw
    bot.file_helper.send("puid" + msg.member.puid)
    if raw.get('Status') == 4:
        if isinstance(msg.chat, wxpy.api.chats.group.Group):
            puid = msg.member.puid
            name = msg.member.nick_name
        else:
            puid = None
            name = None

        if puid:
            msg_id_regex = re.compile('<msgid>(\d+)</msgid>')
            # acquire recalled message msgid
            old_msg_id = msg_id_regex.findall(raw.get('Content'))[0]
            # acquire member's last 10 messages
            chat_msgs = msgs.get(puid)
            # iterate through old messages
            for chat_msg in chat_msgs[::-1]:
                # skip not recalled message
                if str(chat_msg.id) != old_msg_id:
                    continue
                chat = chat_msg.chat
                # if recalled message is text
                if chat_msg.type == "Text":
                    # if message was too long, ignore
                    if len(chat_msg.text) >= 150:
                        warning = "【您撤回的消息过长，有炸群嫌疑，不予处理！！！】"
                        bot.file_helper.send('%s撤回了一条文本消息--【%s】'.decode('utf-8') % (name, warning))
                        break
                    # repost recalled message
                    bot.file_helper.send('in text if')
                    chat_msg.forward(all_groups[0], prefix='%s撤回了一条文本消息，消息内容为：'.decode('utf-8') % name)
                # if recalled message is location
                elif chat_msg.type == "Map":
                    map_regex = re.compile(r'label="(.+?)"')
                    # acquire recalled location info
                    map = map_regex.findall(chat_msg.raw.get("OriContent"))[0]
                    # repost recalled message
                    msg.reply('%s撤回了一条位置消息，位置信息为：【%s】'.decode('utf-8') % (name, map))
                else:
                    # get message info
                    msg_type = msg_types.get(chat_msg.type).decode('utf-8')
                    # repost recalled message
                    chat_msg.forward(chat, prefix='%s撤回了一条%s消息， 消息内容为：'.decode('utf-8') % (name, msg_type))
                break
    else:
        if isinstance(msg.chat, wxpy.api.chats.group.Group):
            # acquire group member puid
            puid = msg.member.puid
        else:
            puid = None

        bot.file_helper.send(puid + "not a recall")
        if puid:
            # message record
            msgs.setdefault(puid, []).append(msg)
            # message record, save up to 10
            msgs[puid] = msg[puid][-10:]


embed()

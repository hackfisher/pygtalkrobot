#!/usr/bin/python
# -*- coding: utf-8 -*-

# PyGtalkRobot: A simple jabber/xmpp bot framework using Regular Expression Pattern as command controller
# Copyright (c) 2008 Demiao Lin <ldmiao@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Homepage: http://code.google.com/p/pygtalkrobot/
#

#
# This is an ordering PyGtalkRobot that serves to set the show type and status text of robot by receiving message commands.
#

import sys
import time
import xmpp
import threading
import pickle

from PyGtalkRobot import GtalkRobot

############################################################################################################################

class OrderingBot(GtalkRobot):
    ########################################################################################################################
    t = None
    orderlist = {}
    subscribedict = {}
    currentday = None
    ########################################################################################################################
    
    #Regular Expression Pattern Tips:
    # I or IGNORECASE <=> (?i)      case insensitive matching
    # L or LOCALE <=> (?L)          make \w, \W, \b, \B dependent on the current locale
    # M or MULTILINE <=> (?m)       matches every new line and not only start/end of the whole string
    # S or DOTALL <=> (?s)          '.' matches ALL chars, including newline
    # U or UNICODE <=> (?u)         Make \w, \W, \b, and \B dependent on the Unicode character properties database.
    # X or VERBOSE <=> (?x)         Ignores whitespace outside character sets
    
    #"command_" is the command prefix, "001" is the priviledge num, "setState" is the method name.
    #This method is used to change the state and status text of the bot.
    def command_001_setState(self, user, message, args):
        #the __doc__ of the function is the Regular Expression of this command, if matched, this command method will be called. 
        #The parameter "args" is a list, which will hold the matched string in parenthesis of Regular Expression.
        '''(available|online|on|busy|dnd|away|idle|out|off|xa)( +(.*))?$(?i)'''
        show = args[0]
        status = args[1]
        jid = user.getStripped()

        # Verify if the user is the Administrator of this bot
        if jid == 'orderingrobot@gmail.com':
            print jid, " ---> ",bot.getResources(jid), bot.getShow(jid), bot.getStatus(jid)
            self.setState(show, status)
            self.replyMessage(user, "State settings changed！")

    #This method is used to send email for users.
    def command_002_SendEmail(self, user, message, args):
        #email ldmiao@gmail.com hello dmeiao, nice to meet you, bla bla ...
        '''[email|mail|em|m]\s+(.*?@.+?)\s+(.*?),\s*(.*?)(?i)'''
        email_addr = args[0]
        subject = args[1]
        body = args[2]
        #call_send_email_function(email_addr, subject,  body)
        
        self.replyMessage(user, "\nEmail sent to "+ email_addr +" at: "+time.strftime("%Y-%m-%d %a %H:%M:%S", time.gmtime()))
    
    #This method is used to response users.
    def command_100_default(self, user, message, args):
        '''.*?(?s)(?m)'''
        infos = message.split()
        username = (str(user.getStripped())).lower();
        today = time.strftime("%Y-%m-%d", time.localtime())
        if not today == self.currentday:
            self.currentday = today
            self.orderlist.clear()
        if infos[0] == 'ordering' and len(infos) >= 2:
            num = int(infos[1])
            self.orderlist[username] = num;
            reply = "亲爱的" + username + "\n"
            reply += "您成功订餐" + str(num) + "份！\n"
            reply += "欢迎明天再次光临!"
            self.replyMessage(user, reply)
        elif infos[0] == 'cancel':
            if self.orderlist.has_key(username):
                del self.orderlist[username]
                self.replyMessage(user, "取消订餐成功！")
            else:
                self.replyMessage(user, "您没有订餐！")
        elif infos[0] == 'query':
            reply = "订餐明细:\n"
            count = 0;
            for k, v in self.orderlist.iteritems():
                reply += "顾客" + k + "订了" + str(v) + "份！\n"
                count += v
            reply += "今天已订餐共" + str(count) + "份！\n"
            self.replyMessage(user, reply)
        elif infos[0] == 'subscribe':
            if len(infos) == 1:
                if self.subscribedict.has_key(username):
                    self.replyMessage(user, '您已经订阅过订餐提醒了！')
                else:
                    nickname = '帅哥/美女'
                    self.subscribedict[username] = nickname
                    self.replyMessage(user, nickname + ':\n订餐提醒订阅成功')
                    self.dumpSubscribeDict()
            elif len(infos) == 2:
                if self.subscribedict.has_key(infos[1].lower()):
                    self.replyMessage(user, infos[1].lower()+ '已经订阅过订餐提醒了！')
                else:
                    nickname = '帅哥/美女'
                    self.subscribedict[infos[1].lower()] = nickname
                    self.replyMessage(user, nickname + ':\n订餐提醒订阅成功')
                    self.dumpSubscribeDict()
            elif len(infos) >= 3:
                if self.subscribedict.has_key(infos[1].lower()):
                    self.replyMessage(user, infos[1].lower()+ '已经订阅过订餐提醒了！')
                else:
                    nickname = infos[2]
                    self.subscribedict[infos[1].lower()] = nickname
                    self.replyMessage(user, '您帮助' + infos[1].lower() + ':' + nickname + ':\n订餐提醒订阅成功')
                    self.dumpSubscribeDict()
        elif infos[0] == 'unsubscribe':
            if len(infos) == 1:
                if not self.subscribedict.has_key(username):
                    self.replyMessage(user, '您没有订阅过订餐提醒！')
                else:
                    del self.subscribedict[username]
                    self.replyMessage(user, '您取消订餐提醒成功！')
                    self.dumpSubscribeDict()
            else:
                arg2 = infos[1].lower()
                if arg2 == 'all':
                    self.subscribedict.clear()
                    self.dumpSubscribeDict()
                    self.replyMessage(user, '清除全部订餐提醒！')
                elif self.subscribedict.has_key(arg2):
                    del self.subscribedict[arg2]
                    self.replyMessage(user, '您帮助'+ arg2 +'取消订餐提醒成功！')
                    self.dumpSubscribeDict()
                else:
                    self.replyMessage(user, arg2 + '没有订阅过订餐提醒！')
        elif infos[0] == 'whoisyourdaddy':
            reply = "下面这些人订阅了订餐提醒:\n"
            count = 0;
            for k, v in self.subscribedict.iteritems():
                reply += "顾客" + k + "，昵称是" + v + '\n'
                count += 1
            reply += "共有" + str(count) + "位顾客订阅了订餐提醒!\n"
            self.replyMessage(user, reply)
        else:
            self.usage(user)

    #The usage of the CLI
    def usage(self, user):
        usage = "当前时间是 " + time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + "\n"
        usage += "----使用口令----" + "\n"
        usage += "订餐1份请输入: ordering 1" + "\n"
        usage += "取消订餐请输入: cancel\n"
        usage += "查询订餐共有几份请输入: query\n"
        usage += "订阅4:30订餐提醒: subscribe\n"
        usage += "取消4:30订餐提醒: unsubscribe\n"
        self.replyMessage(user, usage);

    def loadSubscribeDict(self):
        self.subscribedict = pickle.load(open('subscribe_dict.dat', 'rb'))

    def dumpSubscribeDict(self):
        pickle.dump(self.subscribedict, open('subscribe_dict.dat', 'wb'))
    
    #execute befor GoOn by denny
    def beforeGoOn(self):
        self.loadSubscribeDict()
        
        self.t = threading.Timer(5.0, self.orderRemind)
        self.t.setDaemon(True)
        self.t.start()
        
    def orderRemind(self):
        while True:
            time.sleep(1)
            now = time.ctime()
            if now[11:19] == '14:27:00' and now[0:3] != 'Sat' and now[0:3] != 'Sun':
                for k, v in self.subscribedict.iteritems():
                    if not self.orderlist.has_key(k):
                        self.conn.send(xmpp.Message(k, '现在时间是' + now + '\n愚人节快乐!\n'+ v + ', 您还没有订餐，需要订餐吗？\n需要帮助请输入 help\n如果不需要订餐提醒请输入unsubscribe'))

    def afterGoOn(self):
        self.dumpSubscribeDict()

############################################################################################################################
if __name__ == "__main__":
    bot = OrderingBot()
    bot.setState('available', "订餐机器人Robot乐意为您效劳！\n订餐(ordering 1)\n查询(query)")
    bot.start("OrderingRobot@gmail.com", "iloverobot")

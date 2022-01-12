# -*- coding: gb18030 -*-
#
# $Id: PostInterface.py,v 1.2 2007-06-14 07:09:43 panguankong Exp $

"""
postoffice interface
"""

import BigWorld
from bwdebug import *

class PostInterface:
	def __init__( self ):
		pass
	
	def onReceiveMail( self, mail ):
		"""
		收到邮件

		功能：
    			用于处理邮件
    		@type	mail	:	POST_MAIL
		@param	mail	:	收信人
		"""
		INFO_MSG("===== onReceiveMail:", mail["des"], mail["src"], mail["msg"])
		pass
	
	def removeMail( self ):
		"""
		删除邮件

		功能：
			从邮件系统删除指定邮件
		"""
		self.postofficeBase.remove( self.playerName )
	
	def sendMail( self, des, existTime, msg, money, item ):
		"""
		发送邮件
		功能：
    			向邮件系统发送邮件
    		@type	des	:	string
		@param	des	:	收信人
		@type	existTime:	int32
		@param	existTime:	有效时间
		@type	msg:		string
		@param	msg:		信息
		@type	money:		int32
		@param	money:		金钱
		@type	item:		string
		@param	item:		物品
		"""
		self.postofficeBase.send( self.playerName, des, existTime, msg, money, item )
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/03/26 07:06:45  panguankong
# 添加文件
#
# 
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
		�յ��ʼ�

		���ܣ�
    			���ڴ����ʼ�
    		@type	mail	:	POST_MAIL
		@param	mail	:	������
		"""
		INFO_MSG("===== onReceiveMail:", mail["des"], mail["src"], mail["msg"])
		pass
	
	def removeMail( self ):
		"""
		ɾ���ʼ�

		���ܣ�
			���ʼ�ϵͳɾ��ָ���ʼ�
		"""
		self.postofficeBase.remove( self.playerName )
	
	def sendMail( self, des, existTime, msg, money, item ):
		"""
		�����ʼ�
		���ܣ�
    			���ʼ�ϵͳ�����ʼ�
    		@type	des	:	string
		@param	des	:	������
		@type	existTime:	int32
		@param	existTime:	��Чʱ��
		@type	msg:		string
		@param	msg:		��Ϣ
		@type	money:		int32
		@param	money:		��Ǯ
		@type	item:		string
		@param	item:		��Ʒ
		"""
		self.postofficeBase.send( self.playerName, des, existTime, msg, money, item )
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/03/26 07:06:45  panguankong
# ����ļ�
#
# 
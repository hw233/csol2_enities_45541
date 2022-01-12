# -*- coding: gb18030 -*-
#
# $Id: SpaceMultiLine.py,v 1.43 2008-08-09 06:02:41 kebiao Exp $

"""
"""

import BigWorld

import Language
from bwdebug import *
import time
import Love3
import Const
from SpaceNormal import SpaceNormal
from ObjectScripts.GameObjectFactory import GameObjectFactory

g_objFactory = GameObjectFactory.instance()

class SpaceMultiLine( SpaceNormal ):
	"""
	���߳�����
	@ivar domainMB:			һ�����������ԣ���¼����������ռ�mailbox������ĳЩ��Ҫ֪ͨ������ռ�Ĳ������˽ӿ����ΪNone���ʾ��ǰ����ʹ��
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceNormal.__init__( self )
		self.lineNumber	= self.params[ "lineNumber" ]	# �ռ���ߺ���

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceNormal.onEnter( self, baseMailbox, params )
		self.domainMB.incPlayerAmount( self.lineNumber )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		����뿪�ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onLeaveʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceNormal.onLeave( self, baseMailbox, params )
		self.domainMB.decPlayerAmount( self.lineNumber )
	
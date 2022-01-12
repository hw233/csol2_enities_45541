# -*- coding: gb18030 -*-

"""
��ģ��ֻ��cellApp��baseApp��ʹ�ã�client����Ҫ��ģ�顣
"""
# $Id: TimeSave.py,v 1.4 2008-04-30 01:38:06 kebiao Exp $

import BigWorld
import time
import csconst
from bwdebug import *

class TimeSave:
	"""
	���˼�룺
	          |-> ���߲�����
	cooldown <              |-> ������Ȼ��ʱ
	          |-> ���߱��� <
	                        |-> ������ͣ��ʱ
	��cell���ݵ�TimeSave�����е�cooldown��ʹ��int(BigWorld.time() * C_SERVER_TIME_AMEND)������
	�ڴ��䵽BaseAppʱ������һ��TimeSaveģ�鴦��cooldown�ı��棬�������ǾͿ��Ա�ֻ֤ʹ��һ��ʱ��������client������������client�����ĸ����ԡ�
	calculateTime()�����Ǹ��ݸ������ӳټ���cooldown��ʱ�䲢���ء�
	isTimeout()���жϵ�ǰ��cooldown�Ƿ��ѹ�ȥ��
	"""
	def __init__( self, section = None ):
		if section is None:
			self._id = 0						# INT16, Ҳ���Ա�ʾcooldown������
			self._isSave = True					# �����Ƿ񱣴�
			self._alwayCalc = False				# ������߱��棬��ô���ߺ��Ƿ񻹼�������ʱ�䣿
		else:
			self.initFromSection( section )

	def init( self, id, isSave, alwayCalc = False ):
		"""
		@param id: INT16
		@type id: INT16
		@type isSave: BOOL
		@type alwayCalc: BOOL
		"""
		self._id = id						# INT16, Ҳ���Ա�ʾcooldown������
		self._isSave = isSave				# �����Ƿ񱣴�
		self._alwayCalc = alwayCalc			# ������߱��棬��ô���ߺ��Ƿ񻹼�������ʱ�䣿

	def initFromSection( self, section ):
		self._id = section.readInt( "id" )
		self._isSave = bool( section.readInt( "isSave" ) )
		if self._isSave:
			self._alwayCalc = bool( section.readInt( "offlineAvailable" ) )
		else:
			self._alwayCalc = False

	def getID( self ):
		return self._id

	def isSave( self ):
		return self._isSave

	def isTimeout( self, cooldownTime ):
		"""
		�ж��Ƿ�ʱ���ѹ�

		@return: BOOL
		"""
		return time.time() >= ( cooldownTime - 0.1 )

	def calculateTime( self, timeVal ):
		"""
		�Ե�ǰʱ������ӳ�ֵ

		@param timeVal: �ӳ�ֵ
		@type  timeVal: FLOAT
		@return: �������µ�cooldownʱ��
		@rtype:  INT32
		"""
		return time.time() + timeVal

#end of class: CooldownType


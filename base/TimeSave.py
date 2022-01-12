# -*- coding: gb18030 -*-

"""
��ģ��ֻ��baseApp��ʹ�á�
"""
# $Id: TimeSave.py,v 1.5 2008-06-10 03:42:44 phw Exp $

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
	��BaseApp�����߲������һ�ɵ����������߱������ʹ����ʵʱ������¼��
	�ڱ����ʱ����baseApp����calculateOnSave()����ת����ǰ��¼�µ�ʱ�䣬
	����ȡ��ʱ����baseApp����calculateOnLoad()����ת������������ʱ�䣻
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

	def isAlwayCalc( self ):
		return self._alwayCalc

	def isTimeout( self, cooldownTime ):
		"""
		�ж��Ƿ�ʱ���ѹ�

		@param cooldownTime: time.time()
		@type  cooldownTime: INT32
		@return: BOOL
		"""
		return int( time.time() ) >= cooldownTime

	def calculateOnLoad( self, coolDown ):
		"""
		�ڼ����������ݵ�ʱ��ָ�coolDown��
		1�������coolDown�����ߺ��ʱ������Ҫ���¼���coolDown�ĵ�ǰʣ��ʱ�䣨lastTime����
		2�������coolDown�����ߺ󲻼�ʱ������Ҫ���¼���coolDown�Ľ���ʱ�䣨endTime����

		@type  coolDown: �Զ���coolDown�������ͣ��μ�defs/alias.xml
		@rtype coolDown: �Զ���coolDown�������ͣ��μ�defs/alias.xml
		"""
		endTime = coolDown[2]
		if self.isTimeout( endTime ): return coolDown
		newCoolDown = list( coolDown )
		lastTime = coolDown[0]

		if self._alwayCalc:
			newLastTime = int( endTime - time.time() )
			newCoolDown[0] = newLastTime
		else:
			newEndTime = int( time.time() + lastTime )
			newCoolDown[2] = newEndTime

		return newCoolDown

	def calculateOnSave( self, coolDown ):
		"""
		�ڱ����������ݵ�ʱ�򱣴�coolDown��
		����ֻ��Ҫ�����coolDown�ĵ�ǰʣ��ʱ��(lastTime)��

		@type  coolDown: �Զ���coolDown�������ͣ��μ�defs/alias.xml
		@rtype coolDown: �Զ���coolDown�������ͣ��μ�defs/alias.xml
		"""
		endTime = coolDown[2]
		if self.isTimeout( endTime ): return coolDown
		newCoolDown = list( coolDown )

		newLastTime = int( endTime - time.time() )
		newCoolDown[0] = newLastTime
		return newCoolDown

#end of class: CooldownType


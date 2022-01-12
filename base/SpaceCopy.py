# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.2 2008-04-30 01:42:15 kebiao Exp $

"""
��׼������Ҳ������Ϊ��������
"""

import BigWorld

import Language
from bwdebug import *
from MsgLogger import g_logger
import time
import Love3
import Const
import csstatus
from SpaceNormal import SpaceNormal
import csdefine

SPACE_LEAVE_MEMORY_TIMER	= 2001	# spaceû�����ʱ�رտռ�TIMERID


class SpaceCopy( SpaceNormal ):
	"""
	��׼������
	@ivar domainMB:			һ�����������ԣ���¼����������ռ�mailbox������ĳЩ��Ҫ֪ͨ������ռ�Ĳ������˽ӿ����ΪNone���ʾ��ǰ����ʹ��
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceNormal.__init__( self )
		self._noPlayerTimerID = 0					# �ռ�û�����ʱ�ر�timer

		try:
			g_logger.countCopyOpenLog( self.getScript().getClassName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

		# entity ����ʱ���ֵ�������ͣ���˲����壬���ⱻ����
		#self.waitingCycle = 0						# �ռ���û�����ʱ��رյ�ʱ��
		#self.maxPlayer = 0							# �ռ���������������� 0 Ϊ������
		self.monsterCountCheckNumber = 100

	def onTimer( self, id, userArg ):
		"""
		"""
		# �ռ�رմ���
		if userArg == SPACE_LEAVE_MEMORY_TIMER:
			self.delTimer( id )
			self._noPlayerTimerID = 0
			self.closeSpace()
			return

		SpaceNormal.onTimer( self, id, userArg )

	def stopCloseCountDownTimer( self ):
		"""
		�������뿪ʱ �������ټ�ʱ��timerID
		"""
		if self._noPlayerTimerID:
			self.delTimer( self._noPlayerTimerID )
			self._noPlayerTimerID = 0

	def startCloseCountDownTimer( self, time ):
		"""
		�����ռ����ټ�ʱ
		"""
		if not self._noPlayerTimerID:
			self._noPlayerTimerID = self.addTimer( time, 0, SPACE_LEAVE_MEMORY_TIMER )

	def entityCreateCell( self, playerBase ):
		"""
		define method.
		������ڸÿռ䴴��cell
		@param playerBase	:	���Base
		@type playerBase	:	mailbox
		"""
		playerBase.createCellFromSpace( self.cell )

	def requestCellComponent( self, mailbox ):
		"""
		define method.
		����cell mailbox
		@param mailbox:	ʵ��mailbox: �ռ䴴����ɺ�֪ͨ��ʵ��mailbox ���Mailbox�ϱ�����onRequestCell����
		@type mailbox:	mailbox
		"""
		mailbox.onRequestCell( self.cell, self )

	def eventHandle( self, eventID, params ):
		"""
		�������е��¼�
		"""
		pass

	def nofityTeamDestroy( self, teamEntityID ):
		"""
		define method
		֪ͨ����ĳ�����ɢ
		"""
		self.getScript().nofityTeamDestroy( self, teamEntityID )
		self.cell.nofityTeamDestroy( teamEntityID )
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/10/03 07:35:20  phw
# no message
#
#
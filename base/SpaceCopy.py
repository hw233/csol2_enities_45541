# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.2 2008-04-30 01:42:15 kebiao Exp $

"""
标准场景，也可以作为场景基类
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

SPACE_LEAVE_MEMORY_TIMER	= 2001	# space没有玩家时关闭空间TIMERID


class SpaceCopy( SpaceNormal ):
	"""
	标准场景。
	@ivar domainMB:			一个声明的属性，记录了它的领域空间mailbox，用于某些需要通知其领域空间的操作，此接口如果为None则表示当前不可使用
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceNormal.__init__( self )
		self._noPlayerTimerID = 0					# 空间没有玩家时关闭timer

		try:
			g_logger.countCopyOpenLog( self.getScript().getClassName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

		# entity 创建时由字典参数传送，因此不定义，以免被覆盖
		#self.waitingCycle = 0						# 空间里没有玩家时离关闭的时间
		#self.maxPlayer = 0							# 空间最多允许进入的人数 0 为无限制
		self.monsterCountCheckNumber = 100

	def onTimer( self, id, userArg ):
		"""
		"""
		# 空间关闭处理
		if userArg == SPACE_LEAVE_MEMORY_TIMER:
			self.delTimer( id )
			self._noPlayerTimerID = 0
			self.closeSpace()
			return

		SpaceNormal.onTimer( self, id, userArg )

	def stopCloseCountDownTimer( self ):
		"""
		获得玩家离开时 进行销毁记时的timerID
		"""
		if self._noPlayerTimerID:
			self.delTimer( self._noPlayerTimerID )
			self._noPlayerTimerID = 0

	def startCloseCountDownTimer( self, time ):
		"""
		启动空间销毁记时
		"""
		if not self._noPlayerTimerID:
			self._noPlayerTimerID = self.addTimer( time, 0, SPACE_LEAVE_MEMORY_TIMER )

	def entityCreateCell( self, playerBase ):
		"""
		define method.
		让玩家在该空间创建cell
		@param playerBase	:	玩家Base
		@type playerBase	:	mailbox
		"""
		playerBase.createCellFromSpace( self.cell )

	def requestCellComponent( self, mailbox ):
		"""
		define method.
		请求cell mailbox
		@param mailbox:	实体mailbox: 空间创建完成后通知的实体mailbox 这个Mailbox上必需有onRequestCell方法
		@type mailbox:	mailbox
		"""
		mailbox.onRequestCell( self.cell, self )

	def eventHandle( self, eventID, params ):
		"""
		处理副本中的事件
		"""
		pass

	def nofityTeamDestroy( self, teamEntityID ):
		"""
		define method
		通知副本某队伍解散
		"""
		self.getScript().nofityTeamDestroy( self, teamEntityID )
		self.cell.nofityTeamDestroy( teamEntityID )
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/10/03 07:35:20  phw
# no message
#
#
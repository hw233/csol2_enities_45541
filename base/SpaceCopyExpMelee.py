# -*- coding: gb18030 -*-
#

from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
import Love3
import BigWorld
from bwdebug import *


class SpaceCopyExpMelee( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		BigWorld.globalData["ExpMeleeMgr"].onRegisterSpace( self )

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method.
		destroy space的唯一入口，所有的space删除都应该走此接口；
		space生命周期结束，删除space
		"""
		BigWorld.globalData["ExpMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.closeSpace( self, deleteFromDB )

	def onLoseCell( self ):
		"""
		CELL死亡
		"""
		BigWorld.globalData["ExpMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.onLoseCell( self )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间，需要根据副本boss的击杀情况给予玩家
		相应的提示，并让玩家选择是继续副本还是离开副本。
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

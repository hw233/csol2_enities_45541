# -*- coding: gb18030 -*-

from NPC import NPC
import BigWorld
import event.EventCenter as ECenter
from bwdebug import *

class TiShouNPC( NPC ):
	"""
	替售NPC
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )


	def removeTSItem( self, uid ):
		"""
		define method
		"""
		print uid


	def testAddItem( self ):
		"""
		"""
		for i in xrange(255, 350):
			item = BigWorld.player().getItem_(i)
			if item:
				uid = BigWorld.player().getItem_(i).uid
				self.cell.addTSItem( uid, 100 )


	def receiveTSInfo( self, shopName, ownerDBID, destroyTime ):
		"""
		define method
		接受替售信息
		"""
		if BigWorld.player().databaseID == ownerDBID : 							# 打开自己的替售窗口
			ECenter.fireEvent( "EVT_ON_TOGGLE_COMMISSION_SALE_WND", self, destroyTime )
		else :																# 查看别人的替售物品
			ECenter.fireEvent( "EVT_ON_TRIGGER_TISHOU_BUY_WINDOW", shopName, BigWorld.player().playerName, self )


	def onStartTS( self ):
		"""
		define method
		开始寄售
		"""
		INFO_MSG( "begin sell" )

	def onStopTS( self ):
		"""
		define method
		结束寄售
		"""
		INFO_MSG( "end sell" )

	def set_tsState( self, old ):
		"""
		寄售状态改变
		"""
		if BigWorld.player().databaseID == self.ownerDBID :
			ECenter.fireEvent( "EVT_ON_TSNPC_FLAGS_CHANGED", old )


# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 20.0						#玩家全部离开副本后，隔多久副本才删除

GOD_WEAPON_QUEST_FJSG			= 40202004		# 神器任务ID

class SpaceCopyFJSG( SpaceCopy ):
	# 封剑神宫
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.addTimer( 3600, 0, 3600 )		# 3600s后，副本自动关闭


	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]
	
	def onGodWeaponFJSG( self ):
		"""
		define method
		完成神器任务
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_FJSG, 1 )
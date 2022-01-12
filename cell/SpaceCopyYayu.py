# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const


DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#玩家全部离开副本后，隔多久副本才删除

GOD_WEAPON_QUEST_YAYU		 = 40202002	# 神器任务猰貐ID

class SpaceCopyYayu( SpaceCopy ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
	
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.copyDataInit( baseMailbox, params )
			self.setTemp( "firstEnter", True )
		baseMailbox.client.onOpenSpaceTowerInterface()
		SpaceCopy.onEnterCommon( self, baseMailbox, params )


	def copyDataInit( self, baseMailbox, params ):
		"""
		副本数据方面的初始化
		"""
		BigWorld.globalData['Yayu_%i' % params['teamID'] ] = True
		self.setTemp('globalkey','Yayu_%i' % params['teamID'])
		
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "" )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, 0 )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )


	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
			8: 猰貐血量百分比
		]
		"""
		# 显示剩余小怪，剩余BOSS。 
		return [ 1, 3, 7, 8, 14 ]
	
	def onYayuDie( self ):
		"""
		define method
		"""
		self.getScript().onYayuDie( self )


	def onYayuHPChange( self, hp, hp_Max ):
		"""
		define method
		"""
		self.getScript().onYayuHPChange( self, hp, hp_Max )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		baseMailbox.client.onCloseSpaceTowerInterface()
		baseMailbox.cell.onLeaveYaYuCopy()
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]


	def onTimer( self, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		SpaceCopy.onTimer( self, id, userArg )


	def onGodWeaponYayuFin( self ):
		"""
		define method
		完成神器任务，猰貐HP剩余90%以上
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_YAYU, 1 )


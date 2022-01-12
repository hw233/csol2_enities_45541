# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#玩家全部离开副本后，隔多久副本才删除
#GOD_WEAPON_QUEST_KR = 40202006		# 神器任务
GOD_WEAPON_QUEST_KR = 40202001			# 神器任务
GOD_WEAPON_QUEST_KR_2 = 50201010		# 神器任务
CLASS_NAME_BOSS_3 = "20114007"			# 后卿
GW_HP_CHANGE_RATE = 0.85	# 任务要求：成功击杀后卿后，神树的血量依然保持在85%以上。

class SpaceCopyKuaFuRemains( SpaceCopy ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.setTemp( "godWoodHPTooLow", False )
	
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )

	def onMonsterDie( self, params ):
		"""
		define method
		当一般怪物死亡
		"""
		self.getScript().onMonsterDie( self, params )
		# 后卿死后，神树的血量依然保持在85%以上，处理特殊任务条件
		if params["className"] == CLASS_NAME_BOSS_3:
			if self.queryTemp( "godWoodHPTooLow" ) is False:
				self.onGodWeaponKR_2()
		
	def onGodWoodHPChange( self, hp, hp_max ):
		"""
		define method
		当神木 HP 低于一定值
		"""
		if hp*1.0/hp_max < GW_HP_CHANGE_RATE:
			self.setTemp( "godWoodHPTooLow", True )

	def shownDetails( self ):
		"""
		"""
		# 显示神树血量
		return [ csconst.SPACE_SPACEDATA_TREE_HP_PRECENT, ]

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			del BigWorld.globalData[self.queryTemp('globalkey')]
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )

	def onGodWeaponKR( self ):
		"""
		完成神器任务
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_KR, 1 )
			
	def onGodWeaponKR_2( self ):
		"""
		完成神器任务2		杀死某boss为止无人死亡
		"""
		if self.queryTemp( "roleDieNum", 0 ) > 0:
			return
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_KR_2, 1 )
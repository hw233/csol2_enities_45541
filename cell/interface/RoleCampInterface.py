# -*- coding: gb18030 -*-

import datetime
import BigWorld
import csdefine
import csconst

class RoleCampInterface:
	def __init__( self ):
		pass
	
	def camp_beKilled( self, killer ):
		"""
		被阵营击杀
		"""
		if killer.getEntityType() == csdefine.ENTITY_TYPE_ROLE and killer.getCamp() != self.getCamp():
			self.camp_refreshBeKill()
			killer.camp_killReward( self, self.level, self.camp_bekill )
			self.camp_bekill += 1
		
	def camp_refreshBeKill( self ):
		if self.camp_refreshTime != str( datetime.date.today() ):
			self.camp_bekill = 0
			self.camp_refreshTime = str( datetime.date.today() )
	
	def camp_addHonour( self, honour ):
		"""
		define method.
		添加阵营荣誉
		"""
		val = honour + honour * self.camp_honourMult # 荣誉多倍奖励
		self.camp_honour += val
	
	def camp_decHonour( self, honour ):
		"""
		define method.
		添加阵营荣誉
		"""
		self.camp_honour -= honour
	
	def camp_getHonour( self ):
		"""
		获取阵营荣誉
		"""
		return self.camp_honour
	
	def camp_getKillReward( self, beKLevel, killNum ):
		"""
		击杀奖励= max(1, 基准奖励 * 等级修正系数 * 多次击杀修正系数 ) 
        等级修正系数= min( 5, 0.5^(( 击杀方等级 - 被击杀方等级 )/10) ) 
		"""
		levelBaseCoe = min( 5, pow( 0.5, ( ( self.level - beKLevel ) / 10 ) ), )
		numKillCoe = pow( 0.5, ( killNum / 5 ) )
		return 	max( 1, int( csconst.CAMP_KILL_REWARD_HONOUR_BASE * levelBaseCoe * numKillCoe ) )
	
	def camp_killReward( self, beKillMB, beKLevel, beKNum ):
		"""
		define method
		阵营击杀奖励
		"""
		rewardHonour = self.camp_getKillReward( beKLevel, beKNum )
		self.camp_addHonour( rewardHonour )
		
	def camp_addMorale( self, camp, amount ):
		"""
		添加阵营积分，Morale：可为负数
		"""
		BigWorld.globalData[ "CampMgr" ].addMorale( camp, amount )
		self.questCampMoraleChange( camp, amount )
		
	def camp_systemCastSpell( self, camp, skillID ):
		"""
		define method
		某阵营玩家使用一个系统技能，用于添加阵营buff
		"""
		if self.getCamp() == camp:
			self.systemCastSpell( skillID )
			
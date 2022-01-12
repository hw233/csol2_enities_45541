# -*- coding: gb18030 -*-

from Monster import Monster
import csdefine
import time
from Domain_Fight import g_fightMgr
import BigWorld


class MonsterYayu( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.think( 3.0 )
		self.setTemp( "bornTime", time.time() )

	def onAddYayuToEnemy( self, timerID, cbID ) :
		"""
		把猰貐加入为敌人
		"""
		yayuEntity = BigWorld.entities.get( self.queryTemp( "enemyYayuID" ) )		#防止猰貐死亡后onTimer到这里会出错。
		if yayuEntity:
			g_fightMgr.buildEnemyRelation( self, yayuEntity )
		


	def canThink( self ):
		"""
		virtual method.
		判定是否可以think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 		# 死亡了停止think
			return False
		if self.subState == csdefine.M_SUB_STATE_GOBACK: 						# 如果目前没有玩家看见我或正在回走，那么我将停止think
			return False
		return True

	def onKuangbao( self, timerID, cbID ) :
		"""
		BOSS 变得狂暴
		"""
		self.magic_damage_percent += 100
		self.calcMagicDamage()
		self.damage_max_base += self.damage_max_base
		self.calcDamageMax()
		self.damage_min_base += self.damage_min_base
		self.calcDamageMin()
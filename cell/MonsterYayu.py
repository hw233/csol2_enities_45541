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
		�Ѫm؅����Ϊ����
		"""
		yayuEntity = BigWorld.entities.get( self.queryTemp( "enemyYayuID" ) )		#��ֹ�m؅������onTimer����������
		if yayuEntity:
			g_fightMgr.buildEnemyRelation( self, yayuEntity )
		


	def canThink( self ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 		# ������ֹͣthink
			return False
		if self.subState == csdefine.M_SUB_STATE_GOBACK: 						# ���Ŀǰû����ҿ����һ����ڻ��ߣ���ô�ҽ�ֹͣthink
			return False
		return True

	def onKuangbao( self, timerID, cbID ) :
		"""
		BOSS ��ÿ�
		"""
		self.magic_damage_percent += 100
		self.calcMagicDamage()
		self.damage_max_base += self.damage_max_base
		self.calcDamageMax()
		self.damage_min_base += self.damage_min_base
		self.calcDamageMin()
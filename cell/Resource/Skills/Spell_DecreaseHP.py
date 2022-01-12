# -*- coding: gb18030 -*-
from SpellBase import *
import csstatus
import csdefine

class Spell_DecreaseHP( CombatSpell ):
	# 减少周围指定类型entity的血量（百分比）
	def __init__( self ):
		"""
		构造函数。
		"""
		CombatSpell.__init__( self )
		self.entityNames = []
		self.percentage = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self.entityNames = dict[ "param1" ].split( ";" )
		self.percentage = int( dict[ "param2" ] )
	
	def getReceivers( self, caster, target ):
		receivers = CombatSpell.getReceivers( self, caster, target )
		for i, entity in enumerate( receivers ):
			if entity.__module__ not in self.entityNames:
				receivers.pop( i )
		
		return receivers
	
	def receive( self, caster, receiver ):
		# 法术到达所要做的事情
		if receiver.isDestroyed:
			return
			
		finiDamage = int( receiver.HP_Max * self.percentage / 100 )
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
			
		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )
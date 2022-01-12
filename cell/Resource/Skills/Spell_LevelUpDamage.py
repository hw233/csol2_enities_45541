# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csdefine
import math
from SpellBase import *
from VehicleHelper import getCurrVehicleID

class Spell_LevelUpDamage( CombatSpell ):
	"""
	升级触发范围伤害技能专用脚本
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_VOID	# 伤害类型暂定为无类型
		self._damage = 0								# 技能伤害

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self._damage = int( dict["param1"] ) if len( dict["param1"] ) > 0 else 0

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用
		return type:int
		"""
		if getCurrVehicleID( caster ):	# 骑乘状态下无法触发
			return csstatus.SKILL_NO_MSG

		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return
		
		finiDamage = self._damage
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
			
		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )
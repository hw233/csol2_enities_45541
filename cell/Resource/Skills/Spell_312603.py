# -*- coding: gb18030 -*-
#
# $Id: Spell_Dispersion.py,v 1.26 2008-08-14 01:11:36 kebiao Exp $

"""
驱散法术。
"""

from SpellBase import *
from Resource import DispersionTable
import csdefine
import csstatus

class Spell_312603( Spell ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF
		
	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		
		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# 最多可驱散个数 DispelAmount
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
				
	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		接受法术之前所要做的事情
		"""
		# 磨损
		#caster.equipAbrasion()
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#处理沉默等一类技能的施法判断
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )
		
	def canDispel( self, caster, receiver, buffData ):
		"""
		可否驱散
		"""
		skill = buffData["skill"]
		if skill.getLevel() <= self.getCastTargetLevelMax():
			if skill.cancelBuff( self._triggerBuffInterruptCode ):
				return True		
		return False
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 驱散目标身上的buff
		rmb = []
		count = 0
		for index, buff in enumerate( receiver.getBuffs() ):
			if self.canDispel( caster, receiver, buff ):
				rmb.append( index )
				count += 1
				if count >= self._dispelAmount:
					break

		# 反向
		rmb.reverse()
		for index in rmb:
			receiver.removeBuff( index, self._triggerBuffInterruptCode )
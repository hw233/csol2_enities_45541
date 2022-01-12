# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemDispersion.py,v 1.26 8:56 2010-7-15 jinagyi Exp $

"""
物品技能 驱散法术。
"""

from Spell_Item import Spell_Item
from Resource import DispersionTable
import csdefine
import csstatus


class Spell_ItemDispersion( Spell_Item ):
	"""
		战士有冰封驱散。 :1
		法师有眩晕驱散。 :2
		剑客有减速驱散。 :3
		射手有昏睡驱散。 :4			
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF
		
	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		
		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# 最多可驱散个数 DispelAmount
		"""
		驱散类型
		战士有冰封驱散。 :EFFECT_STATE_VERTIGO
		法师有眩晕驱散。 :EFFECT_STATE_VERTIGO
		剑客有减速驱散。 :EFFECT_STATE_VERTIGO
		射手有昏睡驱散。 :EFFECT_STATE_VERTIGO		
		"""
		type = dict.get( "param2" , "" )
		if len( type ) > 0:
			self._effectType = eval( "csdefine." + type )				
		else:
			self._effectType = -1
			
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
			
		if self._effectType != csdefine.EFFECT_STATE_VERTIGO and caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if self._effectType != csdefine.EFFECT_STATE_SLEEP and caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if self._effectType != csdefine.EFFECT_STATE_HUSH_MAGIC and caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell_Item.useableCheck( self, caster, target )
		
	def canDispel( self, caster, receiver, buffData ):
		"""
		可否驱散
		"""
		skill = buffData["skill"]
		if skill.getLevel() < self.getLevel():# 只能驱散比自己级别底的BUFF
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
		receiver.clearBuff( self._triggerBuffInterruptCode )
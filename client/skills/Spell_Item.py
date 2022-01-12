# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from SpellBase import *
from event.EventCenter import *
import ItemTypeEnum
import csstatus
from Function import Functor
import csdefine

class Spell_Item( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置 
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		
	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		
		# 如果可以物品释放，那么可以中断当前技能，所以此步骤不做判断（仅客户端）。
#		if caster.intonating():
#			return csstatus.SKILL_ITEM_INTONATING
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM	
			
		state = self.validCaster( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查施法者的消耗是否足够
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查技能cooldown 根据快捷栏变色的需求调整技能条件的判断顺序 这个只能放最后
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		if self.getIntonateTime() > 0.1 and caster.isJumping(): # 跳跃中提示“吟唱被打断”，csol-899
			return csstatus.SKILL_IN_ATTACK
		return csstatus.SKILL_GO_ON	
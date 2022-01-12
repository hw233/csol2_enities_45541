# -*- coding: gb18030 -*-
#
# 2009-02-03 宋佩芳
#

from Spell_BuffNormal import Spell_BuffNormal
from SpellBase import *
import csstatus
import csconst
import time
import csdefine
import ECBExtend

class Spell_122159001( Spell_BuffNormal ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )

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
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 必须是玩家类型或者宠物类型或者镖车（保镖）类型的实体才有触发
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) ):
			return

		currSunBathAreaCount = receiver.queryTemp( "sun_bath_area_count", 0 ) + 1
		receiver.setTemp( "sun_bath_area_count", currSunBathAreaCount )
		if currSunBathAreaCount <= 1:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				receiver.statusMessage( csstatus.ROLE_ENTER_SUN_BATH_MAP )
			self.receiveLinkBuff( receiver, receiver )

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.actCounterInc( csdefine.ACTION_FORBID_PK )	# 禁止玩家PK的标记
			date = time.localtime()[2]
			if receiver.sunBathDailyRecord.date != date:
				receiver.sunBathDailyRecord.date = date
				receiver.sunBathDailyRecord.sunBathCount = 0
				receiver.sunBathDailyRecord.prayCount = 0
			receiver.setTemp( "ADD_SUN_BATH_COUNT_TIMER_ID", receiver.addTimer( 1, 10, ECBExtend.ADD_SUN_BATH_COUNT ) )
			# 日光浴经验的公式是 玩家级别 + 23
			increaseEXP = receiver.level + 23
			receiver.setTemp( "clean_sun_bath_exp", increaseEXP )
			actPet = receiver.pcg_getActPet()
			if actPet :														# 如果玩家携带有出征宠物
				actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )		# 则收回之

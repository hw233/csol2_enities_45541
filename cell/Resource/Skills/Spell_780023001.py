# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_BuffNormal import Spell_Buff

class Spell_780023001( Spell_Buff ):
	"""
	进入舞厅，施放技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Buff.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Buff.init( self, dict )

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
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) ):
			return

		receiver.actCounterInc( csdefine.ACTION_FORBID_PK )						# 进入舞厅，禁止玩家PK的标记
		actPet = receiver.pcg_getActPet()
		if actPet :																# 如果玩家携带有出征宠物
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )				# 则收回之
		receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )			# 收回坐骑
		receiver.actCounterInc( csdefine.ACTION_ALLOW_DANCE )					# 允许跳舞

		# 刷新角色一天跳舞积分
		if not receiver.dancePointDailyRecord.checklastTime():					# 判断是否同一天
			receiver.dancePointDailyRecord.reset()

		self.receiveLinkBuff( receiver, receiver )

		receiver.statusMessage( csstatus.JING_WU_SHI_KE_ENTER )

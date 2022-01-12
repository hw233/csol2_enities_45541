# -*- coding: gb18030 -*-
#
#

import csdefine
import csstatus
from SpellBase import Spell
import Const

class Spell_122159020( Spell ):
	"""
	离开舞厅施放技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
	
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
		技能实现的目的
		"""
		# 必须是玩家类型或者宠物类型或者镖车（保镖）类型的实体才有触发
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) ):
			return
		
		receiver.actCounterDec( csdefine.ACTION_FORBID_PK )		# 允许玩家PK的标记
		#receiver.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
		
		receiver.statusMessage( csstatus.JING_WU_SHI_KE_LEAVE )

# -*- coding: gb18030 -*-
#
# $Id: Spell_TeamDancing.py,v 1.28 2009.11.04 10:02:41 pengju Exp $

"""
队伍共舞
2009.11.04: by pengju
"""

import random
import BigWorld
import csdefine
import csstatus
from SpellBase import *
from bwdebug import *

class Spell_TeamDancing( Spell ):
	def __init__( self ):
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_ACTION

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
		if caster.isTeamFollowing():
			return csstatus.JING_WU_SHI_KE_DANCE_NO_FOLLOWING
		
		state = caster.getState()
		# 只有处于单人舞、双人舞或者自由状态才能施放技能
		if state == csdefine.ENTITY_STATE_DANCE and caster.dancePartnerID == 0 or \
			state == csdefine.ENTITY_STATE_DOUBLE_DANCE or \
			state == csdefine.ENTITY_STATE_FREE :
			return Spell.useableCheck( self, caster, target )
		return csstatus.JING_WU_SHI_KE_NOT_FREE

	def receive( self, caster, receiver ) :
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		caster.teamDance()

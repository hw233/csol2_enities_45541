# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.28 2008-08-13 07:55:41 kebiao Exp $

"""
单人舞
2009.07.16: by huangyongwei
"""

import random
import BigWorld
import csdefine
import csstatus
from SpellBase import *
from bwdebug import *

class Spell_DblDancing( Spell ):
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
		state = caster.getState()
		if state == csdefine.ENTITY_STATE_DANCE and \
			caster.dancePartnerID == 0 :								# 单人舞状态
				return Spell.useableCheck( self, caster, target )
		elif state == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			return csstatus.JING_WU_SHI_KE_IN_DANCE
		elif state == csdefine.ENTITY_STATE_FREE :						# 自由状态
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
		caster.sendRequestDance( receiver )

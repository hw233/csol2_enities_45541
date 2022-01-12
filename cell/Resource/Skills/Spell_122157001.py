# -*- coding: gb18030 -*-
#
# $Id: Spell_121014.py,v 1.5 2008-07-15 04:06:26 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_BuffNormal import Spell_Buff
import utils
import csstatus
import csdefine
import BigWorld

class Spell_122157001( Spell_Buff ):
	"""
	破釜沉舟	四项属性提高10%.

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
		return Spell_Buff.useableCheck( self, caster, target )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		p1 = receiver
		if p1.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = p1.getOwner()
			if owner.etype == "MAILBOX" : return
			pl = owner.entity
		if not p1.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]:		# 只有城市战争防守才可以获得该BUFF
			return
		Spell_Buff.receiveLinkBuff( self, caster, receiver )					# 施放者获得该buff。

# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 05:43:42  kebiao
# no message
#
#
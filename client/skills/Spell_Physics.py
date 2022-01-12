# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.5 2008-07-15 04:08:27 kebiao Exp $

"""
普通物理技能
"""
import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
from bwdebug import *
from skills.SpellBase import *
from Time import Time

class Spell_Physics( Spell ):
	"""
	普通物理技能
	"""
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

	def getType( self ):
		"""
		获得技能类型。
		"""
		return csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL

	def getRangeMax( self, caster ):
		"""
		获得射程。
		"""
		return caster.range	# 普通物理攻击通过role的攻击距离来判断长度

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if Time.time() < caster.hitDelay + 0.05:					# if current interval less than interval of player in hit
			return csstatus.SKILL_NOT_HIT_TIME							# set this the sign
		return Spell.useableCheck( self, caster, target )
	
	def getIcon( self ):
		pl = BigWorld.player()
		try:
			if pl.primaryHandEmpty():
				return Spell.getIcon( self )
			else:
				item = pl.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
				return item.icon()
		except AttributeError, errstr:
			WARNING_MSG( errstr )
			return Spell.getIcon( self )

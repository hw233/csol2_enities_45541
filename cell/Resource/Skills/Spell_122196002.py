# -*- coding: gb18030 -*-

"""
烈焰新星
"""

from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import utils
import csstatus
import csdefine
import BigWorld

class Spell_122196002( Spell_BuffNormal ):
	"""
	烈焰新星
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

	def getReceivers( self, caster, target ) :
		"""
		virtual method
		默认只对受术目标施放。
		"""
		receivers = []
		targetEntity = target.getObject()
		if not targetEntity.isDestroyed and \
		( targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or targetEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) ):
			receivers.append( targetEntity )

		return receivers

	def _validCaster( self, caster ):
		"""
		virtual method.
		检查施法者是否满足吟唱条件
		@return: INT，see also SkillDefine.SKILL_*
		"""
		return csstatus.SKILL_GO_ON

# -*- coding: gb18030 -*-

"""
陷龙潭
"""

from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import utils
import csstatus
import csdefine
import BigWorld

class Spell_122195002( Spell_BuffNormal ):
	"""
	陷龙潭
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
		self.className = str( dict[ "param1" ] )		# 陷龙潭只对特定怪物有效

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if receiver.className != self.className:	# 陷龙潭只对特定怪物有效
			return
		
		Spell_BuffNormal.receiveLinkBuff( self, caster, receiver )					# 施放者获得该buff。
#

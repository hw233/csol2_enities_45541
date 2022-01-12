# -*- coding: gb18030 -*-
#

"""
将施法者从目标的治疗列表、伤害列表、战斗列表这三个列表中删除
"""


from SpellBase.Spell import Spell
import random
import csdefine
from Domain_Fight import g_fightMgr

class Spell_312618( Spell ):
	"""	
	将施法者从目标的治疗列表、伤害列表、战斗列表这三个列表中删除
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
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		g_fightMgr.breakEnemyRelation( receiver, caster )

		

# -*- coding: gb18030 -*-

from bwdebug import *
from SpellBase import Spell
import csconst

class Spell_Dance( Spell ):
	"""
	劲舞时刻斗舞副本中用施放的空间技能
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.danceAction = None


	def init( self, dictData ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dictData )
		self.danceAction = dictData["param1"]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell.receive( self, caster, receiver )	
		print "Spell_Dance caster is ",caster
		if caster.__class__.__name__ == "Role": #玩家放的技能，才给NPC发,如果是npc放的就什么都不做
			if caster.entitiesInRangeExt( 35, "DanceNPC", caster.position ):
				danceNPC = caster.entitiesInRangeExt( csconst.DANCEHALLAOI, "DanceNPC", caster.position )[0] 	#取得玩家给范围内的NPC，由于此副本只有一个NPC
				danceNPC.checkDanceResult(self.getID())
				
				


			
# -*- coding: gb18030 -*-

from bwdebug import *
from SpellBase import Spell
import csconst

class Spell_Dance( Spell ):
	"""
	����ʱ�̶��踱������ʩ�ŵĿռ似��
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.danceAction = None


	def init( self, dictData ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dictData )
		self.danceAction = dictData["param1"]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell.receive( self, caster, receiver )	
		print "Spell_Dance caster is ",caster
		if caster.__class__.__name__ == "Role": #��ҷŵļ��ܣ��Ÿ�NPC��,�����npc�ŵľ�ʲô������
			if caster.entitiesInRangeExt( 35, "DanceNPC", caster.position ):
				danceNPC = caster.entitiesInRangeExt( csconst.DANCEHALLAOI, "DanceNPC", caster.position )[0] 	#ȡ����Ҹ���Χ�ڵ�NPC�����ڴ˸���ֻ��һ��NPC
				danceNPC.checkDanceResult(self.getID())
				
				


			
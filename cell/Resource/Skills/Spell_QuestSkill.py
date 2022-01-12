# -*- coding: gb18030 -*-

from SpellBase import *
import csstatus

class Spell_QuestSkill( Spell ):
	def __init__( self ):
		Spell.__init__( self )
		
	def init( self, dictDat ):
		"""
		读取技能配置
		@param dictDat:	配置数据
		@type dictDat:	python dictDat
		"""
		Spell.init( self, dictDat )
		self.questIDList = [ int( questID ) for questID in dictDat["param1"].split(";") ]
		self.skillIDList = [int( skillID ) for skillID in dictDat["param2"].split(";")]
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		for index,questID in enumerate(self.questIDList):
			if receiver.has_quest( questID ):
				spellID = self.skillIDList[ index ]
				caster.spellTarget( spellID, receiver.id )
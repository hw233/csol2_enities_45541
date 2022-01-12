# -*- coding: gb18030 -*-

from Spell_QuestItem_To_NPCObject import Spell_QuestItem_To_NPCObject


class Spell_342013( Spell_QuestItem_To_NPCObject ):
	"""
	春节活动的爆竹技能。
	"""
	def __init__( self ):
		Spell_QuestItem_To_NPCObject.__init__( self )
		
	def init( self, dict ):
		"""
		"""
		Spell_QuestItem_To_NPCObject.init( self, dict )
		self._talkString = str( dict["param5"] )
		
	def receive( self, caster, receiver ):
		"""
		Virtual method.
		接收技能
		"""
		caster.setGossipText( self._talkString )
		caster.sendGossipComplete( receiver.id )
		Spell_QuestItem_To_NPCObject.receive( self, caster, receiver )
		
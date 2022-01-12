# -*- coding:gb18030 -*-

from SpellBase import Spell
from interface.AIInterface import AIInterface
from bwdebug import *

class Spell_CheckPlayerQuestStateForAI( Spell ):
	"""
	ͨ�����ܼ���������״̬����ͨ��ai����֪ͨnpc����Ӧ����
	"""
	def __init__( self ):
		Spell.__init__( self )
		self.aiCommand = 0	# �������״̬�����������͵�aiָ��
		self.questID = 0	# ����id
		self.questState = 0	# ����������״̬
		
	def init( self, data ):
		Spell.init( self, data )
		self.questID = int( data["param1"] ) if len( data["param1"] ) > 0 else 0
		self.aiCommand = int( data["param2"] ) if len( data["param2"] ) > 0 else 0
		self.questState = int( data["param3"] ) if len( data["param3"] ) > 0 else 0
		
	def receive( self, caster, receiver ):
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if not isinstance( caster, AIInterface ):
			ERROR_MSG( "caster( %s ) error,must be instance of AIInterface." % caster.getName() )
			return
		quest = receiver.getQuest( self.questID )
		if quest and quest.query( receiver ) == self.questState:
			caster.onAICommand( caster.id, caster.className, self.aiCommand )
		else:
			DEBUG_MSG( "dont need command back,quest ID:%i,aiCommand:%i,questState:%i,caster:%s" % ( self.questID, self.aiCommand, self.questState, caster.getName() ) )
			
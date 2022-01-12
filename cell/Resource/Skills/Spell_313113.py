# -*- coding:gb18030 -*-

#

from Spell_313100004 import Spell_313100004

class Spell_313113( Spell_313100004 ):
	"""
	����Ʒ������������ೡ����������Ŷ����������������,����ָ����NPC����AIָ��
	"""	
	
	def __init__( self ):
		Spell_313100004.__init__( self )
		self.range = 0.0
		self.className = ""
		self.entityType = ""
		self.commandString = 0


	def receive( self, caster, receiver ):
		"""
		"""
		Spell_313100004.receive( self, caster, receiver )
		# ������AIָ��
		self.range = float( receiver.getScript().param2 )
		self.className =receiver.getScript().param3
		self.entityType = receiver.getScript().param4
		self.commandString = int( receiver.getScript().param5 )
		
		
		monsterList = receiver.entitiesInRangeExt( self.range, self.entityType, receiver.position )
		for e in monsterList:
			if self.className == "":								# ���classNameΪ�գ�����AIָ���ָ����Χ������͵����й���
				e.sendAICommand( e.id, self.commandString )		
			else:													# ���className��Ϊ�գ�����AIָ���ָ���Ĺ���
				if e.className == self.className:
					e.sendAICommand( e.id, self.commandString )	# ��������߲��ܹ�����aiָ�˵���˼��ܵ�����������������


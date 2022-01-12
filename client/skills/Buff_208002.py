# -*- coding: gb18030 -*-


from bwdebug import *
import event.EventCenter as ECenter
from SpellBase import *
import Math
import Define

class Buff_208002( Buff ):
	"""
	�̶������ƶ�
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Buff.__init__( self )
		self.speed = 0.0
		self.direction = None
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type  dict:			python �ֵ�
		"""
		Buff.init( self, dict )
		self.speed = float( dict.get("Param1") )
		self.direction = Math.Vector3( eval( dict.get("Param2") ) )
	
		
	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.moveDirection = [ self.direction[0], self.direction[2], self.speed ]
			target.updateVelocity()
				

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id:
			target.moveDirection = []
			target.stopMoving()
			

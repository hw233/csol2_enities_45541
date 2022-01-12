# -*- coding: gb18030 -*-


from bwdebug import *
import event.EventCenter as ECenter
from SpellBase import *
import Define
import csdefine
import BigWorld

class Buff_208003( Buff ):
	"""
	������
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Buff.__init__( self )
		self.speed = 0.0
		self.isFly = False
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type  dict:			python �ֵ�
		"""
		Buff.init( self, dict )
		self.speed = float( dict.get("Param1") )
		self.time = float( dict.get("Param2") )
	
		
	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_208003 )
			target.isBlowUp = True
			physics = target.getPhysics()
			physics.fall = False
			physics.velocity = ( 0, self.speed, 0 )
			BigWorld.callback( self.time, physics.stop )
		if target.getEntityType() == csdefine.ENTITY_TYPE_MONSTER:
			target.filter = BigWorld.AvatarFilter()

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id:
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_208003 )
			target.physics.fall = True
			target.isBlowUp = False
			target.stopMove()
		if target.getEntityType() == csdefine.ENTITY_TYPE_MONSTER:
			target.filter = target.filterCreator()
			

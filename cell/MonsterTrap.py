# -*- coding: gb18030 -*-
# MonsterTrap.py
# ���Թ���������

import ECBExtend
from Monster import Monster

class MonsterTrap( Monster ):
	"""
	���Թ���������
	"""
	def __init__(self):
		Monster.__init__(self)

		if self.radius > 0.0:
			self.controlID = self.addProximityExt( self.radius, 0x01 )
		
		if self.lifetime > 0:
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def onEnterTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if self.enterSpell > 0:
			self.spellTarget( self.enterSpell, entity.id )

	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		self.spellTarget( self.leaveSpell, entity.id )

	def onLevelTrapPickRemoteDo( self, ) :
		"""
		����뿪����Զ��ִ�в���
		"""
		reList = []
		if self.leaveSpell > 0:
			reList.append( ( "systemCastSpell", [ self.leaveSpell, ] ) )
		
		return reList

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		ɾ������
		"""
		self.onDieLeaveTrap()
		self.destroy()

	def onDieLeaveTrap( self ):
		"""
		"""
		# ����ʱ����Ҫ��entity�뿪����
		entityList = []
		entityList += self.entitiesInRangeExt( self.radius + 1, "Monster", self.position )
		entityList += self.entitiesInRangeExt( self.radius + 1, "Role", self.position )
		entityList += self.entitiesInRangeExt( self.radius + 1, "Pet", self.position )
		
		if self.leaveSpell > 0:
			for entity in entityList:
				if entity.isDestroyed:
					baseMailbox = self.getGBAE()
					if baseMailbox is None :
						ERROR_MSG( "The baseMailbox should not be None, or all of that must have been breakdown!" )
						return
					baseMailbox.castSpellBroadcast( entity.id, self.leaveSpell )
				else :
					self.spellTarget( self.leaveSpell, entity.id )

	def onDie( self, killerID ):
		"""
		virtual method.

		�������鴦��
		"""
		self.onDieLeaveTrap()
		Monster.onDie( self, killerID )

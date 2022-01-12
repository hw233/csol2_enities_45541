# -*- coding: gb18030 -*-
#


import BigWorld
from bwdebug import *
import csconst
import csdefine
import csstatus
from Function import newUID
from SpellBase import *
from Skill_Normal import Skill_Normal


class Skill_611702( Skill_Normal ):
	"""
	���ﱻ������:��������,�����ܵ��������˺�,��һ���ı���������Է�
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self._param1 = 0
		self._param2 = 0
		self._param3 = 0
		self._param4 = 0
		self._param5 = 0
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		
		
		#param1 �Ƕ�Ӧ�Ը���
		#param2 ��Ӧ�Ը���
		#param3 ��Ӧ���Ը�
		#param4 �Ƕ�Ӧ�Ը�����
		#param5 ��Ӧ�Ը�����
		
		Skill_Normal.init( self, dict )
		self._param1 = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 )  / 100.0	
		self._param2 = float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0.0 )  / 100.0	
		self._param3 = float( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0.0 ) 	
		self._param4 = float (dict[ "param4" ] if len( dict[ "param4" ]) > 0 else 0.0) / 100.0
		self._param5 = float (dict[ "param5" ] if len( dict[ "param5" ]) > 0 else 0.0) / 100.0
		self.reboundPercent = self._param1
		self.reboundProb = self._param4
	
	def attach( self, ownerEntity ):
		if ownerEntity.isEntityType(csdefine.ENTITY_TYPE_PET) :
			#ownerEntity.appendVictimHit( self.getNewObj() )
			if ownerEntity.character == self._param3:
				self.reboundPercent = self._param2 # ��Ӧ�Ը������
				self.reboundProb = self._param5 # ��Ӧ�Ը�����
			
			#���������ӷ���
			self.__addEffect(ownerEntity)
			
			#�������˵ķ���Ч��
			petOwner=ownerEntity.getOwner()
			if petOwner.etype == "REAL" :
				self.__addEffect(petOwner.entity)
			else :
				petOwner.attachSkillOnReal(self)
				
		else :# owner callback
			#�������˵ķ���Ч��
			self.__addEffect(ownerEntity)
			
	
	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		if ownerEntity.isEntityType(csdefine.ENTITY_TYPE_PET) :
			#ownerEntity.removeVictimHit( self.getUID() )
			if ownerEntity.character == self._param3:
				self.reboundPercent = self._param2 #��Ӧ�Ը�ļ�ǿ�ͷ���
				self.reboundProb = self._param5 # ��Ӧ�Ը�����
			
			#ȥ������������ӦЧ��
			self.__removeEffect(ownerEntity)
	
			
			#ȥ����������������ӦЧ��
			petOwner = ownerEntity.getOwner()
			if petOwner.etype == "REAL":
				self.__removeEffect(petOwner.entity)
			else :
				petOwner.entity.detachSkillOnReal(self)
		else :# owner callback
			self.__removeEffect(ownerEntity)

	#private
	def __addEffect(self,entity):
		#���Ϸ������
		oldReboundProb = entity.queryTemp("rebound_magic_damage_probability",0.0)
		entity.setTemp( "rebound_magic_damage_probability", self.reboundProb + oldReboundProb)
			
		#���Ϸ������
		oldReboundPercent = entity.queryTemp( "rebound_magic_damage_percent", 0.0 )
		entity.setTemp( "rebound_magic_damage_percent", self.reboundPercent + oldReboundPercent )
	
	#private	
	def __removeEffect(self,entity):
		#ȥ���������
		oldReboundProb = entity.queryTemp("rebound_magic_damage_probability",0.0)
		newReboundProb = oldReboundProb - self.reboundProb
		if newReboundProb >0.0 :
			entity.setTemp("rebound_magic_damage_probability",newReboundProb)
		else :
			entity.popTemp("rebound_magic_damage_probability")
			
		#ȥ���������
		oldReboundPercent = entity.queryTemp( "rebound_magic_damage_percent", 0.0 )
		newReboundPercent = oldReboundPercent - self.reboundPercent
		if newReboundPercent > 0.0:
			entity.setTemp( "rebound_magic_damage_percent", newReboundPercent )
		else :
			entity.popTemp("rebound_magic_damage_percent")
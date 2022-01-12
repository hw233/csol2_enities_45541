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
	宠物被动技能:法术反震,将所受到的物理伤害,按一定的比例反射给对方
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
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		
		
		#param1 非对应性格反震
		#param2 对应性格反震
		#param3 对应的性格
		#param4 非对应性格反震几率
		#param5 对应性格反震几率
		
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
				self.reboundPercent = self._param2 # 对应性格反震比率
				self.reboundProb = self._param5 # 对应性格反震几率
			
			#给宠物增加反震
			self.__addEffect(ownerEntity)
			
			#增加主人的反震效果
			petOwner=ownerEntity.getOwner()
			if petOwner.etype == "REAL" :
				self.__addEffect(petOwner.entity)
			else :
				petOwner.attachSkillOnReal(self)
				
		else :# owner callback
			#增加主人的反震效果
			self.__addEffect(ownerEntity)
			
	
	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if ownerEntity.isEntityType(csdefine.ENTITY_TYPE_PET) :
			#ownerEntity.removeVictimHit( self.getUID() )
			if ownerEntity.character == self._param3:
				self.reboundPercent = self._param2 #对应性格的加强型反震
				self.reboundProb = self._param5 # 对应性格反震几率
			
			#去掉宠物身上相应效果
			self.__removeEffect(ownerEntity)
	
			
			#去掉宠物主人身上相应效果
			petOwner = ownerEntity.getOwner()
			if petOwner.etype == "REAL":
				self.__removeEffect(petOwner.entity)
			else :
				petOwner.entity.detachSkillOnReal(self)
		else :# owner callback
			self.__removeEffect(ownerEntity)

	#private
	def __addEffect(self,entity):
		#加上反震概率
		oldReboundProb = entity.queryTemp("rebound_magic_damage_probability",0.0)
		entity.setTemp( "rebound_magic_damage_probability", self.reboundProb + oldReboundProb)
			
		#加上反震比率
		oldReboundPercent = entity.queryTemp( "rebound_magic_damage_percent", 0.0 )
		entity.setTemp( "rebound_magic_damage_percent", self.reboundPercent + oldReboundPercent )
	
	#private	
	def __removeEffect(self,entity):
		#去掉反震概率
		oldReboundProb = entity.queryTemp("rebound_magic_damage_probability",0.0)
		newReboundProb = oldReboundProb - self.reboundProb
		if newReboundProb >0.0 :
			entity.setTemp("rebound_magic_damage_probability",newReboundProb)
		else :
			entity.popTemp("rebound_magic_damage_probability")
			
		#去掉反震比率
		oldReboundPercent = entity.queryTemp( "rebound_magic_damage_percent", 0.0 )
		newReboundPercent = oldReboundPercent - self.reboundPercent
		if newReboundPercent > 0.0:
			entity.setTemp( "rebound_magic_damage_percent", newReboundPercent )
		else :
			entity.popTemp("rebound_magic_damage_percent")
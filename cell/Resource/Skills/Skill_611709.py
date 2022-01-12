# -*- coding:gb18030 -*-

from SpellBase import *
from Skill_Normal import Skill_Normal
from bwdebug import *
from Function import newUID
import random
import csdefine
import csstatus

class Skill_611709( Skill_Normal ):
	"""
	宠物被动技能吸血
	
	主人和自身使用物理攻击伤害对方时，
	有a%的几率，所造成伤害的b%转化为自身生命的提高。
	勇敢型宠物吸血几率提高c%，效果提高d%。
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0			# 触发吸血的一般几率
		self.param2 = 0			# 触发吸血的加强几率
		self.param3 = 0			# 一般吸血比例
		self.param4 = 0			# 加强吸血比例
		self.param5 = 0			# 能获得加强效果的性格
		self.effectPercent1 = 0	# 根据宠物性格确定的触发吸血几率
		self.effectPercent2 = 0 # 根据宠物性格确定的吸血比例
		
	def init( self, dict ):
		"""
		"""
		Skill_Normal.init( self, dict )
		self.param1 = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) / 100.0
		self.param2 = float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) / 100.0
		self.param3 = float( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 ) / 100.0
		self.param4 = float( dict[ "param4" ] if len( dict[ "param4" ] ) > 0 else 0 ) / 100.0
		self.param5 = int( dict[ "param5" ] )
		
	def attach( self, attachEntity ):
		"""
		"""
		if attachEntity.__class__.__name__ == "Pet":
			if attachEntity.character == self.param5:
				self.effectPercent1 = self.param2
				self.effectPercent2 = self.param4
			else:
				self.effectPercent1 = self.param1
				self.effectPercent2 = self.param3
			tempSkill = self.getNewObj()
			attachEntity.appendAttackerAfterDamage( tempSkill )
			petOwner = attachEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				entity.appendAttackerAfterDamage( tempSkill )
				# 记录宠物天赋技能attach时的uid，以便在detach的时候使用petInbornSkillAttachData为dict,key为skillID，value为attach的skill uid。
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", {} )
				petInbornSkillAttachData[tempSkill.getID()] = tempSkill.getUID()
				entity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
			else:
				entity.attachSkillOnReal( tempSkill )
		else:
			attachEntity.appendAttackerAfterDamage( self.getNewObj() )
			petInbornSkillAttachData = attachEntity.queryTemp( "petInbornSkillAttachData", {} )
			petInbornSkillAttachData[self.getID()] = self.getUID()
			
	def detach( self, attachEntity ):
		"""
		"""
		if attachEntity.__class__.__name__ == "Pet":
			attachEntity.removeAttackerAfterDamage( self.getUID() )
			petOwner = attachEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", None )
				if petInbornSkillAttachData is None:
					ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % entity.getName() )
					return
				skillUID = petInbornSkillAttachData.pop( self.getID() )
				entity.removeAttackerAfterDamage( skillUID )
			else:
				entity.detachSkillOnReal( self )
		else:
			petInbornSkillAttachData = attachEntity.queryTemp( "petInbornSkillAttachData", None )
			if petInbornSkillAttachData is None:
				ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % attachEntity.getName() )
				return
			skillUID = petInbornSkillAttachData.pop( self.getID() )
			attachEntity.removeAttackerAfterDamage( skillUID )
			
	def springOnDamage( self, caster, receiver, skill, damage  ):
		"""
		打出伤害后触发吸血
		
		virtual method.
		在伤害计算后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在受到伤害以后再触发的效果；
		
		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   skill: 技能实例
		@type    skill: 
		@param   damage: 施法者造成的伤害
		@type    damage: int32
		"""
		if skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS and skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL:
			return
		if random.random() > self.effectPercent1:
			return
			
		absorbValue = int( damage * self.effectPercent2 )
		if absorbValue > 0:
			caster.addHP( absorbValue )
			caster.statusMessage( csstatus.SKILL_PET_INBORN_SKILL_SPRING, self.getName() )
			#SKILL_HP_BUFF_CURE:%s恢复了你%i点生命值。
			caster.statusMessage( csstatus.SKILL_HP_BUFF_CURE, self.getName(), absorbValue )
			
	def addToDict( self ):
		"""
		返回一个字典，技能实例的打包传输数据
		"""
		return { "param":{"effectPercent1":self.effectPercent1, "effectPercent2":self.effectPercent2} }
		
	def createFromDict( self, data ):
		"""
		使用打包传输的数据生成一个技能实例
		"""
		obj = Skill_611709()
		obj.__dict__.update( self.__dict__ )
		dataParam = data["param"]
		obj.effectPercent1 = dataParam["effectPercent1"]
		obj.effectPercent2 = dataParam["effectPercent2"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj
		
# -*-coding:gb18030 -*-

from bwdebug import *
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID
import random
import csstatus

class Skill_611712( Skill_Normal ):
	"""
	主人和宠物进行物理攻击时，有a%几率让目标获得重伤效果，在之后的3秒内，每秒受到此次攻击伤害b%的伤害。
	活泼型宠物触发几率提高c%，效果提高d%。
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0
		self.effectPercent = 0	# 技能触发的概率
		self.buffIndex = 0		# 技能发挥作用时选择的buff index
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.param1 = float( data[ "param1" ] if len( data[ "param1" ] ) > 0 else 0 ) / 100.0
		self.param2 = float( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 ) / 100.0
		self.param3 = int( data[ "param3" ] )
		
	def springOnDamage( self, caster, receiver, skill, damage  ):
		"""
		打出伤害后
		
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
		@type    skill: SKILL
		@param   damage: 施法者造成的伤害
		@type    damage: int32
		"""
		if random.random() > self.effectPercent:	# 没有触发
			return
		buffData = self.getBuffLink( self.buffIndex )
		if random.randint( 1, 100 ) > buffData.getLinkRate():	# buff本身的概率判定
			return
		caster.statusMessage( csstatus.SKILL_PET_INBORN_SKILL_SPRING, self.getName() )
		newBuff = buffData.getBuff().adapt( damage )	# 使用技能此次产生的伤害生成一个新的buff实例
		newBuff.receive( caster, receiver )				# 接收buff，receive()会自动判断receiver是否为realEntity
		
	def attach( self, attachEntity ):
		"""
		"""
		if attachEntity.__class__.__name__ == "Pet":
			if attachEntity.character == self.param3:
				self.effectPercent = self.param2
				self.buffIndex = 1
			else:
				self.effectPercent = self.param1
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
			attachEntity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
			
	def detach( self, attachEntity ):
		"""
		"""
		if attachEntity.__class__.__name__ == "Pet":
			attachEntity.removeAttackerAfterDamage( self )
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
			
	def addToDict( self ):
		"""
		"""
		return { "param":{"effectPercent" : self.effectPercent, "buffIndex":self.buffIndex} }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Skill_611712()
		obj.__dict__.update( self.__dict__ )
		paramData = data["param"]
		obj.effectPercent = paramData["effectPercent"]
		obj.buffIndex = paramData["buffIndex"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj
		
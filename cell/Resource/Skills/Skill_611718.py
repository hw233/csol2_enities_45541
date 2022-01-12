# -*- coding:gb18030 -*-


from bwdebug import *
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID
import random
import csstatus

class Skill_611718( Skill_Normal ):
	"""
	宠物技能 狂怒
	
	主人和自身进行物理或法术攻击时，有a%几率使己方获得狂怒buff。
	造成所有伤害提高b%，持续c秒。勇敢型宠物触发几率提高d%，效果提高e%。
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0
		self.effectPercent = 0
		self.buffIndex = 0
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.param1 = float( data["param1"] if len( data["param1"] ) > 0 else 0 ) / 100.0
		self.param2 = float( data["param2"] if len( data["param2"] ) > 0 else 0 ) / 100.0
		self.param3 = int( data["param3"] )
		
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
			attachEntity.appendAttackerHit( tempSkill )
			petOwner = attachEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				entity.appendAttackerHit( tempSkill )
				# 记录宠物天赋技能attach时的uid，以便在detach的时候使用petInbornSkillAttachData为dict,key为skillID，value为attach的skill uid。
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", {} )
				petInbornSkillAttachData[tempSkill.getID()] = tempSkill.getUID()
				entity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
			else:
				entity.attachSkillOnReal( tempSkill )
		else:
			tempSkill = self.getNewObj()
			attachEntity.appendAttackerHit( tempSkill )
			petInbornSkillAttachData = attachEntity.queryTemp( "petInbornSkillAttachData", {} )
			petInbornSkillAttachData[self.getID()] = self.getUID()
			attachEntity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
			
	def detach( self, attachEntity ):
		"""
		"""
		if attachEntity.__class__.__name__ == "Pet":
			attachEntity.removeAttackerHit( self )
			petOwner = attachEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", None )
				if petInbornSkillAttachData is None:
					ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % entity.getName() )
					return
				skillUID = petInbornSkillAttachData.pop( self.getID() )
				entity.removeAttackerHit( skillUID )
			else:
				entity.detachSkillOnReal( self )
		else:
			petInbornSkillAttachData = attachEntity.queryTemp( "petInbornSkillAttachData", None )
			if petInbornSkillAttachData is None:
				ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % attachEntity.getName() )
				return
			skillUID = petInbornSkillAttachData.pop( self.getID() )
			attachEntity.removeAttackerHit( skillUID )
			
	def springOnHit( self, caster, receiver, damageType ):
		"""
		"""
		if random.random() > self.effectPercent:	# 没有触发
			return
		buff = self.getBuffLink( self.buffIndex )
		if random.randint( 1, 100 ) > buff.getLinkRate():	# buff本身的概率判定
			return
		caster.statusMessage( csstatus.SKILL_PET_INBORN_SKILL_SPRING, self.getName() )
		buff.getBuff().receive( caster, caster )			# 接收buff，receive()会自动判断receiver是否为realEntity
		
	def addToDict( self ):
		"""
		"""
		return { "param":{"effectPercent" : self.effectPercent, "buffIndex":self.buffIndex}, "uid":self.getUID() }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Skill_611718()
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
		
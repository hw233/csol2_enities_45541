# -*- coding:gb18030 -*-


from bwdebug import *
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID
import random
import csstatus

class Skill_611714( Skill_Normal ):
	"""
	宠物技能 护身
	
	当主人和自身在受到伤害的时候，有a%的几率产生一个魔法护盾,让生命是损失转换为法力的消耗。
	每点生命减少消耗b点法力。（如果此时剩余法力不足以抵抗本次伤害所造成的全部法力消耗，
	那么本次伤害未被法力抵抗的值依然会造成生命的减少。）
	稳重型宠物可以使护身效果出发几率提高c%，每点伤害所消耗法力减少d点。
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
			attachEntity.appendVictimHit( self.getNewObj() )
			petOwner = attachEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				tempSkill = self.getNewObj()
				entity.appendVictimHit( tempSkill )
				
				# 记录宠物天赋技能attach时的uid，以便在detach的时候使用petInbornSkillAttachData为dict,key为skillID，value为attach的skill uid。
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", {} )
				petInbornSkillAttachData[tempSkill.getID()] = tempSkill.getUID()
				entity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
			else:
				entity.attachSkillOnReal( tempSkill )
		else:
			attachEntity.appendVictimHit( self.getNewObj() )
			petInbornSkillAttachData = attachEntity.queryTemp( "petInbornSkillAttachData", {} )
			petInbornSkillAttachData[self.getID()] = self.getUID()
			attachEntity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
			
	def detach( self, attachEntity ):
		"""
		"""
		if attachEntity.__class__.__name__ == "Pet":
			attachEntity.removeVictimHit( self )
			petOwner = attachEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", None )
				if petInbornSkillAttachData is None:
					ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % entity.getName() )
					return
				skillUID = petInbornSkillAttachData.pop( self.getID() )
				entity.removeVictimHit( skillUID )
			else:
				entity.detachSkillOnReal( self )
		else:
			petInbornSkillAttachData = attachEntity.queryTemp( "petInbornSkillAttachData", None )
			if petInbornSkillAttachData is None:
				ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % attachEntity.getName() )
				return
			skillUID = petInbornSkillAttachData.pop( self.getID() )
			attachEntity.removeVictimHit( skillUID )
			
	def springOnHit( self, caster, receiver, damageType ):
		"""
		"""
		if random.random() > self.effectPercent:	# 没有触发
			return
		buff = self.getBuffLink( self.buffIndex )
		if random.randint( 1, 100 ) > buff.getLinkRate():	# buff本身的概率判定
			return
		receiver.statusMessage( csstatus.SKILL_PET_INBORN_SKILL_SPRING, self.getName() )
		buff.getBuff().receive( caster, receiver )			# 接收buff，receive()会自动判断receiver是否为realEntity
		
	def addToDict( self ):
		"""
		"""
		return { "param":{"effectPercent" : self.effectPercent, "buffIndex":self.buffIndex}, "uid":self.getUID() }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Skill_611714()
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
		
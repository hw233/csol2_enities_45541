# -*- coding:gb18030 -*-

from bwdebug import *
import random
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID
import random
import csstatus

class Skill_PetSkillHitSpringBuff( Skill_Normal ):
	"""
	宠物被动技能 宠物或主人击中对方时 给对方施加一个效果，例如：穿透、麻痹、禁咒
	
	主人和宠物进行物理或法术攻击时，有a%的几率让目标获得某种效果(buff)，加强型宠物触发几率提高c%，
	buff效果也会得到加强，加强型性格使用buff2效果，其他则使用buff1
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0			# 宠物性格，此性格宠物获得的效果会得到加强
		self.effectPercent = 0	# 技能触发的概率
		self.buffIndex = 0		# 技能发挥作用时选择的buff index
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.param1 = float( data[ "param1" ] if len( data[ "param1" ] ) > 0 else 0 ) / 100.0
		self.param2 = float( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 ) / 100.0
		self.param3 = int( data[ "param3" ] )
		
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
				# 记录宠物天赋技能attach时的uid，以便在detach的时候使用petInbornSkillAttachData为dict,key为skillID，value为attach的skill uid。
				petInbornSkillAttachData = entity.queryTemp( "petInbornSkillAttachData", {} )
				petInbornSkillAttachData[tempSkill.getID()] = tempSkill.getUID()
				entity.setTemp( "petInbornSkillAttachData", petInbornSkillAttachData )
				entity.appendAttackerHit( self.getNewObj() )
			else:
				entity.attachSkillOnReal( tempSkill )
		else:
			attachEntity.appendAttackerHit( self.getNewObj() )
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
				ERROR_MSG( "player( %s ) dettach pet skill error:petInbornSkillAttachData is None." % entity.getName() )
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
		buff.getBuff().receive( caster, receiver )			# 接收buff，receive()会自动判断receiver是否为realEntity
		
	def addToDict( self ):
		"""
		生成用于传输的数据
		"""
		return { "param":{"effectPercent" : self.effectPercent, "buffIndex":self.buffIndex } }
		
	def createFromDict( self, data ):
		"""
		创建技能实例
		"""
		obj = Skill_PetSkillHitSpringBuff()
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
		
		
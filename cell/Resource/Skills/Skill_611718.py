# -*- coding:gb18030 -*-


from bwdebug import *
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID
import random
import csstatus

class Skill_611718( Skill_Normal ):
	"""
	���＼�� ��ŭ
	
	���˺�������������������ʱ����a%����ʹ������ÿ�ŭbuff��
	��������˺����b%������c�롣�¸��ͳ��ﴥ���������d%��Ч�����e%��
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
				# ��¼�����츳����attachʱ��uid���Ա���detach��ʱ��ʹ��petInbornSkillAttachDataΪdict,keyΪskillID��valueΪattach��skill uid��
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
		if random.random() > self.effectPercent:	# û�д���
			return
		buff = self.getBuffLink( self.buffIndex )
		if random.randint( 1, 100 ) > buff.getLinkRate():	# buff����ĸ����ж�
			return
		caster.statusMessage( csstatus.SKILL_PET_INBORN_SKILL_SPRING, self.getName() )
		buff.getBuff().receive( caster, caster )			# ����buff��receive()���Զ��ж�receiver�Ƿ�ΪrealEntity
		
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
		
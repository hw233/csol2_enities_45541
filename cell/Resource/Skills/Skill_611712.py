# -*-coding:gb18030 -*-

from bwdebug import *
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID
import random
import csstatus

class Skill_611712( Skill_Normal ):
	"""
	���˺ͳ������������ʱ����a%������Ŀ��������Ч������֮���3���ڣ�ÿ���ܵ��˴ι����˺�b%���˺���
	�����ͳ��ﴥ���������c%��Ч�����d%��
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0
		self.effectPercent = 0	# ���ܴ����ĸ���
		self.buffIndex = 0		# ���ܷ�������ʱѡ���buff index
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.param1 = float( data[ "param1" ] if len( data[ "param1" ] ) > 0 else 0 ) / 100.0
		self.param2 = float( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 ) / 100.0
		self.param3 = int( data[ "param3" ] )
		
	def springOnDamage( self, caster, receiver, skill, damage  ):
		"""
		����˺���
		
		virtual method.
		���˺�����󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ���ܵ��˺��Ժ��ٴ�����Ч����
		
		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   skill: ����ʵ��
		@type    skill: SKILL
		@param   damage: ʩ������ɵ��˺�
		@type    damage: int32
		"""
		if random.random() > self.effectPercent:	# û�д���
			return
		buffData = self.getBuffLink( self.buffIndex )
		if random.randint( 1, 100 ) > buffData.getLinkRate():	# buff����ĸ����ж�
			return
		caster.statusMessage( csstatus.SKILL_PET_INBORN_SKILL_SPRING, self.getName() )
		newBuff = buffData.getBuff().adapt( damage )	# ʹ�ü��ܴ˴β������˺�����һ���µ�buffʵ��
		newBuff.receive( caster, receiver )				# ����buff��receive()���Զ��ж�receiver�Ƿ�ΪrealEntity
		
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
				# ��¼�����츳����attachʱ��uid���Ա���detach��ʱ��ʹ��petInbornSkillAttachDataΪdict,keyΪskillID��valueΪattach��skill uid��
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
		
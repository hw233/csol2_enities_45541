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
	���ﱻ��������Ѫ
	
	���˺�����ʹ���������˺��Է�ʱ��
	��a%�ļ��ʣ�������˺���b%ת��Ϊ������������ߡ�
	�¸��ͳ�����Ѫ�������c%��Ч�����d%��
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0			# ������Ѫ��һ�㼸��
		self.param2 = 0			# ������Ѫ�ļ�ǿ����
		self.param3 = 0			# һ����Ѫ����
		self.param4 = 0			# ��ǿ��Ѫ����
		self.param5 = 0			# �ܻ�ü�ǿЧ�����Ը�
		self.effectPercent1 = 0	# ���ݳ����Ը�ȷ���Ĵ�����Ѫ����
		self.effectPercent2 = 0 # ���ݳ����Ը�ȷ������Ѫ����
		
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
		����˺��󴥷���Ѫ
		
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
		@type    skill: 
		@param   damage: ʩ������ɵ��˺�
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
			#SKILL_HP_BUFF_CURE:%s�ָ�����%i������ֵ��
			caster.statusMessage( csstatus.SKILL_HP_BUFF_CURE, self.getName(), absorbValue )
			
	def addToDict( self ):
		"""
		����һ���ֵ䣬����ʵ���Ĵ����������
		"""
		return { "param":{"effectPercent1":self.effectPercent1, "effectPercent2":self.effectPercent2} }
		
	def createFromDict( self, data ):
		"""
		ʹ�ô���������������һ������ʵ��
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
		
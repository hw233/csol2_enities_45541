# -*- coding:gb18030 -*-

import random
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID

class Skill_BeHitSpringSpell( Skill_Normal ):
	"""
	��ұ����к��м��ʶ�����/Ŀ��ż���
	���磬����Χ���/����Ŀ������˺�����ѣ��xx
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_Normal.__init__( self )
		self.triggerSkillID = 0		# ����ID
		self.effectPercent = 0.0	# ��������
		self.isOwnerSpell = False	# �������Ƕ�Ŀ�꣬Ĭ���Ƕ�Ŀ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self.triggerSkillID = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )
		self.effectPercent = float( dict["param2"] if len( dict["param2"] ) > 0 else 0 ) / 100.0
		self.isOwnerSpell = bool( int( dict["param3"] if len( dict["param3"] ) > 0 else 0 ) )

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.appendVictimHit( self.getNewObj() )

	def detach( self, ownerEntity ):
		"""
		virtual method
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.removeVictimHit( self.getUID() )

	def springOnHit( self, caster, receiver, damageType ):
		"""
		�����к�Ч��
		"""
		if random.random() > self.effectPercent:	# û�д���
			return

		if self.isOwnerSpell:	# ������ż���
			receiver.spellTarget( self.triggerSkillID, receiver.id )
		else:					# ��Ŀ��ż���
			receiver.spellTarget( self.triggerSkillID, caster.id )

	def addToDict( self ):
		"""
		�������ڴ��������
		"""
		return { "param":{"triggerSkillID":self.triggerSkillID, "effectPercent":self.effectPercent, "isOwnerSpell":self.isOwnerSpell} }

	def createFromDict( self, data ):
		"""
		��������ʵ��
		"""
		obj = Skill_BeHitSpringSpell()
		obj.__dict__.update( self.__dict__ )
		paramData = data["param"]
		obj.triggerSkillID = paramData["triggerSkillID"]
		obj.effectPercent = paramData["effectPercent"]
		obj.isOwnerSpell = paramData["isOwnerSpell"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj

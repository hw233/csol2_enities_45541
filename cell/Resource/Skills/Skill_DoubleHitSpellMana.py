# -*- coding: gb18030 -*-

import random
from SpellBase import *
from Skill_DoubleHitSpell import Skill_DoubleHitSpell
from Function import newUID

class Skill_DoubleHitSpellMana( Skill_DoubleHitSpell ):
	"""
	��ұ������к��м��ʶ�����/Ŀ���ͷ�һ������Ҫ����ħ���ı�־
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_DoubleHitSpell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_DoubleHitSpell.init( self, dict )

	def springOnDoubleHit( self, caster, receiver, damageType ):
		"""
		����������Ч��
		"""
		if self.isOwnerSpell:
			if caster.queryTemp( "FORBID_NOT_NEED_MANA", False ):
				return
		else:
			if receiver.queryTemp( "FORBID_NOT_NEED_MANA", False ):
				return

		Skill_DoubleHitSpell.springOnDoubleHit( self, caster, receiver, damageType )

	def addToDict( self ):
		"""
		�������ڴ��������
		"""
		return { "param":{"triggerSkillID":self.triggerSkillID, "effectPercent":self.effectPercent, "isOwnerSpell":self.isOwnerSpell} }

	def createFromDict( self, data ):
		"""
		��������ʵ��
		"""
		obj = Skill_DoubleHitSpellMana()
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

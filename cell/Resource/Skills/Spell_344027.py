# -*- coding:gb18030 -*-

from bwdebug import *
import csstatus
from Love3 import g_skills
from Spell_Item import Spell_Item

class Spell_344027( Spell_Item ):
	"""
	���Ӳɼ����������ȣ�����Ʒ����ֻ�ܶ��Լ��ͷţ���Ϊ�ͷż���ʱ�޷����Ŀ��Ĳɼ���������
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.skillID = 0
		self.sleight = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Item.init( self, data )
		self.skillID = int( data["param1"] if data["param1"] > 0 else 0 )	# Ҫ���������ȵĲɼ�����id
		self.sleight = int( data["param2"] if data["param2"] > 0 else 0 )	# Ҫ���ӵ�������
		
	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		��Ҫ��������Ϣ�����ⲻ��ʹ����Ʒʱ��ʾʹ�ü���
		"""
		if not caster.liv_hasLearnSkill( self.skillID ):
			return csstatus.LIVING_SKILL_HASNT_LEARN
		if caster.isSleightLevelMax( self.skillID ):
			return csstatus.LIVING_CANT_LEVEL_UP_SKILL
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		"""
		skillInstance = g_skills[self.skillID]
		skillName = ""
		if skillInstance is None:
			ERROR_MSG( "Living skill %s is None."%(self.skillID) )
		else:
			skillName = skillInstance.getName()
		receiver.addSleight( self.skillID, self.sleight )
		receiver.statusMessage( csstatus.LIVING_SKILL_SLE_UP, skillName, receiver.getSleight( self.skillID ), receiver.getSleightMax( self.skillID ) )
		
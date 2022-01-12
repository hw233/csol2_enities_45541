# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *

from SpellBase import *
from Skill_Damage import Skill_Damage

import csconst
import csdefine
import csstatus
import random


class Skill_MagicDamage( Skill_Damage ):
	"""
	���������˺���:�����˺�

	Ŀǰ��������,��������ĿǰΪֹȷ����һЩ��Ϊ����Ӧװ���������Լ��ܵ�����,
	�Ժ���Ҫ�Ա������ܽṹ��������滮.11:14 2008-10-24,wsf
	"""
	def __init__( self ):
		"""
		"""
		Skill_Damage.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Damage.init( self, dict )


	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		���㱩���˺��ӱ�
		@param caster: ��������
		@type  caster: entity
		@return type:�����õ��ı�������
		"""
		return caster.magic_double_hit_multiple


	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		�жϹ������Ƿ񱬻�
		return type:bool
		"""
		return random.random() < ( caster.magic_double_hit_probability + ( receiver.be_magic_double_hit_probability - receiver.be_magic_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )






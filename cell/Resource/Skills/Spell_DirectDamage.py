# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl
from Spell_PhysSkill import Spell_PhysSkill2
from Spell_Magic import Spell_Magic

class Spell_DirectPhyDamage( Spell_PhysSkill2 ):
	"""
	Ԫ���˺�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻�����������������
		��ɫ�����������ֵ���ܹ�ʽ�еĻ���ֵ��=0
		����������ˣ��ܹ�ʽ�еĻ���ֵ��= ����ֵ/(0.1*����ֵ+150*�������ȼ�+1000) 
		�ڹ����ļ����У�����ֵ���Ȼ���ɷ������ˣ�Ȼ���ٺ͹��������л��㡣
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		@return: FLOAT
		"""
		return 0


class Spell_DirectMagicDamage( Spell_Magic ):
	"""
	Ԫ���˺�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻�����������������
		��ɫ�����������ֵ���ܹ�ʽ�еĻ���ֵ��=0
		����������ˣ��ܹ�ʽ�еĻ���ֵ��= ����ֵ/(0.1*����ֵ+150*�������ȼ�+1000) 
		�ڹ����ļ����У�����ֵ���Ȼ���ɷ������ˣ�Ȼ���ٺ͹��������л��㡣
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		@return: FLOAT
		"""
		return 0
		
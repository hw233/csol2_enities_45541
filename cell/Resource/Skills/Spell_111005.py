# -*- coding: gb18030 -*-
#
# $Id: Spell_111005.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from Spell_PhysSkill import Spell_PhyVolley


class Spell_111005( Spell_PhyVolley ):
	"""
	��ɱ���ܣ���Ŀ�굥λ����൱��������ֵ����50%�������˺�
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhyVolley.__init__( self )
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhyVolley.init( self, dict )
		self._param = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  / 100.0	
		
	def calcDamage( self, caster, receiver, skillDamage ):
		"""
		virtual method.
		����ֱ���˺�
		��ͨ�����˺����ܹ�ʽ�еĻ���ֵ��=��������*��1-������������������ˣ�
		���������˺����ܹ�ʽ�еĻ���ֵ��=���ܹ�����*��1-������������������ˣ�
		
		@param source: ������
		@type  source: entity
		@param target: ��������
		@type  target: entity
		@param skillDamage: ���ܹ�����
		@return: INT32
		"""
		return receiver.HP_Max * self._param
		
#$Log: not supported by cvs2svn $
#
#
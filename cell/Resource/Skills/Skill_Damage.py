# -*- coding: gb18030 -*-


from bwdebug import *
from Skill_Normal import Skill_Normal
import BigWorld
import csconst
import csstatus
import csdefine
import random


class Skill_Damage( Skill_Normal ):
	"""
	�������� �����˺���
	
	Ŀǰ��������,��������ĿǰΪֹȷ����һЩ��Ϊ����Ӧװ���������Լ��ܵ�����,
	�Ժ���Ҫ�Ա������ܽṹ��������滮.11:14 2008-10-24,wsf
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		
		
	def calcProperty( self, baseVal, extraVal, percentVal, value ):
		"""
		�������������ܹ�ʽ
		����ֵ=������ֵ+����ֵ��*��1+�ӳɣ�+��ֵ
		@param baseVal: ����ֵ
		@param extraVal: ����ֵ
		@param percentVal: �ӳ�
		@param value: ��ֵ
		"""
		return ( baseVal + extraVal ) * ( 1 + percentVal ) + value
		
		
	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		����������
		
		
		�������������ʣ��ܹ�ʽ�еĻ���ֵ��=95% -�����������ȼ�-�������ȼ���^1.61*3%
		
		��������������ȼ�-�������ȼ���<0���򣨱��������ȼ�-�������ȼ���=0���Ϊ0��
		���95% -�����������ȼ�-�������ȼ���^1.61*3%<1%�������ȡ1%��
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		return type:	Float
		"""
		ERROR_MSG( "This is virtual method." )
		
		
	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻�����������������
		��ɫ�����������ֵ���ܹ�ʽ�еĻ���ֵ��=0
		����������ˣ��ܹ�ʽ�еĻ���ֵ��=�������ֵ/���������ֵ+45*�������ȼ�+350��
		�ڹ����ļ����У�����ֵ���Ȼ���ɷ������ˣ�Ȼ���ٺ͹��������л��㡣
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		@return: FLOAT
		"""
		ERROR_MSG( "This is virtual method." )
		
		
	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		���㱻�����������˺�����
		�˺�=�����˺�x (1 �C �������������˺�������) 
		�C �������������˺�����ֵ
		�˺�����Ϊ0��
		ע���˺�ΪDOT�ͳ����˺�������˺���ֵ�������ٷִ����á�
		���У������˺������ʼ������˺�����ֵ�ο���ʽ�ĵ�����ʽ���£�
		��ɫ���������˺�����������ܹ�ʽ�еĻ���ֵ��=0
		��ɫ���������˺�����ֵ���ܹ�ʽ�еĻ���ֵ��=0
		@param target: ��������
		@type  target: entity
		@param  damage: �����м��жϺ���˺�
		@type   damage: INT
		@return: INT32
		"""
		return caster.calcDamageScissor( receiver, damage )
		
		
	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		���㱩���˺��ӱ�
		@param caster: ��������
		@type  caster: entity
		@return type:�����õ��ı�������
		"""
		ERROR_MSG( "This is virtual method." )
		return 1.0
		
	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		�жϹ������Ƿ񱬻�
		return type:bool
		"""
		ERROR_MSG( "This is virtual method." )
		
		
	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		��ʽ1�����ܹ��������ܹ�ʽ�еĻ���ֵ��=���ܱ���Ĺ�����+��ɫ����������
		�����ܹ�ʽ�о��ǣ������ܱ���Ĺ�����+��ɫ����������*��1+���������ӳɣ�+����������ֵ
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		return random.randint( self._effect_min, self._effect_max )
		
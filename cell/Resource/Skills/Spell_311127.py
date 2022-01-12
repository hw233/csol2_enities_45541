# -*- coding: gb18030 -*-
#
from bwdebug import *
import BigWorld
import csconst
from Spell_PhysSkill import Spell_PhysSkill
import time

class Spell_311127( Spell_PhysSkill ):
	"""
	��ɱ������ ���ܱ���Ĺ�����+��ɫ����������  ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )

	def calcDamage( self, source, target, skillDamage ):
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
		damagePer = 1.0
		indexs = target.findBuffsByBuffID( 107012 )
		if len( indexs ):
			index = indexs[0]
			buff = target.getBuff( index )
			endTime = buff["persistent"]
			nowTime = time.time()
			skill = buff["skill"]
			lastTime = skill._persistent
			per = ( lastTime - ( endTime - nowTime ) )/( lastTime * 1.0 )
			if per < 0: per = 0
			if per > 1: per = 1
			damagePer += per

		# ���㱻�����������������
		armor = self.calcVictimResist( source, target )
		damage = ( skillDamage * ( 1 - armor ) ) * ( 1 + target.receive_damage_percent / csconst.FLOAT_ZIP_PERCENT ) + target.receive_damage_value
		endDamage = int( damage * damagePer )
		return endDamage

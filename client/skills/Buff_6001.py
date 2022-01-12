# -*- coding: gb18030 -*-

"""
BUFF�����ࡣ
"""
import BigWorld
from SpellBase import *


class Buff_6001( Buff ):
	"""
	example:�������buff
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.isPlayWaterRun = True
			target.setArmCaps()

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		yaw = 0
		if target.id == BigWorld.player().id:
			target.isPlayWaterRun = False
			target.setArmCaps()
	
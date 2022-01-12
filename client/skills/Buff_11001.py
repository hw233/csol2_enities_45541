# -*- coding: gb18030 -*-
#���� buff�ͻ��˽ű�

from bwdebug import *
from SpellBase import *
import Math

class Buff_11001( Buff ):
	"""
	���� buff�ͻ��˽ű�
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self.color = Math.Vector4( 1.0, 1.0, 1.0, 1.0 )
		self.lastTime = 0.0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )
		param2 = dict[ "Param2" ].split(";")
		if len( param2 ) >= 2:
			self.color = eval( param2[0] )
			self.lastTime = eval( param2[1] )

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		target.addModelColorBG( self.getID(), self.color, self.lastTime )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		target.removeModelColorBG( self.getID() )


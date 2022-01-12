# -*- coding: gb18030 -*-

from bwdebug import *
from SpellBase import *
import BigWorld
import Math

class Buff_107002( Buff ):
	"""
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self.color = Math.Vector4(1,1,1,1)
		self.lastTime = 0.0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )
		param2 = dict[ "Param2" ].split(";")
		if len( param2 ) == 5:
			x = 0.0
			y = 0.0
			z = 0.0
			a = 0.0
			b = 0.0
			try:
				x = float( param2[0] )
				y = float( param2[1] )
		 		z = float( param2[2] )
		 		a = float( param2[3] )
		 		b = float( param2[4] )
		 	except:
		 		pass
			self.color = Math.Vector4( x, y, z, a )
			self.lastTime = b

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


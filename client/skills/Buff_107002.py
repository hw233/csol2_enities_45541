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
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self.color = Math.Vector4(1,1,1,1)
		self.lastTime = 0.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
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
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		target.addModelColorBG( self.getID(), self.color, self.lastTime )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		target.removeModelColorBG( self.getID() )


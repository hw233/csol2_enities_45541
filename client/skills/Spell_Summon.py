# -*- coding: gb18030 -*-

"""
召唤客户端类
"""
from bwdebug import *
from SpellBase import *
import BigWorld
from Function import Functor

class Spell_Summon( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.randomPosFlag = False  #是否要将施法者放入随机分配坐标点
		
		
	def init( self, data ):
		Spell.init( self, data )
		if data["param4"] != "" :
			self.randomPosFlag = bool( int(data["param4"]) )
		else:
			self.randomPosFlag = False

	def cast( self, caster, targetObject ):
		"""
		"""
		Spell.cast( self, caster, targetObject )
		if  self.randomPosFlag:
			caster.setVisibility(False)
			BigWorld.callback( 1.5, Functor( self.showModel, caster ) )
		
	def showModel( self,caster ):
		caster.updateVisibility()
		caster.fadeInModel()


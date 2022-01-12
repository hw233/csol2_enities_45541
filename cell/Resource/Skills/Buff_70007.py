# -*- coding:gb18030 -*-

from bwdebug import *
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_70007( Buff_Normal ):
	"""
	法术姿态
	
	法术攻击力提高%，进入法术姿态
	"""
	def __init__( self ):
		Buff_Normal.__init__( self )
		self.posture = csdefine.ENTITY_POSTURE_MAGIC
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		# 法术攻击力提高%
		self.param1 = float( data["Param1"] if data["Param1"] > 0 else 0 ) * 100
		self.param2 = int( data[ "Param2" ] if len( data[ "Param2" ] ) > 0 else 0 )
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.changePosture( self.posture )
		receiver.magic_damage_percent += self.param1
		receiver.magic_damage_value += self.param2
		receiver.calcMagicDamage()
		
	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.changePosture( self.posture )
		receiver.magic_damage_percent += self.param1
		receiver.magic_damage_value += self.param2
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.changePosture( csdefine.ENTITY_POSTURE_NONE )
		receiver.magic_damage_percent -= self.param1
		receiver.magic_damage_value -= self.param2
		receiver.calcMagicDamage()
		
		
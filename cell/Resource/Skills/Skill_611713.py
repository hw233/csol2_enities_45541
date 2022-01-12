# -*- coding:gb18030 -*-

from bwdebug import *
from SpellBase import *
from Function import newUID
from Skill_Normal import Skill_Normal
import random


class Skill_611713( Skill_Normal ):
	"""
	宠物被动技能 温顺
	
	使这只宠物因出战或死亡所降低的快乐度减少a%。因死亡造成寿命损失降低b%。
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.param1 = float( data["param1"] if len( data["param1"] ) > 0 else 0 ) / 100.0
		self.param2 = float( data["param2"] if len( data["param2"] ) > 0 else 0 ) / 100.0
		
	def attach( self, attachEntity ):
		"""
		"""
		attachEntity.setTemp( "pet_joyancy_reduce_discount", self.param1 )
		attachEntity.setTemp( "pet_life_reduce_discount", self.param2 )
		
	def detach( self, attachEntity ):
		"""
		"""
		attachEntity.removeTemp( "pet_joyancy_reduce_discount" )
		attachEntity.removeTemp( "pet_life_reduce_discount" )
		
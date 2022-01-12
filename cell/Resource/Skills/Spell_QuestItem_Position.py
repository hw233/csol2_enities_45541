# -*- coding: gb18030 -*-
#

"""
在某个位置范围使用道具
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items
import Math
import math


class Spell_QuestItem_Position( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self.__position		= Math.Vector3( eval(dict["param1"]) )
		self.__range		= int( dict["param2"] )
		self.__questID	 	= int( dict["param3"] )
		self.__taskIndex	= int( dict["param4"] )
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		caster.questTaskIncreaseState( self.__questID, self.__taskIndex )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if not math.fabs( self.__position[0] - caster.position[0] ) < self.__range:
			return csstatus.SKILL_USE_ITEM_WRONG_POSITION
		if not math.fabs( self.__position[2] - caster.position[2] ) < self.__range:
			return csstatus.SKILL_USE_ITEM_WRONG_POSITION
		return Spell_Item.useableCheck( self, caster, target)
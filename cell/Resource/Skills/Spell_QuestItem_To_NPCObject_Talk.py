# -*- coding: gb18030 -*-
#

"""
摧毁场景物件
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items


class Spell_QuestItem_To_NPCObject_Talk( Spell_Item ):
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
		self.__className	= str( dict["param1"] ) 
		self.__questID		= int( dict["param2"] )
		self.__taskIndex 	= int( dict["param3"] )
		self.__count		= int( dict["param4"] )
		self.__talks		= str( dict["param5"] )
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		try:
			count = caster.questsTable[self.__questID].getTasks()[self.__taskIndex].val1
		except KeyError:	# 有可能使用这个物品时没有接取相关任务，容错处理。
			pass
		else:
			if count < self.__count:
				start 	= self.__talks.find('%i:'%(count+1)) + len("%i"%(count+1)) + 1
				end 	= self.__talks.find('%i:'%(count+2))

				if end == -1:
					text = self.__talks[start:]
				else:
					text = self.__talks[start:end]

				caster.setGossipText( text )
				caster.sendGossipComplete( receiver.id )
				#caster.questTaskIncreaseState( self.__questID, self.__taskIndex )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if self.__className != target.getObject().className:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET


		return Spell_Item.useableCheck( self, caster, target)


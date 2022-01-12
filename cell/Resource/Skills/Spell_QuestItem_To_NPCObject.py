# -*- coding: gb18030 -*-
#

"""
对NPC使用道具
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items
import ECBExtend
import csconst
import csdefine


class Spell_QuestItem_To_NPCObject( Spell_Item ):
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
		#self.__classNames = str( dict["param1"] ).split(":")
		self.__questID	 = int( dict["param1"] )
		taskInfo = str( dict["param2"] ).split("|")			#className:TaskIndex|className:Index|...
		
		self.__classNameDict = {}
		for i in taskInfo:
			className, taskIndex = i.split(":")
			self.__classNameDict[className] = int( taskIndex )
		
		self.__isDestroy	 = int( dict["param3"] )
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		caster.questTaskIncreaseState( self.__questID, self.__classNameDict[receiver.className] )
		if self.__isDestroy:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_QUEST_BOX ):
				receiver.onReceiveSpell( caster, None )
			else:
				receiver.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if not target.getObject().className in self.__classNameDict:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		return Spell_Item.useableCheck( self, caster, target)


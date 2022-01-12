# -*- coding: gb18030 -*-
#

"""
��NPCʹ�õ���
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items
import csdefine


class Spell_QuestItem_StopNpcBuff( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )



	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.__init__( self )
		self.__className 	= int( dict["Param1"] )
		self.__buffID	 	= int( dict["Param2"] )
		self.__questID	 	= int( dict["Param3"] )
		self.__taskIndex	= int( dict["Param4"] )
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		playerEntity.questTaskIncreaseState( self.__questID, self.__taskIndex )
		receiver.removeBuffByID( self.__buffID, [csdefine.BUFF_INTERRUPT_NONE] )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if self.__className != target.getObject().className:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		if len( target.findBuffsByBuffID( self.__buffID ) ) == 0:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		return Spell_Item.useableCheck( self, caster, target)


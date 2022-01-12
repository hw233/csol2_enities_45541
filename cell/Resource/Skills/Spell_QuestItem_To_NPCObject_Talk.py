# -*- coding: gb18030 -*-
#

"""
�ݻٳ������
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
		���캯����
		"""
		Spell_Item.__init__( self )



	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
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
		����������Ҫ��������
		"""
		try:
			count = caster.questsTable[self.__questID].getTasks()[self.__taskIndex].val1
		except KeyError:	# �п���ʹ�������Ʒʱû�н�ȡ��������ݴ���
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


# -*- coding: gb18030 -*-
#
# $Id: Exp $

import BigWorld
import csdefine
from NPCObject import NPCObject
import random
import time
from Love3 import g_trapSoundsLoader

OBJECT_BAD_BUFF 	= 1						#����BUFF
OBJECT_GOOD_BUFF 	= 2						#����BUFF
OBJECT_ITEM			= 3						#������Ʒ
OBJECT_SOUND_BUFF	= 4						#��ЧBUFF

clsName_map = {}
OBJECT_LIST = {OBJECT_BAD_BUFF:[760002002,760004002,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,],\
				OBJECT_GOOD_BUFF:[760002002,760004002,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,],\
				OBJECT_ITEM:[40501001,40501002,40501003,40501004,40501005,40501006,40501008,40501009,40501010,40501011],
				}

"""
ѣ��: 760002002
֩����(����):760004002
������ƣ����ҿռ䣩:760005002
���ػ��ף����ػ��ף�:760008002
������������������:760009002
���Σ����٣�:760012003


�ٻ���:40501001
�δ�:40501002
̩ɽ�Ƽ�:40501003
֩����:40501004
�Իü�:40501005
һƬ��̶:40501006
����Ȧ:40501008
���:40501009
�����:40501010
Ǯ����:40501011
"""

"""
CLASSNAME:30111324	��̶		buffID:760006002
CLASSNAME:30111323	֩����   	buffID:760004002
"""


NITAN_TIMER = 1
DESTROY_TIME = 2

class TrapEntity( NPCObject ) :
	"""
	"""
	def __init__( self ) :
		NPCObject.__init__( self )
		self.trapRange = 2.0
		if self.className == '30111324':
			self.addTimer( 60, 0, DESTROY_TIME )
			self.trapRange = 10.0
		if g_trapSoundsLoader.hasSoundInfo( self.className ):
			self.trapRange = g_trapSoundsLoader.getTrapRange( self.className )
			self.addProximityExt( self.trapRange )
			return
		self.setTemp( "trap_entity_last_time", time.time() + 60 )
		self.addProximityExt( self.trapRange )
	
	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		if self.trapOnly == True:
			if self.className == '30111323':
				self.spell( entity, 760004002 )
				self.destroy()
			elif self.className == '30111324':
				entity.setTemp( "trap_entity_last_time", self.queryTemp( "trap_entity_last_time", 0 ) )
				self.spell( entity, 760006002 )
			return
		if g_trapSoundsLoader.hasSoundInfo( self.className ):					#����Ч����
			soundInfo = g_trapSoundsLoader.getSoundInfo( self.className )
			self.playSoundToPlayer( entity, soundInfo )
			return
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			objectType = random.randint( 1, 3 )
			if OBJECT_BAD_BUFF == objectType:
				index = random.randint( 0, len( OBJECT_LIST[objectType] ) - 1 )
				buffID = OBJECT_LIST[objectType][index]
				self.spell( entity, buffID )
			elif OBJECT_GOOD_BUFF == objectType:
				index = random.randint( 0, len( OBJECT_LIST[objectType] ) - 1 )
				buffID = OBJECT_LIST[objectType][index]
				self.spell( entity, buffID )	
			elif OBJECT_ITEM == objectType:
				if not entity.getFreeRaceBagOrder() == -1:
					index = random.randint( 0, len( OBJECT_LIST[objectType] ) - 1 )
					itemID = OBJECT_LIST[objectType][index]
					self.sendItemToPlayer( entity, itemID )
				else:	
					self.destroy()

	def spell( self, entity, buffID ):
		"""
		����ɫ��BUFF
		"""
		if not hasattr( entity,"spellTarget"):
			return
		entity.spellTarget( int(buffID), entity.id )
		if self.className == '30111323' or self.className == '30111324' :
			return	
		self.destroy()

	def sendItemToPlayer( self, entity, itemID ):
		"""
		����ɫһ��������Ʒ
		"""
		item = entity.createDynamicItem( itemID )
		if item == None:
			print itemID
			return
		entity.addRaceItem( item )
		self.destroy()
	
	def playSoundToPlayer( self, entity, soundInfo ):
		"""
		����ɫ������Ч
		"""
		if soundInfo is None:return
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return
		questID = soundInfo["questID"]
		questStatus = soundInfo["questStatus"]
		soundEvent = soundInfo["soundEvent"]
		entity.playSoundByQuest( questID, questStatus, soundEvent )
	
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == DESTROY_TIME:
			self.destroy()

	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if not entity.isDestroyed:
			if self.className == '30111324':
				entity.removeBuffByID( 76000600201, [csdefine.BUFF_INTERRUPT_NONE] )
			
			if g_trapSoundsLoader.hasSoundInfo( self.className ):
				if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					entity.client.onStopMonsterSound()

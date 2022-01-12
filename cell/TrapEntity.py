# -*- coding: gb18030 -*-
#
# $Id: Exp $

import BigWorld
import csdefine
from NPCObject import NPCObject
import random
import time
from Love3 import g_trapSoundsLoader

OBJECT_BAD_BUFF 	= 1						#有意BUFF
OBJECT_GOOD_BUFF 	= 2						#恶意BUFF
OBJECT_ITEM			= 3						#赛马物品
OBJECT_SOUND_BUFF	= 4						#音效BUFF

clsName_map = {}
OBJECT_LIST = {OBJECT_BAD_BUFF:[760002002,760004002,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,],\
				OBJECT_GOOD_BUFF:[760002002,760004002,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,760005002,760008002,760009002,760012003,],\
				OBJECT_ITEM:[40501001,40501002,40501003,40501004,40501005,40501006,40501008,40501009,40501010,40501011],
				}

"""
眩晕: 760002002
蜘蛛网(束缚):760004002
精神控制（错乱空间）:760005002
神秘护甲（神秘护甲）:760008002
精神焕发（精神焕发）:760009002
变形（加速）:760012003


迟缓剂:40501001
晕锤:40501002
泰山移驾:40501003
蜘蛛网:40501004
迷幻剂:40501005
一片泥潭:40501006
保护圈:40501008
马刺:40501009
经验包:40501010
钱袋子:40501011
"""

"""
CLASSNAME:30111324	泥潭		buffID:760006002
CLASSNAME:30111323	蜘蛛网   	buffID:760004002
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
		if g_trapSoundsLoader.hasSoundInfo( self.className ):					#有音效配置
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
		给角色加BUFF
		"""
		if not hasattr( entity,"spellTarget"):
			return
		entity.spellTarget( int(buffID), entity.id )
		if self.className == '30111323' or self.className == '30111324' :
			return	
		self.destroy()

	def sendItemToPlayer( self, entity, itemID ):
		"""
		给角色一个赛马物品
		"""
		item = entity.createDynamicItem( itemID )
		if item == None:
			print itemID
			return
		entity.addRaceItem( item )
		self.destroy()
	
	def playSoundToPlayer( self, entity, soundInfo ):
		"""
		给角色播放音效
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

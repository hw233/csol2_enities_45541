# -*- coding: gb18030 -*-
#
# $Id: Exp $

import BigWorld
import csdefine
from NPCObject import NPCObject
import random
import time


ITEM_RELATED_SKILL_DICT = { "30111324":760006002, "30111323":760004002, "30111322":760005002 }
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


class TowerDefenseTrapEntity( NPCObject ) :
	"""
	"""
	def __init__( self ) :
		NPCObject.__init__( self )
		self.trapRange = 2.0
		self.addProximityExt( self.trapRange )
	
	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			for i in ITEM_RELATED_SKILL_DICT.iterkeys():
				if i == self.className:
					entity.client.addTowerDefenseSpaceSkill( ITEM_RELATED_SKILL_DICT[i], csdefine.SPACE_TYPE_TOWER_DEFENSE )
					self.destroy()

	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		pass
		
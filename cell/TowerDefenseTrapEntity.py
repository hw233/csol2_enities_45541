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
		
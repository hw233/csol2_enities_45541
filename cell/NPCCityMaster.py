# -*- coding: gb18030 -*-
import csdefine
import BigWorld
from interface.GameObject import GameObject
VOLATILE_INFO_CLOSED = (BigWorld.VOLATILE_NEVER,) * 4

class NPCCityMaster( GameObject ):
	def __init__( self ):
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CITY_MASTER )
		self.volatileInfo = VOLATILE_INFO_CLOSED
		
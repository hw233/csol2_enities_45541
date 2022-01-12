# -*- coding: gb18030 -*-
# $Id: NPC108Star.py,v 1.11 2008-08-21 03:26:27 zhangyuxing Exp $

import BigWorld
import NPC
from bwdebug import *
import csdefine
import ECBExtend
import items
g_items = items.instance()

class CityWarFungus( NPC.NPC ):
	"""
	城市战场蘑菇
	"""
	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		selfEntity.addTimer( 180, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
		
	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if not playerEntity.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]:
			return
			
		if dlgKey == "getTarget":
			params = { "dropType" : csdefine.DROPPEDBOX_TYPE_OTHER, "ownerIDs": [ playerEntity.id ] }
			itemBox = BigWorld.createEntity( "DroppedBox", selfEntity.spaceID, selfEntity.position, selfEntity.direction, params )
			itemBox.init( ( playerEntity.id, 0 ), [ g_items.createDynamicItem( 50201256 , 1 ) ] )			
			selfEntity.destroy()
			return
			
		playerEntity.spellTarget( 711017001, selfEntity.id )
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
	����ս��Ģ��
	"""
	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		selfEntity.addTimer( 180, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
		
	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
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
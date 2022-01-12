# -*- coding: gb18030 -*-
#
# $Id: $

import BigWorld
import csdefine
from bwdebug import DEBUG_MSG
from Monster import Monster


class Monster_YiJieZhanChangStone(Monster):
	"""
	���ս���еĺ����ʯ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		Monster.initEntity( self, selfEntity )
		
		if not selfEntity.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			return
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.remoteScriptCall( "onYiJieStoneCreate", () )

	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ����selfEntity��die()������ʱ������
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		
		killer = BigWorld.entities.get( killerID )
		killerDBID = 0
		if not killer : return
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			killerDBID = killer.databaseID
		elif killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
			killer = killer.getOwner().entity
			killerDBID = getattr( killer, "databaseID", 0 )
		if killerDBID == 0 : return
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.remoteScriptCall( "onYiJieStoneDie", ( killerDBID, ) )
		
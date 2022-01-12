# -*- coding: gb18030 -*-
import time
import random
import BigWorld

from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import csconst
import csstatus
import Const

class SpaceCopyAoZhan( SpaceCopy ):
	# ��սȺ��
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
	
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		SpaceCopy.initEntity( self, selfEntity )
	
	def packedDomainData( self, entity ):
		"""
		����SpaceDomainShenGuiMiJingʱ�����ݲ���
		"""
		d = {}
		d[ "playerDBID" ] = entity.databaseID
		return d
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		d = {}
		d[ "roleName" ] = entity.getName()
		d.update( SpaceCopy.packedSpaceDataOnEnter( self, entity ) )
		return d
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		����
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		startTime = selfEntity.params[ "roundTime" ] + 60 - time.time()#׼��ʱ����60��
		if startTime:
			if startTime > 60:
				startTime = 60
			baseMailbox.client.aoZhan_countDown( int( startTime ) )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		�뿪
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		killerType = 0
		killerBase = None
		if killer:
			killerType = killer.getEntityType()
			if killerType == csdefine.ENTITY_TYPE_PET:
				petOwner = killer.getOwner()
				if petOwner.etype == "MAILBOX":
					killerBase = petOwner.entity.base
			else:
				killerBase  = killer.base
		
		role.getCurrentSpaceBase().cell.onRoleBeKill( role.base, killerBase )
	
	def activityStart( self, selfEntity ):
		selfEntity.battleData.setPkMode()
	
	def kickAllPlayer( self, selfEntity ):
		"""
		��������������߳�
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoEnterPos()
			else:
				e.cell.gotoEnterPos()
	
	def closeActivity( self, selfEntity ):
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_IS_CLOSE, "" )
			else:
				e.cell.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_IS_CLOSE, "" )
				
		selfEntity.addTimer( 15.0, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( 20.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
		selfEntity.battleData.resertPkMode()
		
	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		SpaceCopy.onTimer( self, selfEntity, id, userArg )
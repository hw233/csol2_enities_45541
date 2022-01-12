# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2008-01-28 06:08:59 kebiao Exp $

"""
"""
import time
import BigWorld
import csdefine
import csconst
from bwdebug import *
from SpaceNormal import SpaceNormal
import Const
import csstatus

class SpaceCopy( SpaceNormal ):
	"""
	����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceNormal.__init__( self )
		BigWorld.cellAppData[ self.getSpaceGlobalKey() ] = self.base

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		self.getScript().onEnter( self, baseMailbox, params )
		if self.getScript().isViewer( params ):
			self.onEnterViewer( baseMailbox, params)
		else:
			self.onEnterCommon( baseMailbox, params )
	
	def onEnterViewer( self, baseMailbox, params ):
		# �Թ۲��ߵ���ݽ��븱��
		self.getScript().onEnterViewer( self, baseMailbox, params )
		baseMailbox.cell.spaceViewerEnterState()
		self.spaceViewers.append( baseMailbox )
	
	def onEnterCommon( self, baseMailbox, params ):
		# �������ķ�ʽ���븱��
		self.getScript().onEnterCommon( self, baseMailbox, params )
		self.registerPlayer( baseMailbox, params )
		# ����PKģʽ,����ǣ������뿪��ȫ���Ƿ����PKģʽ���жϣ�
		baseMailbox.cell.lockPkMode()
		baseMailbox.cell.setTemp( "copy_space_lock_pkmode", 1 )
		#���븱��֪ͨ�ı�ս����ϵģʽ
		if self.getScript().getSpaceType() in csconst.SPACE_MAPPING_RELATION_TYPE_DICT:
			baseMailbox.cell.changeRelationMode( csconst.SPACE_MAPPING_RELATION_TYPE_DICT[ self.getScript().getSpaceType() ] )
		# ֪ͨbase����¼��ǰ�ж��ٸ���ҽ�����space�����жϵ�ǰspace�Ƿ���Ա
		self.base.onEnter( baseMailbox, params )
		# ���õײ�ӿ�
		SpaceNormal.onEnter( self, baseMailbox, params )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		if self.getScript().isViewer( params ):
			self.onLeaveViewer( baseMailbox, params)
		else:
			self.onLeaveCommon( baseMailbox, params )

	def onLeaveViewer( self, baseMailbox, params ):
		# �Թ۲��ߵ�����˳�����
		self.getScript().onLeaveViewer( self, baseMailbox, params )
		baseMailbox.cell.spaceViewerLeaveState()
		for index, mailbox in enumerate( self.spaceViewers ):
			if mailbox.id == baseMailbox.id:
				self.spaceViewers.pop( index )
				break
	
	def onLeaveCommon( self, baseMailbox, params ):
		# �������ķ�ʽ�˳�����
		self.getScript().onLeaveCommon( self, baseMailbox, params )
		self.unregisterPlayer( baseMailbox, params )
		# ����PKģʽ
		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.removeTemp( "copy_space_lock_pkmode" )
		#�뿪����֪ͨս����ϵģʽ�ı�
		if self.getScript().getSpaceType() in csconst.SPACE_MAPPING_RELATION_TYPE_DICT:
			baseMailbox.cell.changeRelationMode( csdefine.RELATION_STATIC_CAMP )
		# ֪ͨbase����¼��ǰ�ж��ٸ���ҽ�����space�����жϵ�ǰspace�Ƿ���Ա
		self.base.onLeave( baseMailbox, params )
		# ���õײ�ӿ�
		baseMailbox.client.onCloseCopySpaceInterface()
		SpaceNormal.onLeave( self, baseMailbox, params )
		
	def registerPlayer( self, baseMailbox, params = {} ): # ���ڰ��������ֹ����ռ䣬��������N���Ķ��󣬶ౣ��һ����Ϣ�����ڶԲ�ͬ����б�̣���������һ��Ĭ�ϲ���params by mushuang
		"""
		ע������space��mailbox���������
		"""
		for pMB in self._players:
			if pMB.id == baseMailbox.id:
				ERROR_MSG( "player(%i) repeat register on space.spaceName: %s, spaceID: %s."%( baseMailbox.id, self.className, self.spaceID ) )
				return
		self._players.append( baseMailbox )
		BigWorld.globalData[ "SpaceViewerMgr" ].playerEnterSpaceCopy( self.className, self.spaceID, time.time(), baseMailbox )
		
	def unregisterPlayer( self, baseMailbox, params = {} ):
		"""
		ȡ������ҵļ�¼
		"""
		BigWorld.globalData[ "SpaceViewerMgr" ].playerLeaveSpaceCopy( self.className, self.spaceID, baseMailbox )
		for i, pMB in enumerate( self._players ):
			if pMB.id == baseMailbox.id:
				self._players.pop( i )
				return
		ERROR_MSG( "unregister player(%i) fail,spaceName: %s."%( baseMailbox.id, self.className ) )
	
	def onAINotifySpaceCreated( self, className, entity ):
		"""
		define method.
		AI֪ͨNPC����
		"""
		for i, mb in enumerate( self.aiRecordMonster ):
			if mb.id == entity.id:
				ERROR_MSG( "monster(%i) repeat register on space.spaceName: %s, spaceID: %s."%( entity.id, self.className, self.spaceID ) )
				return
				
		self.aiRecordMonster.append( entity )

	def onAINotifySpaceDied( self, className, entity ):
		"""
		define method.
		AI֪ͨNPC����
		"""
		for i, mb in enumerate( self.aiRecordMonster ):
			if mb.id == entity.id:
				self.aiRecordMonster.pop( i )
				return
				
		ERROR_MSG( "unregister monster(%i) fail,spaceName: %s."%( entity.id, self.className ) )
		
	def onConditionChange( self, params ):
		"""
		define method
		���ڸ������¼��仯֪ͨ��
		�������¼��仯�����Ƕ���仯����һ�����ݵ���ɣ�Ҳ������һ����
		"""
		self.getScript().onConditionChange( self, params )


	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		�˽ӿ�����֪ͨ��ɫ���ص�ͼ��ϣ������ƶ��ˣ�����������������Ϸ���ݽ�����
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		"""
		SpaceNormal.onTeleportReady( self, baseMailbox )
		baseMailbox.client.onOpenCopySpaceInterface( self.shownDetails() )
		
	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
		]
		"""
		# Ĭ����ʾ�������������ʾ����Ҫ����Ҫ�����ⶨ��shownDetails
		return [ 0, 1, 3 ]
	
	def onDestroy( self ):
		"""
		cell ��ɾ��ʱ����
		"""
		gbKey = self.getSpaceGlobalKey()
		if BigWorld.cellAppData.has_key( gbKey ):
			del BigWorld.cellAppData[ gbKey ]
			
		SpaceNormal.onDestroy( self )

	def onTimer( self, id, userArg ):
		"""
		���ǵײ��onTimer()�������
		"""
		if userArg == Const.SPACE_COPY_CLOSE_CBID:
			self.base.closeSpace( True )
			return
		SpaceNormal.onTimer( self, id, userArg )
	
		
	def getSpaceGlobalKey( self ):
		"""
		��ȡ�������global key
		"""
		spaceType = self.getScript().getSpaceType()
		teamId = self.params['teamID'] if self.params.has_key( "teamID" ) else 0
		difficulty = self.params[ "difficulty" ] if self.params.has_key( "difficulty" ) else 0
		if Const.SPACE_COPY_GLOBAL_KEY.has_key( spaceType ):
			return Const.GET_SPACE_COPY_GLOBAL_KEY( spaceType, teamId, difficulty )
		else:
			return ""
	
	def nofityTeamDestroy( self, teamEntityID ):
		"""
		define method
		֪ͨ����ĳ�����ɢ
		"""
		self.getScript().nofityTeamDestroy( self, teamEntityID )
	
	def getPlayerNumber( self ):
		return len( self._players )
	
	def checkSpaceIsFull( self ):
		"""
		���ռ��Ƿ���Ա
		"""
		return False
	
	def onPlayerReqEnter( self, actType, playerMB, playerDBID, pos, direction ):
		"""
		define method
		�����������븱��
		"""
		if self.checkSpaceIsFull():
			playerMB.client.onStatusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_FULL, "" )
		else:
			playerMB.cell.onSpaceCopyTeleport( actType, self.className, pos, direction, not( playerDBID in self._enterRecord ) )
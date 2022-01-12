# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import Const
import ECBExtend
import random
import cschannel_msgs
from bwdebug import *
import Resource.BoardEventLoader
from config.server.ChessBoardData import Datas as g_boardData

g_boardEvent = Resource.BoardEventLoader.g_boardEventLoader()

ENTERN_DESTINY_TRANS_MENBER_DISTANCE = 30.0	# ����������Χ

class RoleDestinyTransInterface:
	"""
	 �����ֻظ����ӿ�
	 """
	def __init__( self ):
		pass

	def roleEnterDestinyTransCheck( self, reqLevel ):
		"""
		define method
		��ҽ��������ֻظ���ǰ���
		"""
		if not self.isTeamCaptain():
			# ���Ƕӳ�
			self.statusMessage( csstatus.DESTINY_TRANS_NOT_CAPTAIN )
			return
		
		if not self.teamMemberComCheck( reqLevel ):
			# �����Ա�����ж�
			return
		
		self.destinyTransSpaceEnter()
	
	def teamMemberComCheck( self, reqLevel ):
		"""
		�����Ա�����ж�
		"""
		# �����ж�
		teamMemberIDs = self.getAllIDNotInRange( ENTERN_DESTINY_TRANS_MENBER_DISTANCE )
		if len( teamMemberIDs ) > 0:
			for id in teamMemberIDs:
				self.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return False
		
		# �ȼ�����������ж�
		roleList = self.getAllMemberInRange( ENTERN_DESTINY_TRANS_MENBER_DISTANCE )
		lowLevelMembersStr = ""
		enteredMembersStr = ""
		for i in roleList:
			if i.level < reqLevel:
				lowLevelMembersStr += ( i.getName() + "," )
			if i.isActivityCanNotJoin( csdefine.ACTIVITY_DENTITY_TRANS_COM ) :
				enteredMembersStr += ( i.getName() + "," )
		
		if lowLevelMembersStr != "":
			# ���������˼��𲻹�
			self.statusMessage( csstatus.DESTINY_TRANS_LEVEL_NOT_ENOUGH, lowLevelMembersStr )
			return False
		
		if enteredMembersStr != "":
			# ���������˲μ����������Ĵ�������
			self.statusMessage( csstatus.DESTINY_TRANS_ENTER_FULL, enteredMembersStr )
			return False
		
		return True

	def destinyTransSpaceEnter( self ):
		"""
		�����������ֻظ���
		"""
		teamMemberList = self.getAllMemberInRange( ENTERN_DESTINY_TRANS_MENBER_DISTANCE )
		playerList, dbidList = [], []
		for m in teamMemberList:
			# ��ֹ�����ظ������
			if m.id not in [ e.id for e in playerList ]:
				playerList.append( m.base )
				dbidList.append( m.databaseID )
				m.set( "destityTransSpaceType", csconst.DESTINY_TRANS_COPY_COMMON )
		
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].onRequestDestinyTransCom( playerList, dbidList, self.teamMailbox.id )

	def destinyTransSpaceStart( self, chessboardNo, gateInfo, livePointInfo, destinyTransKey ):
		"""
		define method
		������������
		chessboardNo: ���̱��
		gateInfo: ��Ա�ؿ���Ϣ
		"""
		self.setTemp( "destinyTransKey", destinyTransKey )
		self.setTemp( "chessboardNo", chessboardNo )
		self.setTemp( "chessPos", gateInfo[ self.databaseID ] )
		self.setTemp( "livePoint", livePointInfo[ self.databaseID ] )
		
		self.addActivityCount( csdefine.ACTIVITY_DENTITY_TRANS_COM )
		self.setCurPosRevivePos()									# ���õ�ǰλ��Ϊ����λ�ã�����ͨ��ʧ�ܺ󱻴��͵����и����

		self.openBoardInterface( chessboardNo, gateInfo, livePointInfo )

	def openBoardInterface( self, chessboardNo, gateInfo, livePointInfo ):
		"""
		define method
		�����̽���
		"""
		INFO_MSG( "DESTRANS_LOG: %s 's current spaceType is %s, last spaceType is %s" % ( self.getNameAndID(), self.spaceType, self.queryTemp( "last_space_type", 0 ) ) )
		self.client.openBoardInterface( chessboardNo, gateInfo, livePointInfo )	# �����̽���

		if self.queryTemp( "livePoint", 0 ) < 0: # �����ҵĸ������Ϊ0�������Զ���ɸ��
			return
		
		if not gateInfo[ self.databaseID ][ 1 ] and gateInfo[ self.databaseID ][ 0 ]:	# δͨ���ҷ���㣬�����ؿ�
			INFO_MSG( "DESTRANS_LOG: %s:Gate %s has not finished yet, reEnter. BoardNo is %i " % ( self.getNameAndID(), gateInfo[ self.databaseID ], chessboardNo ) )
			self.endMoveChess( self.id )
		else:
			self.addSysThrowSieveTimer()							# ��ʼ����ʱ

	def reOpenBoardInterface( self, chessboardNo, gateInfo, livePointInfo, destinyTransKey ):
		"""
		define method
		����������´����̽���
		"""
		self.setTemp( "destinyTransKey", destinyTransKey )
		self.setTemp( "chessboardNo", chessboardNo )
		self.setTemp( "chessPos", gateInfo[ self.databaseID ] )
		self.setTemp( "livePoint", livePointInfo[ self.databaseID ] )
		
		self.openBoardInterface( chessboardNo, gateInfo, livePointInfo )

	def addSysThrowSieveTimer( self ):
		"""
		����Զ���ɸ��timer
		"""
		if self.queryTemp( "livePoint", 0 ) < 0: # �����ҵĸ������Ϊ0�������Զ���ɸ��
			return
		autoThrowTimer = self.addTimer( Const.AUTO_THROW_SIEVE_TIME, 0, ECBExtend.AUTO_THROW_SIEVE_TIMER_CBID )
		self.setTemp( "autoThrowTimer", autoThrowTimer )
		self.client.onCountDown( Const.AUTO_THROW_SIEVE_TIME )

	def onAutoThrowSieve( self, controllerID, userData ):
		"""
		�Զ���ɸ��
		"""
		point = random.randint( 1, 6 )
		self.setTemp( "SIEVE_POINT", point )
		self.client.onGetSievePoint( point )		# ֪ͨ�ͻ��˲��Ŷ���

	def throwSieve( self, srcEntityID ):
		"""
		Exposed Mehod
		�ͻ���������ɸ��
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		
		autoThrowTimer = self.queryTemp( "autoThrowTimer", 0 )
		if autoThrowTimer:
			self.cancel( autoThrowTimer )
		
		point = random.randint( 1, 6 )
		self.setTemp( "SIEVE_POINT", point )
		self.client.onGetSievePoint( point )		# ֪ͨ�ͻ��˲��Ŷ���

	def endPlaySieveAnimation( self, srcEntityID ):
		"""
		Exposed Method
		�ͻ��˲�����ɸ�Ӷ�����������ʼ�ƶ�����
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		
		point = self.queryTemp( "SIEVE_POINT", 0 )
		self.moveChess( point )

	def moveChess( self, point ):
		"""
		�ƶ�����
		"""
		oldChessPos = self.queryTemp( "chessPos", 0 )
		chessboardNo = self.queryTemp( "chessboardNo", 0 )
		if not chessboardNo:
			ERROR_MSG( "%s 's chess board number is 0 " % self.getNameAndID() )
			return
		
		chessPos = [ 0, 0 ]
		chessPos[0] = min( max( 0, oldChessPos[0] + point ), len( g_boardData[ chessboardNo ] ) - 1 )
		
		eventID = g_boardData[ chessboardNo ][ chessPos[0] ]
		event = g_boardEvent.__getitem__( eventID )
		if event.type == csdefine.CHESS_BOARD_EVE_MOVE:
			chessPos[ 1 ] = 1

		self.setTemp( "chessPos", chessPos )
		# ֪ͨ������
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].updateRoleGateInfo( self.base, self.databaseID, self.teamMailbox.id, chessPos )

	def endMoveChess( self, srcEntityID ):
		"""
		Exposed Mehod
		�ƶ����ӽ�������ʼ�����ؿ�
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		
		chessPos = self.queryTemp( "chessPos", [ 0, 0] )
		if chessPos[0] <= 0:
			self.addSysThrowSieveTimer()					# ��ʼ����ʱ
			self.client.onCountDown( Const.AUTO_THROW_SIEVE_TIME )
		else:
			self.triggerBoardEvent()

	def triggerBoardEvent( self ):
		"""
		���������¼�
		"""
		chessPos = self.queryTemp( "chessPos", [ 0, 0 ] )
		chessboardNo = self.queryTemp( "chessboardNo", 0 )
		if not chessboardNo:
			ERROR_MSG( "DESTRANS_LOG:%s 's chess board number is 0 " % self.getNameAndID() )
			return
		
		eventID = g_boardData[ chessboardNo ][ chessPos[0] ]
		event = g_boardEvent.__getitem__( eventID )
		event.do( self )

	def enterDestinyTransGate( self, eventType, eventID ):
		"""
		����ؿ�
		"""
		self.setTemp( "DESTINY_EVENT_ID", eventID )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].roleReqEnterDestinyGate( eventType, self.base )

	def getBoardEvent( self ):
		"""
		��ȡ�����¼�
		"""
		eventID = self.queryTemp( "DESTINY_EVENT_ID",0 )
		if not eventID:
			return 
		event = g_boardEvent[eventID]
		return event

	def onEnterDestinyTransGate( self ):
		"""
		define mehod
		����ؿ���
		"""
		event = self.getBoardEvent()
		if not event:
			return
		event.triggerExtraEffect( self )

	def onLeaveDestinyTransGate( self ):
		"""
		define method
		�뿪�ؿ�
		"""
		event = self.getBoardEvent()
		if not event:
			return
		event.endExtraEffect( self )

	def onPassedGate( self ):
		"""
		define method 
		��ɹؿ�
		"""
		self.onLeaveDestinyTransGate()
		self.client.desTrans_msgs( csdefine.DESTINY_TRANS_FINISH_GATE )

		chessPos = self.queryTemp( "chessPos", [ 0, 0 ] )
		chessPos[ 1 ] = 1
		self.setTemp( "chessPos", chessPos )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].onRolePassedGate( self.base, self.databaseID, self.teamMailbox.id )

	def onFailedGate( self ):
		"""
		define method
		ͨ��ʧ��
		"""
		self.onLeaveDestinyTransGate()
		self.client.desTrans_msgs( csdefine.DESTINY_TRANS_FAILED_GATE )
		self.addLivePoint( -1 )

	def addLivePoint( self, value ):
		"""
		��Ӹ���㣬������ʾ��ȥ�������
		"""
		livePoint = self.queryTemp( "livePoint", 0 ) + value
		if livePoint < -1:
			return
		self.setTemp( "livePoint", livePoint )
		BigWorld.globalData["SpaceDestinyTransMgr"].onRoleLivePointChanged( self.base, self.databaseID, self.teamMailbox.id, livePoint )

	def roleReviveCostLivePoint( self, srcEntityID ):
		"""
		Exposed Method
		��ҵ�����ť
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		autoReviveTimer = self.queryTemp( "autoReviveTimer", 0 )
		if autoReviveTimer:
			self.cancel( autoReviveTimer )
		self.reviveCostLivePoint( )

	def reviveCostLivePoint( self, controllerID = 0 , userData = "" ):
		"""
		���ĸ���㸴��(Ŀǰֻ�������ֻظ�����ʹ��)
		"""
		self.addLivePoint( -1 )
		self.tombPunish()
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.onRevive()
		self.reTriggerNearTrap()

	def onDestroy( self ):
		"""
		�������
		"""
		destinyTransKey = self.queryTemp( "destinyTransKey", "" )
		if destinyTransKey:
			BigWorld.globalData["SpaceDestinyTransMgr"].onRoleDestroy( self.base, destinyTransKey )

	def onTime_RoleRevivePreSpace( self, controllerID, userData ):
		"""
		ͨ��ʧ��,����
		"""
		self.addLivePoint( -1 )
		self.revive( self.id, csdefine.REVIVE_PRE_SPACE )

	def dt_onLeaveTeam( self ):
		"""
		��Ӵ���
		"""
		destinyTransKey = self.queryTemp( "destinyTransKey", "" )
		if destinyTransKey:
			BigWorld.globalData["SpaceDestinyTransMgr"].onRoleLeaveTeam( self.base,self.databaseID, destinyTransKey )

	def dt_onLeaveTeamCB( self ):
		"""
		define method
		��ӻص�
		"""
		self.resetDestinyTransData()

	def resetDestinyTransData( self ):
		"""
		define method
		�����������
		"""
		self.onLeaveDestinyTransGate()
		self.removeTemp( "destinyTransKey" )
		self.removeTemp( "chessboardNo" )
		self.removeTemp( "chessPos" )
		self.removeTemp( "livePoint" )
		self.removeTemp( "autoThrowTimer" )
		self.removeTemp( "autoReviveTimer" )
		self.removeTemp( "last_space_type" )
		self.removeTemp( "SIEVE_POINT" )
		self.removeTemp( "DESTINY_EVENT_ID" )
		self.remove( "destityTransSpaceType" )
		self.client.closeBoardInterface( 1 )

	def onPassedAllGate( self ):
		"""
		define method
		ͨ��
		"""
		self.resetDestinyTransData()

	def destinyTransCheck( self ):
		"""
		�������ֻظ������ͳ���ʱ����Ҫ���ݶ����Ƿ�����������̽���
		"""
		destinyTransKey = self.queryTemp( "destinyTransKey", "" )
		if destinyTransKey and self.teamMailbox:
			INFO_MSG( "DESTRANS_LOG: %s 's current spaceType is %s, last spaceType is %s" % ( self.getNameAndID(), self.spaceType, self.queryTemp( "last_space_type", 0 ) ) )
			if self.queryTemp( "last_space_type", 0 ) == csdefine.SPACE_TYPE_DESTINY_TRANS:
				self.requestOpenBoardInterface()
			else:
				self.client.closeBoardInterface( 0 )
		self.removeTemp( "last_space_type" )

	def requestOpenBoardInterface( self ):
		"""
		�ؿ�������������̽���
		"""
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].roleReqOpenBoardInterface( self.base, self.teamMailbox.id )

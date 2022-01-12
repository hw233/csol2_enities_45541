# -*- coding: gb18030 -*-

from bwdebug import *
import event.EventCenter as ECenter

class RoleDestinyTransInterface:
	"""
	 �����ֻظ����ӿ�
	 """
	def __init__( self ):
		self.livePoint = 0
	
	def openBoardInterface( self, boardNo, gateInfo, livePointInfo ):
		"""
		define method
		�����̽���
		"""
		INFO_MSG( "Open board interface, board number is %i, gateInfo is %s, livePointInfo %s " % ( boardNo, gateInfo, livePointInfo ) )
		for dbid, livePoint in livePointInfo.items():
			if self.databaseID == dbid:
				self.livePoint = livePoint
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_INTERFACE_SHOW", boardNo, gateInfo, livePointInfo )

	def onCountDown( self, time ):
		"""
		define method
		��ʼ����ʱ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_COUNTDOWN", time )
		INFO_MSG( "Start to count down, time is %i s" % time )

	def throwSieve( self ):
		"""
		��ɸ��
		"""
		self.cell.throwSieve()

	def onGetSievePoint( self, point ):
		"""
		define method
		�����ɸ�ӵ���
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_SIEVE_POINT", point )
		INFO_MSG( " Get sieve point %i from server" % point )

	def endPlaySieveAnimation(  self ):
		"""
		������ɸ�Ӷ�������
		"""
		self.cell.endPlaySieveAnimation()

	def onMoveRoleChess( self, roleID, step ):
		"""
		define method
		�ƶ�����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_MOVE_CHESS", roleID, step )
		INFO_MSG( "Move role %i chess to point %i" % ( roleID, step ) )

	def onMoveRoleChessToStart( self, roleID ):
		"""
		define method
		�ƶ����ӵ����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_MOVE_TO_START", roleID )
		INFO_MSG( "Move role %i chess to start point !" % roleID )
		
	def endMoveChess( self ):
		"""
		�ƶ����ӽ���
		"""
		self.cell.endMoveChess()

	def closeBoardInterface( self, dispose = False ):
		"""
		define method
		�ر����̽���
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_INTERFACE_CLOSE", dispose )
		INFO_MSG( " Close Board interface!! " )

	def onRoleLivePointChanged( self, dbid, livePoint ):
		"""
		define mehtod
		��Ҹ�����������仯
		"""
		if self.databaseID == dbid:
			self.livePoint = livePoint
		INFO_MSG( "Change role %i livePoint to point %i" % ( dbid, livePoint ) )
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_LIVE_POINT_CHANGED", dbid, livePoint )

	def desTrans_msgs( self, msgType ):
		"""
		define method
		��ʾ��ʾ��Ϣ
		msgType��csdefine �ж���,eg:DESTINY_TRANS_FAILED_GATE
		"""
		INFO_MSG( "Show info msg , msgType %i " % msgType )
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_DESTRANS_MSGS", msgType )
		

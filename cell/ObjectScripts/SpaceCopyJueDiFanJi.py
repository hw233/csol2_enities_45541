# -*- coding: gb18030 -*-


from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
from bwdebug import *

import BigWorld
import csdefine
import Const
import ECBExtend



PK_PROTECT_TIME = 20.0
NOTICE_PLAYER_TIME = 15.0
ROLE_NUM		= 2				#��ս�������
CLOSE_SPACE_TIME = 20.0			#��ս������رո�����ʱ��
KICK_PLAYER_TIME = 15.0			#��ս�������߳���ҵ�ʱ��
PK_TIME			 = 2 * 60		#ս��ʱ��

ROLE_PK_TIMER = 100001			#��������timer
ADVANCE_END_TIMER = 100002		#��ǰ����ս��timer
NOTICE_PLAYER_TIMER = 100003	#֪ͨ��һ���5s��Ҫ��ʼ��


VICTORY_MONEY		= 3			#ʤ����Ǯ����
DRAW_MONEY			= 2			#ƽ�ֽ�Ǯ����
FAILED_MONEY		= 1			#ʧ�ܽ�Ǯ����
VICTORY_EXP			= 3			#ʤ�����齱��
DRAW_EXP			= 2			#ƽ�־��齱��
FAILED_EXP			= 1			#ʧ�ܾ��齱��


class CCSaveProcess( CopyContent ):
	"""
	#����15s��pk����
	"""
	def __init__( self ):
		"""
		"""
		self.key = "saveProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( PK_PROTECT_TIME, 0, NEXT_CONTENT )
		spaceEntity.addTimer( NOTICE_PLAYER_TIME, 0, NOTICE_PLAYER_TIMER )


		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# ǿ��������ҽ���ϵͳ��ƽģʽ
			e.cell.lockPkMode()																# ����pkģʽ����������

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )					# ǿ��������ҽ����ƽģʽ
		baseMailbox.cell.lockPkMode()														# ����pkģʽ����������


	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.unLockPkMode()
			e.cell.setSysPKMode( 0 )
		if len( spaceEntity._players ) < ROLE_NUM:
			#�޳���ң��رո���
			if len( spaceEntity._players ) == 1:
				#�ڸ����е���һ�ʤ
				playerID = spaceEntity._players[0].id
				player = BigWorld.entities.get( playerID, None )
				if player:
					victoryDBID = 0
					failedDBID = 0
					if player.databaseID == spaceEntity.params[ "left" ]:
						victoryDBID = spaceEntity.params[ "left" ]
						failedDBID = spaceEntity.params[ "right" ]
					elif player.databaseID == spaceEntity.params[ "right" ]:
						victoryDBID = spaceEntity.params[ "right" ]
						failedDBID = spaceEntity.params[ "left" ]
					BigWorld.globalData[ "JueDiFanJiMgr" ].onAddJueDiFanJiScore( victoryDBID, failedDBID, csdefine.JUE_DI_FAN_JI_VICTORY_STATUS, player.HP )
					BigWorld.globalData[ "JueDiFanJiMgr" ].sendOfflineReward( failedDBID, csdefine.JUE_DI_FAN_JI_FAILED_STATUS )
					BigWorld.globalData[ "JueDiFanJiMgr" ].sendOnlineReward( player.base, player.databaseID, csdefine.JUE_DI_FAN_JI_VICTORY_STATUS, player.getLevel() )
					#��Ϊֻ��һ������ˣ����ߵ�������޷�֪ͨ��ͻ���ȥ��ʾ�Ƿ��뿪�ĶԻ���
			elif len( spaceEntity._players ) == 0:
				#������ҵ�ƥ���¼
				BigWorld.globalData[ "JueDiFanJiMgr" ].onClearRecord( spaceEntity.params[ "left" ] )
				BigWorld.globalData[ "JueDiFanJiMgr" ].onClearRecord( spaceEntity.params[ "right" ] )
				BigWorld.globalData[ "JueDiFanJiMgr" ].clearVictoryCountDict( spaceEntity.params[ "left" ] )
				BigWorld.globalData[ "JueDiFanJiMgr" ].clearVictoryCountDict( spaceEntity.params[ "right" ] )
			spaceEntity.getScript().doNextSeveralContent( spaceEntity, 1 )
		elif len( spaceEntity._players ) == ROLE_NUM:
			playerID1 = spaceEntity._players[0].id
			playerID2 = spaceEntity._players[1].id
			player1 = BigWorld.entities.get( playerID1, None )
			player2 = BigWorld.entities.get( playerID2, None )
			if player1 and player2:
				if player1.databaseID == spaceEntity.params[ "left" ]:
					position, direction = spaceEntity.getScript().left_playerBattlePoint
					player1.teleport( None, position, direction )
					position, direction = spaceEntity.getScript().right_playerBattlePoint
					player2.teleport( None, position, direction )
				elif player1.databaseID == spaceEntity.params[ "right" ]:
					position, direction = spaceEntity.getScript().left_playerBattlePoint
					player2.teleport( None, position, direction )
					position, direction = spaceEntity.getScript().right_playerBattlePoint
					player1.teleport( None, position, direction )
		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()				# ����pkģʽ
		baseMailbox.cell.setSysPKMode( 0 )
		
		CopyContent.onLeave( self, spaceEntity, baseMailbox, params )

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == NOTICE_PLAYER_TIMER:
			for e in spaceEntity._players:
				e.client.onJueDiFanJiCountDown( int( PK_PROTECT_TIME - NOTICE_PLAYER_TIME ) )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )


class CCPKProcess( CopyContent ):
	"""
	��ʽ�����׶�
	"""
	def __init__( self ):
		"""
		"""
		self.key = "pkProcess"
		self.val = 1

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		player = BigWorld.entities.get( baseMailbox.id, None )
		position = ( 0, 0, 0 )
		direction = ( 0, 0, 0 )
		if player:
			if player.databaseID == spaceEntity.params[ "left" ]:
				position, direction = spaceEntity.getScript().left_playerBattlePoint
			elif player.databaseID == spaceEntity.params[ "right" ]:
				position, direction = spaceEntity.getScript().right_playerBattlePoint
			player.teleport( None, position, direction )
		baseMailbox.cell.setPkMode( baseMailbox.id, csdefine.PK_CONTROL_PROTECT_NONE )		# ǿ��������ҽ���ȫ��ģʽ
		baseMailbox.cell.lockPkMode()														# ����pkģʽ����������

	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.setPkMode( e.id, csdefine.PK_CONTROL_PROTECT_NONE )						# ǿ��������ҽ���ȫ��ģʽ
			e.cell.lockPkMode()																	# ����pkģʽ����������
		timerID = spaceEntity.addTimer( PK_TIME, 0, ROLE_PK_TIMER )
		spaceEntity.setTemp( "jueDiFanJiTimer", timerID )
		
	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.unLockPkMode()													#����pkģʽ
		CopyContent.endContent( self, spaceEntity )

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == ROLE_PK_TIMER:				#��������ս������ô��ƽ�֣�ͬʱ���ϸ����ر�timer
			spaceEntity.removeTemp( "jueDiFanJiTimer" )
			if len( spaceEntity._players ) == ROLE_NUM:
				playerID1 = spaceEntity._players[0].id
				playerID2 = spaceEntity._players[1].id
				player1 = BigWorld.entities.get( playerID1, None )
				player2 = BigWorld.entities.get( playerID2, None )
				if player1 and player2:
					BigWorld.globalData[ "JueDiFanJiMgr" ].onAddJueDiFanJiScore( player1.databaseID, player2.databaseID, csdefine.JUE_DI_FAN_JI_DRAW_STATUS, -1 )
					BigWorld.globalData[ "JueDiFanJiMgr" ].sendOnlineReward( player1.base, player1.databaseID, csdefine.JUE_DI_FAN_JI_DRAW_STATUS, player1.getLevel() )
					BigWorld.globalData[ "JueDiFanJiMgr" ].sendOnlineReward( player2.base, player2.databaseID, csdefine.JUE_DI_FAN_JI_DRAW_STATUS, player2.getLevel() )
			spaceEntity.addTimer( 0.0, 0, NEXT_CONTENT)
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
			
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		if spaceEntity.queryTemp( "jueDiFanJiTimer", 0 ):
			if len( spaceEntity._players ) == 2:
				if baseMailbox.id == spaceEntity._players[0].id:
					victoryPlayerID = spaceEntity._players[1].id
					victoryPlayer = BigWorld.entities.get( victoryPlayerID, None )
					failedPlayer = BigWorld.entities.get( baseMailbox.id, None )
				else:
					victoryPlayerID = spaceEntity._players[0].id
					victoryPlayer = BigWorld.entities.get( victoryPlayerID, None )
					failedPlayer = BigWorld.entities.get( baseMailbox.id, None )
				if victoryPlayer and failedPlayer:
					BigWorld.globalData[ "JueDiFanJiMgr" ].onAddJueDiFanJiScore( victoryPlayer.databaseID, failedPlayer.databaseID, csdefine.JUE_DI_FAN_JI_VICTORY_STATUS, victoryPlayer.HP )
					BigWorld.globalData[ "JueDiFanJiMgr" ].sendOnlineReward( victoryPlayer.base, victoryPlayer.databaseID, csdefine.JUE_DI_FAN_JI_VICTORY_STATUS, victoryPlayer.getLevel() )
					BigWorld.globalData[ "JueDiFanJiMgr" ].sendOfflineReward( failedPlayer.databaseID, csdefine.JUE_DI_FAN_JI_FAILED_STATUS )
				spaceEntity.addTimer( 0.0, 0, NEXT_CONTENT)
		baseMailbox.cell.unLockPkMode()				# ����pkģʽ
		CopyContent.onLeave( self, spaceEntity, baseMailbox, params )


class CCEndProcess( CopyContent ):
	"""
	���������׶�
	"""
	def __init__( self ):
		"""
		"""
		self.key = "endProcess"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# ǿ��������ҽ���ϵͳ��ƽģʽ
			e.cell.lockPkMode()																# ����pkģʽ����������
		spaceEntity.addTimer( KICK_PLAYER_TIME, 0, Const.SPACE_TIMER_ARG_KICK )
		spaceEntity.addTimer( CLOSE_SPACE_TIME, 0, Const.SPACE_TIMER_ARG_CLOSE )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )					# ǿ��������ҽ����ƽģʽ
		baseMailbox.cell.lockPkMode()														# ����pkģʽ����������

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_KICK:
			for e in spaceEntity._players:
				e.cell.unLockPkMode()
			spaceEntity.getScript().kickAllPlayer( spaceEntity )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()				# ����pkģʽ

class SpaceCopyJueDiFanJi( SpaceCopyTemplate ) :
	"""
	���ط��������
	"""
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )
		self.isSpaceDesideDrop = True


	def initContent( self ):
		"""
		"""
		self.contents.append( CCSaveProcess() )
		self.contents.append( CCPKProcess() )
		self.contents.append( CCEndProcess() )
	
	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTemplate.load( self, section )
		data = section[ "Space" ][ "right_playerBattlePoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerBattlePoint = ( pos, direction )

		data = section[ "Space" ][ "left_playerBattlePoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerBattlePoint = ( pos, direction )
	
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )
		
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )
	
	def onRoleDie( self, role, killer ):
		"""
		virtual method.
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 3.0, 0, ECBExtend.ROLE_REVIVE_TIMER )
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			killer = BigWorld.entities.get( killer.ownerID, None )
			if killer is None:
				return
				
		spaceEntity = BigWorld.entities.get( role.getCurrentSpaceBase().id, None )
		if spaceEntity and spaceEntity.queryTemp( "jueDiFanJi_onRoleDie", 0 ):
			return
		if killer and killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			BigWorld.globalData[ "JueDiFanJiMgr" ].onAddJueDiFanJiScore( killer.databaseID, role.databaseID, csdefine.JUE_DI_FAN_JI_VICTORY_STATUS, killer.HP )
			BigWorld.globalData[ "JueDiFanJiMgr" ].sendOnlineReward( killer.base, killer.databaseID, csdefine.JUE_DI_FAN_JI_VICTORY_STATUS, killer.getLevel() )
			BigWorld.globalData[ "JueDiFanJiMgr" ].sendOnlineReward( role.base, role.databaseID, csdefine.JUE_DI_FAN_JI_FAILED_STATUS, role.getLevel() )
			spaceEntity = BigWorld.entities.get( role.getCurrentSpaceBase().id, None )
			if spaceEntity:
				spaceEntity.setTemp( "jueDiFanJi_onRoleDie", 1 )
				spaceEntity.addTimer( 0.0, 0, NEXT_CONTENT)

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		��ҽ��븱��
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.onJueDiEnter()
		if selfEntity.params.has_key( "playerHP" ) and selfEntity.params.has_key( "playerHPToDBID" ):				#����м�¼Ѫ����˵�����ѡ�������ʤ
			victoryPlayer = BigWorld.entities.get( baseMailbox.id, None )
			if victoryPlayer and victoryPlayer.databaseID == selfEntity.params[ "playerHPToDBID" ]:
				victoryPlayer.setTemp( "before_jueDiFanJi_HP", victoryPlayer.HP )
				victoryPlayer.setHP( selfEntity.params[ "playerHP" ] )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player:
			player.setTemp( "forbid_revert_hp", False )
		pass

	def doNextSeveralContent( self, selfEntity, count ):
		"""
		���н������ĵڼ�������
		"""
		index = selfEntity.queryTemp( "contentIndex", -1 )
		index += count
		selfEntity.setTemp( "contentIndex", index )
		if len( self.contents ) > index:
			self.contents[index].doContent( selfEntity )
			INFO_MSG( selfEntity.className, self.contents[index].key )
			
	def doSpecifiedContent( self, selfEntity, index ):
		"""
		���������ĳ������������
		"""
		selfEntity.setTemp( "contentIndex", index )
		if len( self.contents ) > index:
			self.contents[index].doContent( selfEntity )
			INFO_MSG( selfEntity.className, self.contents[index].key )
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		����뿪����
		"""
		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.setSysPKMode( 0 )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player:
			player.removeTemp( "forbid_revert_hp" )
			hp = player.queryTemp( "before_jueDiFanJi_HP", -1 )
			if hp != -1:
				player.setHP( hp )
				player.removeTemp( "before_jueDiFanJi_HP" )
			selectRepeatedVictory = player.queryTemp( "selectRepeatedVictory", 0)
			if not selectRepeatedVictory:
				BigWorld.globalData[ "JueDiFanJiMgr" ].clearVictoryCountDict( player.databaseID )
		baseMailbox.client.leaveJueDiFanJiSpace()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
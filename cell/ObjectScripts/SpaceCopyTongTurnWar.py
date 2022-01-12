# -*- coding: gb18030 -*-

import time
import Math
import csdefine
import csstatus
import cschannel_msgs
import ECBExtend
from bwdebug import *
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

from SpaceCopyTemplate import SpaceCopyTemplate

PROCESS_OVER_TIMER = 111
CHANGE_PK_MODEL_TIMER = 222
SKILL_ID = 860020001		# ������ID
STATE_SKILL = 860021001			# ս��״̬����ID

class CCPrepareProcess( CopyContent ):
	"""
	30��׼��ʱ��
	"""
	def __init__( self ):
		self.key = "prepareProcess"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		����ִ��
		"""
		spaceEntity.addTimer( 40, 0, NEXT_CONTENT )
		
class CCWarProcess( CopyContent ):
	"""
	�Ծֽ׶Σ�����С�֣�
	"""
	def __init__( self ):
		self.key = "warProcess"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		teamIDs = spaceEntity.queryTemp( "teamIDs", ( 0, 0 ) )
		if len( spaceEntity._players ) == 0:			# û�˽����ͽ�������
			spaceEntity.base.allWarOver( teamIDs[0], teamIDs[1], False )
			return
		
		dbids = []
		findLeftPlayer = False
		findRightPlayer = False
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				dbids.append( player.databaseID )
				if player.teamMailbox.id == teamIDs[0]:
					findLeftPlayer = True
				elif player.teamMailbox.id == teamIDs[1]:
					findRightPlayer = True
		
		# �����ǲ�����һ������û�˽���
		if not findLeftPlayer:																		# �Ҳ��������ң��Ҷ�ֱ�ӻ�ʤ
			spaceEntity.base.allWarOver( teamIDs[0], teamIDs[1], True )
			return
		if not findRightPlayer:																		# �Ҳ����Ҷ���ң����ֱ�ӻ�ʤ
			spaceEntity.base.allWarOver( teamIDs[1], teamIDs[0], True )
			return
		
		# �����ǲ����׾ֵ����û�н���
		if currentFightPlayer[0] not in dbids:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[0] )
			return
		if currentFightPlayer[1] not in dbids:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[1] )
			return
			
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				if player.databaseID in currentFightPlayer:
					player.client.turnWar_showPrepareTime( 3 )
					player.spellTarget( SKILL_ID, player.id )
		
		spaceEntity.addTimer( 3, 0, CHANGE_PK_MODEL_TIMER )		# һ��ʱ���ı�PKģʽΪ���ģʽ
			
		spaceEntity.setTemp( "processOverTimer", spaceEntity.addTimer( 3 * 60, 0, PROCESS_OVER_TIMER ) )
		
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ�뿪
		"""
		# �뿪�������Է������ʤ
		losePlayer = BigWorld.entities.get( baseMailbox.id )
		if not losePlayer:
			return
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		if params["databaseID"] in currentFightPlayer:				# ���ڶԾֵ�����뿪
			teamIDs = spaceEntity.queryTemp( "teamIDs", ( 0, 0 ) )
			if params["databaseID"] == currentFightPlayer[0]:
				teamID = teamIDs[0]
				anotherPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[1] )
				if anotherPlayer:
					spaceEntity.revert_HpMp( anotherPlayer )
			else:
				teamID = teamIDs[1]
				anotherPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[0] )
				if anotherPlayer:
					spaceEntity.revert_HpMp( anotherPlayer )
					
			spaceEntity.base.onPlayerLeave( params["databaseID"] )
			self.oneWarOver( spaceEntity )
		
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == PROCESS_OVER_TIMER:
			self.onWarTimeOver( spaceEntity )
		if userArg == CHANGE_PK_MODEL_TIMER:
			for e in spaceEntity._players:
				player = BigWorld.entities.get( e.id )
				if player:
					currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
					if player.databaseID in currentFightPlayer:
						player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
						if not player.queryTemp( "turnWar_isFightPlayer", False ):						# ���ϳ������Ҫ��ս��״̬buff
							player.setTemp( "turnWar_isFightPlayer", True )
							player.spellTarget( STATE_SKILL, player.id )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
		
	def onWarTimeOver( self, spaceEntity ):
		"""
		һ��ʱ�䵽
		"""
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		player1 = self.findPlayerByDBID( spaceEntity, currentFightPlayer[0] )
		player2 = self.findPlayerByDBID( spaceEntity, currentFightPlayer[1] )
		if not player1 or not player2:
			ERROR_MSG( "SpaceTongTurnWar(%i) can't find player when one war time over!"%spaceEntity.id )
			return
		if player1.HP > player2.HP:
			spaceEntity.base.onPlayerWin( player2.databaseID, player2.teamMailbox.id, player2.base )
			spaceEntity.revert_HpMp( player1 )
		elif player1.HP < player2.HP:
			spaceEntity.base.onPlayerWin( player1.databaseID, player1.teamMailbox.id, player1.base )
			spaceEntity.revert_HpMp( player2 )
		else:			# ƽ��
			spaceEntity.base.onBothPlayerLoseOrLeave( True, [ player1.base, player2.base ] )
		
		self.oneWarOver( spaceEntity )
	
	def startNextWar( self, spaceEntity ):
		"""
		��ʼ��һ�ֶԾ�
		"""
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		leftPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[0] )
		rightPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[1] )
		
		# һ�󴮵��жϣ�Ϊ�˱�֤������ս��Ҷ��ڸ�����
		if not leftPlayer and not rightPlayer:
			spaceEntity.base.onBothPlayerLoseOrLeave( False, [] )
			return
		elif not leftPlayer:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[0] )
			return
		elif not rightPlayer:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[1] )
			return
		
		leftPlayer.changePosition( Math.Vector3( spaceEntity.getScript().left_fightPoint ) )	# �仯λ�õ����ս��
		leftPlayer.client.turnWar_showPrepareTime( 3 )
		leftPlayer.spellTarget( SKILL_ID, leftPlayer.id )
		
		rightPlayer.changePosition( Math.Vector3( spaceEntity.getScript().right_fightPoint ) ) 	# �仯λ�õ��ҳ�ս��
		rightPlayer.client.turnWar_showPrepareTime( 3 )
		rightPlayer.spellTarget( SKILL_ID, rightPlayer.id )
		
		spaceEntity.setTemp( "processOverTimer", spaceEntity.addTimer( 3 * 60, 0, PROCESS_OVER_TIMER ) )
		spaceEntity.addTimer( 3, 0, CHANGE_PK_MODEL_TIMER )		# һ��ʱ���ı�PKģʽΪ���ģʽ
	
	def findPlayerByDBID( self, spaceEntity, dbID ):
		"""
		����dbid�Ҹ������
		"""
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if not player:
				return None
			if player.databaseID == dbID:
				return player
		return None
			
	def onActivityOver( self, spaceEntity ):
		"""
		�ʱ�����
		"""
		player1 = None
		player2 = None
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		for e in spaceEntity._players:
			player = BigWorld.entities.get(e.id)
			if not player:
				return
			if player.databaseID == currentFightPlayer[0]:
				player1 = player
			elif player.databaseID == currentFightPlayer[1]:
				player2 = player
		
		if player1 and player2:
			if player1.HP > player2.HP:
				spaceEntity.base.resultOnActivityOver( player2.teamMailbox.id, player1.teamMailbox.id )
			elif player1.HP < player2.HP:
				spaceEntity.base.resultOnActivityOver( player1.teamMailbox.id, player2.teamMailbox.id )
			else:			# ƽ��
				spaceEntity.base.resultOnActivityOver( None, None )
		else:
			spaceEntity.getScript().onConditionChange( spaceEntity, {} )
	
	def endContent( self, spaceEntity ):
		if spaceEntity.queryTemp( "processOverTimer", None):
			spaceEntity.cancel( spaceEntity.popTemp( "processOverTimer") )
		CopyContent.endContent( self, spaceEntity )
	
	def oneWarOver( self, spaceEntity ):
		if spaceEntity.queryTemp( "processOverTimer", None):
			spaceEntity.cancel( spaceEntity.popTemp( "processOverTimer") )
		
class CCShowRestTime( CopyContent ):
	"""
	��ʾ10���ӵ���ʱ
	"""
	def __init__( self ):
		self.key = "showRestTime"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
		for e in spaceEntity._players:
			e.client.turnWar_showTelportTime( 10 )
	
class SpaceCopyTongTurnWar( SpaceCopyTemplate ):
	"""
	��ᳵ��ս�ռ�
	"""
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		
	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTemplate.load( self, section )
		
		spaceData = section[ "Space" ]
		# ����1����λ��
		self.left_watchPoint = tuple( [ float(x) for x in spaceData[ "leftTeam_watchPoint" ].asString.split() ] )
		self.left_fightPoint = tuple( [ float(x) for x in spaceData[ "leftTeam_fightPoint" ].asString.split() ] )
		
		# ����2����λ��
		self.right_watchPoint = tuple( [ float(x) for x in spaceData[ "rightTeam_watchPoint" ].asString.split() ] )
		self.right_fightPoint = tuple( [ float(x) for x in spaceData[ "rightTeam_fightPoint" ].asString.split() ] )
		
		# ս�ܹ�ս��
		self.loser_watchPoint = tuple( [ float(x) for x in spaceData[ "loser_watchPoint" ].asString.split() ] )
		
	def initContent( self ):
		"""
		"""
		self.contents.append( CCPrepareProcess() )
		self.contents.append( CCWarProcess() )
		self.contents.append( CCShowRestTime() )
		self.contents.append( CCKickPlayersProcess() )
		
	def packedDomainData( self, player ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { "teamID" : player.teamMailbox.id, "databaseID": player.databaseID, "spaceKey" : player.teamMailbox.id }
	
	def packedSpaceDataOnEnter( self, player ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		dict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			dict["teamID"] = player.teamMailbox.id
		return dict
		
	def packedSpaceDataOnLeave( self, player ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, player )
		packDict[ "isWatchState" ] = player.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		packDict["databaseID"] = player.databaseID
		return packDict
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.setTemp( "forbid_revert_hp", False)
			player.setTemp( "forbid_revert_mp", False)
			player.lockPkMode()
			player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# ����ս
		
			currentFightPlayer = selfEntity.queryTemp( "currentFightPlayer", (0,0) )
			if player.databaseID in selfEntity.queryTemp( "losedPlayer", [] ):			# ��ս�ܣ�����ս�ܹ�ս��
				player.changePosition( Math.Vector3( self.loser_watchPoint ) )
			elif player.databaseID in currentFightPlayer:								# ����ǵ�ǰ������ң�����
				player.setTemp( "turnWar_isFightPlayer", True )
				player.spellTarget( STATE_SKILL, player.id )							# ��ս��״̬��Buff������һ�䲻�ܽ���˳�򣬷������buff�������Ƴ�
			else:																		# ���򴫵��ȴ���
				teamIDs = selfEntity.queryTemp( "teamIDs", ( 0, 0 ) )
				if params["teamID"] == teamIDs[0]:																	# �Լ�������Ӵ������ս��
					player.changePosition( Math.Vector3( self.left_watchPoint ) )
				else:																								# �Լ������ҶӴ����ҹ�ս��
					player.changePosition( Math.Vector3( self.right_watchPoint ) )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		isWatchState = params[ "isWatchState" ]
		if isWatchState:
			baseMailbox.cell.onLeaveWatchMode()
		
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.unLockPkMode()
			player.setSysPKMode( 0 )
			player.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )			# ����ս
			player.removeTemp( "turnWar_isFightPlayer" )
			player.removeTemp( "forbid_revert_hp" )
			player.removeTemp( "forbid_revert_mp" )
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 3, 0, ECBExtend.ROLE_REVIVE_TIMER )
		role.getCurrentSpaceBase().onPlayerWin( role.databaseID, role.teamMailbox.id, role.base )
		
		spaceEntity = BigWorld.entities.get( role.getCurrentSpaceBase().id )
		if spaceEntity:
			spaceEntity.revert_HpMp( killer )
			currentContent = self.getCurrentContent( spaceEntity )
			if currentContent.key == "warProcess":
				currentContent.oneWarOver( spaceEntity )
	
	def startNextWar( self, spaceEntity ):
		"""
		��ʼ��һ�Ծ�
		"""
		currentContent = self.getCurrentContent( spaceEntity )
		currentContent.startNextWar( spaceEntity )
		
	def allWarOver( self, spaceEntity ):
		"""
		���жԾֽ���
		"""
		currentContent = self.getCurrentContent( spaceEntity )
		if currentContent.key == "warProcess":
			self.onConditionChange( spaceEntity, {} )
	
	def onActivityOver( self, spaceEntity ):
		currentContent = self.getCurrentContent( spaceEntity )
		if currentContent.key == "warProcess":
			currentContent.onActivityOver( spaceEntity )
			
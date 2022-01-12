# -*- coding: gb18030 -*-

# ����һ�ű�

import time
import Math
import random
import csdefine
import csstatus
import cschannel_msgs
import ECBExtend
from bwdebug import *
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate

START_TIMER = 111
CHANGE_PK_MODEL_TIMER = 222

STATE_SKILL = 860021001			# ս��״̬����ID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP

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
		spaceEntity.setTemp( "beforeStartWar", True )
		
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
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		
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
		for dbid in currentFightPlayer[0]:
			if dbid not in dbids:
				spaceEntity.base.onPlayerLeave( dbid )
		for dbid in currentFightPlayer[1]:
			if dbid not in dbids:
				spaceEntity.base.onPlayerLeave( dbid )
		
		spaceEntity.addTimer( 3, 0, START_TIMER )
	
	def startWar( self, spaceEntity ):
		"""
		��ʽ��ս
		"""
		spaceEntity.removeTemp( "beforeStartWar" )
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		
		fightPlayers = []
		for i in currentFightPlayer[0]:
			fightPlayers.append( i )
		for i in currentFightPlayer[1]:
			fightPlayers.append( i )
			
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				if player.databaseID in fightPlayers:
					player.client.turnWar_showPrepareTime( 3 )
		
		spaceEntity.addTimer( 3, 0, CHANGE_PK_MODEL_TIMER )		# һ��ʱ���ı�PKģʽΪ���ģʽ
		
	def telportPlayer( self, spaceEntity, playerDBID, position ):
		"""
		������ҵ���ս��
		"""
		player = self.findPlayerByDBID( spaceEntity, playerDBID )
		if player:
			player.changePosAndDir( position, Math.Vector3( spaceEntity.getScript().centerPoint ) )
			if spaceEntity.queryTemp( "beforeStartWar", False ) and not player.popTemp( "isFixed"):		# ��δ��ʼ��ս
				player.actCounterInc( STATES )
				player.setTemp( "isFixed", True )
			else:
				player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
				player.setTemp( "turnWar_isFightPlayer", True )
				player.spellTarget( STATE_SKILL, player.id )
		else:
			spaceEntity.base.onPlayerLeave( playerDBID )
		
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ�뿪
		"""
		# �뿪�������Է������ʤ
		losePlayer = BigWorld.entities.get( baseMailbox.id )
		if not losePlayer:
			return
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		if params["databaseID"] in currentFightPlayer[0] or params["databaseID"] in currentFightPlayer[1]:				# ���ڶԾֵ�����뿪
			spaceEntity.base.onPlayerLeave( params["databaseID"] )
		
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == START_TIMER:
			self.startWar( spaceEntity )
		elif userArg == CHANGE_PK_MODEL_TIMER:
			for e in spaceEntity._players:
				player = BigWorld.entities.get( e.id )
				if player:
					if player.popTemp( "isFixed" ):
						player.actCounterDec( STATES )			# �Ƴ�����
					currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
					if player.databaseID in currentFightPlayer[0] or player.databaseID in currentFightPlayer[1]:
						player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
						if not player.queryTemp( "turnWar_isFightPlayer", False ):						# ���ϳ������Ҫ��ս��״̬buff
							player.setTemp( "turnWar_isFightPlayer", True )
							player.spellTarget( STATE_SKILL, player.id )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
	
	def findPlayerByDBID( self, spaceEntity, dbID ):
		"""
		����dbid�Ҹ������
		"""
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if not player:
				continue
			if player.databaseID == dbID:
				return player
		return None
			
	def onActivityOver( self, spaceEntity ):
		"""
		�ʱ�����
		"""
		player1 = None
		player2 = None
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		for e in spaceEntity._players:
			player = BigWorld.entities.get(e.id)
			if not player:
				return
			if player.databaseID in currentFightPlayer[0]:
				player1 = player
			elif player.databaseID in currentFightPlayer[1]:
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
	
class SpaceCopyTongTurnWar_FS( SpaceCopyTeamTemplate ):
	"""
	��ᳵ��ս�ռ�
	"""
	def __init__( self ):
		SpaceCopyTeamTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		
	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeamTemplate.load( self, section )
		
		spaceData = section[ "Space" ]
		# ����1����λ��
		self.left_watchPoint = eval( spaceData[ "leftTeam_watchPoint" ].asString )
		#self.left_watchDirection = tuple( [ float(x) for x in spaceData[ "leftTeam_watchPoint" ]["position"].asString.split() ] )
		self.left_fightPoint = eval( spaceData[ "leftTeam_fightPoint" ].asString )
		
		# ����2����λ��
		self.right_watchPoint = eval( spaceData[ "rightTeam_watchPoint" ].asString )
		self.right_fightPoint = eval( spaceData[ "rightTeam_fightPoint" ].asString )
		
		# ս�ܹ�ս��
		self.loser_watchPoint = eval( spaceData[ "loser_watchPoint" ].asString )
		self.centerPoint = eval( spaceData[ "centerPoint" ].asString )
		
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
		return { "teamID" : player.teamMailbox.id, "databaseID": player.databaseID ,"spaceKey": player.teamMailbox.id}
	
	def packedSpaceDataOnEnter( self, player ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		dict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			dict["teamID"] = player.teamMailbox.id
		return dict
		
	def packedSpaceDataOnLeave( self, player ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnLeave( self, player )
		packDict[ "isWatchState" ] = player.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		packDict["databaseID"] = player.databaseID
		return packDict
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.reduce_role_damage_extra += 6000
			player.calcReduceRoleDamage()
			player.HP_Max *= 2							# Ѫ�����޷���
			player.addHP( player.HP_Max - player.HP )
			player.addHP( player.MP_Max - player.MP )
			
			player.setTemp( "forbid_revert_hp", False)
			player.lockPkMode()
			player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# ����ս
		
			currentFightPlayer = selfEntity.queryTemp( "currentFightPlayer", ([],[]) )
			if player.databaseID in selfEntity.queryTemp( "losedPlayer", [] ):			# ��ս�ܣ�����ս�ܹ�ս��
				player.changePosAndDir( Math.Vector3( self.loser_watchPoint ), Math.Vector3( self.centerPoint ) )
			elif player.databaseID in currentFightPlayer[0] or player.databaseID in currentFightPlayer[1]:								# ����ǵ�ǰ�������
				player.changePosAndDir( self.randomPosition( player ), Math.Vector3( self.centerPoint ) )			# ���ɢ�������⿪ʼ��ʱ�����һ��
				player.setTemp( "turnWar_isFightPlayer", True )
				player.spellTarget( STATE_SKILL, player.id )							# ��ս��״̬��Buff������һ�䲻�ܽ���˳�򣬷������buff�������Ƴ�
				if selfEntity.queryTemp( "beforeStartWar", False ) and not player.popTemp( "isFixed"):
					player.actCounterInc( STATES )											# ��Ӷ���
					player.setTemp( "isFixed", True )
			else:																		# ���򴫵��ȴ���
				teamIDs = selfEntity.queryTemp( "teamIDs", ( 0, 0 ) )
				if params["teamID"] == teamIDs[0]:																	# �Լ�������Ӵ������ս��
					player.changePosAndDir( Math.Vector3( self.left_watchPoint ), Math.Vector3( self.centerPoint ) )
				else:																								# �Լ������ҶӴ����ҹ�ս��
					player.changePosAndDir( Math.Vector3( self.right_watchPoint ), Math.Vector3( self.centerPoint ) )
	
	def randomPosition( self, player ):
		"""
		
		"""
		pos = Math.Vector3( player.position )
		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
		return pos
		
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		isWatchState = params[ "isWatchState" ]
		if isWatchState:
			baseMailbox.cell.onLeaveWatchMode()
		
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.reduce_role_damage_extra -= 6000
			player.calcReduceRoleDamage()
			player.calcHPMax()
			
			player.unLockPkMode()
			player.setSysPKMode( 0 )
			player.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )			# ����ս
			player.removeTemp( "turnWar_isFightPlayer" )
			player.removeTemp( "forbid_revert_hp" )
			currentFightPlayer = selfEntity.queryTemp( "currentFightPlayer", ([],[]) )
			if player.popTemp( "isFixed"):
				player.actCounterDec( STATES )			# �Ƴ�����
		SpaceCopyTeamTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 3, 0, ECBExtend.ROLE_REVIVE_TIMER )
		role.getCurrentSpaceBase().onPlayerWin( role.databaseID, role.teamMailbox.id, role.base, killer.databaseID )
		
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
			
	def telportPlayer( self, spaceEntity, playerDBID, position ):
		"""
		������ҵ���ս��
		"""
		currentContent = self.getCurrentContent( spaceEntity )
		if currentContent.key == "warProcess":
			currentContent.telportPlayer( spaceEntity, playerDBID, position )
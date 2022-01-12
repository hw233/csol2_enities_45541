# -*- coding: gb18030 -*-

import re
import csdefine
import Const
import csstatus
from bwdebug import *
from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

BATTLE_PREPARE_TIME				 = 60 * 2
WAIT_BATTLE_FIELD_RESET_TIME	 = 60 * 3
KICK_PLAYER_TIME				 = 30
BATTLE_FIELD_RESET_TIME			 = 60
BASE_ON_OCCUPIED_NOTICE_TIMES	 = 3

PRE_CONTENT					 = 20140213
BATTLE_FIELD_RESET			 = 20140214
KICK_PLAYER_TIMER			 = 20140215
STATUS_MESSAGE_TIMER		 = 20140224

# ����λ��
DEFEND_TONG_ENTER_POS			= 1		# ���������
DEFEND_LEAGUES_ENTER_POS		= 2		# �������˴����
ATTACK_TONG_ENTER_POS			= 3		# �ط������
ATTACK_LEFT_LEAGUES_ENTER_POS	= 4		# �ط�����1�����
ATTACK_RIGHT_LEAGUES_ENTER_POS	= 5		# �ط�����2�����

class CCPrepareProcess( CopyContent ):
	"""
	2����׼��ʱ��
	"""
	def __init__( self ):
		self.key = "prepareProcess"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		����ִ��
		"""
		spaceEntity.addTimer( BATTLE_PREPARE_TIME, 0, NEXT_CONTENT )
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )

	def endContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.destroyLightWall( )
		CopyContent.endContent( self, spaceEntity )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ����
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )			# ǿ��������ҽ����ƽģʽ

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ�뿪
		"""
		baseMailbox.cell.setSysPKMode( 0 )

class CCCombatProcess( CopyContent ):
	"""
	ս��ʱ��
	"""
	def __init__( self ):
		self.key = "combatProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		����ִ��
		"""
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_LEAGUE )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ����
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_LEAGUE )			# ǿ��������ҽ�������ģʽ

	def onConditionChange( self, spaceEntity, params ):
		"""
		һ�����������仯��֪ͨ����
		"""
		spaceEntity.resetTimer =  spaceEntity.addTimer( WAIT_BATTLE_FIELD_RESET_TIME, 0, BATTLE_FIELD_RESET )

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		CopyContent.onTimer( self, spaceEntity, id, userArg )
		if userArg == BATTLE_FIELD_RESET:
			spaceEntity.cancel(  spaceEntity.resetTimer )
			spaceEntity.resetTimer = 0
			self.onBattleFieldResetTimer( spaceEntity )

	def onBattleFieldResetTimer( self, spaceEntity ):
		"""
		ս������timer
		"""
		belong = spaceEntity.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_HEROMONU ][0].values()[ 0 ]
		if belong != csdefine.CITY_WAR_FINAL_FACTION_DEFEND:
			self.endContent( spaceEntity )

class CCBattleFieldReset( CopyContent ):
	"""
	ս������
	"""
	def __init__( self ):
		self.key = "battleFieldReset"
		self.val = 1

	def beginContent( self, spaceEntity ):
		"""
		���ݿ�ʼ
		���ս������Timer
		"""
		spaceEntity.addTimer( BATTLE_FIELD_RESET_TIME, 0, PRE_CONTENT )

	def onContent( self, spaceEntity ):
		"""
		����ִ��
		֪ͨ����ս������
		"""
		spaceEntity.setTemp( "BATTLE_FIELD_RESET", True )	# ֹͣ�������
		spaceEntity.battleFieldReset()
		spaceEntity.spawnLightWall()

	def endContent( self, spaceEntity ):
		"""
		���ݽ���,ִ����һ������
		"""
		spaceEntity.destroyLightWall()
		spaceEntity.removeTemp( "BATTLE_FIELD_RESET" )
		spaceEntity.getScript().doPreContent( spaceEntity )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ����
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_LEAGUE )			# ǿ��������ҽ�������ģʽ

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		CopyContent.onTimer( self, spaceEntity, id, userArg )
		if userArg == PRE_CONTENT:
			self.endContent( spaceEntity )

class SpaceCopyCityWarFinal( SpaceCopyTemplate ):
	"""
	�����ս����
	"""
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )

	def initContent( self ):
		"""
		"""
		self.contents.append( CCPrepareProcess() )
		self.contents.append( CCCombatProcess() )
		self.contents.append( CCBattleFieldReset() )
		self.contents.append( CCKickPlayersProcess() )

	def load( self, section ):
		"""
		�������м�������
		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTemplate.load( self, section )
		
		spaceData = section[ "Space" ]
		
		# �سǰ�����λ��
		defend_tong_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["defend_tong_enterPos"].asString ) )
		defend_league_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["defend_league_enterPos"].asString ) )
		
		# ���ǰ�����λ��
		attack_tong_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_tong_enterPos"].asString ) )
		attack_leftLeague_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_leftLeague_enterPos"].asString ) )
		attack_rightLeague_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_rightLeague_enterPos"].asString ) )
		
		self.enterPosMapping = { 1: defend_tong_enterPos,
								 2: defend_league_enterPos,
								 3: attack_tong_enterPos,
								 4: attack_leftLeague_enterPos,
								 5: attack_rightLeague_enterPos,
								}

	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		"""
		dict = {}
		dict[ "tongDBID" ] = entity.tong_dbID
		dict[ "camp" ] = entity.getCamp()
		dict[ "roleDBID" ] = entity.databaseID
		dict[ "roleName" ] = entity.getName()
		dict[ "spaceName" ] = entity.spaceType
		return dict

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "roleDBID" ] = entity.databaseID
		packDict[ "roleName" ] = entity.getName()
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "roleName" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		belong = selfEntity.getTongBelong( tongDBID )
		self.setRoleBelong( baseMailbox, belong )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onLeaveCityWarSpace()
		baseMailbox.cell.setSysPKMode( 0 )										# ���Ĭ��sysPKMode

	def setRoleBelong( self, baseMailbox, belong ):
		"""
		������ҹ���
		"""
		baseMailbox.cell.setTemp( "CITY_WAR_FINAL_BELONG", belong )

	def resetTongInfos( self, selfEntity ):
		"""
		���ò�ս�����Ϣ
		"""
		newTongInfos = {}
		newTongInfos[ "defend" ] = {}			# �سǷ�
		newTongInfos[ "attack"] = {}			# ���Ƿ�
		
		for key, item in selfEntity.tongInfos.iteritems():
			# �سǷ�����Ϊ���Ƿ�
			if key == "defend":
				for tongDBID in item.keys():
					maxNum = item[ tongDBID ][ "maxNum" ]
					if tongDBID == selfEntity.attack:
						enterPos = ATTACK_TONG_ENTER_POS
					else:
						enterPos = ATTACK_LEFT_LEAGUES_ENTER_POS
					newTongInfos[ "attack"][ tongDBID ] = { "maxNum": maxNum, "enterPos":  enterPos }
			# ���Ƿ�����سǷ�
			elif key == "attack":
				for tongDBID in item.keys():
					maxNum = item[ tongDBID ][ "maxNum"]
					if tongDBID == selfEntity.defend:
						enterPos = DEFEND_TONG_ENTER_POS
					else:
						enterPos = DEFEND_LEAGUES_ENTER_POS
					newTongInfos[ "defend" ][ tongDBID ] = { "maxNum": maxNum, "enterPos": enterPos }
		selfEntity.tongInfos = newTongInfos

	def getTongBasePos( self, selfEntity, tongDBID ):
		"""
		��ð��Ĵ�Ӫλ��
		"""
		for key, item in selfEntity.tongInfos.iteritems():
			for dbid in item.keys():
				if dbid == tongDBID:
					enterPosNo = item[ dbid ]["enterPos"]
					break
		enterPos = self.enterPosMapping[ enterPosNo ]
		pos, dir = enterPos[ :3 ], enterPos[ 3 :]
		return pos, dir

	def teleportPlayerToBelongBase( self, selfEntity ):
		"""
		ս������ʱ��������Ҵ��͵�������Ӫ
		"""
		for tongDBID, info in selfEntity.warInfos.infos.iteritems():
			belong = selfEntity.getTongBelong( tongDBID )
			pos, dir = self.getTongBasePos( selfEntity, tongDBID )
			for roleDBID, member in info.members.iteritems():
				roleMB = member.mailBox
				self.setRoleBelong( roleMB, belong )
				
				role = BigWorld.entities.get( roleMB.id )
				if role:
					role.teleportToSpace( pos, dir, selfEntity, selfEntity.spaceID )
				else:
					role.cell.teleportToSpace( pos, dir, selfEntity, selfEntity.spaceID )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.
		ĳrole�ڸø���������
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Role %i kill a enemy." % role.id )
		if not killer:		# �Ҳ���ɱ���ߣ�����
			return

		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				return
			killer = owner.entity

		if killer.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.belong, 0, role.tong_dbID, role.databaseID )
		else:
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.tong_dbID, killer.databaseID, role.tong_dbID, role.databaseID )

	def onRoleRelive( self, selfEntity, mailbox, tongDBID ):
		"""
		ս������
		"""
		pos, dir = self.getTongBasePos( selfEntity, tongDBID )
		mailbox.cell.tong_onCityWarFinalReliveCB( pos, dir, selfEntity, selfEntity.spaceID )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		���ǵײ��onTimer()�������
		"""
		SpaceCopyTemplate.onTimer( self, selfEntity, id, userArg )
		if userArg == KICK_PLAYER_TIMER:
			self.doLastContent( selfEntity )
		elif userArg == STATUS_MESSAGE_TIMER:
			self.onTimerStatusMessage( selfEntity, id )

	def closeSpace( self, selfEntity ):
		"""
		�رո���( ִ������޳���ҵĲ��� )
		"""
		selfEntity.addTimer( KICK_PLAYER_TIME, 0, KICK_PLAYER_TIMER )
		self.statusMessageAllPlayer( selfEntity, csstatus.TONG_CITY_WAR_FINAL_KICK_PLAYER, str( ( 30, ) ) )

	def doPreContent( self, selfEntity ):
		"""
		ִ����һ���׶�
		"""
		index = selfEntity.queryTemp( "contentIndex", -1 )
		index -= 1
		selfEntity.setTemp( "contentIndex", index )
		if len( self.contents ) > index:
			self.contents[index].doContent( selfEntity )
			INFO_MSG( "TONG_CITY_WAR_FINAL: Space %s begin to do content %s " % ( selfEntity.className, self.contents[index].key ) )

	def doLastContent( self, selfEntity ):
		"""
		ִ�����Ľ׶�
		"""
		index = len( self.contents ) -1
		selfEntity.setTemp( "contentIndex", index  )
		self.contents[index].doContent( selfEntity )

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		֪ͨ������ ָ������Ϣ( ÿ��10����ʾһ�Σ���3�� )
		"""
		isFind = False
		for msg in selfEntity.msgs:
			if msg[ "msgKey" ] == ( msgKey, args ):
				isFind = True
				msg[ "times" ] += 1
				if msg[ "times" ] > BASE_ON_OCCUPIED_NOTICE_TIMES:		# �����Ѿ���ʾ�Ĵ���
					selfEntity.msgs.remove( msg ) 
					return
				msg[ "timerID" ] = selfEntity.addTimer( 10, 0, STATUS_MESSAGE_TIMER )
				break
		
		if not isFind:
			dict = {}
			dict[ "msgKey" ] = ( msgKey, args )
			dict[ "times" ] = 1
			dict[ "timerID" ] = selfEntity.addTimer( 10, 0, STATUS_MESSAGE_TIMER )
			selfEntity.msgs.append( dict )
		
		for e in selfEntity._players:
			e.client.onStatusMessage( msgKey, *args )

	def onTimerStatusMessage( self, selfEntity, id ):
		"""
		Timer֪ͨ������ʾ��Ϣ
		"""
		for msg in selfEntity.msgs:
			if msg[ "timerID" ] == id:
				msgKey = msg[ "msgKey"]
				self.statusMessageAllPlayer( selfEntity, msgKey[0], *msgKey[1] ) 
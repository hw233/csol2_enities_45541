# -*- coding: gb18030 -*-

# Ӣ������
import time
import random
import BigWorld

import csconst
import csdefine
import csstatus
from bwdebug import *
import random
import ECBExtend

from CopyContent import *

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
from GameObjectFactory import g_objFactory
import time

PLAYER_SOLDIER_MONSTER_TYPE = 11			# ���С��
NPC_SOLDIER_MONSTER_TYPE = 22			# NPCС��
ELITE_MONSTER_TYPE = 1					# ��Ӣ

SPAWN_ELITE_1	=	111
SPAWN_ELITE_2	=	222
SPAWN_ELITE_3	=	333

SPACE_LAST_TIME = 1800

class CCAttackBase( CopyContent ):
	"""
	��������
	"""
	def __init__( self ):
		self.key = "attckBase"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( SPACE_LAST_TIME, 0, NEXT_CONTENT )					# 30���Ӻ󸱱��ر�
		spaceEntity.addTimer( 3 * 60, 0, SPAWN_ELITE_1 )
		spaceEntity.addTimer( 6 * 60, 0, SPAWN_ELITE_2 )
		spaceEntity.addTimer( 9 * 60, 0, SPAWN_ELITE_3 )
	
	def doConditionChange( self, spaceEntity, params ):
		"""
		�����ı�֪ͨ
		"""
		CopyContent.doConditionChange( self, spaceEntity, params )
		if params.has_key( "spawnPlayerSoldier" ):											# ˢ��ҵ�С��
			spaceEntity.base.spawnMonsters( {"monsterType":  PLAYER_SOLDIER_MONSTER_TYPE, "level": spaceEntity.teamLevel } )
		if params.has_key( "spawnNPCSoldier" ):												# ˢNPC��С��
			spaceEntity.base.spawnMonsters( {"monsterType":  NPC_SOLDIER_MONSTER_TYPE, "level": spaceEntity.teamLevel } )
		if params.has_key( "playerBaseIsKilled" ):
			spaceEntity.addTimer( 60, 0, NEXT_CONTENT )		# ��һ��ر����ƣ���ǰ��������,5���Ӻ���ұ���������
			self.givePlayerReward( spaceEntity, False )		# ���������������
		if params.has_key( "monsterBaseIsKilled" ):
			spaceEntity.addTimer( 60, 0, NEXT_CONTENT )		# ������ر����ƣ���ǰ��������
			self.givePlayerReward( spaceEntity, True )		# ������һ�ʤ����
		if params.has_key( "reason" ) and params["reason"] == "timeOver":
			return True
		return False
	
	def givePlayerReward( self, spaceEntity, isWin ):
		"""
		������
		@param isWin : ����Ƿ�ʤ��
		@param Type : bool
		"""
		if isWin:
			for e in spaceEntity._players:
				if BigWorld.entities.has_key( e.id ):
					print" give win reward"
		else:
			for e in spaceEntity._players:
				if BigWorld.entities.has_key( e.id ):
					print" give lose reward"
	
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == SPAWN_ELITE_1 or userArg == SPAWN_ELITE_2 or userArg == SPAWN_ELITE_3:			# ˢ��Ӣ
			spaceEntity.base.spawnMonsters( {"monsterType":  ELITE_MONSTER_TYPE, "level": spaceEntity.teamLevel } )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
	
class SpaceCopyYXLM( SpaceCopyTeamTemplate ):
	"""
	���ظ�����Ӣ�����ˣ�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeamTemplate.__init__( self )
		self.isSpaceDesideDrop = True
		self.recordKey = "yingxionglianmeng_record"
		self.patrolLists = []
		self.patrolNpcs = []
		self.spaceBirthInf = None
		
	def load( self, section ):
		SpaceCopyTeamTemplate.load( self, section )
		pos = tuple( [ float(x) for x in section[ "Space" ][ "birthPos/position" ].asString.split() ] )
		direction = tuple( [ float(x) for x in section[ "Space" ][ "birthPos/direction" ].asString.split() ] )
		self.spaceBirthInf = ( pos, direction )
		
	def initContent( self ):
		self.contents.append( CCWait() )
		self.contents.append( CCAttackBase() )
		self.contents.append( CCKickPlayersProcess() )
	
	def packedDomainData( self, entity ):
		"""
		"""
		d = { "dbID" : entity.databaseID, "spaceKey" : entity.databaseID}
		if entity.teamMailbox:
			# �Ѽ�����飬ȡ��������
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			# ȡ�����ж�Աbasemailboxs
			teamMemberMailboxsList = entity.getTeamMemberMailboxs()
			if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
				teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
				
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				d[ "membersMailboxs" ] = teamMemberMailboxsList
			
			d[ "teamInfos" ] = entity.popTemp( "YX_teamInofs", [] )	
			d[ "difficulty" ] = entity.popTemp( "YXLMEnterType" )
			d[ "robotInfos" ] = entity.popTemp( "YX_robotInfos" )
			d["spaceKey"] = entity.teamMailbox.id
		return d
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id
			
		packDict[ "playerDBID" ] = entity.databaseID
		return packDict
	
	def packedSpaceDataOnLeave( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnLeave( self, entity )
		packDict["playerDBID"] = entity.databaseID
		packDict["player_accumPoint"] = entity.accumPoint
		return packDict
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		SpaceCopyTeamTemplate.onLoadEntityProperties_( self, section )
		if section.has_key( "patrolLists" ):
			str1 = section["patrolLists"].asString
			self.patrolLists = str1.split('|')
		if section.has_key( "patrolNpcs" ):
			str2 = section["patrolNpcs"].asString
			self.patrolNpcList = str2.split('|')
		
	def initPatrolInfo( self, spaceEntity ):
		"""
		���ø���Ѳ��·�ߺ�Ѳ��NPC��Ϣ
		"""
		random.shuffle( self.patrolLists )
		tempList = []
		for i in self.patrolLists:
			tempList.append( i )
		spaceEntity.setTemp( "spacePatrolLists", tempList )
		spaceEntity.setTemp( "spacePatrolNpcList", self.patrolNpcList )
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_YING_XIONG_LIAN_MENG, self.recordKey )
			
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		for i in selfEntity.queryTemp( "playerAccumPointList", [] ):			# ��ҵڶ��ν�����ʱ���ָ��ϴε�����ֵ
			if i[0] == params["playerDBID"]:
				baseMailbox.cell.addAccumPoint( i[1] )
				break
		
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			if player.isInTeam():
				player.setTemp( "onEnterYXLM", params['teamID'] )
		
		if not selfEntity.queryTemp( "tempHaveCome", False ):	# ֻ����һ��
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.setTemp( "copyStartTime", time.time() )	# ������ʼʱ��
		
		# ��������ʹ��
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		# �������ֵ��¼
		playerAccumRecord = selfEntity.queryTemp( "playerAccumPointList", [] )			# [( playerDBID , accumPoint ),...]
		for info in playerAccumRecord:
			if info[0] == params["playerDBID"]:				# ���Ƶ�ԭ�����������ֵ��¼
				playerAccumRecord.remove( info )
				break
		playerAccumRecord.append( ( params["playerDBID"], params["player_accumPoint"] ) )
		selfEntity.setTemp( "playerAccumPointList", playerAccumRecord )			# ��¼������µ�����ֵ����
		baseMailbox.cell.resetAccumPoint()
		SpaceCopyTeamTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
	
	def getEnterInf( self, playerEntity ):
		# ��ȡ����������
		return self.spaceBirthInf
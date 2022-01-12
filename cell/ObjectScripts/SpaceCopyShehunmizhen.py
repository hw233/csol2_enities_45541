# -*- coding: gb18030 -*-

from bwdebug import *
import cschannel_msgs
import BigWorld
import csconst
import time
import csdefine
import ECBExtend
import copy
import random
from SpaceCopyMapsTeam import SpaceCopyMapsTeam

class SpaceCopyShehunmizhen( SpaceCopyMapsTeam ):
	"""
	�������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyMapsTeam.__init__( self )
		self.recordKey = "shmz_record"
		self.difficulty = 0
		self._curSpawnBossNeedNum = []
		self.spaceDoorInfo = []
		self.spaceDoorPos = []
		self.spaceDoorDir = []
		self.spaceDoorMode = []

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyMapsTeam.load( self, section )
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt
		if section[ "Space" ].has_key( "curSpawnBossNeedNum" ):
			tempSpawnBossNeedNumList = section[ "Space" ][ "curSpawnBossNeedNum" ].asString.split(";")
			for num in tempSpawnBossNeedNumList:
				self._curSpawnBossNeedNum.append( int( num ) )
		
		if section[ "Space" ].has_key( "spaceDoorInfo" ):		# ����ƽ̨������
			for item in section[ "Space" ][ "spaceDoorInfo" ].values():
				doorInfo = {}
				doorInfo[ "useRectangle" ] = item.readInt( "useRectangle" )
				doorInfo[ "radius" ] = item.readFloat( "radius" )
				doorInfo[ "volume" ] = item.readVector3( "volume" )
				doorInfo[ "destSpace" ] = item.readString( "destSpace" )
				doorInfo[ "uname" ] = item.readString( "uname" )
				destPosition = item.readString( "destPosition" )
				doorInfo[ "destPosition" ] = tuple( [ float(x) for x in destPosition.split() ] )
				self.spaceDoorInfo.append( doorInfo )
		
		if section["Space"].has_key( "spaceDoorPos"):			# ����ƽ̨������λ��
			spaceDoorPos = section[ "Space" ][ "spaceDoorPos" ].asString.split(";")
			for pos in spaceDoorPos:
				self.spaceDoorPos.append( tuple( [ float(x) for x in pos.split() ] ) )

		if section["Space"].has_key( "spaceDoorDir"):			# ����ƽ̨������λ��
			spaceDoorDir = section[ "Space" ][ "spaceDoorDir" ].asString.split(";")
			for pos in spaceDoorDir:
				self.spaceDoorDir.append( tuple( [ float(x) for x in pos.split() ] ) )
				
		if section["Space"].has_key( "spaceDoorMode"):			# ����ƽ̨������ģ��
			spaceDoorMode = section[ "Space" ][ "spaceDoorMode" ].asString.split(";")
			for mode in spaceDoorMode:
				self.spaceDoorMode.append( mode )

	def packedDomainData( self, entity ):
		"""
		"""
		data = SpaceCopyMapsTeam.packedDomainData( self, entity )
		if entity.teamMailbox:
			data["mailbox"] = entity.base
			# ���ö���ƽ���ȼ�����ߵȼ�������ȼ�Ϊ�ӳ��ȼ�����ߵȼ�Ϊ�ӳ��ȼ���3��
			if entity.isTeamCaptain():
				data["teamLevel"] = entity.level
				data["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				if self._isPickMembers:
					data["membersMailboxs"] = self._pickMemberData( entity )
			else:
				captain = entity.getTeamCaptain()
				if captain:
					data["teamLevel"] = captain.level
					data["teamMaxLevel"] = min( captain.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				else:
					data["teamLevel"] = entity.level
					data["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )

		return data

	def _pickMemberData( self, entity ):
		# �����������
		teamMemberMailboxsList = entity.getTeamMemberMailboxs()
		if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
			teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
		
		return teamMemberMailboxsList

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyMapsTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		�����������
		"""
		if baseMailbox is not None and self._spaceMapsNo == 0 and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_SHE_HUN_MI_ZHEN, self.recordKey )

		SpaceCopyMapsTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.queryTemp( "tempHaveCome", False ):	# ֻ����һ��
			selfEntity.base.spawnMonsters( { "level" : selfEntity.teamLevel } )		# ˢ������
			selfEntity.setTemp( "tempHaveCome", True )
			if len( self.spaceDoorInfo ) > 0:				# ����ǳ���ƽ̨������Ҫˢ������
				self.createSpaceDoor( selfEntity )

		#��������ʹ��
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.createTime )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, self._spaceLife * 60 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TOTAL_BOSS, self._copyBossNum )

		baseMailbox.client.startCopyTime( self._spaceLife * 60 - int( time.time() - selfEntity.createTime ) )	# ֪ͨ�ͻ��˸�������ʱ

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )	# �����븱����ʱ���Ƿ��ж��飬��ֹ������������������û�ڶ�����

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		"""
		SpaceCopyMapsTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.endCopyTime()

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""	
		if self._bossID and monsterClassName in self._bossID:		# ��ǰ��ͼ��Boss
			tempCount = selfEntity.queryTemp( "bossCount" )
			tempCount -= 1
			selfEntity.setTemp( "bossCount", tempCount )
			selfEntity.domainMB.killCopyBoss( selfEntity.copyKey )
		else:
			tempMonCount = selfEntity.queryTemp( "allMonsterCount" )
			tempMonCount -= 1
			selfEntity.setTemp( "allMonsterCount", tempMonCount )
			selfEntity.domainMB.killCopyMonster( selfEntity.copyKey )
		
			if selfEntity.queryTemp( "allMonsterCount" ) <= 0:
				self.createDoor( selfEntity, False )
				selfEntity.base.onChatChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.SHE_HUN_MI_ZHEN_SPACE_DOOR_OPEN , "" )
				
				if len( self.spaceDoorInfo ) == 0:
					selfEntity.domainMB.allCopyMonsterkilled( selfEntity.copyKey, selfEntity.className )
					
				for id in selfEntity.queryTemp( "tempCallMonsterIDs", [] ):
					if BigWorld.entities.has_key( id ):
						entity = BigWorld.entities[id]
						entity.destroy()

	def setCopyKillBoss( self, selfEntity, bossNum ):
		"""
		define method
		���ø���BOSS����
		"""
		SpaceCopyMapsTeam.setCopyKillBoss( self, selfEntity, bossNum )
		if self._copyBossNum ==  bossNum:
			selfEntity.domainMB.closeCopyItem( { "teamID": selfEntity.copyKey } )
			selfEntity.base.onChatChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.SHE_HUN_MI_ZHEN_SPACE_CLOSE_SPACE , "" )

	def createSpaceDoor( self, selfEntity ):
		"""
		ˢ����ƽ̨������
		"""
		spaceDoorPos = copy.deepcopy( self.spaceDoorPos )
		spaceDoorList = []
		for item in self.spaceDoorInfo:
			pos = random.sample( spaceDoorPos, 1 )[ 0 ]			# ���λ��
			spaceDoorPos.remove( pos )
			index = self.spaceDoorPos.index( pos )
			dir = self.spaceDoorDir[ index ]
			modeInfo = self.spaceDoorMode[ index ].split( "," )
			modelNumber = modeInfo[0]			# λ�ú�ģ��һ��
			try:
				modelScale =  float( modeInfo[1] )
			except:
				modelScale = 1.0
			item[ "modelNumber" ] = modelNumber
			e = BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, pos, dir, item )
			if e != None:
				e.modelScale = modelScale
				spaceDoorList.append( e )
		selfEntity.setTemp( "spaceDoorList", spaceDoorList )

	def onAllCopyMonsterkilled( self, selfEntity, spaceName ):
		"""
		������С��ȫ������ɱ
		"""
		if len( self.spaceDoorInfo ) > 0:
			self.destroySpaceDoor( selfEntity, spaceName )

	def destroySpaceDoor( self, selfEntity, spaceName ):
		"""
		���ٴ�����
		"""
		spaceDoorList = selfEntity.queryTemp( "spaceDoorList", [] )
		if len( spaceDoorList ) == 0:
			return
		for door in spaceDoorList:
			if door.destSpace == spaceName:
				spaceDoorList.remove( door )
				selfEntity.setTemp( "spaceDoorList", spaceDoorList )
				door.destroy()
			return

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )

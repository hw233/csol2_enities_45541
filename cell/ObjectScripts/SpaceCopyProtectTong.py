# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.17 2008-06-23 01:32:24 kebiao Exp $

"""
"""
import BigWorld
import ShareTexts as ST
import csstatus
import csdefine
import random
import csconst
import ECBExtend
import Love3
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
from ObjectScripts.GameObjectFactory import g_objFactory


class SpaceCopyProtectTong( SpaceCopyTeam ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		self._spaceType = csdefine.SPACE_TYPE_PROTECT_TONG

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyTeam.load( self, section )
		self._posData = {}
		self.bossPoint = []
		self.monsterInfo = []	# like as [ [boss���,С�ֱ��], ... ]
		
		self.setEntityProperty( "uname", section.readString( "spaceName" ) )					# ��������
		
		for item in section[ "Space" ]["monsterInfo"].values():
			self.monsterInfo.append( [ monsterID for monsterID in item.asString.split(";")] )
			
		for idx, item in enumerate( section[ "Space" ][ "monsterPoint" ].values() ):
			ls = []
			self._posData[ idx ] = ls
			for point in item.values():
				ls.append( ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) ) )

		self.bossPoint = [ ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) ) for point in section["Space"]["BossPoint"].values() ]
		point = section[ "Space" ][ "doorPoint" ]
		self.doorPoint = ( eval( point["pos"].asString ), point["radius"].asFloat )

		point = section[ "Space" ][ "playerEnterPoint" ]
		self.playerEnterPoint = ( eval( point[ "pos" ].asString ), eval( point[ "direction" ].asString ) )

	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'dbID' : entity.popTemp( "enterSpaceID" ) }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.isTeamCaptain():
			tongDBID, enterPosition, enterDirection = entity.popTemp( "ProtectTongData", ( BigWorld.globalData[ "AS_ProtectTong" ][0], (0,0,0), (0, 0, 0 ) ) )
			packDict[ "playerLevel" ] = entity.level
			packDict[ "spaceName" ] = entity.popTemp( "currentSpaceName", 0 )
			packDict[ "enterPosition" ] = enterPosition
			packDict[ "enterDirection" ] = enterDirection
			packDict[ "isTongMember" ] = entity.tong_dbID == BigWorld.globalData[ "AS_ProtectTong" ][0]
			packDict[ "duizhang" ] = entity.getName()
			
		return packDict

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.setTemp( "currMonsterTotal", 0 )		# ��ǰ��ʣ���ٹ����ڸ���
		BigWorld.globalData[ "ProtectTong" ].onRegisterProtectTongSpace( selfEntity.base )
		selfEntity.params[ "tongDBID" ] = BigWorld.globalData[ "AS_ProtectTong" ][0]

		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, self.getName() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )

	def addCastMonsterCount( self, selfEntity, count ):
		"""
		currMonsterTotal: ��ǰ��ʣ���ٹ����ڸ���
		"""
		selfEntity.setTemp( "currMonsterTotal", selfEntity.queryTemp( "currMonsterTotal" ) + count )

	def getCurrentMonsterCount( self, selfEntity ):
		return selfEntity.queryTemp( "currMonsterTotal" )

	def castAllMonster( self, selfEntity, playerLevel ):
		"""
		��ÿ����ˢ�����еĹ���
		"""

		slist = []
		for lst in self._posData.itervalues():
			slist.extend( lst )

		monsterCount = len( slist )
		isTongMember = selfEntity.queryTemp( "isTongMember" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, monsterCount )
		for x in xrange( monsterCount ):
			idx = random.randint( 0, len( slist ) - 1 )
			posData = slist.pop( idx )
			monsterID = self.monsterInfo[ random.randint( 0, len( self.monsterInfo ) - 1 ) ][ 1 ]
			monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className, "isTongMember" : isTongMember } }
			monInfo[ "spawnPos" ] = posData[0]
			monInfo[ "randomWalkRange" ] = posData[2]
			monInfo[ "level" ] = playerLevel
			selfEntity.createNPCObject( monsterID, posData[0], posData[1], monInfo )
			self.addCastMonsterCount( selfEntity, 1 )

	def castBoss( self, selfEntity, level ):
		"""
		ˢ��boss
		"""
		isTongMember = selfEntity.queryTemp( "isTongMember" )
		bossID = self.monsterInfo[ random.randint( 0, len( self.monsterInfo ) - 1 ) ][ 0 ]
		posData = self.bossPoint[ random.randint( 0, len( self.bossPoint ) - 1 ) ]
		monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className, "isTongMember" : isTongMember } }
		monInfo[ "spawnPos" ] = posData[0]
		monInfo[ "randomWalkRange" ] = posData[1][2]
		monInfo[ "level" ] = level
		selfEntity.createNPCObject( bossID, posData[0], posData[1], monInfo )
		self.addCastMonsterCount( selfEntity, 1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )
		statusID = csstatus.PROTECT_TONG_BOSS
		if BigWorld.globalData[ "AS_ProtectTong" ][2] == csdefine.PROTECT_TONG_MID_AUTUMN:
			statusID = csstatus.PROTECT_TONG_AUTUMN_BOSS
		self.statusMessageAllPlayer( selfEntity, statusID )

	def onProtectTongEnd( self, selfEntity, isTimeout ):
		"""
		�����
		"""
		if isTimeout:
			if selfEntity.queryTemp( "OverProtectTong", -1 ) == True:
				return
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			BigWorld.globalData[ "ProtectTong" ].protectTongOver( selfEntity.queryTemp("duizhang"), BigWorld.globalData[ "AS_ProtectTong" ][2] )
			# ��ʼ����ʱ30��رո���
			selfEntity.setTemp( "leaveTimer", selfEntity.addTimer( 20, 0, 0  ) )
			self.customCreateDoor( selfEntity, selfEntity.queryTemp("spaceName"), selfEntity.queryTemp("enterPosition"), selfEntity.queryTemp("enterDirection") )
			self.statusMessageAllPlayer( selfEntity, csstatus.PROTECT_TONG_OVER )
		else:
			if selfEntity.queryTemp( "OverProtectTong", -1 ) == False:
				return

			self.allMemberLeaveSpace( selfEntity )

		selfEntity.setTemp( "OverProtectTong", isTimeout )

	def allMemberLeaveSpace( self, selfEntity ):
		"""
		���г�Ա��Ӧ���뿪����
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].setTemp( "enter_tong_territory_datas", { "enterOtherTong" : selfEntity.params[ "tongDBID" ] } )
				BigWorld.entities[ e.id ].gotoSpace( "fu_ben_bang_hui_ling_di", selfEntity.queryTemp( "enterPosition" ), selfEntity.queryTemp( "enterDirection" ) )

			else:
				e.cell.setTemp( "enter_tong_territory_datas", { "enterOtherTong" : selfEntity.params[ "tongDBID" ] } )
				e.cell.gotoSpace( "fu_ben_bang_hui_ling_di", selfEntity.queryTemp( "enterPosition" ), selfEntity.queryTemp( "enterDirection" ) )

		# ��ʼ����ʱ30��رո���
		selfEntity.setTemp( "destroyTimer", selfEntity.addTimer( 10, 0, 0  ) )

	def onProtectTongMonsterDie( self, selfEntity, position ):
		"""
		һ������������
		"""
		# ���õ�ǰ��������
		currMonsterTotal = selfEntity.queryTemp( "currMonsterTotal" )
		selfEntity.setTemp( "currMonsterTotal", currMonsterTotal - 1 )

		if selfEntity.queryTemp( "castBossWaitTimeID" ) == None:
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, currMonsterTotal - 1 )
			if currMonsterTotal <= 1:
				selfEntity.setTemp( "castBossWaitTimeID", selfEntity.addTimer( 10, 0, 0 ) )
		else:
			if currMonsterTotal <= 1:
				self.onProtectTongEnd( selfEntity, True )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if selfEntity.queryTemp( "destroyTimer", 0 ) == id:
			selfEntity.base.closeSpace( True )
		elif selfEntity.queryTemp( "castBossWaitTimeID", 0 ) == id:
			selfEntity.cancel( selfEntity.queryTemp( "castBossWaitTimeID", 0 ) )
			selfEntity.setTemp( "castBossWaitTimeID", -100 )
			self.castBoss( selfEntity, selfEntity.queryTemp( "playerLevel", 10 ) )
		elif selfEntity.queryTemp( "leaveTimer", 0 ) == id:
			self.allMemberLeaveSpace( selfEntity )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		# �ӳ���һ�ν�����ˢ�����еĹ���
		if not selfEntity.queryTemp( "playerLevel" ) and params.has_key( "playerLevel" ):
			selfEntity.setTemp( "playerLevel", params[ "playerLevel" ] )
			selfEntity.setTemp( "spaceName", params[ "spaceName" ] )
			selfEntity.setTemp( "enterPosition", params[ "enterPosition" ] )
			selfEntity.setTemp( "enterDirection", params[ "enterDirection" ] )
			selfEntity.setTemp( "duizhang", params[ "duizhang" ] )
			selfEntity.setTemp( "isTongMember", params[ "isTongMember" ] )
			self.castAllMonster( selfEntity, params[ "playerLevel" ] )

		#baseMailbox.cell.setTemp( "ProtectTongData", ( selfEntity.params[ "tongDBID" ], selfEntity.queryTemp( "enterPosition" ), selfEntity.queryTemp( "enterDirection" ) ) )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		֪ͨ������ ָ������Ϣ
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				p = BigWorld.entities[ e.id ]
				p.statusMessage( msgKey, *args )
			else:
				ERROR_MSG( "player %i not found" % e.id )

	def createDoor( self, selfEntity ):
		"""
		����Door
		"""
		pass

	def customCreateDoor( self, selfEntity, spaceName, destPosition, destDirection ):
		"""
		����Door
		"""
		doordict = {"name" : "haha"}
		doordict["radius"] = self.doorPoint[1]
		doordict["destSpace"] = spaceName
		doordict["destPosition"] = destPosition
		doordict["destDirection"] = destDirection
		doordict["modelNumber"] = None
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, self.doorPoint[0], (0, 0, 0), doordict )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		tongDBID, enterPosition, enterDirection = playerEntity.popTemp( "ProtectTongData", \
																( BigWorld.globalData[ "AS_ProtectTong" ][0], (0,0,0), (0, 0, 0 ) ) )

		playerEntity.setTemp( "enter_tong_territory_datas", { "enterOtherTong" : tongDBID } )

		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		��Ա�뿪���鴦��
		"""
		tongDBID, enterPosition, enterDirection = playerEntity.popTemp( "ProtectTongData", \
																( BigWorld.globalData[ "AS_ProtectTong" ][0], (0,0,0), (0, 0, 0 ) ) )

		if not playerEntity.isInTeam():
			playerEntity.gotoSpace( "fu_ben_bang_hui_ling_di", enterPosition, enterDirection )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		pass

#
# $Log: not supported by cvs2svn $
#

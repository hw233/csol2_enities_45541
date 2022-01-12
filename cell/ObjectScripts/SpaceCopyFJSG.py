# -*- coding: gb18030 -*-


from SpaceCopyTemplate import SpaceCopyTemplate
import csconst
from CopyContent import *
import time
import random
import csdefine
import csstatus
import Const
import ECBExtend

FISH_ID 	 = "20722016"	# ���˵�className
FISH_BOSS_ID = "20712020"	# Զ������ͷ���className
FISH_KING_ID = "20754013"	# ������������className 45%����ˢ��
FISH_KING_ODDS = 45			# Զ�����˴���45%����ˢ��

SHFYZ_ID = "20742030"		# ���ӡ��
BOSS_YGFSS_ID	= "20754014"	# Զ�ŷ�ˮ�޵�className
BOSS_TU_FU_XUE_ZHAN		= "20714005"	# ����Ѫն��className
SHARK_DOOR	= "10143005"				# �����ţ�ͨ��key����
FOUR_LIGHT_DOOR = "20251051"			# �ĸ�������������
YOU_GUO_ID	= "20251049"				# �͹���id

BOSS_SHUI_JI_ID = "20742031"			# ˮ��
BOSS_YJSH		= "20714006"			# �㽫�

YGYRLS_ID       = "20754018"			#Զ��������ʿ
YGJYYR_ID       = "20754019"			#Զ�ž�Ӣ����
SHYQ_ID      	= "20714007"			#���Ȯ
REVIVAL_SHYQ_ID = "20714008"			# ��������Ȯ��className��û�о���

YGFSS_DOOR_ID 	= "20251052"			# Զ�ŷ�ˮ��ǰ��
YGFSS_DOOR_BACK_ID = "20251053"			# Զ�ŷ�ˮ�޺���
TU_FU_XUE_ZHAN_DOOR_ID = "20251054"		# ����Ѫն����
SJ_DOOR_ID		= "20251055"			# ˮ��ǰ��

BOSS_NUM = 4
MONSTER_NUM = 92

CLOSE_COPY_USERARG = 3600				# 3600s�󣬸����ر�time���

FIND_SPAWN_RANGE		= 200					# ������Χ��С
SPAWN_YGYU_POS			= ( -90.136047, -3.734375, 109.015465 ) #Զ������ͷ��ˢ��λ��


class CCFish( CopyContent ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key = "fish"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		#spaceEntity.base.spawnMonsters( { "entityName" : FISH_ID, "level": spaceEntity.params["copyLevel"] } )
		spaceEntity.base.spawnMonsters( { "entityName" : FISH_BOSS_ID, "level": spaceEntity.params["copyLevel"] } )
		spaceEntity.base.spawnMonsters( { "entityName" : YGYRLS_ID, "level": spaceEntity.params["copyLevel"] } )
		spaceEntity.base.spawnMonsters( { "entityName" : YGJYYR_ID, "level": spaceEntity.params["copyLevel"] } )
		spaceEntity.base.spawnMonsters( { "entityName" : SHYQ_ID, "level": spaceEntity.params["copyLevel"], "revivalEntityName" : REVIVAL_SHYQ_ID } )
		# ˢ�����ӡ��
		spaceEntity.base.spawnMonsters( { "entityName" : SHFYZ_ID, "level": spaceEntity.params["copyLevel"] } )
		#self.onConditionChange( spaceEntity, {} )

class CCFourLight( CopyContent ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key = "ligth"
		self.val = 4

	def onContent( self, spaceEntity ):
		"""
		"""
		#spaceEntity.base.ˢ��Ѳ�߱�
		if random.randint( 1, 100 ) <= FISH_KING_ODDS:		# ˢ��45���ʳ��ֵ�boss
			spaceEntity.base.spawnMonsters( { "entityName" : FISH_KING_ID, "level": spaceEntity.params["copyLevel"] } )

	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.onConditionChange( self, spaceEntity, params )
		for e in spaceEntity._players:
			e.client.onStatusMessage( csstatus.FJSG_ONE_LIGHT, "" )

	def endContent( self, spaceEntity ):
		"""
		���ݽ���
		"""
		spaceEntity.base.openDoor( { "entityName" : FOUR_LIGHT_DOOR } )
		for e in spaceEntity._players:
			e.client.onStatusMessage( csstatus.FJSG_FOUR_LIGHT, "" )
		CopyContent.endContent( self, spaceEntity )



class CCBoss( CopyContent ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key = "twoBoss"
		self.val = 2

	def onContent( self, spaceEntity ):
		"""
		"""
		# Զ�ŷ�ˮ��ǰ�Ŵ�
		spaceEntity.base.openDoor( { "entityName" : YGFSS_DOOR_ID } )
		# ˢ��Զ�ŷ�ˮ��
		spaceEntity.base.spawnMonsters( { "entityName" : BOSS_YGFSS_ID, "level": spaceEntity.params["copyLevel"] } )
		# ˢ���͹�����Ϊ�ü��ܴ��� ��
		# spaceEntity.base.spawnMonsters( { "entityName" : YOU_GUO_ID, "level": spaceEntity.params["copyLevel"], "radius" : 1.0, "enterSpell" : 313100010, "leaveSpell" : 313100011 } )
		# ˢ������Ѫն
		spaceEntity.base.spawnMonsters( { "entityName" : BOSS_TU_FU_XUE_ZHAN, "level": spaceEntity.params["copyLevel"] } )

		# ˮ����ǰ�Ŵ�
		spaceEntity.base.openDoor( { "entityName" : SJ_DOOR_ID } )
		# ˢ��ˮ��
		spaceEntity.base.spawnMonsters( { "entityName" : BOSS_SHUI_JI_ID, "level": spaceEntity.params["copyLevel"] } )
		# ˢ���㽫�
		spaceEntity.base.spawnMonsters( { "entityName" : BOSS_YJSH, "level": spaceEntity.params["copyLevel"] } )

	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		if "monster" not in params:
			return
		CopyContent.onConditionChange( self, spaceEntity, params )

	def endContent( self, spaceEntity ):
		"""
		���ݽ���
		"""
		CopyContent.endContent( self, spaceEntity )



class CCLastBoss( CopyContent ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key = "lastBoss"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		pass


	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		pass

	def endContent( self, spaceEntity ):
		"""
		���ݽ���
		"""
		pass




class SpaceCopyFJSG( SpaceCopyTemplate ):
	# �⽣��
	def __init__( self ):
		"""
		"""
		SpaceCopyTemplate.__init__( self )
		self.recordKey = "fjsg_record"


	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCFish() )
		self.contents.append( CCWait() )
		self.contents.append( CCFourLight() )
		self.contents.append( CCWait() )
		self.contents.append( CCBoss() )
		#self.contents.append( CCLastBoss() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )


	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		data = {"copyLevel"			: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"enterMonsterID"	:	player.queryTemp( "copySpaceEnterMonsterID", 0 ),
				"difficulty"		:	player.popTemp( "EnterSpaceCopyFJSGType", 0 ),
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			packDict[ "teamID" ] = player.teamMailbox.id
		
		packDict[ "dbID" ] = player.databaseID
		return packDict


	def onStartContent( self, selfEntity, baseMailbox, params ):
		"""
		"""
		#BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, "�⽣��" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, 3600 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, MONSTER_NUM )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, BOSS_NUM )

		SpaceCopyTemplate.onStartContent( self, selfEntity, baseMailbox, params )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 90 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 90 )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		��Ա�뿪���鴦��
		"""
		if not playerEntity.isInTeam() or playerEntity.query( "lastFJSGTeamID", 0 ) != playerEntity.getTeamMailbox().id:
			playerEntity.gotoForetime()

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0:
			BigWorld.globalData['FJSG_%i'%params['teamID'] ] = True
			selfEntity.setTemp('globalkey','FJSG_%i'%params['teamID'])
			#selfEntity.addTimer( 1800, 0, 123453 )
		
		baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG, self.recordKey )
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		
		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_COPY_USERARG:		# 3600s�󣬹رո���
			self.closeCopy( selfEntity )
		
		SpaceCopyTemplate.onTimer( self, selfEntity, id, userArg )

	def closeCopy( self, selfEntity ):
		"""
		�����ر�
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""
		uskCount = None
		monster = BigWorld.entities.get( monsterID )
		if monster and monster.isReal():
			uskCount = monster.queryTemp( "uskCount" )
			
		if monsterClassName == BOSS_YGFSS_ID:
			# Զ�ŷ�ˮ�޺��Ŵ򿪣�ǰ�Ŵ�
			selfEntity.base.openDoor( { "entityName" : YGFSS_DOOR_ID } )
			selfEntity.base.openDoor( { "entityName" : YGFSS_DOOR_BACK_ID } )
			selfEntity.setTemp( "bossNum", selfEntity.queryTemp( "bossNum", 0 ) + 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, BOSS_NUM - selfEntity.queryTemp( "bossNum", 0 ) )
		elif monsterClassName == BOSS_TU_FU_XUE_ZHAN:
			selfEntity.base.openDoor( { "entityName" : TU_FU_XUE_ZHAN_DOOR_ID } )
			selfEntity.setTemp( "bossNum", selfEntity.queryTemp( "bossNum", 0 ) + 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, BOSS_NUM - selfEntity.queryTemp( "bossNum", 0 ) )
		elif monsterClassName == BOSS_SHUI_JI_ID:
			if uskCount is not None and uskCount > 0:		# ������������ˮ���Ͷ���һ���໥��Ѫ�������񲻳ɹ�
				selfEntity.setTemp( "godWeaponMissionFaile", 1 )
			selfEntity.setTemp( "bossNum", selfEntity.queryTemp( "bossNum", 0 ) + 1 )
			selfEntity.base.openDoor( { "entityName" : SJ_DOOR_ID } )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, BOSS_NUM - selfEntity.queryTemp( "bossNum", 0 ) )
		elif monsterClassName == BOSS_YJSH:
			if uskCount is not None and uskCount > 0:		# ������������ˮ���Ͷ���һ���໥��Ѫ�������񲻳ɹ�
				selfEntity.setTemp( "godWeaponMissionFaile", 1 )
			selfEntity.setTemp( "bossNum", selfEntity.queryTemp( "bossNum", 0 ) + 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, BOSS_NUM - selfEntity.queryTemp( "bossNum", 0 ) )
		elif monsterClassName == SHFYZ_ID or monsterClassName == FISH_BOSS_ID or monsterClassName == SHYQ_ID or monsterClassName == YGYRLS_ID or monsterClassName == YGJYYR_ID:
			selfEntity.setTemp( "monsterNum", selfEntity.queryTemp( "monsterNum", 0 ) + 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, MONSTER_NUM - selfEntity.queryTemp( "monsterNum", 0 ) )

		if selfEntity.queryTemp( "bossNum" ) == 4:
			self.getCurrentContent( selfEntity ).endContent( selfEntity )
			# ������������ѯ&����
			godWeaponMissionRes = selfEntity.queryTemp( "godWeaponMissionFaile" )
			if godWeaponMissionRes != 1:
				selfEntity.onGodWeaponFJSG()


		if monsterClassName == FISH_BOSS_ID:								#CSOL-8829												
			spawnsPoint = selfEntity.entitiesInRangeExt( FIND_SPAWN_RANGE, "SpawnPointCopy", SPAWN_YGYU_POS )
			for i in spawnsPoint:
				if i.spawnType == "SpawnPointCopyRevival":
					i.getScript().stopRevival( i, REVIVAL_SHYQ_ID )
			
			monsters = selfEntity.entitiesInRangeExt( FIND_SPAWN_RANGE, "Monster", SPAWN_YGYU_POS )
			for i in monsters:
				if i.className == REVIVAL_SHYQ_ID:
					i.destroy()
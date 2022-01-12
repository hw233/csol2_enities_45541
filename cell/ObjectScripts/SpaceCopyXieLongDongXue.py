# -*- coding: gb18030 -*-

"""
а����Ѩ����
"""

from SpaceCopyTeam import SpaceCopyTeam
import BigWorld
import time
import cschannel_msgs
from GameObject import GameObject
import csdefine
import ECBExtend
import csconst
import Const
from bwdebug import *
from Resource.SpaceCopyCountLoader import SpaceCopyCountLoader
g_SpaceCopyCount = SpaceCopyCountLoader.instance()

WAIT 					= 30				#�ȴ�һ��ˢ��

CLOSE_COPY_USERARG = 3600					# 3600s�󣬸����ر�time���
WAIT_SPAWN_USERARG = 10						# ��ʼˢ��
CLOSE_COPY_IN_ADVANCE_USERARG = 1			# ��ǰ�رո���time���

YING_LONG_FIGHT_LAST_TIME			= 120	# ��������ɱ��Ӧ������ʱ��
#BOSS_CLASS_NAME = [ "20154019", "20154019", "20154019" ]


class SpaceCopyXieLongDongXue( SpaceCopyTeam ):
	"""
	а����Ѩ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		self.recordKey = "xldx_record"

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyTeam.load( self, section )
		#self._playerAoI = section.readFloat( "playerAoI", csconst.ROLE_AOI_RADIUS )	# �Ѿ���Ϊ�ռ��ͨ�����ã���space�н�������

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 1
		data = {"copyLevel"			: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"enterMonsterID"	:	player.queryTemp( "copySpaceEnterMonsterID", 0 ),
				"difficulty"		:	player.popTemp( "EnterSpaceXieLongType", 0 ),
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		����а����Ѩ
		"""
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_XIE_LONG, self.recordKey )
			
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.queryTemp( "tempHaveCome", False ):	# ֻ����һ��
			selfEntity.setTemp( "copyStartTime", time.time() )	# ������ʼʱ��
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.addTimer( WAIT, 0, WAIT_SPAWN_USERARG )

		# ��������ʹ��
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, 3600 )
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		�����뿪����
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_COPY_USERARG:		# 3600s�󣬹رո���
			self.closeCopy( selfEntity )
		elif userArg == CLOSE_COPY_IN_ADVANCE_USERARG:		# ��ǰ�رո���
			self.closeCopy( selfEntity )
		elif userArg == WAIT_SPAWN_USERARG:
			selfEntity.base.spawnMonsters( { "level": selfEntity.params["copyLevel"] } )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def closeCopy( self, selfEntity ):
		"""
		�����ر�
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
			e.client.onCloseCopySpaceInterface()
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
		#selfEntity.base.closeSpace( True )		# �ر�(�����رջ�����̹��ػ��Ŀͻ��˴���û�йص���space��onLeaveCommonû�б�����)

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""
		bossCls = g_SpaceCopyCount.getSpaceAssignCls( self.getSpaceType(), "bossCls" )
		if monsterClassName in bossCls:		# Ӧ�����󣬴���������������
			fightStartTick = None
			monster = BigWorld.entities.get( monsterID )
			if monster and monster.isReal():
				fightStartTick = monster.queryTemp( "fightStartTick" )
			if fightStartTick is not None and time.time() - fightStartTick < YING_LONG_FIGHT_LAST_TIME:
				selfEntity.onGodWeaponXL()

			self.broadcastInCopy( selfEntity, cschannel_msgs.BCT_FUBEN_XIE_LONG_DONG_XUE_OVER )
			selfEntity.addTimer( 60.0, 0.0, CLOSE_COPY_IN_ADVANCE_USERARG )			# 30��󣬹رո�����ʤ
			selfEntity.setTemp( "bossCount", selfEntity.queryTemp( "bossCount" ) - 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.queryTemp( "bossCount" ) )
		else:	# ���С������
			selfEntity.setTemp( "allMonsterCount", selfEntity.queryTemp( "allMonsterCount" ) - 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.queryTemp( "allMonsterCount" ) )
			if selfEntity.queryTemp( "allMonsterCount", 0 ) == 0:
				self.broadcastInCopy( selfEntity, cschannel_msgs.BCT_FUBEN_XIE_LONG_DONG_XUE_BOSS_COME )
				selfEntity.base.spawnMonsters( { "bossID": self.getBossClassName( selfEntity ), "level": selfEntity.params["copyLevel"] } )

	def broadcastInCopy( self, selfEntity, msg ):
		"""
		�����й㲥
		"""
		for baseMailBox in selfEntity._players:
			baseMailBox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, [] )
			
	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )

	def getBossClassName( self, selfEntity ):
		bossCls = g_SpaceCopyCount.getSpaceAssignCls( self.getSpaceType(), "bossCls" )
		try:
			bossClassName = bossCls[ selfEntity.params[ "difficulty" ] ]
		except:
			bossClassName = ""
		return bossClassName

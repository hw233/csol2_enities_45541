# -*- coding: gb18030 -*-

from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

import csdefine
import cschannel_msgs
import random
import BigWorld
import ECBExtend
import time
import csconst
import csstatus
from csconst import ROLE_COMPETITION_TIME
from csconst import END_TIME
from GameObjectFactory import g_objFactory


NOTICE_TIMER01			= 1				# 活动提示
NOTICE_TIMER02			= 2				# 活动提示
NOTICE_TIMER03			= 3				# 活动提示
END_ROLECOMPETITION		= 12			# 关闭副本
BEGIN_ROLECOMPETITION0	= 13			# 刚开始
BEGIN_ROLECOMPETITION1	= 14			# 开始5分钟
BEGIN_ROLECOMPETITION2	= 15			# 开始15分钟
BEGIN_ROLECOMPETITION_NOTICE	= 16	# 通知客户端更新积分显示
ONE_MINUTE				= 60			# 1分钟

REWARD_BOX1 = "10121055"
REWARD_BOX2 = "10121056"
REWARD_BOX3 = "10121057"

REWARD_POSITION_1 = ( -2.375, 9.01, 16.637)
REWARD_POSITION_2 = ( -2.375, 9.01, 16.637)
REWARD_POSITION_3 = ( -2.375, 9.01, 16.637)


class CCSaveModelProcess( CopyContent ):
	"""
	#产生3分钟pk保护
	"""
	def __init__( self ):
		"""
		"""
		self.key = "saveProcess"
		self.val = 1
		self.reserveTime = 0
		self.cishu = 0

	def onContent( self, spaceEntity ):
		"""
		"""
		pkProtectTime = 5 * ONE_MINUTE - ( spaceEntity.queryTemp("createTime", 0 ) - spaceEntity.queryTemp("roleCompetitionStartEnterTime" ) )
		spaceEntity.addTimer( pkProtectTime, 0, NEXT_CONTENT )
		spaceEntity.addTimer( pkProtectTime % 30, 0, NOTICE_TIMER01 )


		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# 强制所有玩家进入系统和平模式
			e.cell.lockPkMode()																# 锁定pk模式，不能设置

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )					# 强制所有玩家进入和平模式
		baseMailbox.cell.lockPkMode()														# 锁定pk模式，不能设置


	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.unLockPkMode()
			e.cell.setSysPKMode( 0 )
		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()				# 解锁pk模式
		baseMailbox.cell.setSysPKMode( 0 )
		CopyContent.onLeave( self, selfEntity, baseMailbox, params )


	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == NOTICE_TIMER01:
			t = spaceEntity.queryTemp( "roleCompetitionStartEnterTime" ) - time.time() + 5 * ONE_MINUTE + self.reserveTime
			m = int ( t / ONE_MINUTE )
			s = int ( t % ONE_MINUTE )
			self.cishu = self.cishu + 1
			if self.cishu == 1:
				if s >= 28 and s <= 32:
					self.reserveTime = 30 - s
				elif s >= 58:
					self.reserveTime = 60 - s
				elif s <= 2:
					self.reserveTime = -s
				t = t + self.reserveTime
				m = int ( t / ONE_MINUTE )
				s = int ( t % ONE_MINUTE )
			for e in spaceEntity._players:
				if m != 0 and s >= 28:
					e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_X_MINUTE_Y_SECOND, str( ( m, 30) ))
				elif m != 0 and s <= 2:
					e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_X_MINUTE, str((m,)) )
				elif m == 0 and s != 0:
					e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_Y_SECOND, str( (30,)) )
			if m != 0:
				spaceEntity.addTimer( 30, 0, NOTICE_TIMER01 )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )


class CCRolePKProcess( CopyContent ):
	"""
	个人竞赛开始
	"""
	def __init__( self ):
		"""
		"""
		self.key = "rolePKProcess"
		self.val = 1


	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setPkMode( baseMailbox.id, csdefine.PK_CONTROL_PROTECT_NONE )		# 强制所有玩家进入和平模式
		baseMailbox.cell.lockPkMode()														# 锁定pk模式，不能设置

	def onContent( self, spaceEntity ):
		"""
		"""
		if len(spaceEntity._players) < 5:
			for e in spaceEntity._players:
				entity = BigWorld.entities[e.id]
				entityName = entity.playerName
				entityScore = entity.queryTemp( "killPersonalCount", 0 )
				entityCompetitionTime = entity.queryTemp( "killPersonalTime", 0 )
				spaceEntity.gradeList.append((entityName,entityScore,entityCompetitionTime))
			for e in spaceEntity._players:
				e.client.receiveRoleCompetitionScore(spaceEntity.gradeList)
		else:
			count = 0
			for e in spaceEntity._players:
				entity = BigWorld.entities[e.id]
				entityName = entity.playerName
				entityScore = entity.queryTemp( "killPersonalCount", 0 )
				entityCompetitionTime = entity.queryTemp( "killPersonalTime", 0 )
				count = count +1
				if count <= 5:
					spaceEntity.gradeList.append((entityName,entityScore,entityCompetitionTime))
			for e in spaceEntity._players:
				e.client.receiveRoleCompetitionScore(spaceEntity.gradeList)

		for e in spaceEntity._players:
			e.cell.setPkMode( e.id, csdefine.PK_CONTROL_PROTECT_NONE )						# 强制所有玩家进入组队pk 状态
			e.cell.lockPkMode()																	# 锁定pk模式，不能设置
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_ROLECOMPETITION_START, [] )
		spaceEntity.addTimer( 0, 0, BEGIN_ROLECOMPETITION0 )
		spaceEntity.addTimer( ROLE_COMPETITION_TIME - 1500, 0, BEGIN_ROLECOMPETITION1 )
		spaceEntity.addTimer( ROLE_COMPETITION_TIME - 900, 0, BEGIN_ROLECOMPETITION2 )
		#spaceEntity.addTimer( 3, 0, BEGIN_ROLECOMPETITION_NOTICE )
		spaceEntity.addTimer( ROLE_COMPETITION_TIME, 0, NEXT_CONTENT )
		spaceEntity.addTimer( ROLE_COMPETITION_TIME - 300, 0, NOTICE_TIMER02 )
		spaceEntity.addTimer( ROLE_COMPETITION_TIME - 60, 0, NOTICE_TIMER03 )


	def endContent( self, spaceEntity ):
		"""
		"""
		personalCount = -1
		personalTime = 9999
		for e in spaceEntity._players:
			e.cell.unLockPkMode()													#解锁pk模式
		if BigWorld.globalData.has_key( "AS_RoleCompetition" ):
			del BigWorld.globalData[ "AS_RoleCompetition" ]
		remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
		for e in remainList:
			if len( remainList ) > 1:
				entity = BigWorld.entities[ e.id ]
				if entity.queryTemp( "killPersonalCount", 0 ) > personalCount:
					personalCount = entity.queryTemp( "killPersonalCount", 0 )
					personalTime = entity.queryTemp( "killPersonalTime", 0 )
					spaceEntity.setTemp( "champion", e.id)
				elif entity.queryTemp( "killPersonalCount", 0 ) == personalCount and entity.queryTemp( "killPersonalTime", 0 ) < personalTime:
					spaceEntity.setTemp( "champion", e.id)
		g_objFactory.getObject( REWARD_BOX3 ).createEntity( spaceEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :spaceEntity.queryTemp( "champion", 0) } } )
		for e in remainList:
			e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()
		CopyContent.onLeave( self, selfEntity, baseMailbox, params )


	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		beKilledCount = 2
		if userArg == NOTICE_TIMER02:
			remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
			for e in remainList:
				e.cell.setTemp( "personalBekilled", beKilledCount)
				e.client.onStatusMessage( csstatus.ROLEPK_OVER_IN_5_MINUTE, "" )
		elif userArg == BEGIN_ROLECOMPETITION0:
			self.onTimerNoticeGrade( spaceEntity )
			for e in spaceEntity._players:
				player = BigWorld.entities[ e.id ]
				e.client.remainRevivalCount( ( e.id, 2 - player.queryTemp( "personalBekilled", 0 ) ) )
			remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
			if len(remainList) == 1:
				spaceEntity.setTemp( "champion", remainList[0].id)
				g_objFactory.getObject( REWARD_BOX3 ).createEntity( spaceEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :spaceEntity.queryTemp( "champion", 0) } } )
				for e in remainList:
					e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
				CopyContent.endContent( self, spaceEntity )
		elif userArg == BEGIN_ROLECOMPETITION1:
			remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
			if len(remainList) <= 20:
				g_objFactory.getObject( REWARD_BOX1 ).createEntity( spaceEntity.spaceID, REWARD_POSITION_1, (0, 0, 0), {} )
				for e in remainList:
					e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_1_NOTICE, [])
		elif userArg == BEGIN_ROLECOMPETITION2:
			remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
			if len(remainList) <= 10:
				g_objFactory.getObject( REWARD_BOX2 ).createEntity( spaceEntity.spaceID, REWARD_POSITION_2, (0, 0, 0) , {} )
				for e in remainList:
					e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_2_NOTICE, [])
		elif userArg == NOTICE_TIMER03:
			remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
			for e in remainList:
				e.client.onStatusMessage( csstatus.ROLEPK_OVER_IN_1_MINUTE, "" )
		elif userArg == BEGIN_ROLECOMPETITION_NOTICE:
			self.onTimerNoticeGrade( spaceEntity )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def onTimerNoticeGrade( self, spaceEntity):
		"""
		触发积分显示的更改
		"""
		spaceEntity.noticeGrade()
		spaceEntity.addTimer( 3, 0, BEGIN_ROLECOMPETITION_NOTICE )

class CCEndProcess( CopyContent ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key = "endProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		personalCount = -1
		personalTime = 9999
		spaceEntity.noticeGrade()
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			e.cell.lockPkMode()
			e.client.onStatusMessage( csstatus.ACTIVITY_IS_OVER, "" )
			e.client.onStatusMessage( csstatus.ACTIVITY_WILL_OVER_IN_2_MINUTE, "" )
			e.cell.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )			#无敌状态
			e.client.onRoleCompetitionEnd()
		remainList = spaceEntity.queryTemp( "remainPlayerMBs", [] )
		for e in remainList:
			if len( remainList ) > 1:
				entity = BigWorld.entities[ e.id ]
				if entity.queryTemp( "killPersonalCount", 0 ) > personalCount:
					personalCount = entity.queryTemp( "killPersonalCount", 0 )
					personalTime = entity.queryTemp( "killPersonalTime", 0 )
					spaceEntity.setTemp( "champion", e.id)
				elif entity.queryTemp( "killPersonalCount", 0 ) == personalCount and entity.queryTemp( "killPersonalTime", 0 ) < personalTime:
					spaceEntity.setTemp( "champion", e.id)
			elif len( remainList ) == 1:
				spaceEntity.setTemp( "champion", e.id)
		if spaceEntity.queryTemp( "champion", 0) != 0:
			playerName = BigWorld.entities[ spaceEntity.queryTemp( "champion", 0) ].getName()
			playerLevel = BigWorld.entities[ spaceEntity.queryTemp( "champion", 0) ].getLevel()
			temp = cschannel_msgs.BCT_ROLECOMPETITION_END % ( playerName, spaceEntity.queryTemp( "copyLevel", 0 )*10 )
			BigWorld.globalData["RoleCompetitionMgr"].roleCompetition_end(temp)
		else:
			BigWorld.globalData["RoleCompetitionMgr"].roleCompetition_end("")
		spaceEntity.addTimer( END_TIME, 0, NEXT_CONTENT )


	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )


class SpaceCopyRoleCompetition( SpaceCopyTemplate ):
	"""
	个人竞技
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		self._updateClientTimeTimer = -1

	def initContent( self ):
		"""
		"""
		self.contents.append( CCSaveModelProcess() )
		self.contents.append( CCRolePKProcess() )
		self.contents.append( CCEndProcess() )
		self.contents.append( CCKickPlayersProcess() )

	def packedDomainData( self, player ):
		"""
		"""
		level = player.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
		data = {"copyLevel" 		: 	level/10,
				"dbID" 				: 	player.databaseID,
				"spaceKey"		: level/10,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, player )
		level = player.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
			
		packDict[ "copyLevel" ] = level/10
		packDict[ "dbID" ] = player.databaseID
		packDict[ "playerName" ] = player.playerName
		return packDict

	def packedSpaceDataOnLeave( self, player ):
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, player )
		packDict[ "isWatchState" ] = player.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		return packDict

	def onRoleDie( self, role, killer ):
		"""
		virtual method.
		如果对方誉点减自己荣誉点的值低于-50，那么玩家获得2点荣誉点。
		如果对方荣誉点减自己荣誉点的值在-50-100之间，那么玩家获得3点荣誉点。
		如果对方荣誉点减自己荣誉点的值在101-200之间，那么玩家获得6点荣誉点。
		如果对方荣誉点减自己荣誉点的值在201-300之间，那么玩家获得9点荣誉点。
		如果对方荣誉点减自己荣誉点的值在301-500之间，那么玩家获得12点荣誉点。
		如果对方荣誉点减自己荣誉点的值在500以上，那么玩家获得15点荣誉点。
		"""
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			killer = BigWorld.entities.get( killer.ownerID, None )
			if killer is None:
				return
				
		beKilledCount = role.queryTemp( "personalBekilled", 0 )
		role.setTemp( "personalBekilled", beKilledCount + 1)
		killCount = killer.queryTemp( "killPersonalCount", 0 )
		killer.setTemp( "killPersonalCount", killCount + 1)
		killer.setTemp( "killPersonalTime", time.time() )
		
		if role.queryTemp( "personalBekilled", 0 ) < 3:
			role.client.challengeOnDie( 0 )
			role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
			role.addTimer( 10, 0, ECBExtend.ROLE_REVIVE_TIMER )

		elif role.queryTemp( "personalBekilled", 0 ) >= 3:
			role.setTemp( "role_competition_die_teleport", True ) #设置临时死亡标记
			role.client.challengeOnDie( 1 )		# 弹出观战选择对话框
			#role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
			#role.addTimer( 2, 0, ECBExtend.ROLE_REVIVE_TIMER )
			#role.spellTarget( SKILL_ID1, role.id )
			#role.getCurrentSpaceBase().cell.removeRoleList( role.base )
			selfEntity = BigWorld.entities[role.getCurrentSpaceBase().id]
			remainList = selfEntity.queryTemp( "remainPlayerMBs", [] )
			for index,mailbox in enumerate( remainList):
				if mailbox.id == role.id:
					del remainList[ index ]
			selfEntity.setTemp( "remainPlayerMBs", remainList )
			remainList = selfEntity.queryTemp( "remainPlayerMBs", [] )
			if not selfEntity.queryTemp( "hasCloseRoleCompetition" ):
				currentTime = time.time()
				if len( remainList ) == 1 and currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) >= 1:
					selfEntity.setTemp( "champion", remainList[0].id)
					if currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) < 5 * 60:
						g_objFactory.getObject( REWARD_BOX1 ).createEntity( selfEntity.spaceID, REWARD_POSITION_1, (0, 0, 0), {} )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_1_NOTICE, [])
						g_objFactory.getObject( REWARD_BOX2 ).createEntity( selfEntity.spaceID, REWARD_POSITION_2, (0, 0, 0) , {} )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_2_NOTICE, [])
						g_objFactory.getObject( REWARD_BOX3 ).createEntity( selfEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :selfEntity.queryTemp( "champion", 0) } } )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
					elif currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) < 15 * 60:
						g_objFactory.getObject( REWARD_BOX2 ).createEntity( selfEntity.spaceID, REWARD_POSITION_2, (0, 0, 0) , {} )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_2_NOTICE, [])
						g_objFactory.getObject( REWARD_BOX3 ).createEntity( selfEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :selfEntity.queryTemp( "champion", 0) } } )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
					elif currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) < 30 * 60:
						g_objFactory.getObject( REWARD_BOX3 ).createEntity( selfEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :selfEntity.queryTemp( "champion", 0) } } )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
					if self.getCurrentContent( selfEntity ) == self.contents[1]:
						SpaceCopyTemplate.doNextContent( self, selfEntity )
			#remainList = selfEntity.queryTemp( "remainPlayerMBs", [] )
			#remainList.remove( role.base )
			#selfEntity.setTemp( "remainPlayerMBs", remainList )
			#role.reviveOnOrigin()
			#role.gotoForetime()
			
		killer.addPersonalScore( 1, csdefine.ACTIVITY_GE_REN_JING_JI )
		role.getCurrentSpaceBase().cell.addRoleKillerCount( killer.id, killer.databaseID)
		#每击杀一个人获得经验值=351*（25+5*角色等级^1.2）
		exp = int( 351 * ( 25 + 5 * killer.level ** 1.2) )
		killer.addExp( exp, csdefine.REWARD_ROLECOMPETITION_EXP )
		killer.client.onStatusMessage( csstatus.REWARD_PERSONALSCORE_FOR_KILL_ONE_ENEMY, str(( 1, )) )
		if role.queryTemp( "personalBekilled", 0 ) <= 2:
			role.client.onStatusMessage( csstatus.LOST_PERSONALSCORE_FOR_BE_KILL, str(( 2 - role.queryTemp( "personalBekilled", 0 ), )) )
			role.client.remainRevivalCount( ( role.id, 2 - role.queryTemp( "personalBekilled", 0 ) ) )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if selfEntity.queryTemp( "createTime", 0 ) == 0:
			selfEntity.setTemp("createTime", time.time() )
			selfEntity.setTemp( "roleCompetitionStartEnterTime", BigWorld.globalData[ "RoleCompetitionStopSignUpTime" ] )
		if selfEntity.queryTemp( "copyLevel", 0 ) == 0:
			selfEntity.setTemp("copyLevel", params["copyLevel"] )
		endTime =5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 ) + ROLE_COMPETITION_TIME
		baseMailbox.client.onEnterRoleCompetitionSpace( int( endTime ) ,int( 5 * ONE_MINUTE - ( selfEntity.queryTemp("createTime", 0 ) - selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 ) ) ))
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		
		rolesScore = selfEntity.queryTemp( "rolesScore" )
		rolesScore[baseMailbox.id] = [ 0, params["dbID"]]
		
		selfEntity.setTemp( "rolesScore", rolesScore )
		
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			player.setTemp( "stored_pk_mode", player.pkMode )

		enterList = selfEntity.queryTemp( "enterPlayerDBIDs", [] )
		enterList.append( params["dbID"] )
		selfEntity.setTemp( "enterPlayerDBIDs", enterList )
		remainList = selfEntity.queryTemp( "remainPlayerMBs", [] )
		remainList.append( baseMailbox )
		selfEntity.setTemp( "remainPlayerMBs", remainList )
		baseMailbox.client.roleCompetitionStart()

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.setSysPKMode( 0 )
		baseMailbox.client.onLeaveRoleCompetitionSpace()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		isWatchState = params[ "isWatchState" ]
		if isWatchState:
			baseMailbox.cell.onLeaveWatchMode()

		if BigWorld.entities.has_key( baseMailbox.id ):
			roleScore = selfEntity.queryTemp( "rolesScore" )
			BigWorld.globalData["RoleCompetitionMgr"].roleCompetition_Record( roleScore[baseMailbox.id][1], csdefine.MATCH_TYPE_PERSON_COMPETITION, roleScore[baseMailbox.id][0], baseMailbox)
			player = BigWorld.entities[baseMailbox.id]
			player.setTemp( "killPersonalCount", 0 )
			player.setTemp( "killPersonalTime", 0 )
			player.setTemp( "personalBekilled", 0 )
			baseMailbox.client.onStatusMessage(csstatus.ROLE_COMPETITION_OUT, "" )
			pkmode = player.queryTemp( "stored_pk_mode" )
			player.unLockPkMode()
			if pkmode != None:
				player.setPkMode( player.id, pkmode )
				
		remainList = selfEntity.queryTemp( "remainPlayerMBs", [] )
		for index,mailbox in enumerate( remainList):
			if mailbox.id == baseMailbox.id:
				del remainList[ index ]
		selfEntity.setTemp( "remainPlayerMBs", remainList )
		remainList = selfEntity.queryTemp( "remainPlayerMBs", [] )
		if not selfEntity.queryTemp( "hasCloseRoleCompetition" ):
			currentTime = time.time()
			if len( remainList ) == 1 and currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) >= 1:
				if self.getCurrentContent( selfEntity ) == self.contents[1]:
					selfEntity.setTemp( "champion", remainList[0].id)
					if currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) < 5 * 60:
						g_objFactory.getObject( REWARD_BOX1 ).createEntity( selfEntity.spaceID, REWARD_POSITION_1, (0, 0, 0), {} )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_1_NOTICE, [])
						g_objFactory.getObject( REWARD_BOX2 ).createEntity( selfEntity.spaceID, REWARD_POSITION_2, (0, 0, 0) , {} )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_2_NOTICE, [])
						g_objFactory.getObject( REWARD_BOX3 ).createEntity( selfEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :selfEntity.queryTemp( "champion", 0) } } )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
					elif currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) < 15 * 60:
						g_objFactory.getObject( REWARD_BOX2 ).createEntity( selfEntity.spaceID, REWARD_POSITION_2, (0, 0, 0) , {} )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_2_NOTICE, [])
						g_objFactory.getObject( REWARD_BOX3 ).createEntity( selfEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :selfEntity.queryTemp( "champion", 0) } } )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
					elif currentTime - (5 * ONE_MINUTE + selfEntity.queryTemp( "roleCompetitionStartEnterTime", 0 )) < 30 * 60:
						g_objFactory.getObject( REWARD_BOX3 ).createEntity( selfEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {"tempMapping" : { "champion" :selfEntity.queryTemp( "champion", 0) } } )
						for e in remainList:
							e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.ROLE_COMPETITION_BOX_3_NOTICE, [])
					SpaceCopyTemplate.doNextContent( self, selfEntity )


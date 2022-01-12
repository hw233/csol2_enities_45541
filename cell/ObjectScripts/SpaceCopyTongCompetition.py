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
import SpaceCopyTongCompetition
from csconst import FAMILY_COMPETITION_TIME
from csconst import SAVE_MODEL_TIME
from csconst import END_TIME
from ObjectScripts.GameObjectFactory import g_objFactory

TONGCOMPETITION_MEMBER_NUMBER01 = 30
TONGCOMPETITION_MEMBER_NUMBER02 = 15
TONGCOMPETITION_TIME01 = 10 * 60
TONGCOMPETITION_TIME02 = 30 * 60
TONGCOMPETITION_TIME03 = 60 * 60

NOTICE_TIMER01			= 1				# 活动提示
NOTICE_TIMER02			= 2				# 活动提示
NOTICE_TIMER03			= 3				# 活动提示
NOTICE_TIMER04			= 4				# 活动提示
NOTICE_TIMER05			= 5				# 活动提示
NOTICE_TIMER06			= 6				# 活动提示
NOTICE_TIMER07			= 7				# 活动提示


TONG_COMPETITION_SINGLE			= 8			# 活动提示
TONG_COMPETITION_10MIN			= 9			# 活动提示
TONG_COMPETITION_30MIN			= 10		# 活动提示

FISTBOXID				= "10121061"
SECONDBOXID				= "10121062"
THIRDBOXID				= "10121063"

REWARD_POSITION = ( -2.375, 9.01, 16.637)



class CCSaveModelProcess( CopyContent ):
	"""
	#产生5分钟pk保护
	"""
	def __init__( self ):
		"""
		"""
		self.key = "saveProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( SAVE_MODEL_TIME, 0, NEXT_CONTENT )
		spaceEntity.addTimer( SAVE_MODEL_TIME - 120, 0, NOTICE_TIMER01 )
		spaceEntity.addTimer( SAVE_MODEL_TIME - 60, 0, NOTICE_TIMER02 )
		spaceEntity.addTimer( SAVE_MODEL_TIME - 30, 0, NOTICE_TIMER03 )
		spaceEntity.addTimer( SAVE_MODEL_TIME - 20, 0, NOTICE_TIMER04 )
		spaceEntity.addTimer( SAVE_MODEL_TIME - 10, 0, NOTICE_TIMER05 )
		spaceEntity.addTimer( SAVE_MODEL_TIME - 1, 0, TONG_COMPETITION_SINGLE )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )					# 强制所有玩家进入和平模式
		baseMailbox.cell.lockPkMode()														# 锁定pk模式，不能设置

	def endContent( self, spaceEntity ):
		"""
		"""
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		for e in enterPlayerMBList:
			e.cell.setSysPKMode( 0 )
			e.cell.unLockPkMode()
			player = BigWorld.entities[e.id]
			BigWorld.globalData["TongCompetitionMgr"].saveTongMemberInfo( player.getName(), e, player.tong_dbID )
		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( 0 )
		baseMailbox.cell.unLockPkMode()				# 解锁pk模式
		CopyContent.onLeave( self, spaceEntity, baseMailbox, params )

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		if userArg == NOTICE_TIMER01:
			for e in enterPlayerMBList:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_2_MINUTE, "" )

		elif userArg == NOTICE_TIMER02:
			for e in enterPlayerMBList:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_1_MINUTE, "" )

		elif userArg == NOTICE_TIMER03:
			for e in enterPlayerMBList:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_30_SECOND, "" )

		elif userArg == NOTICE_TIMER04:
			for e in enterPlayerMBList:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_20_SECOND, "" )

		elif userArg == NOTICE_TIMER05:
			for e in enterPlayerMBList:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_10_SECOND, "" )

		elif userArg == TONG_COMPETITION_SINGLE:
			tonglist = []
			for e in enterPlayerMBList:
				player = BigWorld.entities[ e.id ]
				tongDBID = player.tong_dbID
				tonglist.append( tongDBID )
			if len( set( tonglist ) ) == 1:
				spaceEntity.base.notifyTongWinner()
				winnerList = spaceEntity.queryTemp( "winnerPlayerDBIDs", [] )
				for e in enterPlayerMBList:
					winnerList.append( e.id )
					role = BigWorld.entities.get( e.id )
					role.statusMessage( csstatus.ROLE_GOTO_BOX3 )
				spaceEntity.setTemp( "winnerPlayerDBIDs", winnerList )
				g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
				#发奖励给冠军帮主
				tongEntity = player.tong_getTongEntity( tongDBID )
				tongEntity.sendAwardToChief()		#发奖励给冠军帮主
				BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
				spaceEntity.setTemp( "JumpToEnd", True )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )


class CCFamilyPKProcess( CopyContent ):
	"""
	帮会竞赛开始
	"""
	def __init__( self ):
		"""
		"""
		self.key = "familyPKProcess"
		self.val = 1

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		if spaceEntity.queryTemp( "JumpToEnd", False ):
			return
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )		# 强制所有玩家进入帮会模式
		baseMailbox.cell.lockPkMode()

	def onContent( self, spaceEntity ):
		"""
		"""
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		for e in enterPlayerMBList:		#显示积分界面
			e.cell.onEnterTongCompetition()
			player = BigWorld.entities.get( e.id )
			leftDeathTimes = 1			# 用于客户端的界面显示
			player.client.onTongCompDeathTimes( leftDeathTimes )
			BigWorld.globalData[ "TongCompetitionID" ] = player.getCurrentSpaceBase().id
		if spaceEntity.queryTemp( "JumpToEnd", False ):
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		for e in enterPlayerMBList:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )
			e.cell.lockPkMode()
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_TONGCOMPETITION_START, [] )
		spaceEntity.setTemp( "endContentTimerID", spaceEntity.addTimer( FAMILY_COMPETITION_TIME, 0, NEXT_CONTENT ) )
		spaceEntity.addTimer( FAMILY_COMPETITION_TIME - 300, 0, NOTICE_TIMER06 )
		spaceEntity.addTimer( FAMILY_COMPETITION_TIME - 600, 0, NOTICE_TIMER07 )
		spaceEntity.addTimer( FAMILY_COMPETITION_TIME - 50 * 60, 0, TONG_COMPETITION_10MIN )		# 比赛开始后到达10分钟时
		spaceEntity.addTimer( FAMILY_COMPETITION_TIME - 30 * 60, 0, TONG_COMPETITION_30MIN )		# 比赛开始后到达30分钟时
		if BigWorld.globalData.has_key( "AS_TongCompetition" ):
			del BigWorld.globalData[ "AS_TongCompetition" ]


	def endContent( self, spaceEntity ):
		"""
		"""
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		if not spaceEntity.queryTemp( "JumpToEnd", False ):
			for e in enterPlayerMBList:
				e.cell.setSysPKMode( 0 )
				e.cell.unLockPkMode()													#解锁pk模式
			awardType = spaceEntity.queryTemp( "AwardType", 0 )
			if awardType == 1:		# 10分钟前决出冠军，刷3个箱子
				g_objFactory.getObject( FISTBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {} )
				g_objFactory.getObject( SECONDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0) , {} )
				g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
			elif awardType == 2:	# 30分钟前决出冠军，刷2个箱子
				g_objFactory.getObject( SECONDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0) , {} )
				g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
			elif awardType == 3:	# 60分钟前决出冠军，刷1个箱子
				g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
			else:
				spaceEntity.base.queryTongWinner()		# 时间到了，判断冠军帮会，给予奖励

		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.client.onStatusMessage( csstatus.TONG_COMPETETION_LEAVE, "" )
		if not spaceEntity.queryTemp( "JumpToEnd", False ):
			baseMailbox.cell.setSysPKMode( 0 )
			baseMailbox.cell.unLockPkMode()

		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		for i, pMB in enumerate( enterPlayerMBList ):
			if pMB.id == baseMailbox.id:
				enterPlayerMBList.pop( i )
		spaceEntity.setTemp( "enterPlayerMB", enterPlayerMBList )
		currentSpaceTime = time.time()
		templist = set([])
		for e in enterPlayerMBList:
				player = BigWorld.entities[ e.id ]
				tongDBID = player.tong_dbID
				templist.add( tongDBID )
		if len( templist ) == 1:
			winnerList = spaceEntity.queryTemp( "winnerPlayerDBIDs", [] )
			for e in enterPlayerMBList:
				winnerList.append( e.id )
			spaceEntity.setTemp( "winnerPlayerDBIDs", winnerList )
			if currentSpaceTime - spaceEntity.queryTemp( "createTime", 0 ) < TONGCOMPETITION_TIME01:		# 10分钟前就已经决出冠军
				for e in enterPlayerMBList:
					role = BigWorld.entities.get( e.id )
					role.statusMessage( csstatus.ROLE_GOTO_BOX1 )
					role.statusMessage( csstatus.ROLE_GOTO_BOX2 )
					role.statusMessage( csstatus.ROLE_GOTO_BOX3 )
				spaceEntity.setTemp( "AwardType", 1 )
				spaceEntity.cancel( spaceEntity.queryTemp("endContentTimerID") )
				#发奖励给冠军帮主
				spaceEntity.base.notifyTongWinner()
				tongEntity = player.tong_getTongEntity( tongDBID )
				tongEntity.sendAwardToChief()
				BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
				spaceEntity.addTimer( 0, 0, NEXT_CONTENT )

			elif currentSpaceTime - spaceEntity.queryTemp( "createTime", 0 ) < TONGCOMPETITION_TIME02:		# 30分钟前就已经决出冠军
				for e in enterPlayerMBList:
					role = BigWorld.entities.get( e.id )
					role.statusMessage( csstatus.ROLE_GOTO_BOX2 )
					role.statusMessage( csstatus.ROLE_GOTO_BOX3 )
				spaceEntity.setTemp( "AwardType", 2 )
				spaceEntity.cancel( spaceEntity.queryTemp("endContentTimerID") )
				#发奖励给冠军帮主
				spaceEntity.base.notifyTongWinner()
				tongEntity = player.tong_getTongEntity( tongDBID )
				tongEntity.sendAwardToChief()
				BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
				spaceEntity.addTimer( 0, 0, NEXT_CONTENT )

			elif currentSpaceTime - spaceEntity.queryTemp( "createTime", 0 ) < TONGCOMPETITION_TIME03:		# 60分钟前就已经决出冠军
				for e in enterPlayerMBList:
					role = BigWorld.entities.get( e.id )
					role.statusMessage( csstatus.ROLE_GOTO_BOX3 )
				spaceEntity.setTemp( "AwardType", 3 )
				spaceEntity.cancel( spaceEntity.queryTemp("endContentTimerID") )
				#发奖励给冠军帮主
				spaceEntity.base.notifyTongWinner()
				tongEntity = player.tong_getTongEntity( tongDBID )
				tongEntity.sendAwardToChief()
				BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
				spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
		if baseMailbox in enterPlayerMBList:		# 非隐身观战的玩家退出游戏时，保留一份数据用于奖励
			BigWorld.globalData["TongCompetitionMgr"].saveLeaveTongMember( BigWorld.entities[ baseMailbox.id ].getName() )
		CopyContent.onLeave( self, spaceEntity, baseMailbox, params )


	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		if userArg == NOTICE_TIMER06:
			for e in enterPlayerMBList:
				e.client.onStatusMessage( csstatus.FAMILYPK_OVER_IN_5_MINUTE, "" )

		elif userArg == NOTICE_TIMER07:
			for e in enterPlayerMBList:
				deathCount = 1
				e.client.onStatusMessage( csstatus.FAMILYPK_OVER_IN_10_MINUTE, "" )
				e.cell.setTemp( "personaldeathCount", deathCount )
				player = BigWorld.entities.get( e.id )
				leftDeathTimes = 0			# 用于客户端的界面显示
				player.client.onTongCompDeathTimes( leftDeathTimes )

		elif userArg == TONG_COMPETITION_10MIN:
			if len( enterPlayerMBList ) <= TONGCOMPETITION_MEMBER_NUMBER01:
				for e in enterPlayerMBList:
					role = BigWorld.entities.get( e.id )
					role.statusMessage( csstatus.ROLE_GOTO_BOX1 )
				g_objFactory.getObject( FISTBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {} )

		elif userArg == TONG_COMPETITION_30MIN:
			if len( enterPlayerMBList ) <= TONGCOMPETITION_MEMBER_NUMBER02:
				for e in enterPlayerMBList:
					role = BigWorld.entities.get( e.id )
					role.statusMessage( csstatus.ROLE_GOTO_BOX2 )
				g_objFactory.getObject( SECONDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {} )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

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
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		for e in enterPlayerMBList:
			e.client.onStatusMessage( csstatus.ACTIVITY_IS_OVER, "" )
			e.client.onStatusMessage( csstatus.ACTIVITY_WILL_OVER_IN_2_MINUTE, "" )
			e.cell.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )			# 无敌状态
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			e.cell.lockPkMode()

		spaceEntity.addTimer( END_TIME, 0, NEXT_CONTENT )

	def endContent( self, spaceEntity ):
		"""
		"""
		enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
		for e in enterPlayerMBList:
			e.cell.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
			e.cell.setSysPKMode( 0 )
		spaceEntity.setTemp( "enterPlayerMB", [] )
		spaceEntity.setTemp( "winnerPlayerDBIDs", [] )
		spaceEntity.setTemp( "enterPlayerDBIDs", [] )
		CopyContent.endContent( self, spaceEntity )
		BigWorld.globalData["TongCompetitionMgr"].onEnd()

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		baseMailbox.client.onFamilyCompetitionEnd()


class SpaceCopyTongCompetition( SpaceCopyTemplate ):
	"""
	帮会竞技
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
		self.contents.append( CCFamilyPKProcess() )
		self.contents.append( CCEndProcess() )
		self.contents.append( CCKickPlayersProcess() )

	def packedDomainData( self, player ):
		"""
		"""
		level = player.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
		data = {"copyLevel" 		: 	level/1000,
				"dbID" 				: 	player.databaseID,
				"tongDBID"			: 	player.tong_dbID,
				"tongName"			: 	player.tongName,
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
		
		packDict[ "copyLevel" ] = level/1000
		packDict[ "dbID" ] = player.databaseID
		packDict[ "tongDBID" ] = player.tong_dbID
		packDict[ "tongName" ] = player.tongName
		return packDict

	def onRoleDie( self, role, killer ):
		"""
		virtual method
		帮会竞技
		"""
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			killer = BigWorld.entities.get( killer.ownerID, None )
			if killer is None:
				return

		killer.client.onStatusMessage( csstatus.REWARD_TONGSCORE_FOR_KILL_ONE_ENEMY, "" )
		deathCount= role.queryTemp( "personaldeathCount", 0 )
		role.setTemp( "personaldeathCount", deathCount + 1 )
		leftDeathTimes = 0		# 用于客户端的界面显示
		role.client.onTongCompDeathTimes( leftDeathTimes )
		tongAwardExp = ( int( pow ( killer.level, 1.2 ) * 5 ) + 25 ) * 70		# 参与奖
		killer.addTongScore( 1 )
		killer.addExp( tongAwardExp, csdefine.CHANGE_EXP_TONGCOMPETITION )

		if role.queryTemp( "personaldeathCount", 0 ) < 2:
			role.client.onStatusMessage( csstatus.LOST_FOR_BE_KILL, "" )
			role.client.challengeOnDie( 0 )		# 弹出复活对话框
			role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
			role.addTimer( 10, 0, ECBExtend.ROLE_REVIVE_TIMER )
		elif role.queryTemp( "personaldeathCount", 0 ) >= 2:		# 第二次死亡把玩家传出副本
			#加入一个隐身的观战buff，玩家点击“是”就可以留下来继续观战，“否”就会被传出副本
			role.client.challengeOnDie( 1 )		# 弹出观战选择对话框
			spaceEntity = BigWorld.entities[role.getCurrentSpaceBase().id]
			spaceEntity.base.removePlayer( role )
			enterPlayerMBList = spaceEntity.queryTemp( "enterPlayerMB", [] )
			role.setTemp( "role_die_teleport", True )		# 设置临时死亡标记
			role.setTemp( "role_die",True )		# 设置副本内不能再复活的标记
			for i, pMB in enumerate( enterPlayerMBList ):
				if pMB.id == role.id:
					enterPlayerMBList.pop( i )
			spaceEntity.setTemp( "enterPlayerMB", enterPlayerMBList )
			currentSpaceTime = time.time()
			templist = set([])
			for e in enterPlayerMBList:
				player = BigWorld.entities[ e.id ]
				tongDBID = player.tong_dbID
				templist.add( tongDBID )
			if len( templist ) == 1:
				winnerList = spaceEntity.queryTemp( "winnerPlayerDBIDs", [] )
				for e in enterPlayerMBList:
					winnerList.append( e.id )
				spaceEntity.setTemp( "winnerPlayerDBIDs", winnerList )
				if currentSpaceTime - spaceEntity.queryTemp( "createTime", 0 ) < TONGCOMPETITION_TIME01:		# 10分钟前就已经决出冠军
					for e in enterPlayerMBList:
						player = BigWorld.entities.get( e.id )
						player.statusMessage( csstatus.ROLE_GOTO_BOX1 )
						player.statusMessage( csstatus.ROLE_GOTO_BOX2 )
						player.statusMessage( csstatus.ROLE_GOTO_BOX3 )
					g_objFactory.getObject( FISTBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {} )
					g_objFactory.getObject( SECONDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0) , {} )
					g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
					#发奖励给冠军帮主
					spaceEntity.base.notifyTongWinner()
					tongEntity = player.tong_getTongEntity( tongDBID )
					tongEntity.sendAwardToChief()
					BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
					SpaceCopyTemplate.doNextContent( self, spaceEntity )

				elif currentSpaceTime - spaceEntity.queryTemp( "createTime", 0 ) < TONGCOMPETITION_TIME02:		# 30分钟前就已经决出冠军
					for e in enterPlayerMBList:
						player = BigWorld.entities.get( e.id )
						player.statusMessage( csstatus.ROLE_GOTO_BOX2 )
						player.statusMessage( csstatus.ROLE_GOTO_BOX3 )
					g_objFactory.getObject( SECONDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0) , {} )
					g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
					#发奖励给冠军帮主
					spaceEntity.base.notifyTongWinner()
					tongEntity = player.tong_getTongEntity( tongDBID )
					tongEntity.sendAwardToChief()
					BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
					SpaceCopyTemplate.doNextContent( self, spaceEntity )

				elif currentSpaceTime - spaceEntity.queryTemp( "createTime", 0 ) < TONGCOMPETITION_TIME03:		# 60分钟前就已经决出冠军
					for e in enterPlayerMBList:
						player = BigWorld.entities.get( e.id )
						player.statusMessage( csstatus.ROLE_GOTO_BOX3 )
					g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :spaceEntity.queryTemp( "winnerPlayerDBIDs", 0) } } )
					#发奖励给冠军帮主
					spaceEntity.base.notifyTongWinner()
					tongEntity = player.tong_getTongEntity( tongDBID )
					tongEntity.sendAwardToChief()
					BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )
					SpaceCopyTemplate.doNextContent( self, spaceEntity )

			BigWorld.globalData["TongCompetitionMgr"].saveLeaveTongMember( BigWorld.entities[ role.id ].getName() )
			
		role.getCurrentSpaceBase().onRoleDied( role.id, role.tong_dbID, killer.id, killer.tong_dbID )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if selfEntity.queryTemp( "createTime", 0 ) == 0:
			selfEntity.setTemp("createTime", time.time() )
		endTime = selfEntity.queryTemp( "createTime", 0 ) + FAMILY_COMPETITION_TIME + SAVE_MODEL_TIME
		baseMailbox.client.onEnterFamilyCompetitionSpace( int( endTime ) )
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
		baseMailbox.cell.lockPkMode()
		enterList = selfEntity.queryTemp( "enterPlayerDBIDs", [] )
		enterList.append( params["dbID"] )
		selfEntity.setTemp( "enterPlayerDBIDs", enterList )
		enterPlayerMBList = selfEntity.queryTemp( "enterPlayerMB", [] )
		enterPlayerMBList.append( baseMailbox )
		selfEntity.setTemp( "enterPlayerMB", enterPlayerMBList )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		BigWorld.globalData[ "tongComPlayerDBID" ] = BigWorld.entities[ baseMailbox.id ].databaseID	# 记录下玩家dbid，用于离线玩家的积分记录
		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.setSysPKMode( 0 )
		baseMailbox.cell.onLeaveTeamCompetition()
		baseMailbox.client.onLeaveFamilyCompetitionSpace()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			player.removeTemp( "personaldeathCount")
			player.removeTemp( "role_die_teleport" )
			player.removeTemp( "role_die" )
		enterPlayerMBList = selfEntity.queryTemp( "enterPlayerMB", [] )
		for i, pMB in enumerate( enterPlayerMBList ):
			if pMB.id == baseMailbox.id:
				enterPlayerMBList.pop( i )
		selfEntity.setTemp( "enterPlayerMB", enterPlayerMBList )


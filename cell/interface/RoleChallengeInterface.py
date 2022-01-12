# -*- coding: gb18030 -*-
import time
import math
import random

from bwdebug import *
import BigWorld
import Math
import Const
import ECBExtend
import csdefine
import csconst
import csstatus
import cschannel_msgs

from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()

CHAMPION_REWARD_ITEM_TEAM_CHALLENGE = 60101244 # 组队竞技冠军奖励包
CHAMPION_REWARD_ITEM_WU_DAO			= 60101246 # 武道大会冠军奖励包
SKILL_ID1	= 322528001

class RoleChallengeInterface:
	# 竞技公用接口,包括“个人竞技”、“组队竞技”、“帮会擂台”、“组队擂台”、“武道大会”、“帮会车轮战”, "阵营车轮战场", "鏖战群雄", "阵营烽火连天"
	def __init__( self ):
		pass
	
	def onCellReady( self ):
		self.aoZhan_playerInit()

	def challengeActivityTransmit( self, type ):
		# define method
		# 活动传送,包括集合/传出
		if csconst.TRANSMIT_SPACE_INFOS.has_key( type ):
			self.gotoSpace( csconst.TRANSMIT_SPACE_INFOS[ type ][ 0 ], Math.Vector3( csconst.TRANSMIT_SPACE_INFOS[ type ][ 1 ]) + ( random.randint(-2,2), 0, random.randint(-2,2) ), Math.Vector3( csconst.TRANSMIT_SPACE_INFOS[ type ][ 2 ]) )

	def challengeSetFlagGather( self, type ):
		# define method
		# 设置活动传送标志
		self.challengeGatherFlags = self.challengeGatherFlags | ( 1 << type )

	def challengeRemoveFlagGather( self, type ):
		# define method
		# 关闭活动传送标志
		self.challengeGatherFlags = self.challengeGatherFlags &~ ( 1 << type )

	def challengeHasFlagGather( self, type ):
		# 查询集合标志
		return self.challengeGatherFlags & ( 1 << type )
	
	def onDestroy( self ):
		# 玩家下线
		BigWorld.globalData[ "TeamChallengeMgr" ].playerDestroy( self.base )
		self.aoZhan_playerDestroy()
	
	def changePosAndDir( self, position, tarPos ):
		"""
		define method
		变化位置并朝向一个目标点
		
		@param position: VECTOR3 要到达的位置
		@param tarPos: VECTOR3 朝向的位置
		"""
		disDir = tarPos - position
		direction = (0,0,disDir.yaw)
		self.teleport( None, position, direction )
		self.client.unifyYaw()

	#--------------------------------------------------------------------
	# 组队擂台
	#--------------------------------------------------------------------
	def challengeTeamSignUp( self, exposed ):
		# 组队擂台报名
		# define method
		if not self.hackVerify_( exposed ):
			return

		if not self.isTeamCaptain():
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_CAPTAIN, "" )
			return

		if len( self.teamMembers ) < csconst.TEAM_CHALLENGE_MEMBER_MUST:
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_MEM_LESS, "" )
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# 死亡
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# 战斗
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		BigWorld.globalData[ "TeamChallengeMgr" ].signUp( self.teamMailbox.id, self.level, self.base )

	def challengeTeamRequestSub( self, exposed ):
		# 申请加入组队擂台候补名单
		# define method
		if not self.hackVerify_( exposed ):
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# 监狱
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return
			
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			# 不在普通地图
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_SPACE_COPY, "" )
			return
			
		if self.isInTeam():
			# 组队
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# 死亡
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# 战斗
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		BigWorld.globalData[ "TeamChallengeMgr" ].substitutePlayer( self.base, self.level )
	
	def challengeTeamCancelSub( self, exposed ):
		# 退出组队擂台候补名单
		# define method
		BigWorld.globalData[ "TeamChallengeMgr" ].calcelSubstitute( self.base )

	def challengeTeamRecruit( self,exposed ):
		# 队伍申请组队擂台招募
		# exposed method
		if not self.hackVerify_( exposed ):
			return

		if not self.isTeamCaptain():
			return

		if len( self.teamMembers ) >= csconst.TEAM_MEMBER_MAX:
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_TEAM_FULL, "" )
			return

		recruitNum = csconst.TEAM_MEMBER_MAX - len( self.teamMembers )

		BigWorld.globalData[ "TeamChallengeMgr" ].recruitTeam( self.teamMailbox, self.base, self.level, recruitNum )
	
	def challengeTeamCancelRecruit( self, exposed ):
		# exposed method
		# 队伍取消组队擂台招募
		BigWorld.globalData[ "TeamChallengeMgr" ].cancelRecruitTeam( self.teamMailbox )

	def challengeTeamRecruitResult( self, exposed, teamID, result ):
		# 返回招募结果
		# exposed method
		if not self.hackVerify_( exposed ):
			return
					
		if result:
			if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON:
				# 监狱
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
				
			elif self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
				# 不在普通地图
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_SPACE_COPY, "" )
				
			elif self.isInTeam():
				# 组队
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM, "" )

			elif self.getState() == csdefine.ENTITY_STATE_DEAD:
				# 死亡
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )

			elif self.getState() == csdefine.ENTITY_STATE_FIGHT:
				# 战斗
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			else:
				BigWorld.globalData[ "TeamManager" ].teamChallengeAddMember(\
					teamID, self.databaseID, self.playerName, self.level, self.base, self.raceclass, self.headTextureID\
				)
				self.client.challengeTeamBeRecruitComplete()
		else:
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_CANCEL, "" )
			BigWorld.globalData[ "TeamChallengeMgr" ].recruitRresult( self.base, self.level, self.teamMailbox.id, False )

	def challengeTeamReward( self, type, arg ):
		# 组队擂台奖励
		# define method
		if type ==  csconst.TEAM_CHALLENGE_REWARD_COMMON:
			rewardExp = int( 2106 * ( 25 + 5 * self.level ** 1.2 ) )
			self.addExp( rewardExp, csdefine.CHANGE_EXP_TEAM_CHALLENGE )
		elif type == csconst.TEAM_CHALLENGE_REWARD_WIN:
			rewardExp = int( 50 * ( 25 + 5 * self.level ** 1.2 ) * ( 4 * arg + 6 ) )
			self.addExp( rewardExp, csdefine.CHANGE_EXP_TEAM_CHALLENGE )

	def teamChallengeSetChampion( self, rewardTime ):
		# 设置组队擂台冠军
		# define method
		self.set( "teamChallengeChampion", ( rewardTime, False ) )

	def teamChallengeGather( self, exposed ):
		# 组队擂台集合
		# Exposed method.
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return

		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )
	
	def teamChallengeOnDieResult( self, exposed, result ):
		# 组队擂台死亡是否观战结果返回
		# Exposed method
		if not self.hackVerify_( exposed ):
			return
		
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_TEAM_CHALLENGE:
			return
			
		if result:
			self.onEnterWatchMode()
			self.getCurrentSpaceBase().cell.addWatchPlayer( self.teamMailbox.id, self.base)
		else:
			self.onLeaveWatchMode()
			self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	#--------------------------------------------------------------------
	# 武道大会
	#--------------------------------------------------------------------
	def wuDaoSignUp( self, exposed ):
		# 武道大会报名
		# Exposed method.
		if not self.hackVerify_( exposed ):
			return
			
		if self.level < 60:
			statusMessage( csstatus.ROLE_HAS_NOT_WUDAO_LEVEL, self._param1 )
			
		BigWorld.globalData['WuDaoMgr'].requestSignUp( self.level, self.base, self.databaseID )
		
	def wuDaoReward( self, round, step, isWinner ):
		# 处理武道大会奖励
		# define method
		if isWinner:
			self.addExp( int( 35 * ( 25 + 5 * self.level ** 1.2 ) * ( 4 * round + 6 ) ), csdefine.CHANGE_EXP_WUDAOAWARD )

	def wuDaoNoticeChampion( self, step, rewardTime ):
		# 通知赛段决出冠军
		# define method
		self.sysBroadcast( cschannel_msgs.CELL_ROLEQUESTINTERFACE_1 %( self.getName(), step*10, step*10+9 ) )
		self.set( "wuDaoChampion", ( rewardTime, False ) )

	def wuDaoGather( self, exposed ):
		# 武道大会集合
		# Exposed method.
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_WUDAO ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return

		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_WUDAO )

	#--------------------------------------------------------------------
	# 帮会擂台
	#--------------------------------------------------------------------
	def tongAbaSignUp( self,exposed ):
		"""
		exposed method
		
		报名帮会擂台
		"""
		if not self.hackVerify_( exposed ):
			return
		if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_ABA ):	# 不是帮主或副帮主,客户端也需判断
			self.onStatusMessage( csstatus.TONG_ABATTOIR_NOT_LEADER,"" )
			return
		self.tong_dlgAbattoirRequest()
		
	def tongAbaGather( self, exposed ):
		"""
		帮会擂台集合
		"""
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return
		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TONG_ABA )

	#--------------------------------------------------------------------
	# 组队竞技
	#--------------------------------------------------------------------
	def teamCompetitionSignUp( self,exposed ):
		"""
		exposed method

		组队竞技报名接口,用于竞技界面
		"""
		if self.level < 60:
			self.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_LEVEL, str(( 60, )) )
			return

		if not self.isInTeam():
			self.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_TEAM, "" )
			return

		if not self.isTeamCaptain():
			self.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_CAPTAIN, "" )
			return

		if not len( self.teamMembers ) >= 3 :
			self.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_AMOUNT,"" )
			return
		self.client.teamCompetitionCheck( 60 )

	def teamCompetitionCheckOK( self, exposed ):
		"""
		exposed method

		组队竞技队伍资格验证
		"""
		if not self.hackVerify_( exposed ):
			return

		level = self.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1

		BigWorld.globalData["TeamCompetitionMgr"].requestTeamCompetition( self.base, level/10, self.teamMailbox )

	def teamCompetitionGather( self, exposed ):
		"""
		组队竞技集合
		"""
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return
		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	#--------------------------------------------------------------------
	# 帮会竞技
	#--------------------------------------------------------------------
	def tongCompetitionGather( self, exposed ):
		"""
		exposed method
		帮会竞技集合
		"""
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return
		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TONG_COMPETITION )

	def tongCompetitionSignUp( self, exposed ):
		"""
		exposed method
		帮会竞技报名接口
		"""
		if not self.hackVerify_( exposed ):
			return

		allowSignUp = BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" )
		if allowSignUp:
			if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_COMPETITION ):	# 报名人必须是帮主或者是副帮主
				self.statusMessage( csstatus.TONG_COMPETETION_NOTICE_2 )
				return
			else:
				self.tong_competitionRequest( self )
		else:
			self.statusMessage( csstatus.TONG_COMPETETION_TONG_SIGNUP )

	#--------------------------------------------------------------------
	# 个人竞技
	#--------------------------------------------------------------------
	def roleCompetitionGather( self, exposed ):
		"""
		exposed method
		个人竞技集合
		"""
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_ROLE_COMPETITION ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return

		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_ROLE_COMPETITION )

	def roleCompetitionSignUp( self, exposed ):
		"""
		exposed method
		个人竞技报名接口
		"""
		if not self.hackVerify_( exposed ):
			return

		if BigWorld.globalData.has_key("AS_RoleCompetitionSignUp"):
			BigWorld.globalData["RoleCompetitionMgr"].requestSignUp( self.level, self.base, self.playerName)
			return
		elif BigWorld.globalData.has_key("AS_RoleCompetitionReady"):
			self.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_4, "" )
			return
		else:
			self.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_6, "" )
			return

	def roleCompetitionOnDieResult( self, exposed, result ):
		"""
		exposed method
		根据不同的选择执行不同的操作
		"""
		if not self.hackVerify_( exposed ):
			return
		if result == True:
			self.onEnterWatchMode()
		else:
			self.reviveOnOrigin()
			self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_ROLE_COMPETITION )
		
	def onEnterWatchMode( self ):
		# 进入观战状态
		self.reviveOnOrigin()
		self.effectStateInc( csdefine.EFFECT_STATE_DEAD_WATCHER )
		self.spellTarget( SKILL_ID1, self.id )

		
	def onLeaveWatchMode( self ):
		# define method
		# 退出观战状态
		self.effectStateDec( csdefine.EFFECT_STATE_DEAD_WATCHER )
		
	#---------------------------------------------------------------------
	#帮会车轮战
	#---------------------------------------------------------------------
	def turnWar_signUp( self, srcEntityID, memberMaxLevel, cityName ):
		"""
		Exposed method
		报名车轮战
		
		param memberMaxLevel:队伍中的最高等级
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["TongManager"].signUp( self.teamMailbox, self.base, memberMaxLevel, self.tong_dbID, self.getCamp(), cityName, self.playerName )
		
	def turnWar_onPrepared( self, srcEntityID ):
		"""
		Exposed method
		队员准备好了
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["TongManager"].onTeamMemberPrepared( self.teamMailbox.id, self.databaseID, self.playerName )
		
	def turnWar_onEnterSpace( self, srcEntityID ):
		"""
		Exposed method
		点击出战,将玩家传入车轮战space
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["TongManager"].requestEnterSpace( self.teamMailbox.id, self.base, self.playerName )
		
	def turnWar_setJoinFlag( self, isJoin ):
		"""
		define method
		只在队长身上设置参加车轮战的标记,限制他加队友
		"""
		self.turnWar_isJoin = isJoin
	
	#---------------------------------------------------------------------
	#阵营车轮战
	#---------------------------------------------------------------------
	def campTurnWar_signUp( self, srcEntityID, memberMaxLevel, cityName ):
		"""
		Exposed method
		报名车轮战
		
		param memberMaxLevel:队伍中的最高等级
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["CampMgr"].turnWar_signUp( self.teamMailbox, self.base, memberMaxLevel, self.getCamp(), cityName, self.playerName )
		
	def campTurnWar_onPrepared( self, srcEntityID ):
		"""
		Exposed method
		队员准备好了
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["CampMgr"].turnWar_onTeamMemberPrepared( self.teamMailbox.id, self.databaseID, self.playerName )
		
	def campTurnWar_onEnterSpace( self, srcEntityID ):
		"""
		Exposed method
		点击出战,将玩家传入车轮战space
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["CampMgr"].turnWar_requestEnterSpace( self.teamMailbox.id, self.base, self.playerName )
		
	def campTurnWar_setJoinFlag( self, isJoin ):
		"""
		define method
		只在队长身上设置参加车轮战的标记,限制他加队友
		"""
		self.turnWar_isJoin = isJoin
	
	#---------------------------------------------------------------------
	#鏖战群雄
	#---------------------------------------------------------------------
	def aoZhan_playerInit( self ):
		"""
		角色上线
		"""
		if self.aoZan_checkJoinFlag():
			BigWorld.globalData[ "AoZhanQunXiongMgr" ].playerInit( self.databaseID,  self.base )
		else:
			if BigWorld.globalData.has_key( "ACTIVITY_AO_ZHAN_SIGN_UP" ):
				self.client.aoZhan_startSignUp()
	
	def aoZhan_playerDestroy( self ):
		"""
		角色下线
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].playerDestroy( self.databaseID )
	
	def aoZhan_signup( self, exposed ):
		"""
		exposed meothod.
		报名
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].onSignUp( self.base, self.databaseID, self.getName(), self.getLevel(), self.getClass() )
	
	def aoZhan_onSignUp( self ):
		"""
		define method.
		报名成功
		"""
		self.client.aoZhan_onSignUp()
	
	def aoZhan_setJoinFlag( self, uuid ):
		"""
		define method
		设置参与标志
		"""
		self.set( "ACTIVITY_%d"%csdefine.ACTIVITY_AO_ZHAN_QUN_XIONG, uuid ) #策划要求10分钟后关
		self.client.aoZhan_setIsJoin( True )
	
	def aoZhan_removeJoinFlag( self ):
		"""
		define method
		删除参与标志
		"""
		self.remove( "ACTIVITY_%d"%csdefine.ACTIVITY_AO_ZHAN_QUN_XIONG )
		self.client.aoZhan_setIsJoin( False )
	
	def aoZan_checkJoinFlag( self ):
		"""
		检查是否参与
		"""
		activityUUID =  self.query( "ACTIVITY_%d"%csdefine.ACTIVITY_AO_ZHAN_QUN_XIONG, "" )
		if BigWorld.globalData.has_key( "ACTIVITY_AO_ZHAN_UUID" ):
			if activityUUID == BigWorld.globalData[ "ACTIVITY_AO_ZHAN_UUID" ]:
				self.client.aoZhan_setIsJoin( True )
				return True
		
		self.remove( "ACTIVITY_%d"%csdefine.ACTIVITY_AO_ZHAN_QUN_XIONG )
		return False

	def aoZhan_getSignUpList( self, exposed ):
		"""
		exposed method.
		请求报名名单
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].getSignUpList( self.base )

	def aoZhan_flushBattlefield( self, exposed ):
		"""
		exposed method.
		请求刷新战绩
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].getBattlefield( self.base )
	
	def aoZhan_gotoEnterNPC( self, exposed ):
		"""
		exposed method
		传送到进入NPC
		"""
		if not self.hackVerify_( exposed ):
			return
			
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_AO_ZHAN_QUN_XIONG:
			self.gotoSpace( "fengming", ( 190.8, 10.4, 160.4 ), ( 0.007, 0.999, 0.034 ) )
			
	#---------------------------------------------------------------------
	#阵营烽火连天
	#---------------------------------------------------------------------
	def onRequestTransportCampFengHuo( self, srcEntityID ):
		"""
		玩家请求传送
		"""
		if not self.hackVerify_( srcEntityID ):
			return
			
		BigWorld.globalData[ "CampMgr" ].onRoleRequestEnterCampFHLT( self.getCamp(), self.databaseID, self.base )
		
	def camp_onFengHuoLianTianOver( self ):
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# 改变状态,满血满魔
				self.reviveActivity()
			
		
		self.client.camp_onFengHuoLianTianOver()
		
	def camp_leaveFengHuoLianTian( self ):
		enterInfos = self.query( "CampFengHuoLianTianEnterInfos" )
		if enterInfos:
			self.gotoSpace( enterInfos[ 0 ], enterInfos[ 1 ], enterInfos[ 2 ] )
			self.remove( "CampFengHuoLianTianEnterInfos" )
		else:
			self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
		
	def activity_gainMoney( self, money, reason ):
		"""
		define method
		活动或者副本奖励金钱
		"""
		self.gainMoney( money, reason )
	
	def setCampFengHuo_signUpFlag( self, state ):
		"""
		define method
		设置阵营烽火连天报名状态
		"""
		DEBUG_MSG( "player id is %s,state is %s"%( self.id, state ) )
		self.campFengHuo_signUpFlag = state
		self.client.setCampFengHuo_signUpFlag( state )
		
	def setCampFengHuoBattleInfo( self, remainTime, battleNum, maxNum ):
		"""
		define method
		设置玩家的报名战场数字和目前已开的最大战场数字
		"""
		DEBUG_MSG( "player id is %s,battleNum is %s,maxNum is %s"%( self.id, battleNum, maxNum ) )
		self.set( "campFengHuo_battleNum", battleNum )
		self.set( "campFengHuo_maxNum", maxNum )
		self.client.setCampFengHuoBattleInfo( remainTime, battleNum, maxNum )
		
	def updateCampFengHuoInfo( self ):
		DEBUG_MSG( "id is %s, campFengHuo_signUpFlag is %s"%( self.id, self.campFengHuo_signUpFlag ) )
		if BigWorld.globalData.has_key( "campFengHuo_startSignUp" ) and BigWorld.globalData[ "campFengHuo_startSignUp" ] and self.campFengHuo_signUpFlag:
			BigWorld.globalData[ "CampMgr" ].onRequestCampFengHuoSignUp( self.getCamp(), self.databaseID, self.base )
			self.client.setCampFengHuo_signUpFlag( self.campFengHuo_signUpFlag )
		
	def updateCampFengHuoBattleInfo( self, maxNum ):
		"""
		更新最大战场数字信息
		"""
		DEBUG_MSG( "player id is %s,maxNum is %s"%( self.id, maxNum ) )
		self.set( "campFengHuo_maxNum", maxNum )
		
	def isOnlineShowCampFengHuoInfo( self, srcEntityID ):
		"""
		是否上线显示阵营烽火连天战场相关信息
		"""
		if not self.hackVerify_( srcEntityID ):
			return
			
		if BigWorld.globalData.has_key( "campFengHuo_startSignUp" ) and BigWorld.globalData[ "campFengHuo_startSignUp" ] and self.campFengHuo_signUpFlag:
			battleNum = self.query( "campFengHuo_battleNum", 0 )
			maxNum = self.query( "campFengHuo_maxNum", 0 )
			if battleNum and maxNum:
				self.client.setCampFengHuoBattleInfo( BigWorld.globalData[ "campFengHuoSignUpTime" ] - time.time(), battleNum, maxNum )
				self.client.setCampFengHuo_signUpFlag( self.campFengHuo_signUpFlag )
			
	def onRequestQuitCampFengHuoSignUp( self, srcEntityID ):
		"""
		玩家请求退出阵营烽火连天报名
		"""
		if not self.hackVerify_( srcEntityID ):
			return
			
		BigWorld.globalData[ "CampMgr" ].onRequestCampFengHuoQuitSignUp( self.getCamp(), self.databaseID, self.base )
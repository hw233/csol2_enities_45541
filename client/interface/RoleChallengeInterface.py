# -*- coding: gb18030 -*-
import BigWorld
import copy
import csdefine
import csconst
import csstatus
import Define
import event.EventCenter as ECenter
import cschannel_msgs
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
from gbref import rds
from bwdebug import *

class RoleChallengeInterface:
	# 竞技公用接口,包括“个人竞技”、“组队竞技”、“帮会擂台”、“组队擂台”、“武道大会”、“帮会车轮战”, "阵营车轮战"， "鏖战群雄", "阵营烽火连天"
	def __init__( self ):
		#竞技等级段
		self.levelSteps = { csdefine.MATCH_TYPE_PERSON_COMPETITION:( 0, 0 ),
					csdefine.MATCH_TYPE_TEAM_COMPETITION:( 0, 0 ),
					csdefine.MATCH_TYPE_TONG_COMPETITION:( 0, 0 ),
					csdefine.MATCH_TYPE_PERSON_ABA:( 0, 0 ),
					csdefine.MATCH_TYPE_TEAM_ABA:( 0, 0 ),
					csdefine.MATCH_TYPE_TONG_ABA:( 0, 0 ),
				}

		#各擂台比赛阶段结果
		self.matchResults = {csdefine.MATCH_TYPE_PERSON_ABA:csdefine.MATCH_LEVEL_NONE,
					csdefine.MATCH_TYPE_TEAM_ABA:csdefine.MATCH_LEVEL_NONE,
					csdefine.MATCH_TYPE_TONG_ABA:csdefine.MATCH_LEVEL_NONE,
				}

		self.campTurnWar_isSignUp = False
		self.campFengHuo_signUpFlag = False
		
	def challengeHasFlagGather( self, type ):
		# 查询集合标志
		return self.challengeGatherFlags & ( 1 << type )

	#--------------------------------------------------------------------
	# 组队擂台
	#--------------------------------------------------------------------
	def challengeTeamSignUp( self ):
		# define method
		# 组队擂台报名
		if not self.isCaptain():
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_CAPTAIN, "" )
			return

		if self.level < csconst.TEAM_CHALLENGE_JOIN_LEVEL_MIN:
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_MUST_LEVEL, "" )
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# 监狱
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# 死亡
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# 战斗
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		minLevel = self.level / 10 * 10
		maxLevel = minLevel + csconst.TEAM_CHALLENGE_JOIN_LEVEL_INCREASE
		if maxLevel + 1 == csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX: # 例如150级的玩家归到140 - 149等级段
			maxLevel += 1

		for mID, member in self.teamMember.iteritems():
			if mID == self.id:
				continue

			if member.level < minLevel or member.level > maxLevel:
				self.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_LEVEL_ERR, "" )
				return

		self.cell.challengeTeamSignUp()

	def challengeTeamRequestSub( self ):
		# 申请加入组队擂台的替补名单
		if self.isInTeam():
			# 已经有队伍
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM, "" )
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# 监狱
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# 死亡
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# 战斗
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		self.cell.challengeTeamRequestSub()

	def challengeTeamCancelSub( self ):
		# 组队擂台退出替补名单
		self.cell.challengeTeamCancelSub()

	def challengeTeamOnCancelSub( self ):
		# 组队擂台退出替补名单回调
		# Defined
		pass

	def challengeTeamRecruit( self ):
		# 队伍申请组队擂台招募
		if not self.isCaptain():
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_CAPTAIN, "" )
			return

		if len( self.teamMember ) == csconst.TEAM_MEMBER_MAX:
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_TEAM_FULL, "" )
			return

		self.cell.challengeTeamRecruit()

	def challengeTeamCancelRecruit( self ):
		# 队伍取消组队擂台招募
		self.cell.challengeTeamCancelRecruit()

	def teamChallengeOnCRecruit( self ):
		# define method
		# 队伍取消组队擂台招募 通知
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_ON_RECRUIT_CANCEL" )

	def challengeTeamGather( self, round ):
		#define method
		# 组队擂台集合
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TEAM_ABA )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.teamChallengeGather()

		msg = mbmsgs[0x0ee1] % round
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def teamChallengeOnRecruit( self ):
		# define method
		# 组队擂台，队伍已加招募列表
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_ON_RECRUIT" )

	def teamChallengeRecruitComplete( self ):
		# define method
		# 组队擂台，队伍已经完成招募
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_ON_RECRUIT_COMPLETE" )

	def challengeTeamBeRecruit( self, teamID ):
		# define method
		# 被招募
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_TEAM_BE_RECRUIT", teamID )

	def challengeTeamBeRecruitComplete( self ):
		# define method
		# 已经成功加入队伍，被告招募完成
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_TEAM_RECRUIT_SUCCESS" )

	def roleCompetition_SignUp( self, step ):
		"""
		个人竞技报名后通知客户端对个人竞技界面进行改变
		"""
		if step == (csconst.ROLE_LEVEL_UPPER_LIMIT - 1) / 10:
			minLevel = step*10
			maxLevel = ( step + 1 )*10
		elif step == csconst.ROLE_LEVEL_UPPER_LIMIT / 10:
			minLevel = step*10 +1
			maxLevel = step*10 + 9
		else:
			minLevel = step*10
			maxLevel = step*10 + 9
		levelStep = ( minLevel, maxLevel )
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_COMPETITION] = levelStep
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_PERSON_COMPETITION, levelStep )

	def onRoleCompetitionEnd( self ):
		"""
		个人竞技结束后通知客户端对个人竞技界面进行改变
		"""
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_COMPETITION] = (0,0)
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_PERSON_COMPETITION, (0,0 ) )

	def teamChallengeUpLevel( self, maxLevel, minLevel ):
		# define method
		# 更新组队擂台参赛等级
		self.levelSteps[csdefine.MATCH_TYPE_TEAM_ABA] = ( minLevel, maxLevel )
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, ( minLevel, maxLevel ) )

	def teamChallengeUpInfo( self, result ):
		# define method
		# 更新组队擂台当前排行
		self.matchResults[csdefine.MATCH_TYPE_TEAM_ABA] = result
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, result )

	def teamChallengeClose( self ):
		# define method
		# 组队擂台活动结束
		self.matchResults[csdefine.MATCH_TYPE_TEAM_ABA] = csdefine.MATCH_LEVEL_NONE
		self.levelSteps[csdefine.MATCH_TYPE_TEAM_ABA] = (0,0)
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, (0,0) )
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_LEVEL_NONE )

	def teamChallengeMember( self, oNum, eNum ):
		# define method
		# 组队擂台人数， oNum:己方， eNum：敌方
		ECenter.fireEvent( "EVT_ON_COPY_TCHALLENGE_OWNER_NUM", oNum )
		ECenter.fireEvent( "EVT_ON_COPY_TCHALLENGE_ENEMY_NUM", eNum )

	def teamChallengeDied( self ):
		# 组队擂台死亡
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.teamChallengeOnDieResult( True )
			elif id == RS_NO :
				BigWorld.player().cell.teamChallengeOnDieResult( False )

		msg = mbmsgs[0x0ee9]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	# ------------------------------------------------------------
	# 武道大会
	# ------------------------------------------------------------
	def wuDaoUpLevel( self, maxLevel, minLevel ):
		# define method
		# 更新武道大会参赛等级
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_ABA] = ( minLevel, maxLevel )
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, ( minLevel, maxLevel ) )

	def wuDaoUpInfo( self, result ):
		# define method
		# 更新武道大会当前排行
		self.matchResults[csdefine.MATCH_TYPE_PERSON_ABA] = result
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_PERSON_ABA, result )

	def wuDaoClose( self ):
		# define method
		# 武道大会关闭
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_ABA] = ( 0, 0 )
		self.matchResults[csdefine.MATCH_TYPE_PERSON_ABA] = csdefine.MATCH_LEVEL_NONE

	def wuDaoGather( self, time ):
		"""
		武道大会集合
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_PERSON_ABA )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.wuDaoGather()

		# "武道大会第%s轮比赛开始,请尽快进入比赛场地！"
		msg = mbmsgs[0x0d42] % time
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def wuDaoSignUp( self ):
		"""
		武道大会报名
		"""
		self.cell.wuDaoSignUp()

	#--------------------------
	# 组队竞技相关
	#--------------------------
	def teamCompetitionCheck( self,minLevel ):
		"""
		Defined method

		验证队伍条件
		@param minLevel : 要求等级
		@type minLevel : UNIT8

		"""
		level = self.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1

		for member in self.teamMember.itervalues():
			if member.objectID != self.id and member.level < minLevel:
				self.statusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_LEVEL )
				return

			memberLevel = member.level
			if memberLevel == csconst.ROLE_LEVEL_UPPER_LIMIT:
				memberLevel = csconst.ROLE_LEVEL_UPPER_LIMIT - 1

			if member.objectID != self.id and level/10 != memberLevel /10:
				self.statusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_LEVEL_AREA_1, str (( member.name, )) )
				return
		self.cell.teamCompetitionCheckOK()

	def teamCompetitionSignUp( self ):
		"""
		组队竞技报名接口
		"""
		self.cell.teamCompetitionSignUp()

	def teamCompetitionGather( self ):
		"""
		defined method

		组队竞技集合接口
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TEAM_COMPETITION )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.teamCompetitionGather()

		# "组队竞技开始入场,请尽快进入比赛场地！"
		msg = mbmsgs[0x0ee4]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def teamCompetitionNotify( self,level ):
		"""
		defined method

		更新组队竞技参与情况
		@param :level  参与等级
		@type :level   UNIT16
		"""
		levelStep = ( 0, 0 )
		if level:
			if level == ( csconst.ROLE_LEVEL_UPPER_LIMIT - 1 )/10:		# 玩家参加的是最高等级段的比赛，等级段上限为最高等级
				levelStep = ( level * 10, csconst.ROLE_LEVEL_UPPER_LIMIT )
			else:
				levelStep = ( level * 10, level * 10 + 9 )
		self.levelSteps[csdefine.MATCH_TYPE_TEAM_COMPETITION] = levelStep
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_COMPETITION, levelStep )

	def updateRestDiedTimes( self ,restDiedTimes ):
		"""
		defined method
		更新组队竞技剩余死亡次数

		@param :restDiedTimes 剩余死亡次数
		@type :UNIT8
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TEAM_COMPETITION_REMAIN", restDiedTimes )

	#--------------------------
	# 帮会擂台相关
	#--------------------------
	def tongAbaSignUp( self ):
		"""
		帮会擂台报名
		"""
		if self.level < csconst.PK_PROTECT_LEVEL:
			self.statusMessage( csstatus.ROLE_LEVEL_LOWER_PK_ALOW_LEVEL )
			return
		self.cell.tongAbaSignUp()

	def tongAbaGather( self,round ):
		"""
		defined method

		帮会擂台集合接口
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TONG_ABA )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.tongAbaGather()

		# "帮会擂台开始入场,请尽快进入比赛场地！"
		if round == csdefine.ABATTOIR_EIGHTHFINAL:
			msg = mbmsgs[0x0ee5]
		elif round == csdefine.ABATTOIR_QUARTERFINAL:
			msg = mbmsgs[0x0ee6]
		elif round == csdefine.ABATTOIR_SEMIFINAL:
			msg = mbmsgs[0x0ee7]
		elif round == csdefine.ABATTOIR_FINAL:
			msg = mbmsgs[0x0ee8]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def receiveAbaRound( self,round ):
		"""
		defined method

		帮会擂台当前比赛情况(xxx强)
		"""
		self.matchResults[csdefine.MATCH_TYPE_TONG_ABA] = round
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_TONG_ABA, round )

	def roleCompetitionSignUp( self ):
		"""
		个人竞技报名接口
		"""
		if self.level < csconst.ROLE_SOMPETITION_JOIN_LEVEL_MIN:
			self.onStatusMessage( csstatus.ROLECOMPETITION_FORBID_LEVEL, str(( csconst.ROLE_SOMPETITION_JOIN_LEVEL_MIN, )) )
		self.cell.roleCompetitionSignUp()

	def roleCompetitionGather( self ):
		"""
		个人竞技集合
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_PERSON_COMPETITION )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.roleCompetitionGather()

		# "个人竞技开始入场,请尽快进入比赛场地！"
		msg = mbmsgs[0x0ee2]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	#--------------------------
	# 帮会竞技相关
	#--------------------------
	def tongCompetitionSignUp( self ):
		"""
		帮会竞技报名接口
		"""
		self.cell.tongCompetitionSignUp()

	def tongCompetitionGather( self ):
		"""
		帮会竞技集合
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TONG_COMPETITION )
		self.levelSteps[csdefine.MATCH_TYPE_TONG_COMPETITION] = ( 60, 150 )
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TONG_COMPETITION, ( 60, 150 ) )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.tongCompetitionGather()

		# "帮会竞技开始入场,请尽快进入比赛场地！"
		msg = mbmsgs[0x0ee3]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def onTongCompDeathTimes( self, leftDeathTimes ):
		"""
		defined method
		更新帮会竞技玩家的剩余复活次数

		@param :restDiedTimes 剩余死亡次数
		@type :UNIT8
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TONG_COMPETITION_REMAIN", leftDeathTimes )
		pass

	def receiveRoleCompetitionScore( self, gradeList ):
		"""
		个人竞技积分显示
		@param gradeList: 一个积分列表，数据格式形如：[(玩家名字，玩家本场积分)]
		注：“产生玩家最高积分的时间”客户端暂时不会用到，可以先保留以备后用
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_ROLE_COMPETITION_POINT", gradeList )

	def roleCompetitionStart( self ):
		ECenter.fireEvent( "EVT_ON_ROLE_COMPETITION_BEING" )

	def roleCompetitionOver( self ):
		ECenter.fireEvent( "EVT_ON_ROLE_COMPETITION_OVER" )

	def remainRevivalCount( self, remainTuple ):
		"""
		个人竞技玩家剩余复活次数显示
		@param count：玩家剩余复活次数
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_ROLE_COMPETITION_REMAIN", remainTuple )
		pass

	def onWatchOrRevive( self ):
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.roleCompetitionOnDieResult( True )
			elif id == RS_NO :
				BigWorld.player().cell.roleCompetitionOnDieResult( False )

		# "是否进入观战模式！"
		msg = mbmsgs[0x0ee9]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def challengeOnDie( self,windowType ):
		"""
		defined method
		在副本中死亡时，如果复活次数用完了则弹出选择观战选择对话框，否则弹出复活框
		@param windowType:对话框类型        0表示弹出复活框，1表示弹出观战选择框
		@type:UNIT8

		"""
		if windowType == 0:
			ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )

		elif windowType == 1:
			self.onWatchOrRevive()

	#-------------------------------------------------------------------------------
	# 帮会车轮战
	#-------------------------------------------------------------------------------
	def turnWar_signUpCheck( self, cityName, memNumLimit ):
		"""
		define method
		报名条件判断
		"""
		max_level = self.level
		if len( self.teamMember ) != memNumLimit:
			self.statusMessage( csstatus.TONG_TURN_WAR_SIGNUP_MEMBER_NUM_WRONG, memNumLimit )
			return
		for info in self.teamMember.values():
			if not info.online:
				self.statusMessage( csstatus.TONG_TURN_WAR_SIGNUP_MEMBER_NUM_WRONG, memNumLimit )
				return
		for id, info in self.teamMember.iteritems():
			if id != self.id and info.level < csconst.TONG_TURN_LEVEL_MIN:
				self.statusMessage( csstatus.TONG_TURN_WAR_SIGNUP_LEVEL_WRONG )
				return
			if not self.tong_memberInfos.has_key( info.DBID ):		# 队友是否在队长的帮会中
				self.statusMessage( csstatus.TONG_TURN_WAR_SIGNUP_DIF_TONG )
				return

			# 取队员的最高等级为报名等级
			if info.level > max_level:
				max_level = info.level

		self.cell.turnWar_signUp( max_level, cityName )

	def turnWar_onSignUpTong( self ):
		"""
		define method
		成功报名帮会车轮战
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_SIGN_UP")
		members = []
		for member in self.teamMember.itervalues():
			info = {}
			info["headIcon"] = member.header
			info["name"] = member.name
			if member.name == self.getName():
				info["state"] = "own_preparing"
			else:
				info["state"] = "other_preparing"
			members.append(info)
		ECenter.fireEvent("EVT_ON_TURNWAR_RECEIVE_SELF_MEMBERS", members)

	def turnWar_onPrepared( self ):
		"""
		点击准备按钮的回调函数
		"""
		self.cell.turnWar_onPrepared()

	def turnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		队伍中有人按了准备后的回调函数
		"""
		if playerName == self.getName():
			state = "own_prepared"
		else:
			state = "other_prepared"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def turnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		有人点了出战
		"""
		if playerName == self.getName():
			state = "own_fighted"
		else:
			state = "other_fighted"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def turnWar_onReceiveSelfInfo( self, teamMemInfos ):
		"""
		define method
		匹配成功，显示己方队员的信息

		@param teamMemInfos : 对方队伍的成员信息
		@type teamMemInfos : [ { "playerDBID", "playerName", "playerBase", "playerMetier", "headTextureID", "time" } ]
		"""
		members = []
		for index, teammateInfo in enumerate(teamMemInfos):
			info = {}
			info["order"] = str(index + 1)
			info["headIcon"] = rds.iconsSound.getHeadTexturePath(teammateInfo["headTextureID"])
			info["name"] = teammateInfo["playerName"]
			if teammateInfo["playerName"] == self.getName():
				info["state"] = "own_fighting"
			else:
				info["state"] = "other_fighting"
			members.append(info)
		ECenter.fireEvent("EVT_ON_TURNWAR_RECEIVE_SELF_MEMBERS", members)

	def turnWar_onReceiveEnemyInfo( self, teamMemInfos ):
		"""
		define method
		匹配成功，显示敌方队员的信息

		@param teamMemInfos : 对方队伍的成员信息
		@type teamMemInfos : [ { "playerName", "headTextureID" } ]
		"""
		members = []
		for index, teammateInfo in enumerate(teamMemInfos):
			info = {}
			info["order"] = str(index + 1)
			info["headIcon"] = rds.iconsSound.getHeadTexturePath(teammateInfo["headTextureID"])
			info["state"] = "other_fighting"
			info["name"] = teammateInfo["playerName"]
			members.append(info)
		ECenter.fireEvent("EVT_ON_TURNWAR_RECEIVE_ENEMY_MEMBERS", members)

	def turnWar_onLeaveTeam( self ):
		"""
		define method
		有队员离队时的处理
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_HIDE_WINDOW")
		if self.teamID != 0:		# 如果已离队，不发送此信息
			self.statusMessage( csstatus.TONG_TURN_MEM_LEAVE_TEAM )

	def turnWar_showPlayerOrder( self, leftPlayerNames, rightPlayerNames ):
		"""
		define method
		显示玩家对战信息

		@param leftPlayerNames： 左方战队玩家名字列表
		@param rightPlayerNames：右方战队玩家名字列表
		"""
		# 显示对阵信息
		if self.getName() in leftPlayerNames:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", leftPlayerNames, rightPlayerNames)
		else:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", rightPlayerNames, leftPlayerNames)

	def turnWar_showPrepareTime( self, timeCount ):
		"""
		define method
		显示准备倒计时
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount, cschannel_msgs.TONG_TURN_WAR_FIGHTING )

	def turnWar_showTelportTime( self, timeCount ):
		"""
		define method
		显示传送倒计时

		@param timeCount: 秒数
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount )

	def turnWar_updatePointShow( self, winTeamID ):
		"""
		define method
		更新积分显示

		@param winTeamID: 获胜队伍ID
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_ADD_SCORE", winTeamID == self.teamID )

	def turnWar_onPlayerLose( self, teamID, playerName ):
		"""
		define method
		某个玩家失败了

		@param teamID: 失败玩家队伍ID
		@param playerName: 失败玩家姓名
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_COMPETITOR_LOSE", playerName )
		
	#-------------------------------------------------------------------------------
	# 阵营车轮战
	#-------------------------------------------------------------------------------
	def campTurnWar_signUpCheck( self, cityName, memNumLimit ):
		"""
		define method
		报名条件判断
		"""
		max_level = self.level
		if len( self.teamMember ) != memNumLimit:
			self.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_MEMBER_NUM_WRONG, memNumLimit )
			return
		for info in self.teamMember.values():
			if not info.online:
				self.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_MEMBER_NUM_WRONG, memNumLimit )
				return
		for id, info in self.teamMember.iteritems():
			if id != self.id and info.level < csconst.CAMP_TURN_LEVEL_MIN:
				self.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_LEVEL_WRONG )
				return
				
			if self.getCamp() != info.getCamp():		# 是否阵营相同
				self.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_DIF )
				return

			# 取队员的最高等级为报名等级
			if info.level > max_level:
				max_level = info.level

		self.cell.campTurnWar_signUp( max_level, cityName )

	def campTurnWar_onSignUp( self ):
		"""
		define method
		成功报名阵营车轮战
		"""
		self.campTurnWar_isSignUp = True
		
		ECenter.fireEvent("EVT_ON_TURNWAR_SIGN_UP")
		members = []
		for member in self.teamMember.itervalues():
			info = {}
			info["headIcon"] = member.header
			info["name"] = member.name
			if member.name == self.getName():
				info["state"] = "own_preparing"
			else:
				info["state"] = "other_preparing"
			members.append(info)
		ECenter.fireEvent("EVT_ON_TURNWAR_RECEIVE_SELF_MEMBERS", members)

	def campTurnWar_onPrepared( self ):
		"""
		点击准备按钮的回调函数
		"""
		self.cell.campTurnWar_onPrepared()

	def campTurnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		队伍中有人按了准备后的回调函数
		"""
		if playerName == self.getName():
			state = "own_prepared"
		else:
			state = "other_prepared"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def campTurnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		有人点了出战
		"""
		if playerName == self.getName():
			state = "own_fighted"
		else:
			state = "other_fighted"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def campTurnWar_onReceiveSelfInfo( self, teamMemInfos ):
		"""
		define method
		匹配成功，显示己方队员的信息

		@param teamMemInfos : 对方队伍的成员信息
		@type teamMemInfos : [ { "playerDBID", "playerName", "playerBase", "playerMetier", "headTextureID", "time" } ]
		"""
		members = []
		for index, teammateInfo in enumerate(teamMemInfos):
			info = {}
			info["order"] = str(index + 1)
			info["headIcon"] = rds.iconsSound.getHeadTexturePath(teammateInfo["headTextureID"])
			info["name"] = teammateInfo["playerName"]
			if teammateInfo["playerName"] == self.getName():
				info["state"] = "own_fighting"
			else:
				info["state"] = "other_fighting"
			members.append(info)
		ECenter.fireEvent("EVT_ON_TURNWAR_RECEIVE_SELF_MEMBERS", members)

	def campTurnWar_onReceiveEnemyInfo( self, teamMemInfos ):
		"""
		define method
		匹配成功，显示敌方队员的信息

		@param teamMemInfos : 对方队伍的成员信息
		@type teamMemInfos : [ { "playerName", "headTextureID" } ]
		"""
		members = []
		for index, teammateInfo in enumerate(teamMemInfos):
			info = {}
			info["order"] = str(index + 1)
			info["headIcon"] = rds.iconsSound.getHeadTexturePath(teammateInfo["headTextureID"])
			info["state"] = "other_fighting"
			info["name"] = teammateInfo["playerName"]
			members.append(info)
		ECenter.fireEvent("EVT_ON_TURNWAR_RECEIVE_ENEMY_MEMBERS", members)

	def campTurnWar_onLeaveTeam( self ):
		"""
		define method
		有队员离队时的处理
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_HIDE_WINDOW")
		if self.teamID != 0:		# 如果已离队，不发送此信息
			self.statusMessage( csstatus.CAMP_TURN_MEM_LEAVE_TEAM )
			self.campTurnWar_isSignUp = False

	def campTurnWar_showPlayerOrder( self, leftPlayerNames, rightPlayerNames ):
		"""
		define method
		显示玩家对战信息

		@param leftPlayerNames： 左方战队玩家名字列表
		@param rightPlayerNames：右方战队玩家名字列表
		"""
		# 显示对阵信息
		if self.getName() in leftPlayerNames:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", leftPlayerNames, rightPlayerNames)
		else:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", rightPlayerNames, leftPlayerNames)

	def campTurnWar_showPrepareTime( self, timeCount ):
		"""
		define method
		显示准备倒计时
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount, cschannel_msgs.CAMP_TURN_WAR_FIGHTING )

	def campTurnWar_showTelportTime( self, timeCount ):
		"""
		define method
		显示传送倒计时

		@param timeCount: 秒数
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount )
		self.campTurnWar_isSignUp = False

	def campTurnWar_updatePointShow( self, winTeamID ):
		"""
		define method
		更新积分显示

		@param winTeamID: 获胜队伍ID
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_ADD_SCORE", winTeamID == self.teamID )

	def campTurnWar_onPlayerLose( self, teamID, playerName ):
		"""
		define method
		某个玩家失败了

		@param teamID: 失败玩家队伍ID
		@param playerName: 失败玩家姓名
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_COMPETITOR_LOSE", playerName )
	
	#---------------------------------------------------------------------
	#鏖战群雄
	#---------------------------------------------------------------------
	def aoZhan_showSignUpWindows( self, signUpList ):
		"""
		define method.
		打开报名名单
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_AOZHAN_SIGNUP_WINDOW", signUpList )
	
	def aoZhan_startSignUp( self ):
		"""
		define method.
		报名开始.
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_AOZHAN_BOX" )
	
	def aoZhan_onEnd( self ):
		"""
		define method.
		结束活动
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_IS_JOIN", False )
	
	def aoZhan_onSignUp( self ):
		"""
		define method.
		报名成功回调
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_SIGNUP" )
		self.statusMessage( csstatus.AO_ZHAN_QUN_XIONG_SIGNUP_OK )
	
	def aoZhan_warStart( self ):
		"""
		define method.
		开始战斗
		"""
		pass
	
	def aoZhan_showBattlefield( self, warInfos, doingMatch ):
		"""
		define method
		打开战绩名单
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_RANK_INFO", warInfos, doingMatch )

	def aoZhan_flushBattlefield( self ):
		"""
		请求刷新战绩
		"""
		self.cell.aoZhan_flushBattlefield()

	def aoZhan_getSignUpList( self ):
		"""
		请求报名名单
		"""
		self.cell.aoZhan_getSignUpList()

	def aoZhan_enterNofity( self ):
		"""
		define method.
		战场开启，进入通知
		"""
		pass
	
	def aoZhan_setIsJoin( self, isJoin ):
		"""
		define method
		通知是否参与活动
		isJoin（ True：参与， False:不参与 ）
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_IS_JOIN", isJoin )
	
	def aoZhan_gotoEnterNPC( self ):
		"""
		传送到进入NPC
		"""
		self.cell.aoZhan_gotoEnterNPC()

	def aoZhan_signUp( self ):
		"""
		鏖战群雄报名
		"""
		self.cell.aoZhan_signup()

	def aoZhan_countDown( self, time ):
		"""
		define method.
		鏖战群雄战斗倒计时
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_COUNT_DOWN", time )
		
	#---------------------------------------------------------------------
	#阵营烽火连天
	#---------------------------------------------------------------------
	def onCampFengHuoSelectTransportOrNot( self ):
		"""
		阵营烽火连天选择是否传送
		"""
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.onRequestTransportCampFengHuo()

		# "是否进入传送！"
		msg = mbmsgs[0x0eeb]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		
	def camp_onFengHuoLianTianOver( self ):
		"""
		阵营烽火连天结束
		"""
		ECenter.fireEvent( "EVT_ON_CAMP_FHLT_SPACE_OVER" )
		
	def camp_onEnterFengHuoLianTianSpace( self, warEndTime, campInfos ):
		"""
		进入阵营烽火连天
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_CAMP_FHLT_SPACE",self, warEndTime, campInfos )
		
	
	def campFHLTProtectTime( self, time ):
		"""
		define method.
		阵营烽火连天准备时间
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_FHLT_PROTECT_TIME", time )
		
	def camp_onFHLTReport( self, camp,  playerName, kill, dead, isInWar ):
		"""
		define method.
		阵营烽火连天更新副本内玩家客户端战果新排名信息
		"""
		DEBUG_MSG( "player id is %s,camp is %s,playerName is %s,kill is %s,dead is %s,isInWar is %s"%( self.id, camp, playerName, kill, dead, isInWar ) )
		ECenter.fireEvent( "EVT_ON_RECIEVE_CAMP_FHLTRANK_DATAS", camp,  playerName, kill, dead, isInWar )
		
	def camp_onUpdateFHLTPoint( self, camp, point ):
		"""
		define method.
		阵营烽火连天服务器传过来的当前某帮会的战场积分
		"""
		DEBUG_MSG( "player id is %s,camp is %s,point is %s"%( self.id, camp, point ) )
		ECenter.fireEvent( "EVT_ON_UPDATE_CAMP_FHLT_POINT", camp, point )
	
	def camp_onLeaveFengHuoLianTianSpace( self ):
		"""
		define method.
		阵营烽火连天玩家离开副本
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_FHLT_SPACE", self )
		
	def setCampFengHuoBattleInfo( self, remainTime, battleNum, maxNum ):
		"""
		define method
		设置阵营烽火连天玩家报名战场数字和当前最大战场数字
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_CAMP_FHLT_BATTLE_NUM",remainTime, battleNum, maxNum )
		
	def setCampFengHuo_signUpFlag( self, state ):
		"""
		define method
		设置阵营烽火连天是否报名成功标志
		"""
		self.campFengHuo_signUpFlag = True
		ECenter.fireEvent( "EVT_ON_HIDE_CAMP_FHLTR_SIGN_WND" )
		
	def onRequestQuitCampFengHuoSignUp( self ):
		"""
		玩家请求退出阵营烽火连天报名
		"""
		self.cell.onRequestQuitCampFengHuoSignUp()

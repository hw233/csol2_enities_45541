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
	# �������ýӿ�,���������˾�����������Ӿ��������������̨�����������̨�����������ᡱ������ᳵ��ս��, "��Ӫ����ս"�� "��սȺ��", "��Ӫ�������"
	def __init__( self ):
		#�����ȼ���
		self.levelSteps = { csdefine.MATCH_TYPE_PERSON_COMPETITION:( 0, 0 ),
					csdefine.MATCH_TYPE_TEAM_COMPETITION:( 0, 0 ),
					csdefine.MATCH_TYPE_TONG_COMPETITION:( 0, 0 ),
					csdefine.MATCH_TYPE_PERSON_ABA:( 0, 0 ),
					csdefine.MATCH_TYPE_TEAM_ABA:( 0, 0 ),
					csdefine.MATCH_TYPE_TONG_ABA:( 0, 0 ),
				}

		#����̨�����׶ν��
		self.matchResults = {csdefine.MATCH_TYPE_PERSON_ABA:csdefine.MATCH_LEVEL_NONE,
					csdefine.MATCH_TYPE_TEAM_ABA:csdefine.MATCH_LEVEL_NONE,
					csdefine.MATCH_TYPE_TONG_ABA:csdefine.MATCH_LEVEL_NONE,
				}

		self.campTurnWar_isSignUp = False
		self.campFengHuo_signUpFlag = False
		
	def challengeHasFlagGather( self, type ):
		# ��ѯ���ϱ�־
		return self.challengeGatherFlags & ( 1 << type )

	#--------------------------------------------------------------------
	# �����̨
	#--------------------------------------------------------------------
	def challengeTeamSignUp( self ):
		# define method
		# �����̨����
		if not self.isCaptain():
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_CAPTAIN, "" )
			return

		if self.level < csconst.TEAM_CHALLENGE_JOIN_LEVEL_MIN:
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_MUST_LEVEL, "" )
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# ����
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# ����
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# ս��
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		minLevel = self.level / 10 * 10
		maxLevel = minLevel + csconst.TEAM_CHALLENGE_JOIN_LEVEL_INCREASE
		if maxLevel + 1 == csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX: # ����150������ҹ鵽140 - 149�ȼ���
			maxLevel += 1

		for mID, member in self.teamMember.iteritems():
			if mID == self.id:
				continue

			if member.level < minLevel or member.level > maxLevel:
				self.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_LEVEL_ERR, "" )
				return

		self.cell.challengeTeamSignUp()

	def challengeTeamRequestSub( self ):
		# ������������̨���油����
		if self.isInTeam():
			# �Ѿ��ж���
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM, "" )
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# ����
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# ����
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# ս��
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		self.cell.challengeTeamRequestSub()

	def challengeTeamCancelSub( self ):
		# �����̨�˳��油����
		self.cell.challengeTeamCancelSub()

	def challengeTeamOnCancelSub( self ):
		# �����̨�˳��油�����ص�
		# Defined
		pass

	def challengeTeamRecruit( self ):
		# �������������̨��ļ
		if not self.isCaptain():
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_CAPTAIN, "" )
			return

		if len( self.teamMember ) == csconst.TEAM_MEMBER_MAX:
			self.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_TEAM_FULL, "" )
			return

		self.cell.challengeTeamRecruit()

	def challengeTeamCancelRecruit( self ):
		# ����ȡ�������̨��ļ
		self.cell.challengeTeamCancelRecruit()

	def teamChallengeOnCRecruit( self ):
		# define method
		# ����ȡ�������̨��ļ ֪ͨ
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_ON_RECRUIT_CANCEL" )

	def challengeTeamGather( self, round ):
		#define method
		# �����̨����
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TEAM_ABA )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.teamChallengeGather()

		msg = mbmsgs[0x0ee1] % round
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def teamChallengeOnRecruit( self ):
		# define method
		# �����̨�������Ѽ���ļ�б�
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_ON_RECRUIT" )

	def teamChallengeRecruitComplete( self ):
		# define method
		# �����̨�������Ѿ������ļ
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_ON_RECRUIT_COMPLETE" )

	def challengeTeamBeRecruit( self, teamID ):
		# define method
		# ����ļ
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_TEAM_BE_RECRUIT", teamID )

	def challengeTeamBeRecruitComplete( self ):
		# define method
		# �Ѿ��ɹ�������飬������ļ���
		ECenter.fireEvent( "EVT_ON_TEAM_CHALLENGE_TEAM_RECRUIT_SUCCESS" )

	def roleCompetition_SignUp( self, step ):
		"""
		���˾���������֪ͨ�ͻ��˶Ը��˾���������иı�
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
		���˾���������֪ͨ�ͻ��˶Ը��˾���������иı�
		"""
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_COMPETITION] = (0,0)
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_PERSON_COMPETITION, (0,0 ) )

	def teamChallengeUpLevel( self, maxLevel, minLevel ):
		# define method
		# ���������̨�����ȼ�
		self.levelSteps[csdefine.MATCH_TYPE_TEAM_ABA] = ( minLevel, maxLevel )
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, ( minLevel, maxLevel ) )

	def teamChallengeUpInfo( self, result ):
		# define method
		# ���������̨��ǰ����
		self.matchResults[csdefine.MATCH_TYPE_TEAM_ABA] = result
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, result )

	def teamChallengeClose( self ):
		# define method
		# �����̨�����
		self.matchResults[csdefine.MATCH_TYPE_TEAM_ABA] = csdefine.MATCH_LEVEL_NONE
		self.levelSteps[csdefine.MATCH_TYPE_TEAM_ABA] = (0,0)
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, (0,0) )
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_LEVEL_NONE )

	def teamChallengeMember( self, oNum, eNum ):
		# define method
		# �����̨������ oNum:������ eNum���з�
		ECenter.fireEvent( "EVT_ON_COPY_TCHALLENGE_OWNER_NUM", oNum )
		ECenter.fireEvent( "EVT_ON_COPY_TCHALLENGE_ENEMY_NUM", eNum )

	def teamChallengeDied( self ):
		# �����̨����
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.teamChallengeOnDieResult( True )
			elif id == RS_NO :
				BigWorld.player().cell.teamChallengeOnDieResult( False )

		msg = mbmsgs[0x0ee9]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	# ------------------------------------------------------------
	# ������
	# ------------------------------------------------------------
	def wuDaoUpLevel( self, maxLevel, minLevel ):
		# define method
		# ��������������ȼ�
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_ABA] = ( minLevel, maxLevel )
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_ABA, ( minLevel, maxLevel ) )

	def wuDaoUpInfo( self, result ):
		# define method
		# ���������ᵱǰ����
		self.matchResults[csdefine.MATCH_TYPE_PERSON_ABA] = result
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_PERSON_ABA, result )

	def wuDaoClose( self ):
		# define method
		# ������ر�
		self.levelSteps[csdefine.MATCH_TYPE_PERSON_ABA] = ( 0, 0 )
		self.matchResults[csdefine.MATCH_TYPE_PERSON_ABA] = csdefine.MATCH_LEVEL_NONE

	def wuDaoGather( self, time ):
		"""
		�����Ἧ��
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_PERSON_ABA )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.wuDaoGather()

		# "�������%s�ֱ�����ʼ,�뾡�����������أ�"
		msg = mbmsgs[0x0d42] % time
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def wuDaoSignUp( self ):
		"""
		�����ᱨ��
		"""
		self.cell.wuDaoSignUp()

	#--------------------------
	# ��Ӿ������
	#--------------------------
	def teamCompetitionCheck( self,minLevel ):
		"""
		Defined method

		��֤��������
		@param minLevel : Ҫ��ȼ�
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
		��Ӿ��������ӿ�
		"""
		self.cell.teamCompetitionSignUp()

	def teamCompetitionGather( self ):
		"""
		defined method

		��Ӿ������Ͻӿ�
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TEAM_COMPETITION )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.teamCompetitionGather()

		# "��Ӿ�����ʼ�볡,�뾡�����������أ�"
		msg = mbmsgs[0x0ee4]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def teamCompetitionNotify( self,level ):
		"""
		defined method

		������Ӿ����������
		@param :level  ����ȼ�
		@type :level   UNIT16
		"""
		levelStep = ( 0, 0 )
		if level:
			if level == ( csconst.ROLE_LEVEL_UPPER_LIMIT - 1 )/10:		# ��Ҳμӵ�����ߵȼ��εı������ȼ�������Ϊ��ߵȼ�
				levelStep = ( level * 10, csconst.ROLE_LEVEL_UPPER_LIMIT )
			else:
				levelStep = ( level * 10, level * 10 + 9 )
		self.levelSteps[csdefine.MATCH_TYPE_TEAM_COMPETITION] = levelStep
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TEAM_COMPETITION, levelStep )

	def updateRestDiedTimes( self ,restDiedTimes ):
		"""
		defined method
		������Ӿ���ʣ����������

		@param :restDiedTimes ʣ����������
		@type :UNIT8
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TEAM_COMPETITION_REMAIN", restDiedTimes )

	#--------------------------
	# �����̨���
	#--------------------------
	def tongAbaSignUp( self ):
		"""
		�����̨����
		"""
		if self.level < csconst.PK_PROTECT_LEVEL:
			self.statusMessage( csstatus.ROLE_LEVEL_LOWER_PK_ALOW_LEVEL )
			return
		self.cell.tongAbaSignUp()

	def tongAbaGather( self,round ):
		"""
		defined method

		�����̨���Ͻӿ�
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TONG_ABA )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.tongAbaGather()

		# "�����̨��ʼ�볡,�뾡�����������أ�"
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

		�����̨��ǰ�������(xxxǿ)
		"""
		self.matchResults[csdefine.MATCH_TYPE_TONG_ABA] = round
		ECenter.fireEvent( "EVT_ON_COMPET_RESULT_CHANGE", csdefine.MATCH_TYPE_TONG_ABA, round )

	def roleCompetitionSignUp( self ):
		"""
		���˾��������ӿ�
		"""
		if self.level < csconst.ROLE_SOMPETITION_JOIN_LEVEL_MIN:
			self.onStatusMessage( csstatus.ROLECOMPETITION_FORBID_LEVEL, str(( csconst.ROLE_SOMPETITION_JOIN_LEVEL_MIN, )) )
		self.cell.roleCompetitionSignUp()

	def roleCompetitionGather( self ):
		"""
		���˾�������
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_PERSON_COMPETITION )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.roleCompetitionGather()

		# "���˾�����ʼ�볡,�뾡�����������أ�"
		msg = mbmsgs[0x0ee2]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	#--------------------------
	# ��Ὰ�����
	#--------------------------
	def tongCompetitionSignUp( self ):
		"""
		��Ὰ�������ӿ�
		"""
		self.cell.tongCompetitionSignUp()

	def tongCompetitionGather( self ):
		"""
		��Ὰ������
		"""
		if BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		ECenter.fireEvent( "EVT_ON_COMPET_GATHER_TRIGGER", csdefine.MATCH_TYPE_TONG_COMPETITION )
		self.levelSteps[csdefine.MATCH_TYPE_TONG_COMPETITION] = ( 60, 150 )
		ECenter.fireEvent( "EVT_ON_COMPET_LEVEL_STEPS_CHANGE", csdefine.MATCH_TYPE_TONG_COMPETITION, ( 60, 150 ) )
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.tongCompetitionGather()

		# "��Ὰ����ʼ�볡,�뾡�����������أ�"
		msg = mbmsgs[0x0ee3]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def onTongCompDeathTimes( self, leftDeathTimes ):
		"""
		defined method
		���°�Ὰ����ҵ�ʣ�ิ�����

		@param :restDiedTimes ʣ����������
		@type :UNIT8
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TONG_COMPETITION_REMAIN", leftDeathTimes )
		pass

	def receiveRoleCompetitionScore( self, gradeList ):
		"""
		���˾���������ʾ
		@param gradeList: һ�������б����ݸ�ʽ���磺[(������֣���ұ�������)]
		ע�������������߻��ֵ�ʱ�䡱�ͻ�����ʱ�����õ��������ȱ����Ա�����
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_ROLE_COMPETITION_POINT", gradeList )

	def roleCompetitionStart( self ):
		ECenter.fireEvent( "EVT_ON_ROLE_COMPETITION_BEING" )

	def roleCompetitionOver( self ):
		ECenter.fireEvent( "EVT_ON_ROLE_COMPETITION_OVER" )

	def remainRevivalCount( self, remainTuple ):
		"""
		���˾������ʣ�ิ�������ʾ
		@param count�����ʣ�ิ�����
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_ROLE_COMPETITION_REMAIN", remainTuple )
		pass

	def onWatchOrRevive( self ):
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.roleCompetitionOnDieResult( True )
			elif id == RS_NO :
				BigWorld.player().cell.roleCompetitionOnDieResult( False )

		# "�Ƿ�����սģʽ��"
		msg = mbmsgs[0x0ee9]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def challengeOnDie( self,windowType ):
		"""
		defined method
		�ڸ���������ʱ�������������������򵯳�ѡ���սѡ��Ի��򣬷��򵯳������
		@param windowType:�Ի�������        0��ʾ���������1��ʾ������սѡ���
		@type:UNIT8

		"""
		if windowType == 0:
			ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )

		elif windowType == 1:
			self.onWatchOrRevive()

	#-------------------------------------------------------------------------------
	# ��ᳵ��ս
	#-------------------------------------------------------------------------------
	def turnWar_signUpCheck( self, cityName, memNumLimit ):
		"""
		define method
		���������ж�
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
			if not self.tong_memberInfos.has_key( info.DBID ):		# �����Ƿ��ڶӳ��İ����
				self.statusMessage( csstatus.TONG_TURN_WAR_SIGNUP_DIF_TONG )
				return

			# ȡ��Ա����ߵȼ�Ϊ�����ȼ�
			if info.level > max_level:
				max_level = info.level

		self.cell.turnWar_signUp( max_level, cityName )

	def turnWar_onSignUpTong( self ):
		"""
		define method
		�ɹ�������ᳵ��ս
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
		���׼����ť�Ļص�����
		"""
		self.cell.turnWar_onPrepared()

	def turnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		���������˰���׼����Ļص�����
		"""
		if playerName == self.getName():
			state = "own_prepared"
		else:
			state = "other_prepared"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def turnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		���˵��˳�ս
		"""
		if playerName == self.getName():
			state = "own_fighted"
		else:
			state = "other_fighted"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def turnWar_onReceiveSelfInfo( self, teamMemInfos ):
		"""
		define method
		ƥ��ɹ�����ʾ������Ա����Ϣ

		@param teamMemInfos : �Է�����ĳ�Ա��Ϣ
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
		ƥ��ɹ�����ʾ�з���Ա����Ϣ

		@param teamMemInfos : �Է�����ĳ�Ա��Ϣ
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
		�ж�Ա���ʱ�Ĵ���
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_HIDE_WINDOW")
		if self.teamID != 0:		# �������ӣ������ʹ���Ϣ
			self.statusMessage( csstatus.TONG_TURN_MEM_LEAVE_TEAM )

	def turnWar_showPlayerOrder( self, leftPlayerNames, rightPlayerNames ):
		"""
		define method
		��ʾ��Ҷ�ս��Ϣ

		@param leftPlayerNames�� ��ս����������б�
		@param rightPlayerNames���ҷ�ս����������б�
		"""
		# ��ʾ������Ϣ
		if self.getName() in leftPlayerNames:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", leftPlayerNames, rightPlayerNames)
		else:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", rightPlayerNames, leftPlayerNames)

	def turnWar_showPrepareTime( self, timeCount ):
		"""
		define method
		��ʾ׼������ʱ
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount, cschannel_msgs.TONG_TURN_WAR_FIGHTING )

	def turnWar_showTelportTime( self, timeCount ):
		"""
		define method
		��ʾ���͵���ʱ

		@param timeCount: ����
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount )

	def turnWar_updatePointShow( self, winTeamID ):
		"""
		define method
		���»�����ʾ

		@param winTeamID: ��ʤ����ID
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_ADD_SCORE", winTeamID == self.teamID )

	def turnWar_onPlayerLose( self, teamID, playerName ):
		"""
		define method
		ĳ�����ʧ����

		@param teamID: ʧ����Ҷ���ID
		@param playerName: ʧ���������
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_COMPETITOR_LOSE", playerName )
		
	#-------------------------------------------------------------------------------
	# ��Ӫ����ս
	#-------------------------------------------------------------------------------
	def campTurnWar_signUpCheck( self, cityName, memNumLimit ):
		"""
		define method
		���������ж�
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
				
			if self.getCamp() != info.getCamp():		# �Ƿ���Ӫ��ͬ
				self.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_DIF )
				return

			# ȡ��Ա����ߵȼ�Ϊ�����ȼ�
			if info.level > max_level:
				max_level = info.level

		self.cell.campTurnWar_signUp( max_level, cityName )

	def campTurnWar_onSignUp( self ):
		"""
		define method
		�ɹ�������Ӫ����ս
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
		���׼����ť�Ļص�����
		"""
		self.cell.campTurnWar_onPrepared()

	def campTurnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		���������˰���׼����Ļص�����
		"""
		if playerName == self.getName():
			state = "own_prepared"
		else:
			state = "other_prepared"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def campTurnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		���˵��˳�ս
		"""
		if playerName == self.getName():
			state = "own_fighted"
		else:
			state = "other_fighted"
		ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE", playerName, state)

	def campTurnWar_onReceiveSelfInfo( self, teamMemInfos ):
		"""
		define method
		ƥ��ɹ�����ʾ������Ա����Ϣ

		@param teamMemInfos : �Է�����ĳ�Ա��Ϣ
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
		ƥ��ɹ�����ʾ�з���Ա����Ϣ

		@param teamMemInfos : �Է�����ĳ�Ա��Ϣ
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
		�ж�Ա���ʱ�Ĵ���
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_HIDE_WINDOW")
		if self.teamID != 0:		# �������ӣ������ʹ���Ϣ
			self.statusMessage( csstatus.CAMP_TURN_MEM_LEAVE_TEAM )
			self.campTurnWar_isSignUp = False

	def campTurnWar_showPlayerOrder( self, leftPlayerNames, rightPlayerNames ):
		"""
		define method
		��ʾ��Ҷ�ս��Ϣ

		@param leftPlayerNames�� ��ս����������б�
		@param rightPlayerNames���ҷ�ս����������б�
		"""
		# ��ʾ������Ϣ
		if self.getName() in leftPlayerNames:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", leftPlayerNames, rightPlayerNames)
		else:
			ECenter.fireEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", rightPlayerNames, leftPlayerNames)

	def campTurnWar_showPrepareTime( self, timeCount ):
		"""
		define method
		��ʾ׼������ʱ
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount, cschannel_msgs.CAMP_TURN_WAR_FIGHTING )

	def campTurnWar_showTelportTime( self, timeCount ):
		"""
		define method
		��ʾ���͵���ʱ

		@param timeCount: ����
		"""
		ECenter.fireEvent("EVT_ON_SHOW_COUNT_DOWN", timeCount )
		self.campTurnWar_isSignUp = False

	def campTurnWar_updatePointShow( self, winTeamID ):
		"""
		define method
		���»�����ʾ

		@param winTeamID: ��ʤ����ID
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_ADD_SCORE", winTeamID == self.teamID )

	def campTurnWar_onPlayerLose( self, teamID, playerName ):
		"""
		define method
		ĳ�����ʧ����

		@param teamID: ʧ����Ҷ���ID
		@param playerName: ʧ���������
		"""
		ECenter.fireEvent("EVT_ON_TURNWAR_COMPETITOR_LOSE", playerName )
	
	#---------------------------------------------------------------------
	#��սȺ��
	#---------------------------------------------------------------------
	def aoZhan_showSignUpWindows( self, signUpList ):
		"""
		define method.
		�򿪱�������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_AOZHAN_SIGNUP_WINDOW", signUpList )
	
	def aoZhan_startSignUp( self ):
		"""
		define method.
		������ʼ.
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_AOZHAN_BOX" )
	
	def aoZhan_onEnd( self ):
		"""
		define method.
		�����
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_IS_JOIN", False )
	
	def aoZhan_onSignUp( self ):
		"""
		define method.
		�����ɹ��ص�
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_SIGNUP" )
		self.statusMessage( csstatus.AO_ZHAN_QUN_XIONG_SIGNUP_OK )
	
	def aoZhan_warStart( self ):
		"""
		define method.
		��ʼս��
		"""
		pass
	
	def aoZhan_showBattlefield( self, warInfos, doingMatch ):
		"""
		define method
		��ս������
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_RANK_INFO", warInfos, doingMatch )

	def aoZhan_flushBattlefield( self ):
		"""
		����ˢ��ս��
		"""
		self.cell.aoZhan_flushBattlefield()

	def aoZhan_getSignUpList( self ):
		"""
		����������
		"""
		self.cell.aoZhan_getSignUpList()

	def aoZhan_enterNofity( self ):
		"""
		define method.
		ս������������֪ͨ
		"""
		pass
	
	def aoZhan_setIsJoin( self, isJoin ):
		"""
		define method
		֪ͨ�Ƿ����
		isJoin�� True�����룬 False:������ ��
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_IS_JOIN", isJoin )
	
	def aoZhan_gotoEnterNPC( self ):
		"""
		���͵�����NPC
		"""
		self.cell.aoZhan_gotoEnterNPC()

	def aoZhan_signUp( self ):
		"""
		��սȺ�۱���
		"""
		self.cell.aoZhan_signup()

	def aoZhan_countDown( self, time ):
		"""
		define method.
		��սȺ��ս������ʱ
		"""
		ECenter.fireEvent( "EVT_ON_AOZHAN_COUNT_DOWN", time )
		
	#---------------------------------------------------------------------
	#��Ӫ�������
	#---------------------------------------------------------------------
	def onCampFengHuoSelectTransportOrNot( self ):
		"""
		��Ӫ�������ѡ���Ƿ���
		"""
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.onRequestTransportCampFengHuo()

		# "�Ƿ���봫�ͣ�"
		msg = mbmsgs[0x0eeb]
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		
	def camp_onFengHuoLianTianOver( self ):
		"""
		��Ӫ����������
		"""
		ECenter.fireEvent( "EVT_ON_CAMP_FHLT_SPACE_OVER" )
		
	def camp_onEnterFengHuoLianTianSpace( self, warEndTime, campInfos ):
		"""
		������Ӫ�������
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_CAMP_FHLT_SPACE",self, warEndTime, campInfos )
		
	
	def campFHLTProtectTime( self, time ):
		"""
		define method.
		��Ӫ�������׼��ʱ��
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_FHLT_PROTECT_TIME", time )
		
	def camp_onFHLTReport( self, camp,  playerName, kill, dead, isInWar ):
		"""
		define method.
		��Ӫ���������¸�������ҿͻ���ս����������Ϣ
		"""
		DEBUG_MSG( "player id is %s,camp is %s,playerName is %s,kill is %s,dead is %s,isInWar is %s"%( self.id, camp, playerName, kill, dead, isInWar ) )
		ECenter.fireEvent( "EVT_ON_RECIEVE_CAMP_FHLTRANK_DATAS", camp,  playerName, kill, dead, isInWar )
		
	def camp_onUpdateFHLTPoint( self, camp, point ):
		"""
		define method.
		��Ӫ�������������������ĵ�ǰĳ����ս������
		"""
		DEBUG_MSG( "player id is %s,camp is %s,point is %s"%( self.id, camp, point ) )
		ECenter.fireEvent( "EVT_ON_UPDATE_CAMP_FHLT_POINT", camp, point )
	
	def camp_onLeaveFengHuoLianTianSpace( self ):
		"""
		define method.
		��Ӫ�����������뿪����
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_FHLT_SPACE", self )
		
	def setCampFengHuoBattleInfo( self, remainTime, battleNum, maxNum ):
		"""
		define method
		������Ӫ���������ұ���ս�����ֺ͵�ǰ���ս������
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_CAMP_FHLT_BATTLE_NUM",remainTime, battleNum, maxNum )
		
	def setCampFengHuo_signUpFlag( self, state ):
		"""
		define method
		������Ӫ��������Ƿ����ɹ���־
		"""
		self.campFengHuo_signUpFlag = True
		ECenter.fireEvent( "EVT_ON_HIDE_CAMP_FHLTR_SIGN_WND" )
		
	def onRequestQuitCampFengHuoSignUp( self ):
		"""
		��������˳���Ӫ������챨��
		"""
		self.cell.onRequestQuitCampFengHuoSignUp()

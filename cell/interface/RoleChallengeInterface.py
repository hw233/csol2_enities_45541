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

CHAMPION_REWARD_ITEM_TEAM_CHALLENGE = 60101244 # ��Ӿ����ھ�������
CHAMPION_REWARD_ITEM_WU_DAO			= 60101246 # ������ھ�������
SKILL_ID1	= 322528001

class RoleChallengeInterface:
	# �������ýӿ�,���������˾�����������Ӿ��������������̨�����������̨�����������ᡱ������ᳵ��ս��, "��Ӫ����ս��", "��սȺ��", "��Ӫ�������"
	def __init__( self ):
		pass
	
	def onCellReady( self ):
		self.aoZhan_playerInit()

	def challengeActivityTransmit( self, type ):
		# define method
		# �����,��������/����
		if csconst.TRANSMIT_SPACE_INFOS.has_key( type ):
			self.gotoSpace( csconst.TRANSMIT_SPACE_INFOS[ type ][ 0 ], Math.Vector3( csconst.TRANSMIT_SPACE_INFOS[ type ][ 1 ]) + ( random.randint(-2,2), 0, random.randint(-2,2) ), Math.Vector3( csconst.TRANSMIT_SPACE_INFOS[ type ][ 2 ]) )

	def challengeSetFlagGather( self, type ):
		# define method
		# ���û���ͱ�־
		self.challengeGatherFlags = self.challengeGatherFlags | ( 1 << type )

	def challengeRemoveFlagGather( self, type ):
		# define method
		# �رջ���ͱ�־
		self.challengeGatherFlags = self.challengeGatherFlags &~ ( 1 << type )

	def challengeHasFlagGather( self, type ):
		# ��ѯ���ϱ�־
		return self.challengeGatherFlags & ( 1 << type )
	
	def onDestroy( self ):
		# �������
		BigWorld.globalData[ "TeamChallengeMgr" ].playerDestroy( self.base )
		self.aoZhan_playerDestroy()
	
	def changePosAndDir( self, position, tarPos ):
		"""
		define method
		�仯λ�ò�����һ��Ŀ���
		
		@param position: VECTOR3 Ҫ�����λ��
		@param tarPos: VECTOR3 �����λ��
		"""
		disDir = tarPos - position
		direction = (0,0,disDir.yaw)
		self.teleport( None, position, direction )
		self.client.unifyYaw()

	#--------------------------------------------------------------------
	# �����̨
	#--------------------------------------------------------------------
	def challengeTeamSignUp( self, exposed ):
		# �����̨����
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
			# ����
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# ս��
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		BigWorld.globalData[ "TeamChallengeMgr" ].signUp( self.teamMailbox.id, self.level, self.base )

	def challengeTeamRequestSub( self, exposed ):
		# ������������̨������
		# define method
		if not self.hackVerify_( exposed ):
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# ����
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
			return
			
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			# ������ͨ��ͼ
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_SPACE_COPY, "" )
			return
			
		if self.isInTeam():
			# ���
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# ����
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# ս��
			self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FIGHT, "" )
			return

		BigWorld.globalData[ "TeamChallengeMgr" ].substitutePlayer( self.base, self.level )
	
	def challengeTeamCancelSub( self, exposed ):
		# �˳������̨������
		# define method
		BigWorld.globalData[ "TeamChallengeMgr" ].calcelSubstitute( self.base )

	def challengeTeamRecruit( self,exposed ):
		# �������������̨��ļ
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
		# ����ȡ�������̨��ļ
		BigWorld.globalData[ "TeamChallengeMgr" ].cancelRecruitTeam( self.teamMailbox )

	def challengeTeamRecruitResult( self, exposed, teamID, result ):
		# ������ļ���
		# exposed method
		if not self.hackVerify_( exposed ):
			return
					
		if result:
			if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON:
				# ����
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_PRISON, "" )
				
			elif self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
				# ������ͨ��ͼ
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IN_SPACE_COPY, "" )
				
			elif self.isInTeam():
				# ���
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM, "" )

			elif self.getState() == csdefine.ENTITY_STATE_DEAD:
				# ����
				self.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_DIE, "" )

			elif self.getState() == csdefine.ENTITY_STATE_FIGHT:
				# ս��
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
		# �����̨����
		# define method
		if type ==  csconst.TEAM_CHALLENGE_REWARD_COMMON:
			rewardExp = int( 2106 * ( 25 + 5 * self.level ** 1.2 ) )
			self.addExp( rewardExp, csdefine.CHANGE_EXP_TEAM_CHALLENGE )
		elif type == csconst.TEAM_CHALLENGE_REWARD_WIN:
			rewardExp = int( 50 * ( 25 + 5 * self.level ** 1.2 ) * ( 4 * arg + 6 ) )
			self.addExp( rewardExp, csdefine.CHANGE_EXP_TEAM_CHALLENGE )

	def teamChallengeSetChampion( self, rewardTime ):
		# ���������̨�ھ�
		# define method
		self.set( "teamChallengeChampion", ( rewardTime, False ) )

	def teamChallengeGather( self, exposed ):
		# �����̨����
		# Exposed method.
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return

		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )
	
	def teamChallengeOnDieResult( self, exposed, result ):
		# �����̨�����Ƿ��ս�������
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
	# ������
	#--------------------------------------------------------------------
	def wuDaoSignUp( self, exposed ):
		# �����ᱨ��
		# Exposed method.
		if not self.hackVerify_( exposed ):
			return
			
		if self.level < 60:
			statusMessage( csstatus.ROLE_HAS_NOT_WUDAO_LEVEL, self._param1 )
			
		BigWorld.globalData['WuDaoMgr'].requestSignUp( self.level, self.base, self.databaseID )
		
	def wuDaoReward( self, round, step, isWinner ):
		# ���������ά��
		# define method
		if isWinner:
			self.addExp( int( 35 * ( 25 + 5 * self.level ** 1.2 ) * ( 4 * round + 6 ) ), csdefine.CHANGE_EXP_WUDAOAWARD )

	def wuDaoNoticeChampion( self, step, rewardTime ):
		# ֪ͨ���ξ����ھ�
		# define method
		self.sysBroadcast( cschannel_msgs.CELL_ROLEQUESTINTERFACE_1 %( self.getName(), step*10, step*10+9 ) )
		self.set( "wuDaoChampion", ( rewardTime, False ) )

	def wuDaoGather( self, exposed ):
		# �����Ἧ��
		# Exposed method.
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_WUDAO ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return

		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_WUDAO )

	#--------------------------------------------------------------------
	# �����̨
	#--------------------------------------------------------------------
	def tongAbaSignUp( self,exposed ):
		"""
		exposed method
		
		���������̨
		"""
		if not self.hackVerify_( exposed ):
			return
		if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_ABA ):	# ���ǰ����򸱰���,�ͻ���Ҳ���ж�
			self.onStatusMessage( csstatus.TONG_ABATTOIR_NOT_LEADER,"" )
			return
		self.tong_dlgAbattoirRequest()
		
	def tongAbaGather( self, exposed ):
		"""
		�����̨����
		"""
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return
		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TONG_ABA )

	#--------------------------------------------------------------------
	# ��Ӿ���
	#--------------------------------------------------------------------
	def teamCompetitionSignUp( self,exposed ):
		"""
		exposed method

		��Ӿ��������ӿ�,���ھ�������
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

		��Ӿ��������ʸ���֤
		"""
		if not self.hackVerify_( exposed ):
			return

		level = self.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1

		BigWorld.globalData["TeamCompetitionMgr"].requestTeamCompetition( self.base, level/10, self.teamMailbox )

	def teamCompetitionGather( self, exposed ):
		"""
		��Ӿ�������
		"""
		if not self.hackVerify_( exposed ):
			return

		if not self.challengeHasFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION ):
			self.client.onStatusMessage( csstatus.GB_GATHER_FAIL, "" )
			return
		self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	#--------------------------------------------------------------------
	# ��Ὰ��
	#--------------------------------------------------------------------
	def tongCompetitionGather( self, exposed ):
		"""
		exposed method
		��Ὰ������
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
		��Ὰ�������ӿ�
		"""
		if not self.hackVerify_( exposed ):
			return

		allowSignUp = BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" )
		if allowSignUp:
			if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_COMPETITION ):	# �����˱����ǰ��������Ǹ�����
				self.statusMessage( csstatus.TONG_COMPETETION_NOTICE_2 )
				return
			else:
				self.tong_competitionRequest( self )
		else:
			self.statusMessage( csstatus.TONG_COMPETETION_TONG_SIGNUP )

	#--------------------------------------------------------------------
	# ���˾���
	#--------------------------------------------------------------------
	def roleCompetitionGather( self, exposed ):
		"""
		exposed method
		���˾�������
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
		���˾��������ӿ�
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
		���ݲ�ͬ��ѡ��ִ�в�ͬ�Ĳ���
		"""
		if not self.hackVerify_( exposed ):
			return
		if result == True:
			self.onEnterWatchMode()
		else:
			self.reviveOnOrigin()
			self.challengeActivityTransmit( csconst.TRANSMIT_TYPE_ROLE_COMPETITION )
		
	def onEnterWatchMode( self ):
		# �����ս״̬
		self.reviveOnOrigin()
		self.effectStateInc( csdefine.EFFECT_STATE_DEAD_WATCHER )
		self.spellTarget( SKILL_ID1, self.id )

		
	def onLeaveWatchMode( self ):
		# define method
		# �˳���ս״̬
		self.effectStateDec( csdefine.EFFECT_STATE_DEAD_WATCHER )
		
	#---------------------------------------------------------------------
	#��ᳵ��ս
	#---------------------------------------------------------------------
	def turnWar_signUp( self, srcEntityID, memberMaxLevel, cityName ):
		"""
		Exposed method
		��������ս
		
		param memberMaxLevel:�����е���ߵȼ�
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["TongManager"].signUp( self.teamMailbox, self.base, memberMaxLevel, self.tong_dbID, self.getCamp(), cityName, self.playerName )
		
	def turnWar_onPrepared( self, srcEntityID ):
		"""
		Exposed method
		��Ա׼������
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["TongManager"].onTeamMemberPrepared( self.teamMailbox.id, self.databaseID, self.playerName )
		
	def turnWar_onEnterSpace( self, srcEntityID ):
		"""
		Exposed method
		�����ս,����Ҵ��복��սspace
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["TongManager"].requestEnterSpace( self.teamMailbox.id, self.base, self.playerName )
		
	def turnWar_setJoinFlag( self, isJoin ):
		"""
		define method
		ֻ�ڶӳ��������òμӳ���ս�ı��,�������Ӷ���
		"""
		self.turnWar_isJoin = isJoin
	
	#---------------------------------------------------------------------
	#��Ӫ����ս
	#---------------------------------------------------------------------
	def campTurnWar_signUp( self, srcEntityID, memberMaxLevel, cityName ):
		"""
		Exposed method
		��������ս
		
		param memberMaxLevel:�����е���ߵȼ�
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["CampMgr"].turnWar_signUp( self.teamMailbox, self.base, memberMaxLevel, self.getCamp(), cityName, self.playerName )
		
	def campTurnWar_onPrepared( self, srcEntityID ):
		"""
		Exposed method
		��Ա׼������
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["CampMgr"].turnWar_onTeamMemberPrepared( self.teamMailbox.id, self.databaseID, self.playerName )
		
	def campTurnWar_onEnterSpace( self, srcEntityID ):
		"""
		Exposed method
		�����ս,����Ҵ��복��սspace
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		BigWorld.globalData["CampMgr"].turnWar_requestEnterSpace( self.teamMailbox.id, self.base, self.playerName )
		
	def campTurnWar_setJoinFlag( self, isJoin ):
		"""
		define method
		ֻ�ڶӳ��������òμӳ���ս�ı��,�������Ӷ���
		"""
		self.turnWar_isJoin = isJoin
	
	#---------------------------------------------------------------------
	#��սȺ��
	#---------------------------------------------------------------------
	def aoZhan_playerInit( self ):
		"""
		��ɫ����
		"""
		if self.aoZan_checkJoinFlag():
			BigWorld.globalData[ "AoZhanQunXiongMgr" ].playerInit( self.databaseID,  self.base )
		else:
			if BigWorld.globalData.has_key( "ACTIVITY_AO_ZHAN_SIGN_UP" ):
				self.client.aoZhan_startSignUp()
	
	def aoZhan_playerDestroy( self ):
		"""
		��ɫ����
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].playerDestroy( self.databaseID )
	
	def aoZhan_signup( self, exposed ):
		"""
		exposed meothod.
		����
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].onSignUp( self.base, self.databaseID, self.getName(), self.getLevel(), self.getClass() )
	
	def aoZhan_onSignUp( self ):
		"""
		define method.
		�����ɹ�
		"""
		self.client.aoZhan_onSignUp()
	
	def aoZhan_setJoinFlag( self, uuid ):
		"""
		define method
		���ò����־
		"""
		self.set( "ACTIVITY_%d"%csdefine.ACTIVITY_AO_ZHAN_QUN_XIONG, uuid ) #�߻�Ҫ��10���Ӻ��
		self.client.aoZhan_setIsJoin( True )
	
	def aoZhan_removeJoinFlag( self ):
		"""
		define method
		ɾ�������־
		"""
		self.remove( "ACTIVITY_%d"%csdefine.ACTIVITY_AO_ZHAN_QUN_XIONG )
		self.client.aoZhan_setIsJoin( False )
	
	def aoZan_checkJoinFlag( self ):
		"""
		����Ƿ����
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
		����������
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].getSignUpList( self.base )

	def aoZhan_flushBattlefield( self, exposed ):
		"""
		exposed method.
		����ˢ��ս��
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].getBattlefield( self.base )
	
	def aoZhan_gotoEnterNPC( self, exposed ):
		"""
		exposed method
		���͵�����NPC
		"""
		if not self.hackVerify_( exposed ):
			return
			
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_AO_ZHAN_QUN_XIONG:
			self.gotoSpace( "fengming", ( 190.8, 10.4, 160.4 ), ( 0.007, 0.999, 0.034 ) )
			
	#---------------------------------------------------------------------
	#��Ӫ�������
	#---------------------------------------------------------------------
	def onRequestTransportCampFengHuo( self, srcEntityID ):
		"""
		���������
		"""
		if not self.hackVerify_( srcEntityID ):
			return
			
		BigWorld.globalData[ "CampMgr" ].onRoleRequestEnterCampFHLT( self.getCamp(), self.databaseID, self.base )
		
	def camp_onFengHuoLianTianOver( self ):
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# �ı�״̬,��Ѫ��ħ
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
		����߸���������Ǯ
		"""
		self.gainMoney( money, reason )
	
	def setCampFengHuo_signUpFlag( self, state ):
		"""
		define method
		������Ӫ������챨��״̬
		"""
		DEBUG_MSG( "player id is %s,state is %s"%( self.id, state ) )
		self.campFengHuo_signUpFlag = state
		self.client.setCampFengHuo_signUpFlag( state )
		
	def setCampFengHuoBattleInfo( self, remainTime, battleNum, maxNum ):
		"""
		define method
		������ҵı���ս�����ֺ�Ŀǰ�ѿ������ս������
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
		�������ս��������Ϣ
		"""
		DEBUG_MSG( "player id is %s,maxNum is %s"%( self.id, maxNum ) )
		self.set( "campFengHuo_maxNum", maxNum )
		
	def isOnlineShowCampFengHuoInfo( self, srcEntityID ):
		"""
		�Ƿ�������ʾ��Ӫ�������ս�������Ϣ
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
		��������˳���Ӫ������챨��
		"""
		if not self.hackVerify_( srcEntityID ):
			return
			
		BigWorld.globalData[ "CampMgr" ].onRequestCampFengHuoQuitSignUp( self.getCamp(), self.databaseID, self.base )
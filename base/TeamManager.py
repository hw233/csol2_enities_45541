# -*- coding: gb18030 -*-
#
# $Id: TeamManager.py,v 1.3 2007-11-16 03:44:02 zhangyuxing Exp $

import BigWorld
from bwdebug import *

class TeamManager(BigWorld.Base):
	def __init__( self ):
		BigWorld.Base.__init__(self)
		self.member = {}

		# ע��ENTITY
		# ���ؿռ�����
		self.registerGlobally("TeamManager", self._onRegisterManager)
		self.deregisterListeners = []

	#-----------------------------------------------------------
	# private
	def _onRegisterManager(self, complete):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TeamManager Fail!" )
			# again
			self.registerGlobally("TeamManager", self._onRegisterManager)
		else:
			BigWorld.globalData["TeamManager"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("Register TeamManager Success!")

	def register( self, teamID, teamMailBox ):
		"""
		<define>
		ע�����

		���̣�
		����¼����ID��MAILBOX

		@param teamID: ����ID
		@type teamID: OBJECT_ID
		@param teamMailBox: ����BASE
		@type teamMailBox: mailbox
		"""
		self.member[teamID] = teamMailBox

	def deregister( self, teamID ):
		"""
		<define>
		ɾ������

		���̣�
		���Ӷ�������ɾ��������Ϣ

		@param teamID: ����ID
		@type teamID: OBJECT_ID
		"""
		if self.member.has_key(teamID):
			self.member.pop( teamID )

		for i in self.deregisterListeners:
			i.onTeamDeregister( teamID )


	def rejoinTeam( self, teamID, playerDBID, playerBase ):
		"""
		<define>
		�������

		���̣�
		���������������Ҷ��飬������ж��飬֪ͨ���鱾�������

		@param teamID: ����ID
		@type teamID: OBJECT_ID
		@param playerDBID: ���DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: ���BASE
		@type playerBase: mailbox
		"""
		if not self.member.has_key( teamID ):
			playerBase.clearTeamInfo()
			return

		self.member[teamID].logon( playerDBID, playerBase )

	def addDeregisterListener( self, mailbox ):
		"""
		define method
		���ӶԶ����ɢ����Ȥ������
		"""
		self.deregisterListeners.append( mailbox )

	def setMessage( self, teamID, statuID ):
		# define method
		# ��ָ���Ķ��鷢����ʾ��Ϣ
		if self.member.has_key( teamID ):
			self.member[teamID].setMessage( statuID )

	# ---------------------------------------------------------
	# �����̨
	# ---------------------------------------------------------
	def teamChallengeAddMember( self, teamID, playerDBID, playerName, playerLevel, playerBase, playerRaceclass, headTextureID ):
		# define method
		# �����̨�Ӷ�Ա
		self.member[teamID].teamChallengeRequestJoin( playerDBID, playerName, playerLevel, playerBase, playerRaceclass, headTextureID )

	def teamChallengeChampion( self, teamID, entityDBIDs, minL, maxL, rewardTime ):
		# define method
		# �����̨�ھ���
		self.member[teamID].teamChallengeChampion( entityDBIDs, minL, maxL, rewardTime )

	def teamChallengeGather( self, teamID, round ):
		# define method
		# ����޶Ӽ���
		self.member[teamID].teamChallengeGather( round )

	def teamChallengeCloseGather( self, teamList ):
		# define method
		# �ر�����޶Ӽ���
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeCloseGather()

	def teamChallengeSetResult( self, teamList, result ):
		# define method
		# ��������޶ӽ��
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeSetResult( result )

	def removeDeregisterListener( self, mailbox ):
		"""
		define method
		ɾ���Զ����ɢ����Ȥ������
		"""
		for i in self.deregisterListeners:
			if i.id == mailbox.id:
				self.deregisterListeners.remove( i )
				break

	def teamChallengeUpLevel( self, teamID, maxLevel, minLevel ):
		# define method
		# ���±����ȼ�
		if self.member.has_key( teamID ):
			self.member[ teamID ].teamChallengeUpLevel( maxLevel, minLevel )

	def teamChallengeUpInfo( self, teamList, result ):
		# define method
		# ���µ�ǰ���������
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeUpInfo( result )

	def teamChallengeClose( self, teamList ):
		# define method
		# �����̨�����
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeClose()

	def teamRemoteCall( self, teamID, rFuncName, args ) :
		"""
		<Define method>
		Զ�̵��ö����ָ������
		@type		teamID : OBJECT_ID
		@param		teamID : �����ID
		@type		rFuncName : STRING
		@param		rFuncName : �����Զ�̷�������
		@type		args : PY_ARGS
		@param		args : Զ�̷���������ɵ�Ԫ��
		"""
		if teamID in self.member :
			getattr( self.member[teamID], rFuncName )( *args )
		else :
			WARNING_MSG( "Team(ID:%i) not found. Remote method is %s" % ( teamID, rFuncName ) )

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/10/09 07:55:45  phw
# method modified: rejoinTeam(), playerBase.teamNotHas() -> playerBase.clearTeamInfo()
#
# Revision 1.1  2006/11/29 02:05:51  panguankong
# ����˶���ϵͳ
#
# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function
import csconst
import csstatus

class FuncAllyRequest( Function ):
	"""
	����Ҫһ�����£�������
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
			return
		player.client.rlt_askForStartAlly()
		
		
class FuncAllyJoinNewMember( Function ):
	"""
	���������ֵ��ˣ��������
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForJoinAllyMember" )
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if not player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_ADD_MEMBER_NO_ALLY )
			#DEBUG_MSG( "��û�н�ݣ���ô������ֵܣ��Һ�æ�ģ���Ҫ���Ұ���" )
			return
		player.client.rlt_askForJoinAllyMember()
		
class FuncAllyChangeTitle( Function ):
	"""
	���Ľ�ݳƺ�
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>FuncAllyChangeTitle" )
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		# �ж��Ƿ����е��ֵܶ��ڣ��ж��Ƿ���Ǯ
		if not player.isInTeam():
			player.statusMessage( csstatus.CANNOT_CHANGE_TITLE_NO_TEAM )
			#DEBUG_MSG( "��Ҫ���Ľ�ݳƺű��������ֵ������һ�ӣ�һ������ɡ�" )
			return
		if not player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_CHANGE_TITLE_NO_ALLY )
			#DEBUG_MSG( "��û�н�ݣ���ô�ĳƺţ��Һ�æ�ģ���Ҫ���Ұ���" )
			return
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
			#DEBUG_MSG( "�öӳ�������˵�ɣ���������һȺ��һ������̫�����ˣ�" )
			return
		if player.money < csconst.ALLY_CHANGE_TITLE_COST:
			player.statusMessage( csstatus.CANNOT_CHANGE_TITLE_NO_MONEY, csconst.ALLY_CHANGE_TITLE_COST/10000 )
			#DEBUG_MSG( "��������Ҫ���ѵģ���׼����5������������" )
			return
		tammateList = talkEntity.searchTeamMember( player.teamMailbox.id, csconst.RELATION_ALLY_SWEAR_DISTANCE )
		if len( player.allyPlayers ) > len( tammateList ):
			player.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "�ǲ������ֵ�û�����������Ͽ������" )
			return
		if len( player.allyPlayers ) + 1 < len( tammateList ):
			player.statusMessage( csstatus.ALLY_CANNOT_WRONG_PLAYER )
			#DEBUG_MSG( "��������ô�в���ɵ��ˣ�" )
			return
		tempDBIDList = [item["playerDBID"] for item in player.allyPlayers]
		tempDBIDList.append( player.databaseID )
		if set( [entity.databaseID for entity in tammateList] ) != set( tempDBIDList ):
			player.statusMessage( csstatus.ALLY_CANNOT_WRONG_PLAYER )
			#DEBUG_MSG( "��������ô�в���ɵ��ˣ�" )
			return
		player.client.rlt_askForChangeAllyTitle()
		
		
class FuncQuitAlly( Function ):
	"""
	�������������˳����
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		player.endGossip( talkEntity )
		if not player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_QUIT_NO_ALLY )
			#DEBUG_MSG( "��û�н�ݣ������˳����Һ�æ�ģ���Ҫ���Ұ���" )
			return
		player.client.rlt_askForQuitAlly()
		
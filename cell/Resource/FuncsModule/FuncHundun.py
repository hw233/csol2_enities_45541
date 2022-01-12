# -*- coding: gb18030 -*-

"""
���������
"""
import time
import BigWorld
from Function import Function
import csdefine
import csstatus
import utils
from bwdebug import *

TEAM_MEMBER_NEED = 3																	#��Ҫ�Ķ����Ա

class FuncHundun( Function ):
	"""
	������縱��
	(fu_ben_hun_dun_ru_qin)
	"""
	def __init__( self, section ):
		"""
		"""
		self.__mapName 		= section["param1"].asString								#��ͼ��
		self.__level		= section["param2"].asInt									#��Ҫ�ȼ�
		
		self.__pos = None																#����λ��
		position = section.readString( "param3" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param3 " % ( self.__class__.__name__, position ) )
		else:
			self.__pos = pos
		
		self.__direction = None
		direction = section.readString( "param4" )										#���볯��
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param4 " % ( self.__class__.__name__, direction ) )
		else:
			self.__direction = dir
			
		self.__distance		= section["param5"].asFloat									#��Ա����

	def do( self, player, talkEntity = None ):
		"""
		����������ָ���
		����
			�������������Ѷ�Ա����������
				�����Աû�н���������ġ����б�Ǽ�¼��ȥ���ģ�
				Ҫ��Ի����Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�
		"""
		player.endGossip( talkEntity )

		if talkEntity.hasFlag( csdefine.ENTITY_FLAG_COPY_STARTING ):
			player.client.onStatusMessage( csstatus.TALK_FORBID_NO_TASK, "" )
			return

		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_LEVEL, str(( self.__level, )) )
			return

		if not player.isInTeam():
			player.client.onStatusMessage( csstatus.TALK_FORBID_TEAM, "" )
			return
	
		#����û�и��������ߴ�������
		if not player.isTeamCaptain():
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_CAPTAIN, "" )
			return

		if player.getTeamCount() < TEAM_MEMBER_NEED :
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_MEMBER_AMOUNT, str(( TEAM_MEMBER_NEED, )) )
			return

		members = player.getAllMemberInRange( self.__distance )
		
		if len( members ) < len( player.teamMembers ):
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_MEMBER_NEAR, "" )
			return
		
		for i in members:
			if i.level < self.__level:
				player.client.onStatusMessage( csstatus.HUNDUN_FORBID_MEMBER_LEVEL, str(( i.getName(), self.__level )) )
				return
		
		BigWorld.cellAppData["HD_%i"%player.teamMailbox.id] = talkEntity.id
		print "monster id:",BigWorld.cellAppData["HD_%i"%player.teamMailbox.id]
		#player.setTemp("copySpaceEnterMonsterID", talkEntity.id )		
		player.gotoSpace( self.__mapName, self.__pos, self.__direction )
		members.remove( player )
		
		for i in members:
			#i.setTemp("copySpaceEnterMonsterID", talkEntity.id )
			i.set( "lastHundunTeamID", player.getTeamMailbox().id )
			i.gotoSpace( self.__mapName, self.__pos, self.__direction )

		#talkEntity.destroy()
		talkEntity.addFlag( csdefine.ENTITY_FLAG_COPY_STARTING )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return BigWorld.globalData.has_key( "AS_Hundun" )




class FuncQueryJiFen( Function ):
	"""
	�鿴���縱��
	(fu_ben_hun_dun_ru_qin)
	"""
	def __init__( self, section ):
		pass
	
	
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		player.client.onStatusMessage( csstatus.HUNDUN_INTEGRAL, str(( player.query("hundun_jifen", 0), )) )


	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True

class FuncChangeJifen( Function ):
	"""
	���縱���һ�����
	(fu_ben_hun_dun_ru_qin)
	"""
	def __init__( self, section ):
		self._new_title 		= section["param1"].asInt									#�һ��ƺ�
		self._need_title		= section["param2"].asInt									#����ƺ�
		self._jifen		 		= section["param3"].asInt									#�������
	
	
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		
		if player.hasTitle( self._new_title ):
			player.client.onStatusMessage( csstatus.TITLE_REPEAT, "" )
			return
		
		if self._need_title != 0 and not player.hasTitle( self._need_title ):
			player.client.onStatusMessage( csstatus.TITLE_CANNOT_CHANGED, "" )
			return
		
		jifen = player.query("hundun_jifen")
		if jifen < self._jifen:
			player.client.onStatusMessage( csstatus.TITLE_FORBID_INTEGRAL_NOT_ENOUGH, str(( self._jifen, )) )
			return
		
		player.set("hundun_jifen", jifen - self._jifen )
		
		player.addTitle( self._new_title )


	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True
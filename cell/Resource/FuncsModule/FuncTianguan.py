# -*- coding: gb18030 -*-
#
# $Id: FuncTianguan.py,v 1.6 2008-09-01 03:37:25 zhangyuxing Exp $

"""
"""
from Function import Function
#import ChuangtianguanMgr
import csdefine
import csstatus
import Language
import time
import BigWorld
import utils
from bwdebug import *
import csdefine

ENTERN_TIANGUAN_MENBER_DISTANCE = 30					#��س�Ա����

class FuncCreateTianguan( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		self.level 		= section.readInt( "param2" )								#�����Ҫ�ȼ�
		self._longM 	= section.readInt( "param3" )								#��ؿ���ʱ�䳤��

		self.position = None														#�������λ��
		position = section.readString( "param4" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param4 " % ( self.__class__.__name__, position ) )
		else:
			self.position = pos
		
		self.direction = None
		direction = section.readString( "param5" )									#������س���
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param5 " % ( self.__class__.__name__, direction ) )
		else:
			self.direction = dir
				
		self.recordKey = "tianguan_record"
		self.spaceName = section.readString( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		������ظ�����
		����
			�������������Ѷ�Ա����������
				������鵱ǰû�и�����
				Ҫ��������Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
				�����Աû�н���������ġ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.TIAN_GUAN_NEED_TEAM )
			return
		if self.level > player.level:
			player.statusMessage( csstatus.ROLE_HAS_NOT_TIANGUAN_LEVEL, self.level )
			return
		if BigWorld.globalData.has_key( 'Tianguan_%i'%player.getTeamMailbox().id ):
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_CHUANG_TIAN_GUAN )  and player.query( "lastTianguanTeamID", 0 ) != player.getTeamMailbox().id:
				player.client.onStatusMessage( csstatus.TIANGUAN_IN_ALREADY, "" )
				return
			player.gotoSpace( self.spaceName, self.position, self.direction )
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
				
			pList = player.getAllMemberInRange( ENTERN_TIANGUAN_MENBER_DISTANCE )
			if not len(pList) >= 3 :
				player.statusMessage( csstatus.ROLE_IS_ENOUGH_MEMBER )
				return	

			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_TIANGUAN_LEVEL, self.level )
					return
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_CHUANG_TIAN_GUAN ) :
					player.statusMessage( csstatus.TIANGUAN_MEMBER_HAS_ENTERED_TODAY, i.getName() )
					return
			player.gotoSpace( self.spaceName, self.position, self.direction )	# �ӳ������һ�����븱��
			pList.remove( player )
			for i in pList:
				if i.id == player.id: #��ֹ��GM������Ӷ������plist�������쳣���Ӷ����´����쳣
					continue
				i.set( "lastTianguanTeamID", player.getTeamMailbox().id )
				i.gotoSpace( self.spaceName, self.position, self.direction )

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
		return True
		#return BigWorld.globalData.has_key( "AS_Tianguan" )


class FuncLastReward( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		pass
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )


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
		if talkEntity.isReal():
			talkEntity.getScript().touch( talkEntity, player )
		else:
			talkEntity.remoteScriptCall( "touch", ( player, ) )
		return False

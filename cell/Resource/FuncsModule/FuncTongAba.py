# -*- coding: gb18030 -*-
#
#

import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import csdefine
import csconst
import csstatus
from Function import Function



class FuncTongAbaRequest( Function ):
	"""
	��������̨��
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )


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
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return

		if player.level < csconst.PK_PROTECT_LEVEL:
			player.setGossipText( cschannel_msgs.TONG_ABA_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return
		
		if not BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_SINGUP:
			# ʱ�䲻��
			player.client.onStatusMessage( csstatus.TONG_ABATTOIR_NOT_SIGN_UP_TIME, "" )
			return
		player.tong_dlgAbattoirRequest()

class FuncTongAbaEnter( Function ):
	"""
	���������̨��ս��
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.map = section.readString( "param1" )
		self.level = section.readInt( "param2" )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.level < self.level:
			player.client.onStatusMessage( csstatus.TONG_NO_WAR_LEVEL, "" )
			player.endGossip( talkEntity )
			return
		if player.tong_grade <= 0 or player.tong_dbID <= 0:
			player.client.onStatusMessage( csstatus.TONG_NO_WAR_NOT_IN_TONG, "" )
			player.endGossip( talkEntity )
			return
		player.gotoSpace( self.map, ( 0, 0, 0 ), ( 0, 0, 0 ) )
		player.endGossip( talkEntity )
		
class FuncTongAbaReward( Function ):
	"""
	��ȡ�ھ�������Ʒ����
	"""
	def __init__( self,section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.itemID = section.readInt( "param1" )	# ��������ƷID
		self.requireTitleID = section.readInt( "param2" )	# �ƺ�ID

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
		if not BigWorld.globalData.has_key("tongAbattoirChampionDBID"):
			player.statusMessage( csstatus.ROLE_HAS_NOT_JOIN_ABATTOIR )
			return
		if not player.databaseID in BigWorld.globalData[ "tongAbattoirChampionDBID" ]:
			player.statusMessage( csstatus.ROLE_HAS_NOT_JOIN_ABATTOIR )
			return
		
		if self.itemID != 0:
			item = player.createDynamicItem( self.itemID )
			kitbagState = player.checkItemsPlaceIntoNK_( [item] )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# �����ռ䲻��
				player.statusMessage( csstatus.CIB_MSG_CANT_OPERATER_FULL )
				player.sendGossipComplete( talkEntity.id )
				return
			player.addItemAndNotify_( item, csdefine.REWARD_TONG_ABA )
			player.addTitle( self.requireTitleID )
			player.selectTitle( player.id, self.requireTitleID )
			
		temp = BigWorld.globalData[ "tongAbattoirChampionDBID" ]
		temp.remove( player.databaseID )
		BigWorld.globalData[ "tongAbattoirChampionDBID" ] = temp
	
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

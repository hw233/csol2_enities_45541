# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import csdefine
import BigWorld
import csstatus
import Language
import time

class FuncTestActivityGift( Function ):
	"""
	���ȼ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._level 	= section.readInt( "param1" )				#����
		self._type		= section.readInt( "param2" )				#���� ��0��Ϊ�ȼ������� 1Ϊ�ƹ�Ա������
		self._signPos	= section.readInt( "param3" )				#��¼λ��
		self._itemID	= section.readInt( "param4" )				#��ƷID

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""

		if player.level < self._level:
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_1)
			player.sendGossipComplete( talkEntity.id )
			return


		arS = player.queryAccountRecord("testActivityRecordSign")
		if arS == "":
			arS = "0"

		if int( arS ) & ( 1 << self._signPos ):
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_2)
			player.sendGossipComplete( talkEntity.id )
			return

		itemIDs = [self._itemID]

		if player.getNormalKitbagFreeOrderCount() < len( itemIDs):
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_3)
			player.sendGossipComplete( talkEntity.id )
			return

		for i in itemIDs:
			m_item = player.createDynamicItem( int(i) )
			player.addItem( m_item, csdefine.ADD_ITEM_TESTACTIVITYGIFT )

		value = int( arS ) + ( 1 << self._signPos )
		player.setAccountRecord( "testActivityRecordSign", str(value) )


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
		arS = player.queryAccountRecord("testActivityRecordSign")
		if arS == "":
			arS = "0"
		return ( player.level >= self._level - 10 ) and ( not ( int(arS ) & ( 1 << self._signPos ) ) )




class FuncTestWeekGift( Function ):
	"""
	ÿ�ܵȼ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._minlevel 	= section.readInt( "param1" )				#��С����
		self._maxlevel 	= section.readInt( "param2" )				#��󼶱�
		self._yuanbao	= section.readInt( "param3" )				#����Ԫ������

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		#(2009, 6, 29, 0, 0, 0, 0, 180, 0)  #�����ܵ����

		#curt = time.mktime( (2009, 6, 29, 0, 0, 0, 0, 180, 0) )
		#wT = int( ( time.time() - curt ) / ( 3600 * 24 * 7 ) )
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)

		if str( wT ) != player.queryAccountRecord( "weekGiftTime" ):
			player.base.remoteCall( "gainSilver", ( self._yuanbao, csdefine.CHANGE_SILVER_TESTWEEKGIFT, ) )
			player.setAccountRecord( "weekGiftTime", str( wT ) )
			player.endGossip( talkEntity )
		else:
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_4)
			player.sendGossipComplete( talkEntity.id )


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
		return ( player.level >= self._minlevel ) and ( player.level <= self._maxlevel )


class FuncSpreaderGift( Function ):
	"""
	�ƹ�Ա����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._level 	= section.readInt( "param1" )				#����
		self._type		= section.readInt( "param2" )				#���� ��0��Ϊ�ȼ������� 1Ϊ�ƹ�Ա������
		self._signPos	= section.readInt( "param3" )				#��¼λ��
		self._itemID	= section.readInt( "param4" )				#��ƷID

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""

		if not player.hasFlag( csdefine.ROLE_FLAG_SPREADER ):
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_5)
			player.sendGossipComplete( talkEntity.id )
			return

		if player.level < self._level:
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_1)
			player.sendGossipComplete( talkEntity.id )
			return

		arS = player.queryAccountRecord("testActivityRecordSign")
		if arS == "":
			arS = "0"

		if int( arS ) & ( 1 << self._signPos ):
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_2)
			player.sendGossipComplete( talkEntity.id )
			return

		sect = Language.openConfigSection( "config/server/TestActivityGift.xml" )

		giftStr = ""
		for iSect in sect.values():
			if iSect["testActivityType"].asInt == self._type and iSect["reLevel"].asInt == self._level:
				giftStr = iSect["gifts"].asString
				break

		if giftStr == "":
			return

		#yuanbao = 0
		itemIDs = [self._itemID]
		"""
		giftStr = giftStr.replace( " ", "" )
		for iType in giftStr.split( "&" ):
			g = iType.split(":")
			if g[0] == "yuanbao":
				yuanbao += int( g[1] )

			if g[0] == "items":
				itemIDs.extend( g[1].split("|") )
		"""
		if player.getNormalKitbagFreeOrderCount() < len( itemIDs):
			player.setGossipText(cschannel_msgs.FENG_CE_JIANG_LI_VOICE_3)
			player.sendGossipComplete( talkEntity.id )
			return
		for i in itemIDs:
			m_item = player.createDynamicItem( int(i) )
			player.addItem( m_item, csdefine.ADD_ITEM_SPREADERGIFT )

		value = int( arS ) + ( 1 << self._signPos )
		player.setAccountRecord( "testActivityRecordSign", str(value) )

		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True


class FuncTestQueryGift( Function ):
	"""
	��ѯ����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
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
		gossipText = ""
#		daysSec = 24 * 3600
#		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)
#		if str( wT ) != player.queryAccountRecord( "weekGiftTime" ):
#			gossipText += "@B@S{4}�����ʺŻ�δ��ȡ����Ԫ��,�뾡���½�ʺ�����ߵȼ���ɫ��ȡ,���������ʧ!"
#		else:
#			gossipText += "@B@S{4}�����ʺ��Ѿ���ȡ�˱���Ԫ����"

		arS = player.queryAccountRecord("testActivityRecordSign")
		if arS == "":
			arS = "0"

		for e in xrange( 1, 6 ):
			if int( arS ) & ( 1 << e ):
				gossipText += cschannel_msgs.FENG_CE_JIANG_LI_VOICE_6 %(e*10)
			else:
				gossipText += cschannel_msgs.FENG_CE_JIANG_LI_VOICE_7 %( e*10, e*10 )

		player.setGossipText( gossipText )
		player.sendGossipComplete( talkEntity.id )

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
		return  True


class FuncQueryWeekOnlineTime( Function ):
	"""
	��ѯ��������ʱ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
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
		player.base.queryWeekOnlineTime( talkEntity.id )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		return  True


class FuncGetWeekOnlineTimeGift( Function ):
	"""
	��ȡ���ܹ���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
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
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)

		if str( wT ) == player.queryAccountRecord( "weekOnlineTimeGift" ):
			player.statusMessage( csstatus.WEEK_ONLINE_TIME_GIFT_DONE )
			return

		if player.level < 60:
			player.statusMessage( csstatus.WEEK_ONLINE_TIME_LIMIT_LEVEL )
			return

		if player.teachCredit < 3000:
			player.statusMessage( csstatus.WEEK_ONLINE_TIME_LIMIT_TEACH_CREDIT )
			return

		player.base.getWeekOnlineTimeGift( wT - 1 )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		return  True


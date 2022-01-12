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
	封测等级奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._level 	= section.readInt( "param1" )				#级别
		self._type		= section.readInt( "param2" )				#类型 （0，为等级奖励， 1为推广员奖励）
		self._signPos	= section.readInt( "param3" )				#记录位置
		self._itemID	= section.readInt( "param4" )				#物品ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
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
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
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
	每周等级奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._minlevel 	= section.readInt( "param1" )				#最小级别
		self._maxlevel 	= section.readInt( "param2" )				#最大级别
		self._yuanbao	= section.readInt( "param3" )				#奖励元宝数量

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		#(2009, 6, 29, 0, 0, 0, 0, 180, 0)  #计算周的起点

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
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return ( player.level >= self._minlevel ) and ( player.level <= self._maxlevel )


class FuncSpreaderGift( Function ):
	"""
	推广员奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._level 	= section.readInt( "param1" )				#级别
		self._type		= section.readInt( "param2" )				#类型 （0，为等级奖励， 1为推广员奖励）
		self._signPos	= section.readInt( "param3" )				#记录位置
		self._itemID	= section.readInt( "param4" )				#物品ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
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
	查询奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		gossipText = ""
#		daysSec = 24 * 3600
#		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)
#		if str( wT ) != player.queryAccountRecord( "weekGiftTime" ):
#			gossipText += "@B@S{4}您的帐号还未领取本周元宝,请尽快登陆帐号中最高等级角色领取,以免造成损失!"
#		else:
#			gossipText += "@B@S{4}您的帐号已经领取了本周元宝。"

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
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return  True


class FuncQueryWeekOnlineTime( Function ):
	"""
	查询本周在线时间
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.base.queryWeekOnlineTime( talkEntity.id )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		return  True


class FuncGetWeekOnlineTimeGift( Function ):
	"""
	领取上周工资
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
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
		检查一个功能是否可以使用
		"""
		return  True


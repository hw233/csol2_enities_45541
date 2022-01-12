# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.17 2008-08-30 09:03:04 huangyongwei Exp $
"""
implement chat system

09/05/2005 : created by phw
11/28/2006 : modified by huangyongwei
"""

import time
import struct
import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
import wizCommand
from MsgLogger import g_logger


# --------------------------------------------------------------------
# implement channels
# --------------------------------------------------------------------
class Channel( object ) :
	def __init__( self, id ) :
		self.id = id										# 频道 ID

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		virtual method
		处理频道消息
		"""
		raise TypeError( "channel '%s' must implement method 'handle'" % self.__class__.__name__ )

# -----------------------------------------------------
class CHN_Near( Channel ) :
	"""
	附近
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理频道消息
		"""
		speaker.planesAllClients( "chat_onChannelMessage", ( csdefine.CHAT_CHANNEL_NEAR, speaker.id, speaker.getName(), msg, blobArgs ) )

# -------------------------------------------
class CHN_World( Channel ) :
	"""
	世界
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理频道消息
		"""
		if speaker.iskitbagsLocked():	# 背包上锁，by姜毅
			speaker.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		if speaker.level < csconst.CHAT_YELL_LEVEL_REQUIRE :
			speaker.statusMessage( csstatus.CHAT_YELL_MONEY_NOTENOUGH )
		elif speaker.queryTemp( "chat_last_yell_time", 0 ) + csconst.CHAT_YELL_DELAY > time.time() :
			speaker.statusMessage( csstatus.CHAT_YELL_TOO_CLOSE )
		elif speaker.payMoney( csconst.CHAT_YELL_USE_MONEY, csdefine.CHANGE_MONEY_CHAT_YELL ) :
			speaker.base.chat_handleMessage( csdefine.CHAT_CHANNEL_WORLD, "", msg, blobArgs )
			speaker.setTemp( "chat_last_yell_time", time.time() )
		else :
			speaker.statusMessage( csstatus.CHAT_YELL_MONEY_NOTENOUGH )

# -------------------------------------------
class CHN_Rumor( Channel ) :
	"""
	谣言
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理频道消息
		"""
		now = time.time()
		lastTime = speaker.queryTemp( "chat_last_rumor_time", 0 )			# 上次发生谣言的时间
		if lastTime + csconst.CHAT_RUMOR_DELAY > now :						# 还没到发言时间
			speaker.statusMessage( csstatus.CHAT_RUMOR_TOO_CLOSE )
			return
		wasteMP = int( csconst.CHAT_RUMOR_MP_DECREMENT * speaker.MP_Max )	# MP 损耗值
		if speaker.MP < wasteMP :											# 当前 MP 不足
			speaker.statusMessage( csstatus.CHAT_RUMOR_MP_NOT_ENOUGH )
			return
		speaker.setTemp( "chat_last_rumor_time", now )						# 记录下本次发言时间
		speaker.addMP( -wasteMP )											# 损耗 MP
		speaker.base.chat_handleMessage( self.id, "", msg, blobArgs )		# 在 base 中广播谣言
		try:
			g_logger.sendRumorLog( speaker.databaseID, speaker.getName(), msg )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

# -------------------------------------------
class CHN_Welkin( Channel ) :
	"""
	天音
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理频道消息
		"""
		if speaker.iskitbagsLocked():	# 背包上锁，by姜毅
			speaker.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		welkinItemID = csconst.CHAT_WELKIN_ITEM
		welkinItem = speaker.findItemFromNKCK_( welkinItemID )							# 查找背包中是否有天音符
		if welkinItem :
			speaker.removeItem_( welkinItem.order, 1, csdefine.DELETE_ITEM_WELKINYELL )	# 如果能在背包中找到天音符，则删除一个天音符
			speaker.base.chat_handleMessage( self.id, "", msg, blobArgs )
		else :																			# 如果背包中没有天音符
			speaker.base.spe_onAutoUseYell( welkinItemID, csdefine.SPECIALSHOP_MONEY_TYPE_GOLD, msg, blobArgs )

# -------------------------------------------
class CHN_Tunnel( Channel ) :
	"""
	地音
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理频道消息
		"""
		if speaker.iskitbagsLocked():	# 背包上锁，by姜毅
			speaker.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		tunnelItemID = csconst.CHAT_TUNNEL_ITEM
		tunnelItem = speaker.findItemFromNKCK_( tunnelItemID )							# 查找背包中是否有地音符
		if tunnelItem is None:	# 地音号角蛋疼地搞出两个品种 这里加入对绑定版的处理 by姜毅
			tunnelItemID = csconst.CHAT_TUNNEL_ITEM_BINDED
			tunnelItem = speaker.findItemFromNKCK_( tunnelItemID )
		if tunnelItem :
			speaker.removeItem_( tunnelItem.order, 1, csdefine.DELETE_ITEM_TUNNELYELL )	# 如果能在背包中找到地音符，则删除一个地音符
			speaker.base.chat_handleMessage( self.id, "", msg, blobArgs )
		else :																			# 如果背包中没有地音符
			tunnelItemID = csconst.CHAT_TUNNEL_ITEM
			speaker.base.spe_onAutoUseYell( tunnelItemID, csdefine.SPECIALSHOP_MONEY_TYPE_SILVER, msg, blobArgs )

class CHN_Local( Channel ) :
	"""
	本地
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 base / cell 发送过来的消息
		"""
		spaceBase = speaker.getCurrentSpaceBase()
		spaceBase.onChatChannelMessage( self.id, speaker.id, speaker.getName(), msg, blobArgs )


# -------------------------------------------
class CHN_Camp( Channel ) :
	"""
	阵营
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理频道消息
		"""
		if speaker.queryTemp( "chat_last_camp_time", 0 ) + csconst.CHAT_CMAP_DELAY > time.time() :
			speaker.statusMessage( csstatus.CHAT_SPEAK_TOO_CLOSE )
		else:
			speaker.base.chat_handleMessage( csdefine.CHAT_CHANNEL_CAMP, "", msg, blobArgs )
			speaker.setTemp( "chat_last_camp_time", time.time() )
			
class CHN_TongCityWar( Channel ) :
	"""
	帮会战争结盟专用频道
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 cell 发送过来的频道消息
		"""
		tong_grade = speaker.tong_grade
		tong_dbID = speaker.tong_dbID
		if speaker.getCurrentSpaceType() == csdefine.SPACE_TYPE_CITY_WAR_FINAL and tong_grade in csdefine.TONG_CITY_WAR_SPEAK:
			# 广播玩家的发言内容到同盟成员的 client
			BigWorld.globalData[ "TongManager" ].sendMessage2Alliance( tong_dbID, speaker.id, speaker.getName(), msg, blobArgs )

# -----------------------------------------------------
_channel_maps = {
	csdefine.CHAT_CHANNEL_NEAR			: CHN_Near,				# 附近（流程：base->cell）
	csdefine.CHAT_CHANNEL_LOCAL			: CHN_Local,			# 本地（流程：base->cell）
	csdefine.CHAT_CHANNEL_WORLD			: CHN_World,			# 世界（流程：base->cell->base）
	csdefine.CHAT_CHANNEL_RUMOR			: CHN_Rumor,			# 谣言（流程：base->cell->base）
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: CHN_Welkin,			# 天音（流程：base->cell->base）
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: CHN_Tunnel,			# 地音（流程：base->cell->base）
	csdefine.CHAT_CHANNEL_CAMP			: CHN_Camp,				# 阵营（流程：base->cell->base）
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : CHN_TongCityWar,		# 帮战 （流程：base-->cell-->TongCityWarFialManger-->同盟成员client）
	}

_channels = {}													# 所有频道列表
for channelID, CLSCannel in _channel_maps.iteritems() :
	_channels[channelID] = CLSCannel( channelID )
del _channel_maps


# --------------------------------------------------------------------
# implement chat system for role inheriting
# 特别提醒：
#	上面的频道是所有角色共用的，请不要在频道中定义角色相关的成员变量
# --------------------------------------------------------------------
class RoleChat :
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# defined mehods.
	# ----------------------------------------------------------------
	def chat_handleMessage( self, channelID, rcvName, msg, blobArgs ) :
		"""
		defined method
		处理一条频道消息，可以给其它 base 或 cell 调用
		@type				channelID : UINT32
		@param				channelID : 频道 ID
		@type				rcvName	  : STRING
		@param				rcvName	  : 消息接收者的名称
		@type				msg		  : STRING
		@param				msg		  : 消息内容
		@type				blobArgs  : BLOB_ARRAY
		@param				blobArgs  : 消息参数列表
		"""
		_channels[channelID].handle( self, rcvName, msg, blobArgs )

	# -------------------------------------------------
	def chat_sendRoleInfo( self, mbBase ) :
		"""
		defined method
		发送角色信息到指定客户端( hyw -- 2008.08.29 )
		@type				mbBase : MAILBOX
		@param				mbBase : 要发送到的客户端对应的 base mailbox
		"""
		if hasattr( mbBase, "client" ) :
			roleInfo = {}
			roleInfo["name"] = self.getName()
			roleInfo["level"] = self.level
			roleInfo["tong"] = self.tongName
			roleInfo["spaceLabel"] = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			mbBase.client.chat_onReceiveRoleInfo( roleInfo )
	
	def chat_switchFengQi( self, srcEntityID, unLocked ):
		"""
		/Exposed method
		设置夜战凤栖聊天框
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.onFengQi:
			return
		wizCommand.wizCommand( self, self.id, "switchFengQi", "%d"%int( unLocked ) )
	
	def chat_onSwitchFengQi( self, unLocked ):
		"""
		GM设置回调
		"""
		self.client.chat_onSwitchFengQi( unLocked )

# RoleChat.py

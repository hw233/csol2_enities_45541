# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.25 2008-08-30 09:02:16 huangyongwei Exp $
"""

09/05/2005 : created by phw
11/28/2006 : modified by huangyongwei
"""

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import ECBExtend
import Love3
import csdefine
import csconst
import csstatus
import Const
import time
import random
from bwdebug import *
from Function import Functor
import struct
import PLMChatRecorder


# --------------------------------------------------------------------
# imolement channels
# 设计思想：
#	① 频道包含一个 exposed 属性，用以标示该频道是否允许客户端直接调用
#	   chat_sendMessage 方法发送消息，从而防止，客户端才用外挂在不允许
#	   的频道中随便发送消息。
#	② 频道包含一个 isLimitByGBTime 属性，标示该频道是否受到全局发言时
#	   间的限制，所有受限制的频道，只要在其中一个频道中发送一条消息，就
#	   会记录下当前时间，如果时间间隔还没到就在另一个受限频道中发送信息
#	   这时将会被拒绝。
#	③ 频道包含一个 validate 验证方法，派生频道可以重载该方法，实现自己
#	   的制约。
#	④ 频道包含一个 handle 消息处理方法，该方法主要处理 base 本身或 cell
#	   发送的消息，因为 base 和 cell 发送的消息，是程序员制定的，因此它
#	   所受到的制约比较少，纯粹是消息转发，所以得独立开来
#	⑤ 频道包含一个 send 消息处理方法，该方法主要处理角色客户端发过来的
#	   消息，因此它的处理比较严谨。
# --------------------------------------------------------------------
class Channel( object ) :
	"""
	频道接口
	"""
	def __init__( self, id ) :
		self.id = id											# 频道 ID
		self.exposed = id in csconst.CHAT_EXPOSED_CHANNELS		# 该频道是否可以被客户端直接发言( 被 cell 调用的频道不能 exposed )
		self.isLimitByGBTime = self.exposed and \
			id in _limitByGBTimeChannels						# 是否受全局时间间隔限制

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def validate( self, speaker, rcvName, msg ) :
		"""
		消息验证
		"""
		if len( msg ) > csconst.CHAT_MESSAGE_UPPER_LIMIT :		# 发言内容过长
			speaker.statusMessage( csstatus.CHAT_WORDS_TOO_LONG )
			return False
		return True

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 base / cell 发送过来的消息
		"""
		pass																			# 默认不作处理

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		if hasattr( speaker, "cell" ) :
			speaker.cell.chat_handleMessage( self.id, rcvName, msg, blobArgs )			# 默认传给 cell 处理
		else :
			WARNING_MSG( "cell of '%s' is not ready or has been died!" % str( speaker ) )

# -----------------------------------------------------
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
		pass

# -------------------------------------------
class CHN_Team( Channel ) :
	"""
	队伍
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		if not speaker.getTeamMailbox() :
			speaker.statusMessage( csstatus.CHAT_NOT_IN_TEAM )
		else :
			speaker.teamChat( msg, blobArgs )

# -------------------------------------------
class CHN_Tong( Channel ) :
	"""
	帮会
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		if not speaker.isJoinTong():
			speaker.statusMessage( csstatus.CHAT_NOT_IN_TONG )
		else :
			speaker.sendMessage2Tong( speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_Whisper( Channel ) :
	"""
	密语
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	# ---------------------------------------
	# private
	# ---------------------------------------
	def __onReceiverFinded( self, speaker, rcvName, msg, blobArgs, receiver ) :
		"""
		注：
			receiver == BASE MAILBOX ：找到目标且已上线
			receiver == True		 ：找到目标但未上线
			receiver == False		 ：其它原因（如无此角色等）
		"""
		if not isinstance( receiver, bool ) :
			receiver.client.chat_onChannelMessage( self.id, speaker.id, speaker.playerName, msg, blobArgs )
			speaker.client.chat_onChannelMessage( self.id, speaker.id, rcvName, msg, blobArgs )
		elif receiver :
			speaker.statusMessage( csstatus.CHAT_WHISPER_NOT_ON_LINE, rcvName )
		else :
			speaker.statusMessage( csstatus.CHAT_WHISPER_NOT_EXIST, rcvName )

	# ---------------------------------------
	# public
	# ---------------------------------------
	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		if speaker.playerName == rcvName :
			speaker.statusMessage( csstatus.CHAT_WHISPER_YOURSELF_REFUSED )
			return
		if speaker.meInBlacklist( rcvName ) :									# 如果角色在对方的黑名单中
			speaker.statusMessage( csstatus.FRIEND_ME_IN_BLACKLIST )
			return
		callback = Functor( self.__onReceiverFinded, speaker, rcvName, msg, blobArgs )
		BigWorld.lookUpBaseByName( "Role", rcvName, callback )

# -------------------------------------------
class CHN_World( Channel ) :
	"""
	世界
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )
		self.isLimitByGBTime = False		# 世界频道有自己的延时规定

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 base / cell 发送过来的消息
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_Rumor( Channel ) :
	"""
	谣言
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 base / cell 发送过来的消息
		"""
		if random.random() >= csconst.CHAT_RUMOR_PROBABILITY :					# 造谣有一定几率失败（暴露发言者身份）
			name = speaker.playerName
		else :
			name = cschannel_msgs.ROLE_INFO_6
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_WelkinYell( Channel ) :
	"""
	天音
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 base / cell 发送过来的消息
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_TunnelYell( Channel ) :
	"""
	地音
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 base / cell 发送过来的消息
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -----------------------------------------------------
class CHN_SysBroadcast( Channel ) :
	"""
	系统广播
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -----------------------------------------------------
class CHN_NPCWorld( Channel ) :
	"""
	NPC 世界
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_Playmate( Channel ) :
	"""
	玩伴聊天
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	# ---------------------------------------
	# private
	# ---------------------------------------
	def __addOFLMsgCB( self, speaker, rcvName, success ) :
		"""
		离线消息添加到数据库回调
		"""
		if success :
			msg = cschannel_msgs.CHAT_FRIEND_RECEIVER_OFFLINE
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )

	def __queryAmountCB( self, speaker, rcvName, msg, blobArgs, amount ) :
		"""
		查询已存在消息数量的回调
		"""
		if amount >= Const.CHAT_FRIEND_OFL_MSG_CAPACITY :							# 消息保存已满
			msg = cschannel_msgs.CHAT_FRIEND_OFFLINE_MSG_OVERFLOW
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )	# spkID 设置为0是表明这是系统消息
		else :
			speaker.client.chat_onChannelMessage( self.id, speaker.id, rcvName, msg, blobArgs )
			callback = Functor( self.__addOFLMsgCB, speaker, rcvName )
			date = time.strftime( "%Y%m%d%H%M%S", time.localtime() )
			PLMChatRecorder.addOFLMessage( speaker.playerName, rcvName, msg, blobArgs, date, callback )

	def __onReceiverFinded( self, speaker, rcvName, msg, blobArgs, receiver ) :
		"""
		注：
			receiver == BASE MAILBOX ：找到目标且已上线
			receiver == True		 ：找到目标但未上线
			receiver == False		 ：其它原因（如无此角色等）
		"""
		if not isinstance( receiver, bool ) :										# 找到了玩家
			receiver.client.chat_onChannelMessage( self.id, speaker.id, speaker.playerName, msg, blobArgs )
			speaker.client.chat_onChannelMessage( self.id, speaker.id, rcvName, msg, blobArgs )
		elif receiver :																# 玩家已下线
			callback = Functor( self.__queryAmountCB, speaker, rcvName, msg, blobArgs )
			PLMChatRecorder.queryMsgsAmount( speaker.playerName, rcvName, callback )
		else :																		# 玩家不存在
			msg = cschannel_msgs.CHAT_FRIEND_RECEIVER_NOT_EXIST
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )

	# ---------------------------------------
	# public
	# ---------------------------------------
	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		处理 client 发送过来的频道消息
		"""
		if speaker.meInBlacklist( rcvName ) :										# 如果角色在对方的黑名单中
			msg = cschannel_msgs.CHAT_FRIEND_IN_BLACKLIST
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )	# spkID 设置为0是通知客户端这是系统消息
			return
		callback = Functor( self.__onReceiverFinded, speaker, rcvName, msg, blobArgs )
		BigWorld.lookUpBaseByName( "Role", rcvName, callback )

# -------------------------------------------
class CHN_Camp( Channel ):
	"""
	阵营
	"""
	def __init__( self, id ):
		Channel.__init__( self, id )
	
	def handle( self, speaker, rcvName, msg, blobArgs ):
		"""
		处理 client 发送过来的频道消息
		"""
		Love3.g_baseApp.campChat( speaker.getCamp(), self.id, speaker.id, speaker.playerName, msg, blobArgs )
		
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
		pass

		
# -----------------------------------------------------
_channel_maps = { \
	# 角色发言频道
	csdefine.CHAT_CHANNEL_NEAR			: Channel,				# 附近( 流程：base->cell->client )
	csdefine.CHAT_CHANNEL_LOCAL			: CHN_Local,			# 本地( 流程： )
	csdefine.CHAT_CHANNEL_TEAM			: CHN_Team,				# 队伍( 流程：base->base 上的队伍系统->成员 client )
	csdefine.CHAT_CHANNEL_TONG			: CHN_Tong,				# 帮会( 流程：base->base 上的帮会系统->成员 client )
	csdefine.CHAT_CHANNEL_WHISPER		: CHN_Whisper,			# 密语( 流程：base->client )
	csdefine.CHAT_CHANNEL_WORLD			: CHN_World,			# 世界( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_RUMOR			: CHN_Rumor,			# 谣言( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: CHN_WelkinYell,		# 天音( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: CHN_TunnelYell,		# 地音( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: CHN_TunnelYell,		# 地音( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : CHN_TongCityWar,		# 帮战( 流程：base-->cell）

	# GM/公告频道
	csdefine.CHAT_CHANNEL_SYSBROADCAST	: CHN_SysBroadcast,		# 系统广播( 流程：base->BaseappEntity-->client )

	# NPC 发言频道
	csdefine.CHAT_CHANNEL_NPC_SPEAK		: CHN_NPCWorld,			# NPC 世界( 流程：base->cell->BaseappEntity-->client )
	#csdefine.CHAT_CHANNEL_NPC_TALK		: Channel,				# NPC 对话（Base 中不会用到，仅仅客户端控制 statusMessage 显示位置的频道）

	# 系统提示
	csdefine.CHAT_CHANNEL_SYSTEM		: Channel,				# 系统频道（显示由服务器产生的各种活动、获得物品/强化/镶嵌等产生）
	#csdefine.CHAT_CHANNEL_COMBAT		: CHN_Combat,			# 战斗信息频道（base 中用不到）
	csdefine.CHAT_CHANNEL_PERSONAL		: Channel,				# 个人频道（显示角色的操作产生的错误信息或提示信息）
	csdefine.CHAT_CHANNEL_MESSAGE		: Channel,				# 消息（形式性频道）
	csdefine.CHAT_CHANNEL_SC_HINT		: Channel,				# 在屏幕中间显示信息的频道（没有固定意义）
	csdefine.CHAT_CHANNEL_MSGBOX		: Channel,				# 用提示框显示信息的频道（没有固定意义）

	# 玩伴聊天
	csdefine.CHAT_CHANNEL_PLAYMATE		: CHN_Playmate,			# 玩伴聊天
	
	# 阵营
	csdefine.CHAT_CHANNEL_CAMP		:CHN_Camp,
	}

# -------------------------------------------
_limitByGBTimeChannels = set( [									# 受全局时间间隔限制的频道
	csdefine.CHAT_CHANNEL_LOCAL,								# 本地
	csdefine.CHAT_CHANNEL_TEAM,									# 队伍
	csdefine.CHAT_CHANNEL_TONG,									# 帮会
	csdefine.CHAT_CHANNEL_WHISPER,								# 密语
	csdefine.CHAT_CHANNEL_PLAYMATE,								# 玩伴
	] )

_channels = {}													# 频道列表
for chid, CLSChannel in _channel_maps.iteritems() :
	_channels[chid] = CLSChannel( chid )
del _channel_maps


# --------------------------------------------------------------------
# chating system ( inherited by Role )
# rewriten by hyw--2009.08.13
# 特别注意：
#	上面的频道是所有角色共用的，请不要在频道中定义角色相关的成员变量
# --------------------------------------------------------------------
class RoleChat :
	def __init__( self ) :
		self.__lastMsgTime = 0					# 上次发言的时间
		self.__lasMsg = ""						# 上一次发言消息
		self.__repeatCount = 0					# 重复话语次数
		self.__tmpOflMsgs = []					# 发送给我的离线消息（临时变量）

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __validate( self, channel, rcvName, msg ) :
		"""
		检查消息的有效性
		注：不带参数的目的是，使得这里只检查角色自身相关的有效性，频道相关的有效性由频道各自处理
		"""
		if channel.isLimitByGBTime :										# 频道受时间间隔限制
			now = BigWorld.time()
			if self.__lastMsgTime + csconst.CHAT_GLOBAL_DELAY > now :		# 发言速度过快
				self.statusMessage( csstatus.CHAT_SPEAK_TOO_CLOSE )
				return False
			self.__lastMsgTime = now
		if self.__lasMsg == msg :											# 信息内容是否与前一次相同
			self.__repeatCount += 1
			if self.__repeatCount > csconst.CHAT_ESTOP_REPEAT_COUNT :		# 重复发言超过指定次数
				self.chat_lockMyChannels( [], csdefine.CHAT_FORBID_REPEAT, \
					csconst.CHAT_ESTOP_TIME )								# 禁言一段时间
				self.statusMessage( csstatus.CHAT_LOCK_REPEAT )
				return False
		else :																# 消息内容与前一次不一样
			self.__lasMsg = msg												# 纪录下本次内容
			self.__repeatCount = 1											# 恢复统计次数
		if not channel.validate( self, rcvName, msg ) :						# 频道自身条件
			return False
		return True

	# -------------------------------------------------
	def __notifyLockReason( self, chids, reason ) :
		"""
		通知客户端，禁言原因
		"""
		if reason == csdefine.CHAT_FORBID_BY_GM :							# 被 GM 禁言
			chName = csconst.CHAT_CHID_2_NAME[chids[0]]
			self.statusMessage( csstatus.CHAT_LOCK_ONE_LOCKED, chName )
		elif reason == csdefine.CHAT_FORBID_REPEAT :						# 因重复话语而被禁言
			self.statusMessage( csstatus.CHAT_LOCK_REPEAT )
		elif reason == csdefine.CHAT_FORBID_JAIL :							# 因入狱而被禁言
			self.statusMessage( csstatus.CHAT_LOCK_IN_PRISOPN )
		elif reason == csdefine.CHAT_FORBID_GUANZHAN:
			self.statusMessage( csstatus.CHAT_LOCK_IN_GUANZHAN )

	# -------------------------------------------------
	def __addForbiddance( self, chid, reason, duration ) :
		"""
		添加一个频道禁言
		"""
		endTime = 0
		if duration > 0 : endTime = time.time() + duration		# 禁言的结束时间（为 0 则标示永久禁言）
		rsdict = self.chat_fbds.get( chid, None )
		if rsdict is None :										# 原来没有频道禁言
			self.chat_fbds[chid] = { reason : endTime }			# 这里保存频道号
			return
		etime = rsdict.get( reason, None )						# 现存的被禁言的结束时间
		if etime is None :										# 如果原来不存在指定原因的禁言
			rsdict[reason] = endTime							# 则加入新的禁言原因
		elif endTime == 0 :										# 如果新添加了与现存某一原因一样的永久禁言
			rsdict[reason] = 0									# 则，设置该原因的禁言为永久禁言
		elif etime > 0 :										# 如果指定原因的禁言已经存在，并且是有期限的
			rsdict[reason] = max( endTime, etime )				# 则，取持续较长那个时间

	def __removeForbiddance( self, chid, reason ) :
		"""
		删除一个频道禁言
		"""
		rsdict = self.chat_fbds.get( chid, None )
		if rsdict is None : return								# 频道没有被禁言
		if reason in rsdict :									# 频道有相关原因的禁言
			del rsdict[reason]									# 则，删除该原因的禁言
		if len( rsdict ) == 0 :									# 频道中已经没有任何原因的禁言
			del self.chat_fbds[chid]							# 则，删除频道

	def __isForbident( self, chid ) :
		"""
		判断指定频道是否被禁言
		"""
		if chid not in self.chat_fbds :							# 指定频道不再禁言列表中
			return False
		rsdict = self.chat_fbds.get( chid )						# 找到该频道的禁言列表
		now = time.time()
		reason = None
		endTime = -1
		for rs, etime in rsdict.items() :						# 找出持续时间最长的原因
			if etime == 0 or etime > now :						# 有永久禁言或未到解禁时间的禁言
				endTime = etime
				reason = rs
				break
			else :												# 已经超过禁言时间
				del rsdict[rs]
				if len( rsdict ) == 0 :
					del self.chat_fbds[chid]
		if reason :
			self.__notifyLockReason( [chid], reason )			# 通知客户端，频道被禁言的原因
			return True
		return False


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def chat_handleMessage( self, chid, rcvName, msg, blobArgs ) :
		"""
		defined method
		处理一条频道消息，只给 cell.RoleChat 调用
		因为有些消息是需要通过 cell 验证才允许发送的，因此要发送一条消息时，
		很可能首先要转到 cell，等 cell 验证完毕，再通过本方法转回来继续处理。
		因此，请不要企图利用该方法发送一条频道消息。
		@type				chid	: UINT32
		@param				chid	: 频道 ID
		@type				rcvName	: STRING
		@param				rcvName	: 消息接收者的名称
		@type				msg		: STRING
		@param				msg		: 消息内容
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		"""
		_channels[chid].handle( self, rcvName, msg, blobArgs )

	# ------------------------------------------------
	def chat_lockMyChannels( self, chids, reason, duration ) :
		"""
		defined private method
		禁止自己的发言频道
		@type			chlist	 : list
		@param			chlist	 : 要禁言的频道列表，如果列表为空，则对所有可发言频道禁言
		@type			reason	 : MACRODEFINATION( UINT16 )
		@param			reason	 : 禁言原因，在 csdefine 中定义：CHAT_FORBID_XXXX
		@type			dulation : UINT32
		@param			dulation : 屏蔽时间，按分钟计算（要永久屏蔽，则为 0）
		"""
		if len( chids ) == 0 :									# 如果频道列表为空
			chids = csconst.CHAT_EXPOSED_CHANNELS				# 则对所有频道禁言
		for chid in chids :										# 逐一放到禁言列表
			self.__addForbiddance( chid, reason, duration )

	def chat_unlockMyChannels( self, chids, reason ) :
		"""
		defined private method
		解禁自己的发言频道
		@type			chlist	 : list
		@param			chlist	 : 要解禁的频道列表，如果列表为空，则对所有可发言频道解禁（注：只对指定原因解禁）
		@type			reason	 : MACRODEFINATION( UINT16 )
		@param			reason	 : 禁言原因，在 csdefine 中定义：CHAT_FORBID_XXXX
		"""
		if len( chids ) == 0 :												# 解锁所有频道
			chids = csconst.CHAT_EXPOSED_CHANNELS
		for chid in chids :
			self.__removeForbiddance( chid, reason )

	# ---------------------------------------
	def chat_lockOthersChannel( self, playerName, chName, dulation ) :
		"""
		defined method
		禁止指定角色的发言频道（给 GM 用）
		@type			playerName : STRING
		@param			playerName : 要封锁的对象名称
		@type			chName	   : STRING
		@param			chName	   : 频道名称（如果频道名称为空，则选中全部频道）
		@type			dulation   : UINT32
		@param			dulation   : 屏蔽时间（要永久屏蔽，则为 0）
		"""
		def onTargetFinded( player ) :
			if player == True :																# 角色不在线
				self.statusMessage( csstatus.CHAT_LOCK_TARGET_OFFLINE, playerName )
			elif player == False :															# 角色不存在
				self.statusMessage( csstatus.CHAT_LOCK_NO_TARGET, playerName )
			else :
				player.chat_lockMyChannels( chName, csdefine.CHAT_FORBID_BY_GM, dulation )	# 找到目标角色，并对其进行了禁言
				if chName == "" :
					self.statusMessage( csstatus.CHAT_LOCK_ALL_SUCCESS, playerName )
					player.client.onStatusMessage( csstatus.CHAT_LOCK_ALL_LOCKED, "" )
				else :
					self.statusMessage( csstatus.CHAT_LOCK_ONE_SUCCESS, playerName, chName )
					player.client.onStatusMessage( csstatus.CHAT_LOCK_ONE_LOCKED, str( ( chName,) ) )

		if chName == "" :															# 对所有频道进行禁言
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )
		elif chName not in csconst.CHAT_NAME_2_CHID :											# 频道不存在
			self.statusMessage( csstatus.CHAT_LOCK_UNKNOW_CHANNEL, chName )
		elif csconst.CHAT_NAME_2_CHID[chName] not in csconst.CHAT_EXPOSED_CHANNELS :			# 不可禁言频道
			self.statusMessage( csstatus.CHAT_LOCK_UNLOCKABLE )
		else :
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )

	def chat_unlockOthersChannel( self, playerName, chName ) :
		"""
		defined method
		解禁指定角色的发言频道（给 GM 用）
		@type			playerName : STRING
		@param			playerName : 要封锁的对象名称
		@type			chName	   : STRING
		@param			chName	   : 频道名称（如果频道名称为空，则选中全部频道）
		"""
		def onTargetFinded( player ) :
			if player == True :															# 角色不在线
				self.statusMessage( csstatus.CHAT_UNLOCK_TARGET_OFFLINE, playerName )
			elif player == False :														# 角色不存在
				self.statusMessage( csstatus.CHAT_UNLOCK_NO_TARGET, playerName )
			else :
				player.chat_unlockMyChannels( chName, csdefine.CHAT_FORBID_BY_GM )		# 找到目标角色，并对其进行了禁言
				if chName == "" :
					self.statusMessage( csstatus.CHAT_UNLOCK_ALL_SUCCESS, playerName )
					player.client.onStatusMessage( csstatus.CHAT_UNLOCK_ALL_LOCKED, "" )
				else :
					self.statusMessage( csstatus.CHAT_UNLOCK_ONE_SUCCESS, playerName, chName )
					player.client.onStatusMessage( csstatus.CHAT_UNLOCK_ALL_LOCKED, str( ( chName,) ) )

		if chName == "" :																# 对所有频道进行禁言
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )
		elif chName not in csconst.CHAT_NAME_2_CHID :									# 频道不存在
			self.statusMessage( csstatus.CHAT_UNLOCK_UNKNOW_CHANNEL, chName )
		elif csconst.CHAT_NAME_2_CHID[chName] not in csconst.CHAT_EXPOSED_CHANNELS :	# 不可禁言频道
			self.statusMessage( csstatus.CHAT_UNLOCK_UNLOCKABLE )
		else :
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def chat_sendMessage( self, chid, rcvName, msg, blobArgs ) :
		"""
		exposed method
		发送消息(给客户端调用，发送频道消息)
		注意：① 只有 exposed 为 True 的频道才能发送
			  ② 本方法只给 client 调用
			  ③ base 和 cell 调用 chat_handleMessage
		@type				chid	 : UINT32
		@param				chid	 : 频道 ID
		@type				rcvName	 : STRING
		@param				rcvName	 : 消息接收者的名称
		@type				msg		 : STRING
		@param				msg		 : 消息内容
		@type				blobArgs : BLOB_ARRAY
		@param				blobArgs : 消息参数列表
		"""
		channel = _channels[chid]
		if not channel.exposed :
			HACK_MSG( "role which dbid '%i' hacks on channel %i!" % ( self.databaseID, chid ) )
			return
		if self.__isForbident( chid ) :						# 被禁言
			return
		if self.__validate( channel, rcvName, msg ) :
			channel.send( self, rcvName, msg, blobArgs )

	# -------------------------------------------------
	def chat_requireRoleInfo( self, roleName ) :
		"""
		exposed method
		请求发送指定玩家的信息
		@type				roleName : str
		@param				roleName : 角色名字
		"""
		def lookResult( mbRole ) :
			if hasattr( mbRole, "cell" ) :					# 如果找到指定玩家，并且存在 cell
				mbRole.cell.chat_sendRoleInfo( self )		# 在向玩家的 cell 申请发送
			else :											# 如果目标玩家已经下线
				self.statusMessage( csstatus.CHAT_REQUIRE_ROLEINFO_NOT_ONLINE )
		Love3.g_baseApp.lookupRoleBaseByName( roleName, lookResult )

	# -------------------------------------------------
	# 离线消息
	# -------------------------------------------------
	def requestOFLMsgs( self ) :
		"""
		查询所有发送给我的离线记录
		"""
		def queryMsgsCB( msgs ) :
			if not len( msgs ) : return
			self.__tmpOflMsgs = msgs
			PLMChatRecorder.removeMsgsToReceiver( self.playerName )		# 离线消息从数据库移除
			self.addTimer( 0, csconst.ROLE_INIT_INTERVAL, ECBExtend.SEND_OFFLINE_MSG_CBID )
		PLMChatRecorder.queryMsgsToReceiver( self.playerName, queryMsgsCB )

	def onTimer_initOflMsgToClient( self, timerID, cbid ) :
		"""
		发送离线消息到客户端
		"""
		countPerTick = min( 3, len( self.__tmpOflMsgs ) )			# 一次最多发送3条消息到客户端
		chid = csdefine.CHAT_CHANNEL_PLAYMATE
		while countPerTick :
			senderName, msg, blobArgs, date = self.__tmpOflMsgs.pop( 0 )
			self.client.chat_onRcvOflMessage( chid, -1, senderName, msg, blobArgs, date )	# spkID 设置为-1指明是离线消息
			countPerTick -= 1
		if not len( self.__tmpOflMsgs ) :
			del self.__tmpOflMsgs
			self.delTimer( timerID )
			self.client.onInitialized( csdefine.ROLE_INIT_OFLMSGS )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onGetCell( self ) :
		"""
		临时用一段时间，删除原来以频道名称为 key 的禁言列表
		"""
		for ch in self.chat_fbds.keys() :
			if type( ch ) is not int :
				del self.chat_fbds[ch]


# RoleChat.py

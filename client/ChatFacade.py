# -*- coding: gb18030 -*-

# $Id: ChatFacade.py,v 1.39 2008-08-30 09:15:54 huangyongwei Exp $
"""
implement chat manager

2009.04.14 : writen by huangyongwei
"""

# common
import re
import time
import string
import cPickle
import BigWorld
import ResMgr
import Language
import csdefine
import csconst
import csstatus
import csstatus_msgs
import ChatObjParser
import weakref
import keys

# client
import GUI
import csstring
import Define

# common
from bwdebug import *
from cscollections import MapList
from Weaker import WeakList
from SmartImport import smartImport
from AbstractTemplates import Singleton
from AbstractTemplates import AbstractClass
from AbstractTemplates import EventDelegate
from Function import Functor

# client
from gbref import rds
from WordsProfanity import wordsProfanity
from ViewInfoMgr import viewInfoMgr
from Color import cscolors
from event import EventCenter as ECenter
from config.client.chat_colors import Datas as chatColors
from items.ItemDataList import ItemDataList
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
from config.client.labels import ChatFacade as lbs_ChatFacade


# --------------------------------------------------------------------
# 频道列表
# 这些频道是 csdefine 中定义的频道
# --------------------------------------------------------------------
class Channel( object ) :
	__cg_formator = None
	__delay_status = {}									# 需要延时显示的状态信息
	__delay_status[0.1] = set( [						# 一级延时
		csstatus.ACCOUNT_STATE_GAIN_EXP,
		csstatus.ACCOUNT_STATE_PET_GAIN_EXP,
		csstatus.ACCOUNT_STATE_UPDATE_GRADE,
		csstatus.ACCOUNT_STATE_PET_UPDATE_GRADE,
		csstatus.ACCOUNT_STATE_CURRENT_LEVEL,
		csstatus.ACCOUNT_STATE_DEAD,
		csstatus.ACCOUNT_STATE_KILL_DEAD_TO,
		csstatus.ACCOUNT_STATE_GAIN_POTENTIAL,
		] )

	def __init__( self, id, name ) :
		self.__id = id											# 频道 ID
		self.__name = name										# 频道名称
		self.__exposed = id in csconst.CHAT_EXPOSED_CHANNELS	# 是否是可发言频道
		self.__shielded = False									# 是否屏蔽消息
		self.__isLimitByGBTime = id in _limit_by_gbtime_chids	# 是否受全局发言时间间隔限制
		self.__setable = id in _setable_chids					# 是否可以设置（玩家可以将该频道设置到某个分页中显示）
		self.__sendable = id in _sendable_chids					# 是否可以在聊天窗口中发送消息（不包括其它地方发送信息）

		self.__handlers = WeakList()							# 即时消息的处理函数

		w = ( 255, 255, 255, 255 )								# 默认为白色
		self.__color = chatColors.get( name, w )				# 频道颜色
		self.__cfgSect = None									# 用自定义频道配置
		
	def __delayFire2( self, spkID, spkName, msg, statusID ) :
		"""
		延时显示消息，如果不属于延时范围内的消息，则返回 False
		"""
		for delayTime, statuses in self.__delay_status.iteritems() :
			if statusID in statuses :
				fn = Functor( self.onReceiveMessage, spkID, spkName, msg, statusID )
				BigWorld.callback( delayTime, fn )
				return True
		return False
		


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __resetColor( self ) :
		"""
		重新设置频道颜色
		"""
		if self.__cfgSect["color"] is None :
			self.__color = chatColors.get( self.__name, ( 255, 255, 255, 255, ) )
		else :
			self.__color = self.__cfgSect.readVector4( "color" )

	def __resetShield( self ) :
		if self.__cfgSect["shield"] is None :
			self.__shielded = False
		else :
			self.__shielded = self.__cfgSect.readBool( "shield" )


	# -------------------------------------------------
	# properties
	# -------------------------------------------------
	@property
	def id( self ) :
		"""
		频道 ID
		"""
		return self.__id

	@property
	def name( self ) :
		"""
		频道名称
		"""
		return self.__name

	@property
	def chPrefix( self ) :
		"""
		频道前缀
		"""
		return lbs_ChatFacade.channelPrefix % self.__name

	@property
	def color( self ) :
		"""
		频道颜色
		"""
		if len( self.__color ) == 4 :
			return self.__color[:-1]
		return self.__color

	# -------------------------------------------------
	@property
	def exposed( self ) :
		"""
		是否允许玩家发送信息
		"""
		return self.__exposed

	@property
	def isLimitByGBTime( self ) :
		"""
		是否受全局时间间隔限制
		"""
		return self.__isLimitByGBTime

	@property
	def setable( self ) :
		"""
		是否可以设置（玩家可以将该频道设置到某个分页中显示）
		"""
		return self.__setable

	@property
	def sendable( self ) :
		"""
		是否可选择发言
		"""
		return self.__sendable

	# -------------------------------------------------
	@property
	def shielded( self ) :
		"""
		是否屏蔽消息
		"""
		return self.__shielded

	# -------------------------------------------------
	@property
	def formator( self ) :
		"""
		文本格式化器具
		"""
		if not self.__cg_formator :
			class Formator : pass
			formator = Formator()
			from guis.tooluis.richtext_plugins.PL_Link import PL_Link
			from guis.tooluis.richtext_plugins.PL_Font import PL_Font
			formator.PL_Link = PL_Link
			formator.PL_Font = PL_Font
			self.__cg_formator = formator
		return self.__cg_formator


	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def send_( self, msg, receiver ) :
		"""
		发送频道信息
		@type			msg		 : str
		@param			msg		 : 发送的消息
		@type			receiver : str
		@param			receiver : 消息接收者
		"""
		if not self.__exposed :
			raise AttributeError( "channel '%s' is unspeakable!" )
		msg, blobArgs = chatObjParsers.parseSendMsg( msg )
		msg = csstring.toString( msg )
		if len( msg ) > csconst.CHAT_MESSAGE_UPPER_LIMIT :							# 发言内容过长
			chatFacade.rcvStatusMsg( csstatus.CHAT_WORDS_TOO_LONG )
			return
		BigWorld.player().base.chat_sendMessage( self.__id, receiver, msg, blobArgs )


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onReceiveMessage2( self, spkID, spkName, msg, *args ) :
		"""
		收到消息
		"""
		if len( args ) == 0 :
			self.onReceiveMessage( spkID, spkName, msg, *args )
		elif not self.__delayFire2( spkID, spkName, msg, *args ):
			self.onReceiveMessage( spkID, spkName, msg, *args )
			
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		收到消息
		"""
		if self.__shielded : return
		for handler in self.__handlers :
			handler( self, spkID, spkName, msg, *args )

	# -------------------------------------------------
	def reset( self, sect ) :
		"""
		角色进入世界是被调用
		"""
		self.__cfgSect = sect
		self.__shielded = False
		self.__resetColor()				# 重新初始化颜色
		#self.__resetShield()			# 重新初始化消息屏蔽状态( 策划要求取消消息屏蔽的功能，因此注销掉 )


	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def shield( self ) :
		"""
		屏蔽接收消息
		"""
		self.__shielded = True
		self.__cfgSect.writeBool( "shield", True )

	def unshield( self ) :
		"""
		解除消息接收屏蔽
		"""
		self.__shielded = False
		self.__cfgSect.writeBool( "shield", False )

	def resetColor( self, color = None ) :
		"""
		重新设置频道颜色，如果 color 为 None，则用默认颜色
		"""
		if color is None :
			w = 255, 255, 255, 255
			self.__color = chatColors.get( self.__name, w )
			self.__cfgSect.deleteSection( "color" )
			return
		if color is str :
			color = cscolors[color]
		color = tuple( color )
		if len( color ) == 3 :
			color = color + ( 255,)
		self.__color = color
		self.__cfgSect.writeVector4( "color", color )

	# -------------------------------------------------
	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		格式化消息文本
		"""
		player = BigWorld.player()
		linker = self.formator.PL_Link
		prefix = self.chPrefix									# 频道前缀
		if spkID == player.id :						# 如果发言者是角色自己，则不将名字格式化为带超链接
			spkName = "[%s]: " % spkName
		elif spkName != "" :									# 如果发言者有名字
			if spkID == 0 :										# 如果发言者是系统(非角色)，则不将名字格式化为带超链接
				spkName = "[%s]: " % spkName
			else :
				if player.onFengQi:							# 夜战凤栖
					entity = BigWorld.entities.get( spkID )
					if entity and entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and \
					self.id in _masked_chids:
						spkName = lbs_ChatFacade.masked
				spkName = "[%s]: " % linker.getSource( \
					spkName, "viewRoleInfo:" + spkName )		# 发言者名称
		return "%s%s%s" % ( prefix, spkName, msg )

	# -------------------------------------------------
	def bindHandler( self, handler ) :
		"""
		绑定一个消息处理方法
		"""
		if handler not in self.__handlers :
			self.__handlers.append( handler )

	def unbindHandler( self, handler ) :
		"""
		移除一个消息处理方法
		"""
		if handler in self.__handlers :
			self.__handlers.remove( handler )

# -----------------------------------------------------
class CH_Near( Channel ) :
	"""
	附近频道
	"""
	def send_( self, msg, receiver ) :
		if BigWorld.player().state == csdefine.ENTITY_STATE_DEAD :
			chatFacade.rcvStatusMsg( csstatus.CHAT_NOT_ROUND_DEAD )
		else :
			Channel.send_( self, msg, receiver )

# -----------------------------------------------------
class CH_Whisper( Channel ) :
	"""
	密语频道
	"""
	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__lastReceiver = ""
		self.__lastWhisper = ""

	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def send_( self, msg, receiver ) :
		Channel.send_( self, msg, receiver )
		self.__lastReceiver = receiver
		self.__lastWhisper = receiver


	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def reset( self, sect ) :
		"""
		角色离开世界时被调用
		"""
		Channel.reset( self, sect )
		self.__lastReceiver = ""
		self.__lastWhisper = ""

	def getLastReceiver( self ) :
		"""
		获取上一次密语目标
		"""
		return self.__lastReceiver

	def getLastWhisper( self ) :
		"""
		获取最近的密语交流目标
		"""
		return self.__lastWhisper

	# -------------------------------------------------
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		接收到密语消息
		"""
		if self.shielded : return
		self.__lastWhisper = spkName
		Channel.onReceiveMessage( self, spkID, spkName, msg, *args )

	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		格式化消息文本
		"""
		player = BigWorld.player()
		linker = self.formator.PL_Link
		prefix = self.chPrefix									# 频道前缀
		nmark = "viewRoleInfo:" + spkName
		if player.onFengQi:
			spkName = lbs_ChatFacade.masked
		speaker = "[%s]" % linker.getSource( spkName, nmark )	# 格式化发言者名称
		if spkID == player.id :						# 发言者是自己
			speaker = lbs_ChatFacade.preWhisperTo % speaker
		else :													# 发言者不是自己
			speaker = lbs_ChatFacade.preWhisperFrom % speaker
		return "%s%s%s" % ( prefix, speaker, msg )

# -----------------------------------------------------
class CH_World( Channel ) :
	"""
	世界频道
	"""
	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__yellVerifier = None					# 收费确认框（写在这里不是很好，但暂时找不到更好的办法）
		self.__lastSendTime = 0						# 最后一次发送世界信息的时间
		self.__needRemind = True					# 是否需要收费提示


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __sendMessage( self, msg ) :
		"""
		直接发送消息
		"""
		Channel.send_( self, msg, "" )
		self.__lastSendTime = time.time()

	def __remind( self, msg, res, unremind ) :
		"""
		呐喊提示
		"""
		if res == RS_YES :
			self.__needRemind = not unremind
			self.__sendMessage( msg )


	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def send_( self, msg, receiver ) :
		if self.__yellVerifier is None :
			self.__yellVerifier = __import__( "guis/general/chatwindow/YellVerifyBox" )

		player = BigWorld.player()
		if player.level < csconst.CHAT_YELL_LEVEL_REQUIRE :					# 等级不够
			chatFacade.rcvStatusMsg( csstatus.CHAT_YELL_UNDER_LEVEL )
		elif self.__lastSendTime + csconst.CHAT_YELL_DELAY > time.time() :	# 两次发送时间间隔低于规定时间间隔
			chatFacade.rcvStatusMsg( csstatus.CHAT_YELL_TOO_CLOSE )
		elif player.money < csconst.CHAT_YELL_USE_MONEY :					# 金钱不够
			chatFacade.rcvStatusMsg( csstatus.CHAT_YELL_MONEY_NOTENOUGH )
		elif self.__needRemind :											# 需要收费提示
			self.__yellVerifier.show( Functor( self.__remind, msg ) )
		else :
			self.__sendMessage( msg )


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		角色进入世界时被调用
		"""
		self.__needRemind = True							# 重新确定收费提示

# -----------------------------------------------------
class CH_Broadcast( Channel ) :
	"""
	广播频道
	"""
	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		格式化消息文本
		"""
		return msg

# -----------------------------------------------------
class CH_NPCSpeak( Channel ) :
	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		NPC 名字不允许点击
		"""
		msgInfos = spkName.split( "\0" )		
		if len( msgInfos ) == 2 :													# 加了名字前缀以指定发言类型
			prefix, spkName = msgInfos
		else :
			prefix = "N"															# 没加名字前缀，默认为“附近”

		if spkName != "" :
			if prefix == "N" :														# NPC 附近
				return "%s[%s]: %s" % ( self.chPrefix, spkName, msg )
			elif prefix == "M" :													# NPC 密语
				return lbs_ChatFacade.npcWhisper % ( self.chPrefix, spkName, msg )
			elif prefix == "W" :													# NPC 呐喊
				return lbs_ChatFacade.npcYell % ( self.chPrefix, spkName, msg )
		return "%s%s: %s" % ( self.chPrefix, lbs_ChatFacade.anoySay, msg )			# NPC 不出错是不会跑到这里来的


# -----------------------------------------------------
class CH_Combat( Channel ) :
	# ---------------------------------------
	# 延时显示的信息
	# ---------------------------------------
	__delay_status = {}									# 需要延时显示的状态信息
	__delay_status[0.1] = set( [						# 一级延时
		] )

	__delay_status[0.2] = set( [						# 二级延时
		] )

	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__settableStatus = {}												# 可设置为是否显示的信息
		self.__settableStatus["enemy"]	 = csstatus_msgs.enemyInjuredStatus		# 敌人受伤信息
		self.__settableStatus["skill"]	 = csstatus_msgs.skillHitStatus			# 技能攻击信息
		self.__settableStatus["revert"]  = csstatus_msgs.revertStatus			# 回复信息
		self.__settableStatus["injured"] = csstatus_msgs.injuerdStatus			# 受伤信息
		self.__settableStatus["buff"]	 = csstatus_msgs.buffStatus				# buff 信息
		self.__eventMacro = "EVT_ON_CHAT_COMBAT_MSG"

	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __isShielded( self, statusID ) :
		"""
		消息是否已经被过滤（设置为不显示），返回 True 表示系统已经将其设置为不显示
		"""
		for key, statuses in self.__settableStatus.iteritems() :
			if not statusID in statuses : continue
			if not viewInfoMgr.getSetting( "hitedInfo", key ) :
				return True
		return False

	# ---------------------------------------
	def __delayFire( self, spkID, spkName, msg, statusID ) :
		"""
		延时显示消息，如果不属于延时范围内的消息，则返回 False
		"""
		for delayTime, statuses in self.__delay_status.iteritems() :
			if statusID in statuses :
				fn = Functor( Channel.onReceiveMessage, self, spkID, spkName, msg, statusID )
				BigWorld.callback( delayTime, fn )
				return True
		return False


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		接受频道消息
		"""
		if len( args ) == 0 :
			Channel.onReceiveMessage( self, spkID, spkName, msg, *args )
		elif self.__isShielded( *args ) :
			return
		elif not self.__delayFire( spkID, spkName, msg, *args ) :
			Channel.onReceiveMessage( self, spkID, spkName, msg, *args )

# -----------------------------------------------------
class CH_MSGBox( Channel ) :
	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__pyInShowBoxes = {}

	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		def callback( statusID, res ) :
			if statusID :
				self.__pyInShowBoxes.pop( statusID )

		statusID = args[0] if len( args ) else None
		if statusID in self.__pyInShowBoxes :
			self.__pyInShowBoxes.pop( statusID ).dispose()
		func = Functor( callback, statusID )
		pyBox = showMessage( msg, "", MB_OK, func, gstStatus = Define.GST_IN_WORLD )
		if statusID : 																	# statusID 有可能为 None，不加这个判断会导致所有ID为None的消息只能同时显示一个 --pj
			self.__pyInShowBoxes[statusID] = pyBox
		Channel.onReceiveMessage( self, spkID, spkName, msg, *args )

# -----------------------------------------------------
class CH_Playmate( Channel ) :
	"""
	两个玩家之间的窗口聊天
	"""

	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		格式化消息文本
		"""
		plFont = self.formator.PL_Font
		player = BigWorld.player()
		if spkID == 0 :												# 系统消息
			msg = plFont.getSource( msg, fc = (255,0,255,255) )
			return msg, ""
		elif spkID == -1 :											# 离线消息
			msg = lbs_ChatFacade.OFFLINE_MSG_PREFIX + msg			# 添加前缀
		elif spkID == player.id :						# 玩家自己的消息
			spkName = player.playerName
		elif player.onFengQi:
			spkName = lbs_ChatFacade.masked
		date = args[0] if len( args ) else ""
		date = plFont.getSource( date, fc = (0,255,255,255) )
		return "[%s] %s" % ( spkName, date ), msg
		
class CH_TongCityWar( Channel ):
	"""
	帮会战争结盟专用频道
	"""
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		接受频道消息
		"""
		if BigWorld.player().getCurrentSpaceType() == csdefine.SPACE_TYPE_CITY_WAR_FINAL: #屏蔽不在副本内的成员消息
			Channel.onReceiveMessage( self, spkID, spkName, msg, *args )


# --------------------------------------------------------------------
# 频道设置列表
# --------------------------------------------------------------------
_channel_maps = {
	# 角色发言频道						  频道类
	csdefine.CHAT_CHANNEL_NEAR			: CH_Near,		# 附近频道
	csdefine.CHAT_CHANNEL_LOCAL			: Channel,		# 本地频道
	csdefine.CHAT_CHANNEL_TEAM			: Channel,		# 队伍频道
	csdefine.CHAT_CHANNEL_TONG			: Channel,		# 帮会频道
	csdefine.CHAT_CHANNEL_WHISPER		: CH_Whisper,	# 私聊频道
	csdefine.CHAT_CHANNEL_WORLD			: CH_World,		# 世界频道
	csdefine.CHAT_CHANNEL_RUMOR			: Channel,		# 谣言频道
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: Channel,		# 天音广播
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: Channel,		# 地音广播
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : CH_TongCityWar,		# 帮会战场

	# GM/公告频道
	csdefine.CHAT_CHANNEL_SYSBROADCAST	: CH_Broadcast,	# 公告广播

	# NPC 发言频道
	csdefine.CHAT_CHANNEL_NPC_SPEAK		: CH_NPCSpeak,	# NPC（附近、密语、世界）
	csdefine.CHAT_CHANNEL_NPC_TALK		: Channel,		# NPC 对话频道

	# 系统提示频道
	csdefine.CHAT_CHANNEL_SYSTEM		: Channel,		# 系统频道（显示由服务器产生的各种活动、获得物品/强化/镶嵌等产生）
	csdefine.CHAT_CHANNEL_COMBAT		: CH_Combat,	# 战斗频道（显示战斗信息）
	csdefine.CHAT_CHANNEL_PERSONAL		: Channel,		# 个人频道（个人频道显示玩家在获得经验、潜能、金钱、物品、元宝的信息）
	csdefine.CHAT_CHANNEL_MESSAGE		: Channel,		# 消息频道（显示角色的操作产生的错误信息或提示信息）
	csdefine.CHAT_CHANNEL_SC_HINT		: Channel,		# 在屏幕中间提示的频道
	csdefine.CHAT_CHANNEL_MSGBOX		: CH_MSGBox,	# 以 MessageBox 提示的频道

	# 独立窗口聊天
	csdefine.CHAT_CHANNEL_PLAYMATE		: CH_Playmate,	# 独立窗口聊天
	
	csdefine.CHAT_CHANNEL_CAMP			: Channel,		# 阵营频道
	}

# -------------------------------------------
# 可以设置到聊天分页中显示的频道
_setable_chids = set([
	# 角色发言频道
	csdefine.CHAT_CHANNEL_NEAR,				# 附近频道
	csdefine.CHAT_CHANNEL_LOCAL,			# 本地频道
	csdefine.CHAT_CHANNEL_TEAM,				# 队伍频道
	csdefine.CHAT_CHANNEL_TONG,				# 帮会频道
	csdefine.CHAT_CHANNEL_WHISPER,			# 私聊频道
	csdefine.CHAT_CHANNEL_WORLD,			# 世界频道
#	csdefine.CHAT_CHANNEL_RUMOR,			# 谣言频道					# 针对有些人用谣言骂人，上面要求暂时屏蔽谣言频道
	csdefine.CHAT_CHANNEL_WELKIN_YELL,		# 天音广播
	csdefine.CHAT_CHANNEL_TUNNEL_YELL,		# 地音广播
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR,	# 帮会战场

	# GM/公告频道
	csdefine.CHAT_CHANNEL_SYSBROADCAST,		# 公告广播

	# NPC 发言频道
	csdefine.CHAT_CHANNEL_NPC_SPEAK,		# NPC（附近、密语、世界）

	# 系统提示频道
	csdefine.CHAT_CHANNEL_SYSTEM,			# 系统频道
	csdefine.CHAT_CHANNEL_COMBAT,			# 战斗频道
	csdefine.CHAT_CHANNEL_PERSONAL,			# 个人频道
	csdefine.CHAT_CHANNEL_MESSAGE,			# 消息频道
	csdefine.CHAT_CHANNEL_MSGBOX,			# 以 MessageBox 提示的频道
	csdefine.CHAT_CHANNEL_CAMP,				# 阵营
	])


# 可选择并可发言的频道和其快捷键（可在聊天窗口中选择发送消息的频道）
_sendable_chids = {
	csdefine.CHAT_CHANNEL_NEAR				: "S",			# 附近
	csdefine.CHAT_CHANNEL_LOCAL				: "M",			# 本地
	csdefine.CHAT_CHANNEL_TEAM				: "P",			# 队伍
	csdefine.CHAT_CHANNEL_TONG				: "G",			# 帮会
	csdefine.CHAT_CHANNEL_WHISPER			: "T",			# 密语
	csdefine.CHAT_CHANNEL_WORLD				: "W",			# 世界
	csdefine.CHAT_CHANNEL_CAMP				: "C",			# 阵营
#	csdefine.CHAT_CHANNEL_RUMOR				: "E",			# 谣言						# 针对有些人用谣言骂人，上面要求暂时屏蔽谣言频道
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR		: "A"	# 帮会战场
	}

# 受全局发言时间间隔限制的频道
_limit_by_gbtime_chids = set( [
	csdefine.CHAT_CHANNEL_NEAR,				# 附近
	csdefine.CHAT_CHANNEL_LOCAL,			# 本地
	csdefine.CHAT_CHANNEL_TEAM,				# 队伍
	csdefine.CHAT_CHANNEL_TONG,				# 帮会
	csdefine.CHAT_CHANNEL_WHISPER,			# 密语
	csdefine.CHAT_CHANNEL_PLAYMATE,			# 玩伴
	csdefine.CHAT_CHANNEL_CAMP,				# 阵营
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR,	# 帮会战场
	] )

# 进行表情解释的频道
_emotion_chids = set( [
	csdefine.CHAT_CHANNEL_NEAR,				# 附近
	csdefine.CHAT_CHANNEL_LOCAL,			# 本地
	csdefine.CHAT_CHANNEL_TEAM,				# 队伍
	csdefine.CHAT_CHANNEL_TONG,				# 帮会
	csdefine.CHAT_CHANNEL_WHISPER,			# 密语
	csdefine.CHAT_CHANNEL_WORLD,			# 世界
	csdefine.CHAT_CHANNEL_RUMOR,			# 谣言
	csdefine.CHAT_CHANNEL_WELKIN_YELL,		# 天音
	csdefine.CHAT_CHANNEL_PLAYMATE,			# 玩伴
	csdefine.CHAT_CHANNEL_CAMP,				# 阵营
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR,	# 帮会战场
	] )

#在夜战凤栖副本屏频名称的道
_masked_chids = set( [
	csdefine.CHAT_CHANNEL_NEAR,
	csdefine.CHAT_CHANNEL_LOCAL,
	] )

# --------------------------------------------------------------------
# 聊天频道管理器
# --------------------------------------------------------------------
class ChatFacade( Singleton ) :
	def __init__( self ) :
		self.channels = MapList()				# 所有频道
		self.setableChannels = []				# 可设置频道( 可设置到某个分页显示的频道 )
		self.__sendableChannels = {}			# 可选择发送信息的频道:{ 快捷键字符 : 对应的频道 }

		self.__lastSendTime = 0					# 前一次发送消息的时间
		self.__statusHandlers = {}				# 状态消息可注册接收器
		self.__cfgPath = ""						# 配置路径
		self.__cfgSect = None					# 配置 section
		self.__initialize()						# 初始化频道列表

		self.__objCount = 0						# 消息中包含的聊天对象个数

		ECenter.registerEvent( "EVT_ON_BEFORE_GAME_QUIT", self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		global _channel_maps
		global _limit_by_gbtime_chids
		ptlist = []
		for chid, CLSChannel in _channel_maps.iteritems() :
			name = csconst.CHAT_CHID_2_NAME[chid]
			channel = CLSChannel( chid, name )
			self.channels[chid] = channel
			if channel.setable :
				self.setableChannels.append( channel )
			shortcut = _sendable_chids.get( chid, None )
			if shortcut :
				self.__sendableChannels[shortcut] = chid
		del _channel_maps											# 完成频道创建，不再需要
		del _limit_by_gbtime_chids

	def __getConfigSect( self ) :
		"""
		获取频道配置路径
		"""
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__cfgPath = "account/%s/%s/chat_colors.xml" % ( accountName, roleName )
		self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
		return self.__cfgSect

	# -------------------------------------------------
	@staticmethod
	def __splitCommand( msg, infos ) :
		"""
		萃取指令
		"""
		if msg.startswith( "/" ) :
			sps = msg[1:].split( None, 1 )
			if len( sps ) == 0 :
				return False
			infos[0] = sps[0]
			if len( sps ) == 2 :
				infos[1] = sps[1]
			else :
				infos[1] = ""
			return True
		return False

	def __handleCommand( self, cmd, args ) :
		"""
		指令消息过滤
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target and BigWorld.entity( target.id ) :			# 有目标的情况下
			player.cell.wizCommand( target.id, cmd, args )		# 指令针对目标发出
		else :
			player.cell.wizCommand( player.id, cmd, args )		# 否则指令针对当前角色发出

	# -------------------------------------------------
	def __handleRegisteredStatus( self, statusID, msg ) :
		"""
		处理被注册了的状态消息
		"""
		if statusID in self.__statusHandlers :
			self.__statusHandlers[statusID]( statusID, msg )


	# ------------------------------------------------
	# callbacks
	# ------------------------------------------------
	def onEvent( self, macroName, *arg ) :
		if macroName == "EVT_ON_BEFORE_GAME_QUIT" :
			if self.__cfgSect is not None :
				try :
					self.__cfgSect.save()				# 退出游戏前保存配置
				except IOError, err :
					ERROR_MSG( "save chat channels setting failed!" )

	def onGameStart( self ) :
		"""
		游戏启动完毕后被调用
		"""
		emotionParser.onGameStart()						# 初始化表情
		chatObjParsers.onGameStart()						# 初始化物品连接

	def onRoleEnterWorld( self ) :
		"""
		角色进入世界是被触发
		"""
		cfgSect = self.__getConfigSect()				# 获取用户频道配置
		for channel in self.channels.values() :
			chName = channel.name
			sect = cfgSect[chName]
			if sect is None :							# 频道配置不存在
				sect = cfgSect.createSection( chName )	# 则，以频道名称创建一个
			channel.reset( sect )

	def onRoleLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		if self.__cfgSect is not None :
			self.__cfgSect.save()
			ResMgr.purge( self.__cfgPath )
			self.__cfgPath = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def saveChannelConfig( self ) :
		"""
		保存频道配置文件
		"""
		self.__cfgSect.save()

	def getSetableCHIDs( self ) :
		"""
		获取所有可以在聊天分页中设置的频道
		"""
		return _setable_chids

	def getChannel( self, chid ) :
		"""
		获取指定 ID 的频道
		"""
		return self.channels[chid]

	def shortcutToCHID( self, shortcut ) :
		"""
		快捷键对应的频道ID
		"""
		shortcut = shortcut.upper()
		for chid, sc in _sendable_chids.iteritems() :
			if sc == shortcut : return chid
		return None

	def chidToShortcut( self, chid ) :
		"""
		频道对应的快捷键
		"""
		return _sendable_chids.get( chid )

	# -------------------------------------------------
	def bindChannelHandler( self, chid, handler ) :
		"""
		绑定消息处理函数
		"""
		self.channels[chid].bindHandler( handler )

	def unbindChannelHandler( self, chid, handler ) :
		"""
		取消消息处理函数的绑定
		"""
		self.channels[chid].unbindHandler( handler )


	# ------------------------------------------------
	# 频道消息相关
	# ------------------------------------------------
	def rcvChannelMsg( self, chid, spkID, spkName, msg, blobArgs, *args ) :
		"""
		接收频道消息
		"""
		if BigWorld.player() is None : return						# 有些消息是纯客户端延时一会再发送的，因此如果此时角色已经退出游戏，将会引起错误
		msg_temp = msg.split("/ltime")
		msg = msg_temp[0]
		channel = self.channels[chid]
		if channel.exposed :										# 如果是玩家可发言频道
			msgSegs = []
			emsgs = emotionParser.tearRcvMsg( msg )					# 分离表情与非表情消息
			for isEmote, msg in emsgs :
				if isEmote :
					msgSegs.append( ( isEmote, msg ) )
					continue
				subSegs = chatObjParsers.tearRcvMsg( msg, blobArgs )# 分离信息对象与普通消息
				msgSegs.extend( subSegs )
			msg = ""
			for ignore, msgSeg in msgSegs :							# 消息重组
				if ignore :
					msg += msgSeg
					continue
				msg += wordsProfanity.filterMsg( msgSeg )			# 如果是普通消息则进行亵渎词汇过滤
		if chid in _emotion_chids :									# 转换表情
			msg = emotionParser.parseRcvMsg( msg )
		if len( blobArgs ) :
			msg = chatObjParsers.parseRcvMsg( msg, blobArgs )		# 转换聊天对象
		if len( msg_temp ) > 1 :
			msg = msg + "/ltime" + msg_temp[1]
		channel.onReceiveMessage( spkID, spkName, msg, *args )

	# ---------------------------------------
	def sendChannelMessage( self, chid, msg, receiver = "" ) :
		"""
		发送频道信息
		注意：这里调用了频道的 send_ 保护方法，我们设定了 ChatFacade 是频道的友元类
		@type				chid 	 : MSCRO DEFINATION
		@pararm				chid	 : 频道 ID
		@type				receiver : str
		@param				receiver : 消息接收者名称
		@type				msg		 : str
		@param				msg		 : 消息内容
		"""
		msg = csstring.toString( msg )
		msgInfo = ["", ""]
		if self.__splitCommand( msg, msgInfo ) :									# 消息中含有指令
			cmd, msg = msgInfo
			cmdUpper = cmd.upper()
			if cmdUpper in self.__sendableChannels :								# 如果消息中带的指令是频道快捷键
				chid = self.__sendableChannels[cmdUpper]							# 则修改频道 ID
			else :
				self.__handleCommand( cmd, msg )									# 否则被认为是系统指令
				return True

		channel = self.channels[chid]
		if channel.isLimitByGBTime :												# 频道是否受全局发言时间间隔限制
			if self.__lastSendTime + csconst.CHAT_GLOBAL_DELAY > time.time() :		# 时间间隔太短
				self.rcvStatusMsg( csstatus.CHAT_SPEAK_TOO_CLOSE )
				return False

		msg = csstring.toWideString( msg )
		self.channels[chid].send_( msg, receiver )									# 注意：设置各频道的 send_ 为 ChatFacade 的友元函数
																					# 不公开频道的 send 方法，是避免用户直接通过频道发送，
																					# 从而不意地绕过了这里之前的判断
		self.__objCount = 0															# 清空消息中包含的聊天对象个数
		self.__lastSendTime = time.time()
		return True

	# ---------------------------------------
	def activeChatWindow( self, chid, receiver = "" ) :
		"""
		激活聊天窗口，并定位到指定消息发送频道
		"""
		if chid in _sendable_chids :
			channel = self.channels[chid]
			ECenter.fireEvent( "EVT_ON_CHAT_ACTIVE_CHAT_SENDER", channel, receiver )

	def whisperWithChatWindow( self, receiver ) :
		"""
		激活聊天窗口，并与指定对象密语
		"""
		if receiver == "" :
			ERROR_MSG( "receiver must't be empty!" )
		else :
			channel = self.channels[csdefine.CHAT_CHANNEL_WHISPER]
			ECenter.fireEvent( "EVT_ON_CHAT_ACTIVE_CHAT_SENDER", channel, receiver )

	# ---------------------------------------
	def insertChatMessage( self, msg ) :
		"""
		在光标处插入聊天信息
		"""
		msgInserter.insertMessage( msg )

	def insertChatObj( self, objType, obj ) :
		"""
		插入一个聊天对象到消息输入框
		"""
		objCount = 3											# 最多只能发送 3 个聊天对象（仅客户端限制，方便起见，这里不对 3 进行宏定义了，直接写死）
		if self.__objCount < objCount :
			msg = chatObjParsers.getMaskObj( objType, obj )
			msgInserter.insertMessage( msg )
		else :
			msg = lbs_ChatFacade.chatObjOverstep % objCount
			BigWorld.player().chat_systemInfo( "(SC):" + msg )
			msgInserter.insertMessage( "" )						# 这里再插入一个空串，其目的是使得消息输入框仍然处于激活状态，否则其焦点将会被抢掉

	def onChatObjCount( self, objCount ):
		"""
		聊天对象改变时调用
		"""
		self.__objCount = objCount
	# ------------------------------------------------
	# 状态消息相关
	# ------------------------------------------------
	def rcvStatusMsg( self, statusID, *args ) :
		"""
		接收状态消息
		"""
		if BigWorld.player() is None : return							# 有些消息是纯客户端延时一会再发送的，因此如果此时角色已经推出游戏，将会引起错误
		statusInfo = csstatus_msgs.getStatusInfo( statusID, *args )
		self.__handleRegisteredStatus( statusID, statusInfo.msg )		# 处理注册了的状态信息
		for chid in statusInfo.chids :
			if chid == csdefine.CHAT_CHANNEL_SYSTEM:
				self.channels[chid].onReceiveMessage2( 0, statusInfo.spkName, statusInfo.msg, statusID )
			else:
				self.channels[chid].onReceiveMessage( 0, statusInfo.spkName, statusInfo.msg, statusID )
	
	def rcvMsgDirect( self, chids, spkName, msg ) :
		"""
		直接接收消息，包含频道、发言者
		"""
		if BigWorld.player() is None : return							# 有些消息是纯客户端延时一会再发送的，因此如果此时角色已经推出游戏，将会引起错误
		
		for chid in chids :
			if chid == csdefine.CHAT_CHANNEL_SYSTEM:
				self.channels[chid].onReceiveMessage2( 0, spkName, msg )
			else:
				self.channels[chid].onReceiveMessage( 0, spkName, msg )

	# ---------------------------------------
	def bindStatus( self, statusID, fnHandler ) :
		"""
		绑定一个状态消息处理函数（指定的消息到来时，fnHandler 会被触发）
		"""
		if statusID not in self.__statusHandlers :
			self.__statusHandlers[statusID] = EventDelegate()
		self.__statusHandlers[statusID].bind( fnHandler )

	def unbindStatus( self, statusID, fnHandler ) :
		"""
		解除状态消息绑定
		"""
		if statusID in self.__statusHandlers :
			eventDelegate = self.__statusHandlers[statusID]
			if eventDelegate.hasHandler( fnHandler ) :
				eventDelegate.unbind( fnHandler )
				if eventDelegate.handlerCount == 0 :
					self.__statusHandlers.pop( statusID )
			else :
				ERROR_MSG( "handler '%s' is not in event delegate of status '%#0x'" % statusID )
		else :
			ERROR_MSG( "no handlers relative to status message: '%#0x'" % statusID )



# --------------------------------------------------------------------
# 消息翻译器
# --------------------------------------------------------------------
class EmotionParser( Singleton ) :
	"""
	表情解释器
	"""
	__cc_cfg	  = "maps/emote/emotionfaces.xml"		# 表情配置路径
	__cc_gui_path = "maps/emote/emote.gui"				# 表情图标 gui 配置路径
	cc_emote_size  = 32, 32

	def __init__( self ) :
		self.__sect = None
		self.__emotions = {}							# { 转义字符 : ( 表情路径, 表情描述 )}
		self.__rtEmotions = {}							# { 转义字符 : CSRichText 转义 }
		self.__reTpl = re.compile("[:)]")				# 表情转义替换正则模板
		self.__linkImage = None
		self.__titleNames = {}
		self.__emotionSigns = {}

	def __initialize( self ) :
		emote = GUI.load( self.__cc_gui_path )
		EmotionParser.cc_emote_size = emote.size		# 获取表情图标大小

		self.__linkImage = smartImport( "guis.tooluis.richtext_plugins.PL_Image:PL_Image" )
		self.__sect = ResMgr.openSection( self.__cc_cfg )
		if self.__sect is None :
			WARNING_MSG( "load chat emotion config file failed!" )
			return
		escs = []
		for pageIndex, sect in self.__sect.items() :
			if sect is None:continue
			index = int( pageIndex )
			self.__titleNames[index] = sect.asString
			if index not in self.__emotionSigns:
				self.__emotionSigns[index] = []
			emotionSigns = self.__emotionSigns[index]
			for mark, subSect in sect.items():
				sign = subSect.readString( "sign" )
				texture = subSect.readString( "path" )
				dsp = subSect.readString( "description" )
				self.__emotions[sign] = ( texture, dsp )
				self.__rtEmotions[sign] = self.__linkImage.getSource( self.__cc_gui_path, texture, text = sign )
				emotionSigns.append( sign )
				escs.append( re.escape( sign ) )
		self.__reTpl = re.compile( "|".join( escs ) )
		Language.purgeConfig( self.__cc_cfg )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def emotionIter( self ) :
		"""
		表情信息迭代器
		"""
		for pageIndex, sect in self.__sect.items() :
			for mark, subSect in sect.items():
				sign = subSect.readString( "sign" )
				path = subSect.readString( "path" )
				dsp = subSect.readString( "description" )
				yield sign, path, dsp

	@property
	def reTpl( self ) :
		"""
		表情转义模板
		"""
		return self.__reTpl

	@property
	def titleNames( self ):
		"""
		表情分页名称
		"""
		return self.__titleNames

	@property
	def emotionSigns( self ):
		"""
		表情转义符
		"""
		return self.__emotionSigns


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onGameStart( self ) :
		"""
		角色进入世界时初始化
		"""
		self.__initialize()

	# -------------------------------------------------
	def getEmotion( self, esc ) :
		"""
		获取表情信息
		"""
		return self.__emotions[esc]

	# -------------------------------------------------
	def formatEmotion( self, esc, lmark = "", size = None ) :
		"""
		@param		esc : 表情符号
		@type		esc : string
		@param		lmark : 超链接标记
		@type		lmark : str
		@param		size : 表情尺寸
		@type		size : tuple
		"""
		texture = self.__emotions[esc][0]
		return self.__linkImage.getSource( self.__cc_gui_path, texture, lmark = lmark, size = size )

	# ---------------------------------------
	def tearRcvMsg( self, msg ) :
		"""
		解释消息转义，并将解释后的消息，分段返回，从而标记出哪段为表情相关文本，哪段是普通文本:
		[( True, @I{...} ), ( False, "xxxx" ), ( False "xxxx" ), ...]
		"""
		emsgs = []
		start = 0
		end = len( msg )
		if self.__reTpl :
			emIter = self.__reTpl.finditer( msg )						# 获取所有表情字段的迭代器
			while True :
				try :
					em = emIter.next()
					eStart = em.start()
					subMsg = msg[start:eStart]
					if start != eStart :
						emsgs.append( ( False, subMsg ) )	# 普通消息
					emsgs.append( ( True, em.group() ) )				# 表情字段
					start = em.end()
				except StopIteration :
					break
		if start != end :
			emsgs.append( ( False, msg[start:end] ) )					# 剩余的非表情消息
		return emsgs

	def parseRcvMsg( self, msg ) :
		"""
		翻译消息转义，并返回 RichText 识别的带表情消息
		"""
		if self.__reTpl:
			replacer = lambda esc : self.__rtEmotions[esc.group()]
			msg = self.__reTpl.sub( replacer, msg )
		return msg


# --------------------------------------------------------------------
# 聊天对象
# --------------------------------------------------------------------
class BaseObj( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self, objType, minLen, defName ) :
		"""
		@type			objType : MSCRO DEFINATION
		@param			objType : 在 common/ChatObjParser.py 中定义
		@type			minLen	: int
		@param			minLen	: 要表达一个对象，需要的最少字节数
		@type			defName : str
		@param			defName : 如果解释失败，默认在聊天中显示的名字
		"""
		self.objType = objType
		self.minLen_ = minLen
		self.defName_ = defName

	def dump( self, text ) :
		"""
		将字符串形式的聊天对象，解释成可打包传输的频道消息参数（转换为发送参数：BLOB）
		返回 blob 或 None
		"""
		pass

	def load( self, info ) :
		"""
		将接收到的频道消息参数转换为可读文本（转换为 RichText 识别的字符串）
		必需返回一个字符串
		"""
		pass

	# ---------------------------------------
	def getMaskText( self, item ) :
		"""
		将物品转换为掩码形式的字符串（转换为 RichTextBox/MLRichTextBox 暗藏的文本）
		必需返回一个字符串
		"""
		pass

	def getViewName( self, text ) :
		"""
		根据暗码形式的物品对象文本，获取用户可看到的对象名称（转换为 RichTextBox/MLRichTextBox 显示的文本）
		必需返回 None，或（字符串，颜色）
		"""
		pass

	__abstract_methods.add( dump )
	__abstract_methods.add( load )
	__abstract_methods.add( getMaskText )
	__abstract_methods.add( getViewName )


# -----------------------------------------------------
# 物品对象
# -----------------------------------------------------
class ChatItem( BaseObj ) :
	LMARK = "chat_item:"

	def __init__( self ) :
		objType = chatObjTypes.ITEM
		minLen = 9
		defName = lbs_ChatFacade.unknowItem
		BaseObj.__init__( self, objType, minLen, defName )


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __getItem( self, text ) :
		"""
		根据掩码形式的物品信息，获取文本对应的物品
		"""
		if len( text ) < self.minLen_ : return None
		try : id, extra = eval( text )
		except : return None
		item = ItemDataList.instance().createDynamicItem( id )
		item.extra = extra
		return item

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def dump( self, text ) :
		"""
		打包一个可以作为聊天参数发送的物品（转换为发送参数：BLOB）
		必需返回 BLOB 或 None
		"""
		item = self.__getItem( text )
		if item :
			info = item.id, item.extra
			return ChatObjParser.dumpObj( self.objType, info )
		return None

	def load( self, info ) :
		"""
		将接收到的频道消息参数转换为可读文本（转换为 RichText 识别的字符串）
		必需返回一个字符串
		"""
		try : id, extra = info
		except : return " "
		item = ItemDataList.instance().createDynamicItem( id )
		if item :
			item.extra = extra
			itemName = item.fullName()
			foreColor = item.getQualityColor()
		else :
			itemName = self.defName_
			foreColor = ChatObjParser.OBJ_COLORS[self.objType]
		lmark = self.LMARK + str( ( id, extra ) ).replace( "}", "\}" )
		linkText = ChatObjParser.viewObj( itemName )
		return chatObjParsers.plnRTLink.getSource( linkText, lmark, cfc = foreColor )

	# ---------------------------------------
	def getMaskText( self, item ) :
		"""
		将物品转换为掩码形式的字符串（转换为 RichTextBox/MLRichTextBox 暗藏的文本）
		必需返回一个字符串
		"""
		itemInfo = item.id, item.extra
		return ChatObjParser.maskObj( self.objType, itemInfo )

	def getViewName( self, text ) :
		"""
		将暗码形式的聊天对象转换为用户形式的聊天对象（转换为 RichTextBox/MLRichTextBox 显示的文本）
		必需返回 None， 或（字符串，颜色）
		"""
		item = self.__getItem( text )
		if item is None : return None
		vname = ChatObjParser.viewObj( item.fullName() )
		color = item.getQualityColor()
		return vname, color


# -----------------------------------------------------
# 链接对象
# -----------------------------------------------------
class LItem( BaseObj ) :
	LMARK = "chat_item:"

	def __init__( self ) :
		objType = chatObjTypes.LINK
		minLen = 9
		defName = lbs_ChatFacade.unknowItem
		BaseObj.__init__( self, objType, minLen, defName )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def dump( self, text ) :
		"""
		打包一个可以作为聊天参数发送的物品（转换为发送参数：BLOB）
		必需返回 BLOB 或 None
		"""		
		info = text
		return ChatObjParser.dumpObj( self.objType, info )

	def load( self, info ) :
		"""
		将接收到的频道消息参数转换为可读文本（转换为 RichText 识别的字符串）
		必需返回一个字符串
		"""
		id, extra = eval( info )
		name = extra["name"]
		linkMark = extra["linkMark"]
		cfc = extra["cfc"]
		hfc = extra["hfc"]
		return chatObjParsers.plnRTLink.getSource( name , linkMark, cfc = cfc, hfc = hfc )

	# ------------------------------------------------------------
	def getMaskText( self, item ) :
		"""
		将物品转换为掩码形式的字符串（转换为 RichTextBox/MLRichTextBox 暗藏的文本）
		必需返回一个字符串
		"""
		itemInfo = ( item.id,{"name":item.name, "linkMark":item.linkMark, "cfc":item.cfc, "hfc":item.hfc} )
		return ChatObjParser.maskObj( self.objType, itemInfo )

	def getViewName( self, text ) :
		"""
		将暗码形式的聊天对象转换为用户形式的聊天对象（转换为 RichTextBox/MLRichTextBox 显示的文本）
		必需返回 None， 或（字符串，颜色）
		"""
		if len( text ) < self.minLen_ : return None
		id, extra = eval( text )
		name = extra["name"]
		cfc =extra["cfc"]
		return name, cfc


# --------------------------------------------------------------------
# 聊天对象管理器
# --------------------------------------------------------------------
class ObjParsers( Singleton ) :
	def __init__( self ) :
		self.parsers = {
			chatObjTypes.ITEM : ChatItem(),
			chatObjTypes.LINK : LItem(),
			}

		self.plnRTLink = None
		self.__objTpl = re.compile( "\$\{o\d+\}" )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def reTpl( self ) :
		return ChatObjParser.g_reObjTpl


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onGameStart( self ) :
		self.plnRTLink = smartImport( "guis.tooluis.richtext_plugins.PL_Link:PL_Link" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getMaskObj( self, objType, obj ) :
		"""
		由聊天对象转换为 RichTextBox/MLRichTextBox 暗藏的文本
		"""
		return self.parsers[objType].getMaskText( obj )

	def getViewObj( self, text ) :
		"""
		根据暗码形式的对象文本，获取可给用户看到 RichTextBox/MLRichTextBox 显示的聊天对象的名称
		"""
		ms = ChatObjParser.getObjMatchs( text )
		if len( ms ) != 1 : return None
		strObj, objType = ms[0].groups()
		parser = self.parsers.get( int( objType ), None )
		if parser is None : return None
		return parser.getViewName( strObj )

	# -------------------------------------------------
	def parseSendMsg( self, msg ) :
		"""
		解释将要发送的消息
		@type			msg : str
		@param			msg : 要发送的消息
		@rtype				: tuple: ( str, str of blob )
		@return				: 将消息分解为主体消息和消息参数后的消息
		"""
		sendMsg = ""
		dobjs = []
		parsers = self.parsers
		ms = ChatObjParser.getObjMatchs( msg )				# 获取所有对象的 re::Match
		start = 0
		for m in ms :
			end = m.end()
			strObj, objType = m.groups()					# ( 聊天对象, 聊天对象的类型 )
			parser = parsers.get( int( objType ), None )	# 获取相应的聊天对象的解释器
			if parser is None :								# 如果找不到对应的解释器
				sendMsg += msg[start:end]					# 则原样文本发送
			else :
				dobj = parser.dump( strObj )				# 否则对聊天对象进行打包
				if dobj :
					objMark = "${o%i}" % len( dobjs )
					sendMsg += msg[start:m.start()] + objMark
					dobjs.append( dobj )
				else :
					sendMsg += msg[start:end]
			start = end
		sendMsg += msg[start:]
		return sendMsg, dobjs

	# ---------------------------------------
	def tearRcvMsg( self, msg, blobArgs ) :
		"""
		解释消息转义，并将解释后的消息，分段返回，从而标记出哪段为聊天对象相关文本，哪段是普通文本:
		[( True, @I{...} ), ( False, "xxxx" ), ( False "xxxx" ), ...]
		"""
		emsgs = []
		start = 0
		end = len( msg )
		emIter = self.__objTpl.finditer( msg )						# 获取所有信息字段的迭代器
		while True :
			try :
				em = emIter.next()
				eStart = em.start()
				if start != eStart :
					emsgs.append( ( False, msg[start:eStart] ) )	# 普通消息
				emsgs.append( ( True, em.group() ) )
				start = em.end()
			except StopIteration :
				break
		if start != end :
			emsgs.append( ( False, msg[start:end] ) )				# 剩余的非表情消息
		return emsgs

	def calcObjAmount( self, text ) :
		"""
		计算文本中所插入对象的数量
		"""
		return len( ChatObjParser.getObjMatchs( text ) )

	def parseRcvMsg( self, msg, blobArgs ) :
		"""
		解释接收到的信息
		@type			msg		 : str
		@param			msg		 : 接收到的消息
		@type			blobArgs : BLOB_ARRAY
		@param			blobArgs : 打包后的物品列表：对“[( id, extra ), ( id, extra ), ...]”进行 cPickle
		@rtype					 : str
		@param					 : 返回解包后的消息
		"""
		args = {}
		for idx, blobObj in enumerate( blobArgs ) :
			viewText = " "
			try :
				objType, obj = cPickle.loads( blobObj )
			except err :
				ERROR_MSG( err )
			else :
				parser = self.parsers.get( objType, None )
				if parser is None :
					ERROR_MSG( "chat object '%i' is not exist!" % objType )
					viewText = str( objType )
				else :
					viewText = parser.load( obj )
			args["o%i" % idx] = viewText
		return string.Template( msg ).safe_substitute( args )


class MessageInserter( Singleton ) :

	def __init__( self ) :
		self.__pyCurInputObj = None						# 当前的消息插入接收对象
		self.__pyDefInputObj = None						# 默认的消息插入接收对象


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onInputObjTabIn( self, pyInputObj ) :
		"""
		某个输入框获得焦点
		"""
		self.__pyCurInputObj = weakref.ref( pyInputObj )

	def __onInputObjTabOut( self, pyInputObj ) :
		"""
		某个输入框失去焦点
		"""
		if BigWorld.isKeyDown( keys.KEY_LCONTROL ) or \
			BigWorld.isKeyDown( keys.KEY_RCONTROL ) :	# 如是是按着Ctrl键，则不撤销
				return									# 当前的消息插入控件
		self.__pyCurInputObj = None


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setDefInputObj( self, pyDefInputObj ) :
		"""
		设置默认的消息插入接收对象
		"""
		if pyDefInputObj is not None :
			self.__pyDefInputObj = weakref.ref( pyDefInputObj )
			self.registerInputObj( pyDefInputObj )
		else :
			if self.__pyDefInputObj :
				pyDefInputObj = self.__pyDefInputObj()
				if pyDefInputObj :
					self.disregisterInputObj( pyDefInputObj )
			self.__pyDefInputObj = None

	def registerInputObj( self, pyInputObj ) :
		"""
		添加接收消息插入的对象
		注意，pyInputObj一定要有notifyInput方法！
		"""
		pyInputObj.onTabIn.bind( self.__onInputObjTabIn )
		pyInputObj.onTabOut.bind( self.__onInputObjTabOut )

	def disregisterInputObj( self, pyInputObj ) :
		"""
		移除接收消息插入的对象
		"""
		pyInputObj.onTabIn.unbind( self.__onInputObjTabIn )
		pyInputObj.onTabOut.unbind( self.__onInputObjTabOut )

	# -------------------------------------------------
	def insertMessage( self, msg ) :
		"""
		插入一段消息
		"""
		pyPotentate = None
		if self.__pyCurInputObj is None :
			if self.__pyDefInputObj is None : return
			pyPotentate = self.__pyDefInputObj()
		else :
			pyPotentate = self.__pyCurInputObj()
			if pyPotentate is None :
				if self.__pyDefInputObj is None : return
				pyPotentate = self.__pyDefInputObj()

		if pyPotentate is not None :
			pyPotentate.notifyInput( msg )

# --------------------------------------------------------------------
# global instances
# --------------------------------------------------------------------
chatObjTypes = ChatObjParser.ObjTypes		# 所有对象类型
chatFacade = ChatFacade()					# 聊天 Facade 层
emotionParser = EmotionParser()				# 表情解释器
chatObjParsers = ObjParsers()				# 对象连接解释器
msgInserter = MessageInserter()				# 消息插入器

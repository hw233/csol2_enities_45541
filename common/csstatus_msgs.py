# -*- coding: gb18030 -*-

# $Id: csstatus_msgs.py,v 1.273 2008-09-05 09:26:11 yangkai Exp $

"""
locates global macros feedback from cell or base to client

2005.06.15 = designed by huangyongwei
"""

import re
import csdefine
import csconst
import csstatus
from bwdebug import *
from csstatus import *
from config.csstatusMsgs import Datas

# --------------------------------------------------------------------
#原csstatus.py
# ID 用法：
#		① ID 为 4 位十六进制（即 16 位二进制标示）。
#		② ID 不能重复。
#		③ ID 的十六进制高两位标示信息提示的类别，每增加一个类别，数值就增 1（最高支持 128 类）。
#		④ ID 的十六进制低两位给予信息提示类别内用（最多可以设置 128 个信息 ID）。
#		⑤ 类别内的信息 ID 要加上类别相关的前缀，以免信息 ID 重复定义。
#		⑥ 每个类别之间用两个“#--------”分割线隔开，分割线之间写上类别注释。
#		⑦ 类别内尽量不要超出 128 个信息 ID 从而使得 ID 号要往类别上增。
#		  （不强制，但遇到 ID 过多的尽量尝试拆分为多个类别，确实不能拆分时也不反对往类别上增一）
#		⑧ 每个类别后加一空行。
#		⑨ 类别内的 ID 可以自行分子类，子分类之间用空格分开，并可以在子类别前加上注释，
#		   但别用“#--------”分割，以免与大类混淆。
#
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# 系统频道前缀映射
# 频道前缀说明：
#	① 使用方法
#	可以随便指定 statusMessage 在以下任何一个或多个频道中显示，
#	指定方法是，在消息的前面加上频道前缀，
#	前缀格式是：
#		"(频道前缀1,频道前缀2):消息内容"
#	例如：
#		_svrStatusMsgs[GB_INVALID_CALLER] = "(SY,SC):您不是合法的操作员！"
#	这样则表示该消息将会同时在“系统”和“屏幕中央”频道显示。
#
#	② 不带频道前缀的信息
#	如果某些消息不带频道前缀，则会默认在个人频道（PA）显示，
#	但带了频道前缀，如果没有“PA”前缀，将不会在个人频道显示。
#
#	③ 添加发言者
#	可以对 statusMessage 添加发言者，发言者一般是“系统”，
#	如果往频道前缀中加入前缀列表中不存在的字符串，则该字符串被认为是发言者
#	如：
#		_svrStatusMsgs[GB_INVALID_CALLER] = "(SY,SC,系统):您不是合法的操作员！"
#	这里，“系统”这两个字被认为是发言者名称。
# --------------------------------------------------------------------
_prefix_channels = {
	# 角色发言频道
	"NE" : csdefine.CHAT_CHANNEL_NEAR,				# 附近频道
	"LO" : csdefine.CHAT_CHANNEL_LOCAL,				# 本地频道
	"TM" : csdefine.CHAT_CHANNEL_TEAM,				# 队伍频道
	"FM" : csdefine.CHAT_CHANNEL_FAMILY,			# 家族频道
	"TG" : csdefine.CHAT_CHANNEL_TONG,				# 帮会频道
	"WP" : csdefine.CHAT_CHANNEL_WHISPER,			# 私聊频道
	"WD" : csdefine.CHAT_CHANNEL_WORLD,				# 世界频道
	"RM" : csdefine.CHAT_CHANNEL_RUMOR,				# 谣言频道
	"WY" : csdefine.CHAT_CHANNEL_WELKIN_YELL,		# 天音广播
	"TY" : csdefine.CHAT_CHANNEL_TUNNEL_YELL,		# 地音广播

	# GM/公告频道
	"BR" : csdefine.CHAT_CHANNEL_SYSBROADCAST,		# GM/系统广播

	# NPC 发言频道
	"NS" : csdefine.CHAT_CHANNEL_NPC_SPEAK,			# NPC 发言频道
	"NT" : csdefine.CHAT_CHANNEL_NPC_TALK,			# NPC 对话频道

	# 系统提示频道
	"SY" : csdefine.CHAT_CHANNEL_SYSTEM,			# 系统频道（显示由服务器产生的各种活动、获得物品/强化/镶嵌等产生）
	"CB" : csdefine.CHAT_CHANNEL_COMBAT,			# 战斗频道（显示战斗信息）
	"PA" : csdefine.CHAT_CHANNEL_PERSONAL,			# 个人频道（个人频道显示玩家在获得经验、潜能、金钱、物品、元宝的信息）
	"MG" : csdefine.CHAT_CHANNEL_MESSAGE,			# 消息频道（显示角色的操作产生的错误信息或提示信息）
	"SC" : csdefine.CHAT_CHANNEL_SC_HINT,			# 在屏幕中间提示的频道
	"MB" : csdefine.CHAT_CHANNEL_MSGBOX,			# 以 MessageBox 提示的频道
	}

# -------------------------------------------
_ch_prefies = set( _prefix_channels.keys() )				# 所有频道前缀集
_chpfxSplitter = re.compile( "(?<=^\().+(?=\):)" )			# 查找频道前缀的正则模板

class MSGInfo( object ) :									# 消息包装
	__slots__ = ["chids", "spkName", "msg"]
	def __init__( self, chs, sk, msg ) :
		self.chids = chs									# 频道列表
		self.spkName = sk									# 发言者
		self.msg = msg										# 消息内容

def getMSGInfo( msg ) :
	"""
	获取频道前缀列表
	"""
	chs = []
	spkName = ""
	match = _chpfxSplitter.search( msg )					# 查找频道前缀
	if match :
		prefies = match.group().split( "," )				# 拆分所有频道前缀
		for prefix in prefies :
			prefix = prefix.strip()
			ch = _prefix_channels.get( prefix, None )		# 获取对应的频道
			if ch :
				chs.append( ch )							# 如果在频道前缀列表中，则认为是频道
			else :
				spkName = prefix							# 如果不在频道前缀列表中，则认为是发言者名称
		msg = msg[match.end() + 2:]							# 则，返回频道前缀和消息
	if not chs and msg != "" :								# 空消息不添加到任何频道
		chs = [csdefine.CHAT_CHANNEL_PERSONAL]				# 否则若没有频道前缀，则返回“个人”频道
	return MSGInfo( chs, spkName, msg )


# --------------------------------------------------------------------
# global status
# --------------------------------------------------------------------
_svrStatusMsgs = {}

for id, msg in Datas.iteritems() :
	_svrStatusMsgs[id] = getMSGInfo( msg )


# --------------------------------------------------------------------
# reference method
# --------------------------------------------------------------------
def getStatusInfo( statusID, *args ) :
	"""
	解释指定 ID 的状态消息,对于解释失败的消息,输出 debug 信息
	@type			statusID : INT32
	@param			statusID : status id defined in common/csstatus.py
	@type			args	 : all types
	@param			args	 : multi arguments
	@rtype					 : MSGInfo
	@return					 : status_msgs.MSGInfo
	"""
	msgInfo = _svrStatusMsgs.get( statusID, None )
	if msgInfo is None :													# 消息没有被定义
		msgInfo = MSGInfo( [csdefine.CHAT_CHANNEL_PERSONAL], "", "" )
		ERROR_MSG( "undefined status message: %#x" % statusID )
	msg = msgInfo.msg
	try :
		msg = msgInfo.msg % args
	except :
		EXCEHOOK_MSG( "error status: '%#x'" % statusID )
	return MSGInfo( msgInfo.chids, msgInfo.spkName, msg )

def getStatusPrefix( statusID ) :
	"""
	get status name's prefix
	@type			statusID : INT32
	@param			statusID : status id defined in common/csstatus.py
	@rtype					 : str
	@return					 : prefix of the status name defined in common/csstatus.py
	"""
	for name in dir( csstatus ):
		value = getattr( csstatus, name )
		if value == statusID :
			return name.split( "_" )[0]
	return None


# --------------------------------------------------------------------
# 可由玩家自行设置为是否显示的信息
# --------------------------------------------------------------------
# 敌人受伤信息
enemyInjuredStatus = set( [
	SKILL_SPELL_RESIST_HIT_FROM_SKILL,				SKILL_SPELL_DOUBLEDAMAGE_TO,				SKILL_BUFF_REBOUND_MAGIC_TO,
	SKILL_BUFF_REBOUND_PHY_TO,						SKILL_SPELL_DAMAGE_TO,
	SKILL_SPELL_DODGE_FROM_SKILL,					SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL,		SKILL_SPELL_PET_DOUBLEDAMAGE_TO,
	SKILL_SPELL_PET_DAMAGE_TO,						SKILL_SPELL_PET_NO_HIT_TO,					SKILL_SPELL_PET_DODGE_TO,
	] )

# 技能攻击信息
skillHitStatus = set( [
	SKILL_SPELL_DODGE_TO_SKILL,
	SKILL_SPELL_DODGE_TO,
	] )

# 回复信息
revertStatus = set( [
	] )

# 受伤信息
injuerdStatus = set( [
	SKILL_SPELL_RESIST_HIT_TO,					SKILL_SPELL_DOUBLEDAMAGE_FROM_SKILL,			SKILL_BUFF_REBOUND_MAGIC,
	SKILL_BUFF_REBOUND_PHY,						SKILL_SPELL_DAMAGE_FROM_SKILL,					SKILL_SPELL_RESIST_HIT_FROM,
	SKILL_SPELL_DOUBLEDAMAGE_FROM,				SKILL_SPELL_DAMAGE_FROM,						SKILL_SPELL_RESIST_HIT_TO_DOUBLEDAMAGE,
	] )

# buff 信息
buffStatus = set( [
	csstatus.ACCOUNT_STATE_REV_BUFF,
	] )


# --------------------------------------------------------------------
# 角色属性变更信息
# --------------------------------------------------------------------

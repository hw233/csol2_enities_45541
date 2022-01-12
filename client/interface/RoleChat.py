# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.39 2008-08-30 09:15:54 huangyongwei Exp $
"""
implement chatting system

09/05/2005 : created by phw
11/28/2006 : modified by huangyongwei
"""

import csdefine
import csstatus
import csstatus_msgs
import event.EventCenter as ECenter
from bwdebug import *
from gbref import rds
from MapMgr import mapMgr
import Const
from ChatFacade import chatFacade
from config.client.labels import RoleChat as lbs_RoleChat
from config.client.SkillAutoConfig import Datas as skill_auto_datas  #add by wuxo 2011-11-17
# --------------------------------------------------------------------
# 实现聊天接口
# --------------------------------------------------------------------
class RoleChat :
	def __init__( self ) :
		self.chat_commands = {}			# 所有可用 GM 指令：{ 指令名称 : 指令等级 }

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStatusMessage_( self, statusID, *args ) :
		"""
		收到状态消息时被调用（由 Role 中的 onStatusMessage def 方法收到消息后，将其参数解释并触发此方法）
		状态信息需要转化为频道信息
		注意：该方法只被 PlayerRole 使用
		"""
		chatFacade.rcvStatusMsg( statusID, *args )

	def _onDirectMessage( self, chids, spkName, msg ) :
		"""
		收到频道消息时被调用（由 Role 中的 onDirectMessage def 方法收到消息后触发此方法）
		注意：该方法只被 PlayerRole 使用
		"""
		chatFacade.rcvMsgDirect( chids, spkName, msg )

	# ----------------------------------------------------------------
	# attribute setting methods
	# ----------------------------------------------------------------
	def set_grade( self, old ) :
		"""
		管理等级改变时被调用
		注意：该方法只被 PlayerRole 使用
		hyw--2009.03.16
		"""
		pass


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def chat_onChannelMessage( self, chid, spkID, spkName, msg, blobArgs ) :
		"""
		defined method
		收到频道消息时被调用
		注意：该方法只被 PlayerRole 使用
		@type		chid	: INT8
		@param 		chid	: speaking channel
		@type		spkID	: OBJECT_ID
		@param		spkID	: 发言者 entity id
		@type		spkName : STRING
		@param 		spkName : spokesman's name
		@type		msg		: STRING
		@param 		msg		: speech
		@type		blobArgs: BLOB
		@param		blobArgs: 消息参数
		@return				: None
		"""
		if spkName in self.blackList : return						# 在自己的黑名单就不接收消息
		chatFacade.rcvChannelMsg( chid, spkID, spkName, msg, blobArgs )

	def chat_onRcvOflMessage( self, chid, spkID, spkName, msg, blobArgs, sendTime ) :
		"""
		defined method
		接收离线消息
		注意：该方法只被 PlayerRole 使用
		@type		chid	: INT8
		@param 		chid	: speaking channel
		@type		spkID	: OBJECT_ID
		@param		spkID	: 发言者 entity id
		@type		spkName : STRING
		@param 		spkName : spokesman's name
		@type		msg		: STRING
		@param 		msg		: speech
		@type		blobArgs: BLOB
		@param		blobArgs: 消息参数
		@type		sendTime: STRING
		@param		sendTime: 消息发送时间
		@return				: None
		"""
		if spkName in self.blackList : return						# 在自己的黑名单就不接收消息
		chatFacade.rcvChannelMsg( chid, spkID, spkName, msg, blobArgs, sendTime )

	# ---------------------------------------
	def chat_systemInfo( self, msg ) :
		"""
		defined method
		发送一条简单的频道组合消息（服务器上应该尽量用 statusMessage 代替此方法）
		注意：① 该消息在哪个频道显示根据 msg 的前缀而定
			  ② 频道前缀说明请看：common/csstatus_msgs.py
			  ③ 不带频道前缀的消息默认在“个人”频道显示
		"""
		msgInfo = csstatus_msgs.getMSGInfo( msg )
		for chid in msgInfo.chids :
			chatFacade.rcvChannelMsg( chid, 0, msgInfo.spkName, msgInfo.msg, [] )

	# -------------------------------------------------
	def chat_onReceiveRoleInfo( self, roleInfo ) :
		"""
		defined method
		收到角色信息
		注意：该方法只被 PlayerRole 使用
		"""
		if roleInfo["name"] == "" :
			self.statusMessage( csstatus.TARGET_IS_NONE_OR_NOT_ONLINE )
		else :
			msg = "%s, " % roleInfo["name"]
			msg += lbs_RoleChat.level % roleInfo["level"]
			if roleInfo["tong"] != "" :
				msg += lbs_RoleChat.tong % roleInfo["tong"]
			spaceLabel = roleInfo["spaceLabel"]
			wholeArea = mapMgr.getWholeArea( spaceLabel )
			if wholeArea :
				msg += lbs_RoleChat.area % wholeArea.name
			else :
				ERROR_MSG( "spaceLabel: '%s' is not exist!" % spaceLabel )						# 应该不会不执行到这里，除非该场景不在 bigmap.xml 中配置
			ECenter.fireEvent( "EVT_ON_CHAT_RECEIVE_ROLE_INFO", msg )

	def chat_onScenarioMsg( self, msg, visible ) :
		"""
		define method
		服务器发送的剧情提示
		@param		msg : 剧情文本
		@type		msg : STRING
		@param 		visible: 是否隐藏玩家界面,False表示不隐藏
		@param		visible: Bool
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS", msg, visible )


	# ----------------------------------------------------------------
	# public( called by client )
	# ----------------------------------------------------------------
	def statusMessage( self, statusID, *args ) :
		"""
		send status message
		注意：该方法只被 PlayerRole 使用（不要企图通过其它角色调用该方法，向此角色发送一条消息）
		@type			statusID : INT16
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		# 自动战斗状态不播放提示信息
		if hasattr( self, "attackState" ) and self.attackState == Const.ATTACK_STATE_AUTO_FIGHT:return
		chatFacade.rcvStatusMsg( statusID, *args )
		#播放相应音效add by wuxo 2012-5-15
		if skill_auto_datas.has_key( statusID ):
			career_gender = self.getClass() + self.getGender()
			if skill_auto_datas[ statusID ].has_key( career_gender ):
				rds.soundMgr.play2DSound( skill_auto_datas[ statusID ][ career_gender ] )

	# -------------------------------------------------
	def chat_requireRoleInfo( self, roleName ) :
		"""
		请求角色信息
		注意：该方法只被 PlayerRole 使用
		hyw -- 2008.08.29
		@type				roleName : str
		@param				roleName : 角色名字
		"""
		self.base.chat_requireRoleInfo( roleName )

	def chat_switchFengQi( self, unLocked ):
		"""
		GM锁定/解锁夜战凤栖聊天框命令
		"""
		self.cell.chat_switchFengQi( unLocked )
	
	def chat_onSwitchFengQi( self, unLocked ):
		"""
		define method
		锁定/解锁夜战凤栖聊天框回调
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_SWITCH_FENGQI", unLocked )

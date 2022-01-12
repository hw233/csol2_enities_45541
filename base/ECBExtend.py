# -*- coding: gb18030 -*-
# $Id: ECBExtend.py,v 1.4 2008-06-10 08:57:00 huangyongwei Exp $

"""
This module implements Entity Callback Extend.
"""

########################################################################
#
# 模块: ECBExtend
# 功能: 实现BigWorld.Entity的Callback扩展类ECBExtend
#       包括下列回调
#         onTimer(controllerID, userData)
#       相关的函数
#         addTimer
#
########################################################################

import BigWorld
from bwdebug import *

#
# Timer Callback ID section from 0x2001-0x3000
#
UPDATE_CLIENT_PET_CBID					= 0x2101		# 宠物初始化( hyw -- 2008.06.09 )
UPDATE_CLIENT_QB_CBID					= 0x2102		# 快捷栏初始化( hyw -- 2008.06.09 )
UPDATE_CLIENT_OPR_CBID					= 0x2103		# 客户端操作记录初始化( hyw -- 2010.04.14 )

# 图片认证
IMAGE_VERIFY_TIMER_CBID					= 0x2201
IMAGE_VERIFY_FIRST_TIMER_CBID			= 0x2202
IMAGE_VERIFY_ANSWER_TIMER_CBID			= 0x2203
# 好友
FRIEND_NOTIFY_FRIEND_TIMER_CBID			= 0x2301
FRIEND_NOTIFY_ADMIRER_TIMER_CBID		= 0x2302
# mail
INIT_MAIL_TO_CLIENT_TIMER_CBID			= 0x2401
# 组队
TEAM_CLEAR_REFUSE_PLAYER_CBID			= 0x2501		# 清理拒绝组队玩家id


#活动标记更新
PLAYER_ACTIVITY_RECORD_REFRESH_CBID		= 0x2601

# 定时奖励 by姜毅
FIX_TIME_REWARD							= 0x2701		# 发送客户端领奖通知
# 老手定时奖励 by姜毅
FIX_TIME_OLD_PLAYER_REWARD				= 0x2702
# 老手定时奖励刷新 by姜毅
FIX_TIME_OLD_PLAYER_REWARD_REFLASH		= 0x2703

# 每日补充活力值 by 姜毅
LIVING_SYSTEM_VIM_CHARGER				= 0x2801

# 帮会会标发送时隔器 by 姜毅
ROLE_TONG_SIGN_SENDER					= 0x2901
ROLE_TONG_SIGN_PACKS_SENDER			= 0x2902



# 发送离线消息到客户端
SEND_OFFLINE_MSG_CBID					= 0x2a01


#创建space
START_CREATE_SPACE_CBID					= 0x2b01

# 副本组队系统
TIMEOUT_CBID_OF_MATCHED_CONFIRM			= 0x2c01		# 匹配确认超时
TIMEOUT_CBID_OF_DUTIES_SELECTION        = 0x2c02        # 职责确认超时
TIME_CBID_OF_RESET_MATCH_STATUS			= 0x2d01        # 在弹出匹配确认过程中，有人点离开，点确认的人3秒后才会改变状态（由于界面有3秒的显示时延）

FISHING_JOY_ITEM_CBID				= 0x2e01					# 玩家使用捕鱼物品有效期Timer

# 每日补充自动战斗时间 by 姜毅
ROLE_AF_TIME_CHARGE					= 0x3001

# 自动战斗付费充值时间计时器 by 姜毅
ROLE_AF_TIME_EXTRA						= 0x3002

#
# 全局Callback字典，用来从指定的ID查询回调函数
#
gcbs = {
	UPDATE_CLIENT_PET_CBID				: "onTimer_pet_updateClient",
	UPDATE_CLIENT_QB_CBID				: "onTimer_qb_updateClient",
	UPDATE_CLIENT_OPR_CBID				: "onTimer_opr_updateClient",
	IMAGE_VERIFY_TIMER_CBID				: "onTimer_imageVerify",
	IMAGE_VERIFY_FIRST_TIMER_CBID		: "onTimer_imageVerifyFirst",
	IMAGE_VERIFY_ANSWER_TIMER_CBID		: "onTimer_imageVerifyAnswer",
	FRIEND_NOTIFY_FRIEND_TIMER_CBID		: "onTimer_friendNotifyFriend",
	FRIEND_NOTIFY_ADMIRER_TIMER_CBID	: "onTimer_relationNotify",
	INIT_MAIL_TO_CLIENT_TIMER_CBID		: "onTimer_initMailToClient",
	TEAM_CLEAR_REFUSE_PLAYER_CBID		: "onTemer_clearFobidTeamPlayer",
#	FIX_TIME_REWARD						: "onTimer_fixTimeReward",
	PLAYER_ACTIVITY_RECORD_REFRESH_CBID	: "onTimer_refreshActivityRecord",
	LIVING_SYSTEM_VIM_CHARGER			: "onTimer_livingSystemVimCharger",
	FIX_TIME_OLD_PLAYER_REWARD			: "onTimer_fixTimeOldPlayerReward",
	FIX_TIME_OLD_PLAYER_REWARD_REFLASH	: "onTimer_fixTimeOldPlayerReflash",
	ROLE_TONG_SIGN_SENDER				: "onTimer_roleTongSignSender",
	ROLE_TONG_SIGN_PACKS_SENDER		: "onTimer_roleTongSignPacksSender",
	ROLE_AF_TIME_CHARGE				: "onTimer_roleAFTimeCharge",
	ROLE_AF_TIME_EXTRA					: "onTimer_roleAFTimeExtra",
	TIMEOUT_CBID_OF_MATCHED_CONFIRM		: "onTimer_matchedConfirmTimeout",
	TIME_CBID_OF_RESET_MATCH_STATUS		: "onTime_reSetMatchStatus",
	SEND_OFFLINE_MSG_CBID				: "onTimer_initOflMsgToClient",
	FISHING_JOY_ITEM_CBID					: "onTimer_fish_useItemTimerOut",
	TIMEOUT_CBID_OF_DUTIES_SELECTION	: "onTimer_dutiesSelectionTimeout",
}

#
# BigWorld.Entity的Callback扩展类ECBExtend
#
# 注意: 本Class不能被单独实例化，只能与BigWorld.Entity同时被ConcreteEntity类继承才有意义
#
class ECBExtend:
	#
	# 功能: 初始化
	# 参数:
	# 返回: 不能被单独实例化
	#
	def __init__( self ):
		pass

	#
	# 功能: 实现BigWorld.Entity.onTimer，当某个Timer Tick到达时被调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       timerID			timer的ID
	#       cbID			Callback ID
	# 返回:
	#
	def onTimer( self, timerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
			#cb( timerID, cbID )	# phw：移到下面
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		# phw: 从上面移下来，因为在这个函数里可能也会有上面的KeyError和AttributeError异常产生
		# 移下来后产生错误时容易测试
		cb( timerID, cbID )

#########################
# End of ECBExtend.py   #
#########################

# -*- coding: gb18030 -*-
# $Id: ECBExtend.py,v 1.4 2008-06-10 08:57:00 huangyongwei Exp $

"""
This module implements Entity Callback Extend.
"""

########################################################################
#
# ģ��: ECBExtend
# ����: ʵ��BigWorld.Entity��Callback��չ��ECBExtend
#       �������лص�
#         onTimer(controllerID, userData)
#       ��صĺ���
#         addTimer
#
########################################################################

import BigWorld
from bwdebug import *

#
# Timer Callback ID section from 0x2001-0x3000
#
UPDATE_CLIENT_PET_CBID					= 0x2101		# �����ʼ��( hyw -- 2008.06.09 )
UPDATE_CLIENT_QB_CBID					= 0x2102		# �������ʼ��( hyw -- 2008.06.09 )
UPDATE_CLIENT_OPR_CBID					= 0x2103		# �ͻ��˲�����¼��ʼ��( hyw -- 2010.04.14 )

# ͼƬ��֤
IMAGE_VERIFY_TIMER_CBID					= 0x2201
IMAGE_VERIFY_FIRST_TIMER_CBID			= 0x2202
IMAGE_VERIFY_ANSWER_TIMER_CBID			= 0x2203
# ����
FRIEND_NOTIFY_FRIEND_TIMER_CBID			= 0x2301
FRIEND_NOTIFY_ADMIRER_TIMER_CBID		= 0x2302
# mail
INIT_MAIL_TO_CLIENT_TIMER_CBID			= 0x2401
# ���
TEAM_CLEAR_REFUSE_PLAYER_CBID			= 0x2501		# ����ܾ�������id


#���Ǹ���
PLAYER_ACTIVITY_RECORD_REFRESH_CBID		= 0x2601

# ��ʱ���� by����
FIX_TIME_REWARD							= 0x2701		# ���Ϳͻ����콱֪ͨ
# ���ֶ�ʱ���� by����
FIX_TIME_OLD_PLAYER_REWARD				= 0x2702
# ���ֶ�ʱ����ˢ�� by����
FIX_TIME_OLD_PLAYER_REWARD_REFLASH		= 0x2703

# ÿ�ղ������ֵ by ����
LIVING_SYSTEM_VIM_CHARGER				= 0x2801

# ����귢��ʱ���� by ����
ROLE_TONG_SIGN_SENDER					= 0x2901
ROLE_TONG_SIGN_PACKS_SENDER			= 0x2902



# ����������Ϣ���ͻ���
SEND_OFFLINE_MSG_CBID					= 0x2a01


#����space
START_CREATE_SPACE_CBID					= 0x2b01

# �������ϵͳ
TIMEOUT_CBID_OF_MATCHED_CONFIRM			= 0x2c01		# ƥ��ȷ�ϳ�ʱ
TIMEOUT_CBID_OF_DUTIES_SELECTION        = 0x2c02        # ְ��ȷ�ϳ�ʱ
TIME_CBID_OF_RESET_MATCH_STATUS			= 0x2d01        # �ڵ���ƥ��ȷ�Ϲ����У����˵��뿪����ȷ�ϵ���3���Ż�ı�״̬�����ڽ�����3�����ʾʱ�ӣ�

FISHING_JOY_ITEM_CBID				= 0x2e01					# ���ʹ�ò�����Ʒ��Ч��Timer

# ÿ�ղ����Զ�ս��ʱ�� by ����
ROLE_AF_TIME_CHARGE					= 0x3001

# �Զ�ս�����ѳ�ֵʱ���ʱ�� by ����
ROLE_AF_TIME_EXTRA						= 0x3002

#
# ȫ��Callback�ֵ䣬������ָ����ID��ѯ�ص�����
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
# BigWorld.Entity��Callback��չ��ECBExtend
#
# ע��: ��Class���ܱ�����ʵ������ֻ����BigWorld.Entityͬʱ��ConcreteEntity��̳в�������
#
class ECBExtend:
	#
	# ����: ��ʼ��
	# ����:
	# ����: ���ܱ�����ʵ����
	#
	def __init__( self ):
		pass

	#
	# ����: ʵ��BigWorld.Entity.onTimer����ĳ��Timer Tick����ʱ������
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       timerID			timer��ID
	#       cbID			Callback ID
	# ����:
	#
	def onTimer( self, timerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
			#cb( timerID, cbID )	# phw���Ƶ�����
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		# phw: ����������������Ϊ��������������Ҳ���������KeyError��AttributeError�쳣����
		# ���������������ʱ���ײ���
		cb( timerID, cbID )

#########################
# End of ECBExtend.py   #
#########################

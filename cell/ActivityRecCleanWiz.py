# -*- coding: gb18030 -*-
#
# GMָ��������¼���
#

import time
import csdefine
import cschannel_msgs
import ShareTexts as ST

g_activity_record_clean = {}

def ACTIVITY_RECORD_CLEAN_FUNCS( activityName, funcName ):
	"""
	ӳ������Ŀ��������ʵ��������
	"""
	g_activity_record_clean[activityName] = funcName


#################################################################
#	����Ϊ������¼
#################################################################

def cleanRaceHorseRec( player ):
	"""
	��������¼
	"""
	player.lastRaceTime = 0


def cleanMonsterActivityRec( player ):
	"""
	������﹥�Ǽ�¼
	"""
	pass


def cleanXiangshiRec( player ):
	"""
	����ƾ����Լ�¼
	"""
	questID = 30701001
	lpLog = player.getLoopQuestLog( questID, True )
	lpLog._degree = 0
	dataQuestID = str(time.localtime()[2])+':' + str( questID )
	if dataQuestID in player.failedGroupQuestList:
		player.failedGroupQuestList.remove( dataQuestID )


def cleanHuishiRec( player ):
	"""
	����ƾٻ��Լ�¼
	"""
	questID = 30701002
	lpLog = player.getLoopQuestLog( questID, True )
	lpLog._degree = 0
	dataQuestID = str(time.localtime()[2])+':' + str( questID )
	if dataQuestID in player.failedGroupQuestList:
		player.failedGroupQuestList.remove( dataQuestID )


def cleanDianshiRec( player ):
	"""
	����ƾٵ��Լ�¼
	"""
	questID = 30701003
	lpLog = player.getLoopQuestLog( questID, True )
	lpLog._degree = 0
	dataQuestID = str(time.localtime()[2])+':' + str( questID )
	if dataQuestID in player.failedGroupQuestList:
		player.failedGroupQuestList.remove( dataQuestID )


def cleanTianguanRec( player ):
	"""
	�����ؼ�¼
	"""
	player.lastTianguanTime = 0


def cleanShuijingRec( player ):
	"""
	���ˮ��������¼
	"""
	player.lastShuijingTime = 0


def cleanDartRec( player ):
	"""
	������ڼ�¼
	"""
	player.questNormalDartRecord.date = 0
	player.questTongDartRecord.data = 0

def cleanQnldRec( player ):
	"""
	���Ǳ���Ҷ���¼
	"""
	player.removeActivityRecord( csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU )

def cleanEnldRec( player ):
	"""
	��������Ҷ���¼
	"""
	player.removeActivityRecord( csdefine.ACTIVITY_JING_YAN_LUAN_DOU )

def cleanWudaoRec( player ):
	"""
	����������¼
	"""
	pass


ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_SAI_MA, cleanRaceHorseRec )			# ��������¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.MONSTERACTIVITY_GONGCHENG, cleanMonsterActivityRec )	# ������﹥�Ǽ�¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.KE_JU_KE_JU_XIANG_SHI, cleanXiangshiRec )			# ����ƾ����Լ�¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.KE_JU_KE_JU_HUI_SHI, cleanHuishiRec )			# ����ƾٻ��Լ�¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.KE_JU_KE_JU_DIAN_SHI, cleanDianshiRec )			# ����ƾٵ��Լ�¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.TIAN_GUAN_MONSTER_DEF_1, cleanTianguanRec )			# �������ؼ�¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_SHUIJING, cleanShuijingRec )			# ���ˮ��������¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.DART_INFO_1, cleanShuijingRec )				# ������ڼ�¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU, cleanQnldRec )				# ���Ǳ���Ҷ���¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU, cleanEnldRec )				# ��������Ҷ���¼
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_WU_DAO_DA_HUI, cleanWudaoRec )			# ����������¼
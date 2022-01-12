# -*- coding: gb18030 -*-
#
# GM指令清除活动记录标记
#

import time
import csdefine
import cschannel_msgs
import ShareTexts as ST

g_activity_record_clean = {}

def ACTIVITY_RECORD_CLEAN_FUNCS( activityName, funcName ):
	"""
	映射任务目标类型与实例化类型
	"""
	g_activity_record_clean[activityName] = funcName


#################################################################
#	以下为清除活动记录
#################################################################

def cleanRaceHorseRec( player ):
	"""
	清除赛马记录
	"""
	player.lastRaceTime = 0


def cleanMonsterActivityRec( player ):
	"""
	清除怪物攻城记录
	"""
	pass


def cleanXiangshiRec( player ):
	"""
	清除科举乡试记录
	"""
	questID = 30701001
	lpLog = player.getLoopQuestLog( questID, True )
	lpLog._degree = 0
	dataQuestID = str(time.localtime()[2])+':' + str( questID )
	if dataQuestID in player.failedGroupQuestList:
		player.failedGroupQuestList.remove( dataQuestID )


def cleanHuishiRec( player ):
	"""
	清除科举会试记录
	"""
	questID = 30701002
	lpLog = player.getLoopQuestLog( questID, True )
	lpLog._degree = 0
	dataQuestID = str(time.localtime()[2])+':' + str( questID )
	if dataQuestID in player.failedGroupQuestList:
		player.failedGroupQuestList.remove( dataQuestID )


def cleanDianshiRec( player ):
	"""
	清除科举殿试记录
	"""
	questID = 30701003
	lpLog = player.getLoopQuestLog( questID, True )
	lpLog._degree = 0
	dataQuestID = str(time.localtime()[2])+':' + str( questID )
	if dataQuestID in player.failedGroupQuestList:
		player.failedGroupQuestList.remove( dataQuestID )


def cleanTianguanRec( player ):
	"""
	清除天关记录
	"""
	player.lastTianguanTime = 0


def cleanShuijingRec( player ):
	"""
	清除水晶副本记录
	"""
	player.lastShuijingTime = 0


def cleanDartRec( player ):
	"""
	清除运镖记录
	"""
	player.questNormalDartRecord.date = 0
	player.questTongDartRecord.data = 0

def cleanQnldRec( player ):
	"""
	清除潜能乱斗记录
	"""
	player.removeActivityRecord( csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU )

def cleanEnldRec( player ):
	"""
	清除经验乱斗记录
	"""
	player.removeActivityRecord( csdefine.ACTIVITY_JING_YAN_LUAN_DOU )

def cleanWudaoRec( player ):
	"""
	清除武道大会记录
	"""
	pass


ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_SAI_MA, cleanRaceHorseRec )			# 清除赛马记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.MONSTERACTIVITY_GONGCHENG, cleanMonsterActivityRec )	# 清除怪物攻城记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.KE_JU_KE_JU_XIANG_SHI, cleanXiangshiRec )			# 清除科举乡试记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.KE_JU_KE_JU_HUI_SHI, cleanHuishiRec )			# 清除科举会试记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.KE_JU_KE_JU_DIAN_SHI, cleanDianshiRec )			# 清除科举殿试记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.TIAN_GUAN_MONSTER_DEF_1, cleanTianguanRec )			# 清除闯天关记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_SHUIJING, cleanShuijingRec )			# 清除水晶副本记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.DART_INFO_1, cleanShuijingRec )				# 清除运镖记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU, cleanQnldRec )				# 清除潜能乱斗记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU, cleanEnldRec )				# 清除经验乱斗记录
ACTIVITY_RECORD_CLEAN_FUNCS( cschannel_msgs.ACTIVITY_WU_DAO_DA_HUI, cleanWudaoRec )			# 清除武道大会记录
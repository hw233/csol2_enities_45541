# -*- coding: gb18030 -*-

import time
import csdefine
from bwdebug import *
import Const
import csstatus

"""
��Ĳ����¼�洢��������ϡ�

DailyActRecord �� AreaActRecord ���Ƕ�����洢��¼�Ľ�����

˵����
DailyActRecord:		tianguan_record: (2012, 10, 15)_2	( ��ʾ�� 2012-10-15 ��һ�������2�δ���� )
WeeklyActRecord:	tianguan_record: (2012, 48)_1			( ��ʾ��2012��ĵ�48�ܲ����һ����ػ)
AreaActRecord:		cms_socks_record: (2012, 10, 15)_100100111	( ��ʾ�� 2012-10-15 ��һ�������һЩ��ͼ��ʥ�����ӻ����������Щ��ͼ���գ�Const.ACTIVITY_AREA_FLAGS )
"""

def week( t=(0,)*9 ):
	"""
	��ȡ��ݺ͵ڼ��ܣ���������һ�ܵĵ�һ�죩
	"""
	return time.strftime("(%Y, %W)", t)

def date( t=(0,)*9 ):
	"""
	��ȡ��ǰ������
	"""
	return time.strftime("(%Y, %m, %d)", t)


class ActRecordBase:
	"""
	"""
	def __init__( self, recordKey, flag, count ):
		self.recordKey = recordKey
		self.actflag = flag
		self.maxCount = count

	def formatTime( self, t ):
		"""
		��ȡʱ���¼
		"""
		return date(t)

	def initRecord( self, player, t ):
		"""
		"""
		recordTime = self.formatTime(t)
		record = player.queryRoleRecord( self.recordKey )
		if record != "" and record.split("_")[0] == recordTime:
			return
		self.record( player, recordTime, 0 )
		self.updateActFlag( player, 0 )

	def incCount( self, player, t ):
		"""
		"""
		recordTime = self.formatTime(t)
		value = player.queryRoleRecord( self.recordKey )
		date,count = value.split("_")
		if date == recordTime:
			count = int( count ) + 1
		else:
			count = 1
		self.record( player, recordTime, count )
		self.updateActFlag( player, count )

	def isValidFor( self, player ):
		"""
		"""
		return self.maxCount > 0 and not player.hasActivityFlag( self.actflag )

	def updateActFlag( self, player, count ):
		"""
		"""
		if self.actCountOverflow( count ):
			player.setActivityFlag( self.actflag )
		else:
			player.removeActivityFlag( self.actflag )

	def actCountOverflow( self, count ):
		"""
		"""
		return self.maxCount <= count

	def record( self, player, recordTime, count ):
		"""
		"""
		player.setRoleRecord( self.recordKey, "%s_%i"%(recordTime,count) )

	def reset( self, player ):
		"""���ü�¼"""
		player.removeRoleRecord( self.recordKey )


class DailyActRecord( ActRecordBase ):
	"""ÿ����µĻ"""
	pass


class WeeklyActRecord( ActRecordBase ):
	"""ÿ�ܸ��µĻ"""
	def formatTime( self, t ):
		"""
		��ȡ��ǰ��¼��ʱ��
		"""
		return week(t)


class AreaActRecord( DailyActRecord ):
	"""ÿ����µ������Ի"""
	def incCount( self, player, t ):
		"""
		"""
		flag = self.getSpaceFlag( player )
		record = player.queryRoleRecord( self.recordKey )
		if record == "":
			value = 1 << flag
		else:
			value = int( record.split("_")[1] ) | ( 1 << flag )
		self.record( player, self.formatTime(t), value )

	def initRecord( self, player, t ):
		"""
		"""
		recordTime = self.formatTime(t)
		record = player.queryRoleRecord( self.recordKey )
		if record != "" and record.split("_")[0] == recordTime:
			return
		self.record( player, recordTime, 0 )

	def isValidFor( self, player ):
		"""
		"""
		if self.maxCount == 0:
			return False
		flag = self.getSpaceFlag( player )
		record = player.queryRoleRecord( self.recordKey )
		if record and int( record.split("_")[1] ) & 1 << flag > 0:
			return False
		else:
			return True

	def getSpaceFlag( self, player ):
		"""
		"""
		spaceLabel = player.queryTemp( "AREA_ACT_RECORD_SPACELABEL", player.spaceType )
		return Const.ACTIVITY_AREA_FLAGS.get( spaceLabel, 31 )


class ActivityRecordMgr:

	def __init__( self ):
		"""
		"""
		self.flagsDict = {
			csdefine.ACTIVITY_CHUANG_TIAN_GUAN 				: DailyActRecord(  "tianguan_record",  csdefine.ACTIVITY_FLAGS_TIANGUAN,  1 ),
			csdefine.ACTIVITY_SHUI_JING 					: DailyActRecord(  "shuijing_record",  csdefine.ACTIVITY_FLAGS_SHUIJING,  1 ),
			csdefine.ACTIVITY_SAI_MA						: DailyActRecord(  "racehorse_record", csdefine.ACTIVITY_FLAGS_RACEHORSE, 1 ),
			csdefine.ACTIVITY_ZHENG_JIU_YA_YU				: DailyActRecord(  "yayu_record", 		csdefine.ACTIVITY_FLAGS_YAYU, 2 ),
			csdefine.ACTIVITY_XIE_LONG						: DailyActRecord(  "xldx_record", 		csdefine.ACTIVITY_FLAGS_XLDX, 1 ),
			csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG			: DailyActRecord(  "fjsg_record", 		csdefine.ACTIVITY_FLAGS_FJSG, 2 ),
			csdefine.ACTIVITY_SHE_HUN_MI_ZHEN				: DailyActRecord( "shmz_record", 		csdefine.ACTIVITY_FLAGS_SHMZ, 2 ),
			csdefine.ACTIVITY_CMS_SOCKS						: AreaActRecord(  "cms_socks_record", csdefine.ACTIVITY_FLAGS_CMS_SOCKS, 0 ),
			csdefine.ACTIVITY_MEMBER_DART					: DailyActRecord( "member_dart", csdefine.ACTIVITY_FLAGS_MEMBER_DART, 1 ),
			csdefine.ACTIVITY_SPRING_RIDDER					: AreaActRecord( "spring_riddle", csdefine.ACTIVITY_FLAGS_SPRING_RIDDLE, 0 ),
			csdefine.ACTIVITY_SHI_TU			 			: DailyActRecord(  "teachEveryDayRewardTime",  csdefine.ACTIVITY_FLAGS_TEACH_REWARD,  1 ),
			csdefine.ACTIVITY_FEI_CHENG_WU_YAO				: DailyActRecord(  "fcwr_record", 		csdefine.ACTIVITY_FLAGS_FCWR, 1 ),
			csdefine.ACTIVITY_TANABATA_QUIZ					: DailyActRecord(  "tanabataQuizRecord",  csdefine.ACTIVITY_FLAGS_TANABATA_QUIZ,  1 ),
			csdefine.ACTIVITY_RUN_RABBIT					: DailyActRecord(  "rabbitRun",  csdefine.ACTIVITY_FLAGS_RABBITRUN,  2 ),
			csdefine.ACTIVITY_KUA_FU						: DailyActRecord( 	"kuafu_record",  csdefine.ACTIVITY_FLAGS_KUAFUREMAIN,  1 ),
			csdefine.ACTIVITY_TONG_FUBEN					: DailyActRecord( "tongfuben_record",  csdefine.ACTIVITY_FLAGS_TONG_FUBEN,  1 ),
			csdefine.ACTIVITY_CHALLENGE_FUBEN				: DailyActRecord(  "challengeFuben_record", csdefine.ACTIVITY_FLAGS_CHALLENGE_FUBEN, 1),
			csdefine.ACTIVITY_CHALLENGE_FUBEN_MANY			: DailyActRecord(  "challengeFuben_many_record", csdefine.ACTIVITY_FLAGS_CHALLENGE_FUBEN_MANY, 1),
			csdefine.ACTIVITY_SHEN_GUI_MI_JING				: DailyActRecord( "shenguimijing_record", csdefine.ACTIVITY_FLAGS_SHENGUIMIJING, 2 ),
			csdefine.ACTIVITY_WU_YAO_QIAN_SHAO				: DailyActRecord(  "wuyaoqianshao_record", csdefine.ACTIVITY_FLAGS_WUYAOQIANSHAO, 2 ),
			csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG				: DailyActRecord( "wuyaowangbaozang_record", csdefine.ACTIVITY_FLAGS_WUYAOWANGBAOZANG, 2 ),
			csdefine.ACTIVITY_YING_XIONG_LIAN_MENG			: DailyActRecord( "yingxionglianmeng_record", csdefine.ACTIVITY_FLAGS_YING_XIONG_LIAN_MENG, 2 ),
			csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU			: WeeklyActRecord( "qnld_record", csdefine.ACTIVITY_FLAGS_QNLD, 1 ),
			csdefine.ACTIVITY_JING_YAN_LUAN_DOU				: WeeklyActRecord( "jyld_record", csdefine.ACTIVITY_FLAGS_JYLD, 1 ),
			csdefine.ACTIVITY_YE_ZHAN_FENG_QI				: DailyActRecord( "yeZhanFengQi_record", csdefine.ACTIVITY_FLAGS_YE_ZHAN_FENG_QI, 2 ),
			csdefine.ACTIVITY_ZHENG_JIU_YA_YU_NEW			: DailyActRecord(  "yayu_record_new", 		csdefine.ACTIVITY_FLAGS_YAYU_NEW, 1 ),
			csdefine.ACTIVITY_DENTITY_TRANS_COM				: DailyActRecord( "destiny_trans_com_record", csdefine.ACTIVITY_FLAGS_DESTINY_TRANS, 2 ),
			csdefine.ACTIVITY_TOWER_DEFENSE					: DailyActRecord( "tower_defense_record", csdefine.ACTIVITY_FLAGS_TOWER_DEFENSE, 2 ),
			csdefine.ACTIVITY_DU_DU_ZHU						: DailyActRecord( "duduzhu_record", csdefine.ACTIVITY_FLAGS_DUDUZHU, 2 ),
			}

	def add( self, player, activityType ):
		"""
		"""
		self.flagsDict[activityType].incCount( player, time.localtime() )

	def remove( self, player, activityType ):
		"""
		"""
		self.flagsDict[activityType].reset( player )

	def initAllActivitysJoinState( self, player ):
		"""
		"""
		for value in self.flagsDict.itervalues():
			value.initRecord( player, time.localtime() )

	def initActivityJoinState( self, player, activityType ):
		"""
		"""
		self.flagsDict[activityType].initRecord( player, time.localtime() )

	def queryActivityJoinState( self, player, activityType ):
		"""
		"""
		if not player.hasInitActivityFlag():
			player.client.onStatusMessage( csstatus.ROLE_RECORD_INIT_FAILED, "" )
			ERROR_MSG( "Role(%i)'s roleRecord init Failed!"%player.databaseID )
			assert 0
		if self.flagsDict[activityType].isValidFor( player ):
			return csdefine.ACTIVITY_CAN_JOIN
		else :
			return csdefine.ACTIVITY_CAN_NOT_JOIN


g_activityRecordMgr = ActivityRecordMgr()



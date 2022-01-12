# -*- coding: gb18030 -*-


#################################################################################################################################
#测试代码
#################################################################################################################################

import cPickle
import ActivityRecordMgr as ajm
reload( ajm )
import BigWorld
import csdefine
import Const
import time


def test( player=None ):
	"""
	"""
	if player is None:
		player = BigWorld.createEntity("Role",1,(0,0,0),(0,0,0),{"raceclass":1<<4})

	testCountInc( player )

	testInSameDateCase( player )

	testInDifferentDateButSameWeekCase( player )

	testInDifferentWeekCase( player )

	testDifferentAreaCase( player )


	print "---------------ActivityFlags test OK-----------------------"


def testCountInc( player ):
	"""
	测试正常的次数增加，导致标志变化的用例
	"""
	player.initRoleRecord( cPickle.dumps( [], 2 ) )
	player.onRoleRecordInitFinish()
	for iType in ajm.g_activityRecordMgr.flagsDict:
		ins = ajm.g_activityRecordMgr.flagsDict[iType]
		assert ( not ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN or ins.maxCount == 0  )
		for i in xrange(0,ins.maxCount):
			ajm.g_activityRecordMgr.add( player, iType )
		ajm.g_activityRecordMgr.initActivityJoinState( player, iType )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN


def testInSameDateCase( player ):
	"""测试同一天初始化多次的情况"""
	player.initRoleRecord( cPickle.dumps( [], 2 ) )
	player.onRoleRecordInitFinish()
	for iType,ins in ajm.g_activityRecordMgr.flagsDict.iteritems():
		for i in xrange(ins.maxCount):
			ajm.g_activityRecordMgr.add( player, iType )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN
		ajm.g_activityRecordMgr.initActivityJoinState( player, iType )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN

	player.initRoleRecord( cPickle.dumps( [], 2 ) )
	player.onRoleRecordInitFinish()
	for iType in ajm.g_activityRecordMgr.flagsDict:
		ins = ajm.g_activityRecordMgr.flagsDict[iType]
		ins.record( player, time.localtime(), 0 )
		ins.updateActFlag( player, 0 )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_JOIN or ins.maxCount == 0
		ajm.g_activityRecordMgr.initActivityJoinState( player, iType )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_JOIN or ins.maxCount == 0


def testInDifferentDateButSameWeekCase( player ):
	"""测试同一周但是不同日期的情况"""
	date1 = (2012, 12, 3, 20, 50, 26, 0, 338, 0)		# 2012.12.03，和time.localtime()得到的格式一样
	date2 = (2012, 12, 4, 20, 50, 26, 0, 339, 0)		# 2012.12.04
	player.initRoleRecord( cPickle.dumps( [], 2 ) )
	player.onRoleRecordInitFinish()
	for iType in ajm.g_activityRecordMgr.flagsDict:
		ins = ajm.g_activityRecordMgr.flagsDict[iType]
		ins.initRecord( player, date1 )
		for i in xrange(ins.maxCount):
			ins.incCount( player, date1 )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN
		ins.initRecord( player, date2 )
		if isinstance( ins, ajm.DailyActRecord ):
			assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_JOIN or ins.maxCount == 0
		elif isinstance( ins, ajm.WeeklyActRecord ):
			assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN


def testInDifferentWeekCase( player ):
	"""测试不同周的情况"""
	date1 = (2012, 12, 3, 20, 50, 26, 0, 338, 0)		# 2012.12.03，和time.localtime()得到的格式一样
	date2 = (2012, 12, 10, 20, 50, 26, 0, 345, 0)		# 2012.12.10
	player.initRoleRecord( cPickle.dumps( [], 2 ) )
	player.onRoleRecordInitFinish()
	for iType in ajm.g_activityRecordMgr.flagsDict:
		ins = ajm.g_activityRecordMgr.flagsDict[iType]
		ins.initRecord( player, date1 )
		for i in xrange(ins.maxCount):
			ins.incCount( player, date1 )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN
		ins.initRecord( player, date2 )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_JOIN or ins.maxCount == 0


def testDifferentAreaCase( player ):
	"""测试不同区域的情况"""
	date = (2012, 12, 10, 20, 50, 26, 0, 345, 0)		# 2012.12.10
	player.initRoleRecord( cPickle.dumps( [], 2 ) )
	player.onRoleRecordInitFinish()
	player.setTemp("AREA_ACT_RECORD_SPACELABEL", 'feng_ming_cheng')
	for iType in ajm.g_activityRecordMgr.flagsDict:
		ins = ajm.g_activityRecordMgr.flagsDict[iType]
		ins.initRecord( player, date )
		for i in xrange(ins.maxCount):
			ins.incCount( player, date )
		assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN
	player.setTemp("AREA_ACT_RECORD_SPACELABEL", 'xin_ban_xin_shou_cun')
	for iType in ajm.g_activityRecordMgr.flagsDict:
		ins = ajm.g_activityRecordMgr.flagsDict[iType]
		if isinstance( ins, ajm.AreaActRecord ):
			assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_JOIN or ins.maxCount == 0
		else:
			assert ajm.g_activityRecordMgr.queryActivityJoinState( player, iType ) == csdefine.ACTIVITY_CAN_NOT_JOIN

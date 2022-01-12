# -*- coding: gb18030 -*-

import BigWorld
import CrondScheme
import event.EventCenter as ECenter
from Time import Time
import cschannel_msgs

ONE_MINUTE_IN_SCEOND 	= 60 		#单位：秒
ONE_HOUR_IN_SCEOND 	= 3600			#单位：秒
UPDATE_TIME = 24						#24 点
ONE_HOUR_IN_MINUTE = 60				# 单位： 分

NOTIFY_TIME	= 5						#通知时间

STATE_NOT_START	= 0					#没开始
STATE_STARTING	= 1					#进行中
STATE_END		= 2					#结束

class ActivitySchedule:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self._timerID = 0
		self._schemes = []
		self._todayActivityTable 	= {}		#今天的活动

												#such as :	key: 	name
												#			value:	[ hour, minute, name, isStart, des,condition,area, state ]
		#state:  	有三中, (0:已结束), (1:在进行), (2:还没进行)
		self._startingActivityInfo 	= {}		#开启的活动
												#such as :  key:    name
												#			value:  1
		self._endActivityInfo 		= {}		#结束的活动

	def add( self, activityName, isStart, des, cmd, condition, area, activityType, line, star, persist ):
		"""
		"""
		scheme = CrondScheme.clientScheme()
		if not scheme.init( cmd ):
			return
		"""
		wdays = []								#为了应对 scheme 对周1-周7 与 time.time()不一样引起的多余复杂性，而需要多写的代码。
		for i in scheme._dateScheme._wdays:
			wdays.append( i + 1 )

		scheme._dateScheme._wdays = wdays
		"""
		des = des.replace('RacehorseManager_start',cmd )
		self._schemes.append( ( scheme, activityName, isStart, des, condition, area, activityType, line, star, persist ) )

	def start( self ):
		"""
		开始今天的活动数据处理机制
		"""
		self.stop()													#清理今天的活动数据

		"""
		由于策划需要的活动数据 是从 早上4点到次日早上4点。
		所以在取数据的时候,就需要考虑是取昨天早上4点到今天早上4点的数据,还是今天早上4点到明天早上4点的数据。

		以下的处理主要是取数据。
		"""
		self.calTodaysTable()
		#数据取玩,开始每一分钟一次的活动时间检测。
		self.process()


	def calTodaysTable( self ):
		"""
		计算今天要的活动数据。一天是一个 UPDATE_TIME 到下一个UPDATE_TIME之间
		"""
		tuple1,tuple2 = self.calVirTodayTuple()

		for iScheme in self._schemes:
			table = iScheme[0].getDayTable( tuple1[0], tuple1[1], tuple1[2] )
			self.addTodayActivityData( table, iScheme[1], iScheme[2], iScheme[3], iScheme[4], iScheme[5], iScheme[6], iScheme[7], iScheme[8], iScheme[9], True )

			table = iScheme[0].getDayTable( tuple2[0], tuple2[1], tuple2[2] )
			self.addTodayActivityData( table, iScheme[1], iScheme[2], iScheme[3], iScheme[4], iScheme[5], iScheme[6], iScheme[7], iScheme[8], iScheme[9], False )



	def addTodayActivityData( self, hourTable, name, isStart, des, condition, area, activityType, line, star, persist, isLastDay ):
		"""
		"""
		for iHourTable in hourTable:
			if isLastDay:
				if Time.localtime()[3] >= UPDATE_TIME :
					if name == cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU or name == cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU:
						self._todayActivityTable[len(self._todayActivityTable)] = [ iHourTable[0], iHourTable[1], name, isStart, des, condition, area, activityType, line, star, persist, STATE_STARTING ]
						continue
				if iHourTable[0] < UPDATE_TIME:
					continue
			else:
				if Time.localtime()[3] < UPDATE_TIME :
					if name == cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU or name == cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU:
						self._todayActivityTable[len(self._todayActivityTable)] = [ iHourTable[0], iHourTable[1], name, isStart, des, condition, area, activityType, line, star, persist, STATE_STARTING ]
						continue
				if iHourTable[0] >= UPDATE_TIME:
					continue

			if name == cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU or name == cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU:
				continue

			self._todayActivityTable[len(self._todayActivityTable)] = [ iHourTable[0], iHourTable[1], name, isStart, des, condition, area, activityType, line, star, persist, STATE_NOT_START ]

	def calVirTodayTuple( self ):
		"""
		计算,游戏需要的一天的时间。
		因为,游戏需要显示的是 一个 UPDATE_TIME 到下一个UPDATE_TIME 之间的时间。
		所以,返回的是两天的tuples
		"""
		curTimeTuple = Time.localtime()
		curtime = Time.time()
		if curTimeTuple[3] < UPDATE_TIME:
			tuple1 = Time.localtime( curtime - ONE_HOUR_IN_SCEOND * 24 )
			tuple2 = curTimeTuple
		else:
			tuple2 = Time.localtime( curtime + ONE_HOUR_IN_SCEOND * 24 )
			tuple1 = curTimeTuple

		return tuple1,tuple2

	def process( self ):
		"""
		每一分钟的数据更新
		"""
		timeTable = Time.localtime()
		curDayMinute = self.calCurrentMinute( timeTable[3], timeTable[4] ) 										#curDayMinute 当前天数是第几分钟。 从早上4点,到第二天4点间计算。
		for i,iValue in self._todayActivityTable.iteritems():

			hour 	= iValue[0]
			minute 	= iValue[1]
			name 	= iValue[2]
			isStart = iValue[3]
			des 	= iValue[4]
			condition = iValue[5]
			area 	= iValue[6]
			activityType 	= iValue[7]
			line 	= iValue[8]
			star 	= iValue[9]
			persist = iValue[10]
			state 	= iValue[11]


			if state == STATE_NOT_START:
				activityDayMinute = self.calCurrentMinute( hour, minute )
				if activityDayMinute < curDayMinute:								#如果这条记录需要被处理
					if isStart:
						if self._startingActivityInfo.has_key( name ):
							self._startingActivityInfo[name].add( i )
						else:
							self._startingActivityInfo[name] = set( [ i ] )
						self._todayActivityTable[i][11] = STATE_STARTING
					else:
						if self._endActivityInfo.has_key( name ):
							self._endActivityInfo[name].add( i )
						else:
							self._endActivityInfo[name] = set([ i ])

				if activityDayMinute > curDayMinute and activityDayMinute < curDayMinute + NOTIFY_TIME:
					if isStart:
						ECenter.fireEvent( "EVT_ON_ACTIVITY_SOON_START" )
		#						#print name,"快要开始了"
					else:
						ECenter.fireEvent( "EVT_ON_ACTIVITY_SOON_END")
		#						#print name,"快要结束了"

		for iName,iValue in self._endActivityInfo.iteritems():
			endDM = 0
			for i in self._endActivityInfo[iName]:
				endHour = self._todayActivityTable[i][0]
				endMinute = self._todayActivityTable[i][1]
				dm = self.calCurrentMinute( endHour, endMinute )
				if endDM <= dm:
					endDM = dm

			startList = []
			if iName not in self._startingActivityInfo:
				continue
			for j in self._startingActivityInfo[iName]:
				startHour   = self._todayActivityTable[j][0]
				startMinute = self._todayActivityTable[j][1]
				if endDM >= self.calCurrentMinute( startHour, startMinute ):
					startList.append( j )
					self._todayActivityTable[j][11] = STATE_END
			for iR in startList:
				self._startingActivityInfo[iName].remove( iR )
				if len(self._startingActivityInfo[iName]) == 0:
					del self._startingActivityInfo[iName]

		if timeTable[3] == UPDATE_TIME and timeTable[4] == 0:
			self._timerID = BigWorld.callback( ONE_MINUTE_IN_SCEOND, self.start )
		else:
			self._timerID = BigWorld.callback( ONE_MINUTE_IN_SCEOND, self.process )

	def calCurrentMinute( self, hour, minute ):
		"""
		计算当前天数是第几分钟。 根据UPDATE_TIME 作为起始点
		"""

		totalMinute = hour * ONE_HOUR_IN_MINUTE + minute - UPDATE_TIME * ONE_HOUR_IN_MINUTE
		if hour < UPDATE_TIME:
			totalMinute += 24 * ONE_HOUR_IN_MINUTE
		return totalMinute

	def getActivityStateInfo( self, state ):
		"""
		"""
		oldInfo = []
		newInfo = []
		for value in self._todayActivityTable.itervalues():
			if value[11] == state and value[3] == True:
				oldInfo.append( value )

		#[ hour, minute, name, isStart, des, state ]

		while len( oldInfo ) > 0 :
			a = 999
			b = 999
			k = 0
			for index, value in enumerate( oldInfo ):
				if value[0] < a or ( value[0] == a and value[1] < b ):
					a = value[0]
					b = value[1]
					k = index
			newInfo.append( oldInfo.pop(k) )
#		for i in newInfo:
#			#print i[0],'点',i[1],'分', i[2], '描述', i[4]
		return newInfo

	def stop( self ):
		"""
		"""
		BigWorld.cancelCallback( self._timerID )
		self._timerID = 0
		self._todayActivityTable 	= {}
		self._startingActivityInfo 	= {}
		self._endActivityInfo 	= {}


	def clean( self ):
		"""
		"""
		self._schemes = []

	def calDayTuple( self, dayMinus ):
		"""
		计算,游戏需要的一天的时间。
		因为,游戏需要显示的是 一个 UPDATE_TIME 到下一个UPDATE_TIME 之间的时间。
		所以,返回的是两天的tuples
		"""
		secondsInDay = ONE_HOUR_IN_SCEOND * 24
		curtime = Time.time() + dayMinus * secondsInDay
		curTimeTuple = Time.localtime( curtime )
		if curTimeTuple[3] < UPDATE_TIME:
			tuple1 = Time.localtime( curtime -  secondsInDay )
			tuple2 = curTimeTuple
		else:
			tuple2 = Time.localtime( curtime + secondsInDay )
			tuple1 = curTimeTuple

		return tuple1,tuple2


	def getDayActivityTable( self, dayMinus ):
		"""
		获得某一天的活动数据。
		dayMinus：
				@des: 与今天相差几天。
					如： 昨天： dayMinus = -1
						 明天： dayMinus = 1
			
		"""
		tuple1,tuple2 = self.calDayTuple( dayMinus )
		
		actTables = {}
		isOutOfData = 2
		if dayMinus > 0:
			isOutOfData = 0
		if dayMinus == 0:
			return {}
		for iScheme in self._schemes:
			hourTable = iScheme[0].getDayTable( tuple1[0], tuple1[1], tuple1[2] )
			self.getDayActivtyData( actTables, hourTable, iScheme[1], iScheme[2], iScheme[3], iScheme[4], iScheme[5], iScheme[6], iScheme[7], iScheme[8], iScheme[9], True, isOutOfData )

			hourTable = iScheme[0].getDayTable( tuple2[0], tuple2[1], tuple2[2] )
			self.getDayActivtyData( actTables, hourTable, iScheme[1], iScheme[2], iScheme[3], iScheme[4], iScheme[5], iScheme[6], iScheme[7], iScheme[8], iScheme[9], False, isOutOfData )
		
		return actTables

	def getDayActivtyData( self, actTables, hourTable, name, isStart, des, condition, area, activityType, line, star, persist, isLastDay, isOutOfData = 0 ):
		"""
		"""
		if not isStart:
			return actTables
		dayActivityTable = actTables
		for iHourTable in hourTable:
			if isLastDay:
				if Time.localtime()[3] >= UPDATE_TIME :
					if name == cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU or name == cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU:
						dayActivityTable[len(dayActivityTable)] = [ iHourTable[0], iHourTable[1], name, isStart, des, condition, area, activityType, line, star, persist, isOutOfData ]
						continue
				if iHourTable[0] < UPDATE_TIME:
					continue
			else:
				if Time.localtime()[3] < UPDATE_TIME :
					if name == cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU or name == cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU:
						dayActivityTable[len(dayActivityTable)] = [ iHourTable[0], iHourTable[1], name, isStart, des, condition, area, activityType, line, star, persist, isOutOfData ]
						continue
				if iHourTable[0] >= UPDATE_TIME:
					continue

			if name == cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU or name == cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU:
				continue
			dayActivityTable[len(dayActivityTable)] = [ iHourTable[0], iHourTable[1], name, isStart, des, condition, area, activityType, line, star, persist, isOutOfData ]

		return actTables


g_activitySchedule = ActivitySchedule()
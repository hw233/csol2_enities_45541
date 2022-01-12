# -*- coding: gb18030 -*-

import BigWorld
import CrondScheme
import event.EventCenter as ECenter
from Time import Time
import cschannel_msgs

ONE_MINUTE_IN_SCEOND 	= 60 		#��λ����
ONE_HOUR_IN_SCEOND 	= 3600			#��λ����
UPDATE_TIME = 24						#24 ��
ONE_HOUR_IN_MINUTE = 60				# ��λ�� ��

NOTIFY_TIME	= 5						#֪ͨʱ��

STATE_NOT_START	= 0					#û��ʼ
STATE_STARTING	= 1					#������
STATE_END		= 2					#����

class ActivitySchedule:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self._timerID = 0
		self._schemes = []
		self._todayActivityTable 	= {}		#����Ļ

												#such as :	key: 	name
												#			value:	[ hour, minute, name, isStart, des,condition,area, state ]
		#state:  	������, (0:�ѽ���), (1:�ڽ���), (2:��û����)
		self._startingActivityInfo 	= {}		#�����Ļ
												#such as :  key:    name
												#			value:  1
		self._endActivityInfo 		= {}		#�����Ļ

	def add( self, activityName, isStart, des, cmd, condition, area, activityType, line, star, persist ):
		"""
		"""
		scheme = CrondScheme.clientScheme()
		if not scheme.init( cmd ):
			return
		"""
		wdays = []								#Ϊ��Ӧ�� scheme ����1-��7 �� time.time()��һ������Ķ��ิ���ԣ�����Ҫ��д�Ĵ��롣
		for i in scheme._dateScheme._wdays:
			wdays.append( i + 1 )

		scheme._dateScheme._wdays = wdays
		"""
		des = des.replace('RacehorseManager_start',cmd )
		self._schemes.append( ( scheme, activityName, isStart, des, condition, area, activityType, line, star, persist ) )

	def start( self ):
		"""
		��ʼ����Ļ���ݴ������
		"""
		self.stop()													#�������Ļ����

		"""
		���ڲ߻���Ҫ�Ļ���� �Ǵ� ����4�㵽��������4�㡣
		������ȡ���ݵ�ʱ��,����Ҫ������ȡ��������4�㵽��������4�������,���ǽ�������4�㵽��������4������ݡ�

		���µĴ�����Ҫ��ȡ���ݡ�
		"""
		self.calTodaysTable()
		#����ȡ��,��ʼÿһ����һ�εĻʱ���⡣
		self.process()


	def calTodaysTable( self ):
		"""
		�������Ҫ�Ļ���ݡ�һ����һ�� UPDATE_TIME ����һ��UPDATE_TIME֮��
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
		����,��Ϸ��Ҫ��һ���ʱ�䡣
		��Ϊ,��Ϸ��Ҫ��ʾ���� һ�� UPDATE_TIME ����һ��UPDATE_TIME ֮���ʱ�䡣
		����,���ص��������tuples
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
		ÿһ���ӵ����ݸ���
		"""
		timeTable = Time.localtime()
		curDayMinute = self.calCurrentMinute( timeTable[3], timeTable[4] ) 										#curDayMinute ��ǰ�����ǵڼ����ӡ� ������4��,���ڶ���4�����㡣
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
				if activityDayMinute < curDayMinute:								#���������¼��Ҫ������
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
		#						#print name,"��Ҫ��ʼ��"
					else:
						ECenter.fireEvent( "EVT_ON_ACTIVITY_SOON_END")
		#						#print name,"��Ҫ������"

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
		���㵱ǰ�����ǵڼ����ӡ� ����UPDATE_TIME ��Ϊ��ʼ��
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
#			#print i[0],'��',i[1],'��', i[2], '����', i[4]
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
		����,��Ϸ��Ҫ��һ���ʱ�䡣
		��Ϊ,��Ϸ��Ҫ��ʾ���� һ�� UPDATE_TIME ����һ��UPDATE_TIME ֮���ʱ�䡣
		����,���ص��������tuples
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
		���ĳһ��Ļ���ݡ�
		dayMinus��
				@des: ��������졣
					�磺 ���죺 dayMinus = -1
						 ���죺 dayMinus = 1
			
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
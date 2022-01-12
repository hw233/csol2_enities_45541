# -*- coding: gb18030 -*-
#
# $Id: TimeString.py, 2013-11-04 08:50:50 lzh Exp $
import time
class HourMinute():
	"""8:00 is a string for initialization ."""
	def __init__(self, string):
		self._hour = int(string.split(":")[0])
		self._minute = int(string.split(":")[1])
		
	def getHour(self):
		return self._hour
		
	def getMinute(self):
		return self._minute
		
	def getHourMinute(self):
		return (self._hour * 60) + self._minute

class Period(HourMinute):
	"""
	"8:00-9:00" is a string for initialization .
	"""
	def __init__(self, string):
		self._time1 = HourMinute(string.split("-")[0])
		self._time2 = HourMinute(string.split("-")[1])
		
	def getStart(self):
		return self._time1.getHourMinute()
		
	def getEnd(self):
		return self._time2.getHourMinute()
		
	def inPeriod(self, localtime):
		#localtime  = (hour * 60) + minute
		if self.getStart() <= localtime <= self.getEnd():
			return True
		return False
		
class WeekTime(Period):
	""" 
	"1|8:00-9:00 " is a string for initialization .
	"""
	def __init__(self, string):
		self._week = int(string[0])
		self._period = Period(string[2:])
	
	def getStart(self):
		return (self._week * 24 * 60) + self._period.getStart()
		
	def getEnd(self):
		return (self._week * 24 * 60) + self._period.getEnd()
		
	def inWeekTime(self, localtime):
		#localtime = week * 1440 + hour * 60 + minute
		if self.getStart() <= localtime <= self.getEnd():
			return True
		return False

class TimeString():
	def __init__(self, string=""):
		if len(string) > 0 and string[-1] == ";":
			self._timestring = string[:-1]  #去掉字符串尾的分号
		self._timestring = string
		
	def timeCheck(self):
		if len(self._timestring) == 0:
			return True
		timestring = time.localtime()
		week = timestring[6] #周几， 0表示星期一，6表示星期天
		hour = timestring[3]  #几时
		minute = timestring[4] #几分
		hourminute = (hour * 60) + minute
		weekhourminute = (week * 24 * 60) + hourminute	
		weekdays = []
		if len(self._timestring.replace(";","")) <= 7 : #周几定时开启 如1;2;3
			days = self._timestring.split(";")
			for day in days :
				weekdays.append(int(day))
			if week in weekdays:
				return True
			
		if ("-" in self._timestring) and ("|" not in self._timestring):   #每天定时开放 如8:00-9:00
			periods = self._timestring.split(";")
			for period in periods:
				period = Period(period)
				if period.inPeriod(hourminute):
					return True
					
		if ("-" in self._timestring) and ("|" in self._timestring):		#周几定时开放 如"1|12:00-14:00;3|15:00-16:00"
			periods = self._timestring.split(";")
			for period in periods:
				period = WeekTime(period)
				if period.inWeekTime(weekhourminute):
					return True
		
		return False 
				

	
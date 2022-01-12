# -*- coding: gb18030 -*-

from __future__ import with_statement
from config import Datas
from config import ActivityDatas

RESULT_FILE = "result.txt"

class LogAnalyse:
	"""
	"""
	_instance = None
	
	def __init__( self ):
		self._instance = self
		
		self.logKeyList = []			#日志记录
		self.configDataList = Datas
		self.copyConfigDataList = self.configDataList.copy()
		self.exitLogList = {}			#存在日志记录的动作列表
		self.notExitLogList = {}		#不存在日志记录的动作列表
		
		self.activityLogKeyList = []
		self.aConfigData = ActivityDatas
		self.copyAconfigData = self.aConfigData.copy()
		self.exitActivityLog = {}
		self.notExitActivityLog = {}
	
	@staticmethod
	def instance():
		"""
		"""
		if LogAnalyse._instance is None:
			LogAnalyse._instance = LogAnalyse()
		return LogAnalyse._instance
		
	def logLoder( self, file ):
		"""
		从日志文件中提取写日志的信息，并生成相应的日志记录列表[[ action1,param1,param2,...],[ action2,param1,param2 ],... ]
		"""
		f = open( file,'r')
		temp = []
		self.logKeyList = []
		for line in f:
			if line.find("mysql$") != -1:
				temp = line.split("||")
				fKey = temp.pop(0)		#去掉无用的第一个元素
				#去掉最后一个元素的"/n"
				lastElement = temp.pop( len(temp)-1 )
				temp.append( lastElement[ 0:len( lastElement )-1 ] )
				e = fKey.split("$")
				if e[1] != "31":
					self.logKeyList.append( temp )
				else:				#如果为活动日志
					self.activityLogKeyList.append( temp )
		f.close()
	
	def buildResult( self ):
		"""
		根据配置与日志记录列表比对，得出没有记录和已经记录的action信息
		"""
		for action,paramDict in self.configDataList.iteritems():
			for logKey in self.logKeyList:
				if action == logKey[0]:
					if len(paramDict) == 0:							# 不需要分析action的参数
						if not self.exitLogList.has_key( action ):
							self.exitLogList[action] = {}
							self.copyConfigDataList.pop( action )
					else:
						for index,value in paramDict.iteritems():
							if logKey[index] in value:
								if logKey[index] in self.copyConfigDataList[action][index]:
									value.remove( logKey[index] )
									if len(value) == 0:
										self.copyConfigDataList.pop(action)
									else:
										self.copyConfigDataList[action][index] = value
								if not self.exitLogList.has_key( action ):
									self.exitLogList[action] = {}
									self.exitLogList[action][index] = [ logKey[index] ]
								else:
									self.exitLogList[action][index].append( logKey[index] )
		self.notExitLogList = self.copyConfigDataList
	
	def buildActivityResult( self ):
		for activity,actionList in self.copyAconfigData.iteritems():
			for i in self.activityLogKeyList:
				if i[0] == activity and i[1] in actionList:
					if not self.exitActivityLog.has_key( activity ):
						self.exitActivityLog[activity] = [ i[1] ]
					else:
						self.exitActivityLog[activity].append( i[1] )
					if i[1] in self.copyAconfigData[activity]:
						self.copyAconfigData[activity].remove( i[1] )
		self.notExitActivityLog = self.copyAconfigData
		
	def createString( self,dict ):
		"""
		将字典转化成规范的字符串
		"""
		resultString = ""
		i = 1
		for k,v in dict.iteritems():
			resultString += str(i)
			resultString += ": "
			if len(v) == 0:
				resultString += k
				resultString += "\n\n"
			else:
				resultString += k
				resultString += ":"
				resultString += str(v)
				resultString += "\n\n"
			i += 1
		
		return resultString
		
	def printResult( self ):
		"""
		输出结果
		"""
		f=open(RESULT_FILE,'w')
		resultStr = "有记录的日志:\n" + self.createString( self.exitLogList ) + "\n" + "记录为零的日志:\n" + self.createString( self.notExitLogList)
		resultStr += "\n\n"
		resultStr += "有记录的活动日志:\n" + self.createString( self.exitActivityLog ) + "\n" + "记录为零的活动日志:\n" + self.createString( self.notExitActivityLog)
		f.write( resultStr )
		
		
	def analyse( self, file ):
		self.logLoder( file )
		self.buildResult()
		self.buildActivityResult()
		self.printResult()
		
instance = LogAnalyse.instance()
instance.analyse("logDir/242.log")

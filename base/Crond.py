# -*- coding: gb18030 -*-


import time
import sys
import BigWorld
from bwdebug import *
from CrondScheme import *
import Const
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()


AUTO_START_CHECK_TIME = 60						#当前距离活动结束时间需要比这个值大，才自动开启活动
HANDLE_AUTO_START_CBID = 123					#处理自动启动活动timerID
class CrondScheme:
	"""
	"""
	def __init__( self, schemeString, schemeInstance, mailbox, callbackName, activeTimes = -1 ):
		"""
		"""
		self.schemeString = schemeString
		self.schemeInstance = schemeInstance
		self.mailbox = mailbox
		self.callbackName = callbackName
		self.nextTime = 0						# 下一次触发的时间
		self.activeTimes = activeTimes			# 触发次数；<= -1 不限次数；== 0 保留，不可用；>= 0 指定次数


class Crond( BigWorld.Base ):
	def __init__( self ):
		"""
		"""
		self._timerID = 0
		# 计划列表，like as [ instance of CrondScheme, ... ]
		self._schemes = []
		self.autoStartList = {}
		self.registerGlobally( "Crond", self._onRegisterManager )
		self.addTimer( 300, 0, HANDLE_AUTO_START_CBID )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register Crond Fail!" )
			# again
			self.registerGlobally( "Crond", self._onRegisterManager )
		else:
			BigWorld.globalData["Crond"] = self		# 注册到所有的服务器中
			INFO_MSG("Crond Create Complete!")

	def _addAndSortScheme( self, crondScheme ):
		"""
		加入一个scheme，并且按触发时间从小到大的放
		@return: 返回插入的位置
		"""
		t = crondScheme.nextTime
		schemes = self._schemes
		
		fault = True
		for i in xrange( len( schemes ) ):
			if t <= schemes[i].nextTime:
				schemes.insert( i, crondScheme )
				fault = False
				break
		if fault:
			schemes.append( crondScheme )
			return len( schemes ) - 1
		return i

	def addScheme( self, schemeString, baseMailBox, callbackName ):
		"""
		defined method.
		此接口的存在是为了兼容旧的使用模式。
		@param timeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		@param baseMailbox: MAILBOX, see also callbackName param
		@param callbackName: string, 当时间到达时将使用此名字从baseMailbox参数中获取回调接口并调用。
		"""
		self.addSchemeEx( schemeString, baseMailBox, callbackName, -1 )

	def addSchemeEx( self, schemeString, baseMailBox, callbackName, activeTimes ):
		"""
		defined method.
		@param timeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		@param baseMailbox: MAILBOX, see also callbackName param
		@param callbackName: string, 当时间到达时将使用此名字从baseMailbox参数中获取回调接口并调用。
		@parma activeTimes: int, 执行几次后失效，详看self.activeTimes变量说明。
		"""
		scheme = Scheme()
		if not scheme.init( schemeString ):
			return

		cs = CrondScheme( schemeString, scheme, baseMailBox, callbackName, activeTimes )
		year,month,day,hour,minute = time.localtime()[:5]
		nextMinute = minute + 1					#这地方需要从下一分中开始计算，否则如果当前分钟有活动A， 则这个结果会返回A的时间，这会出错的
		cs.nextTime = scheme.calculateNext( year,month,day,hour,nextMinute )
		if self._addAndSortScheme( cs ) == 0:
			self.stop()
			self.start()

	def removeScheme( self, schemeString, baseMailBox, callbackName ):
		"""
		defined method.
		移除一个匹配的时间计划。
		@param timeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		"""
		for index, s in enumerate( self._schemes ):
			if s.schemeString == schemeString and s.mailbox.id == baseMailBox.id and s.callbackName == callbackName:
				del self._schemes[index]
				if len( self._schemes ) == 0:
					self.stop()
				return

	def addAutoStartScheme( self, taskName, baseMailBox, callbackName ):
		"""
		define method
		处理一些需要在服务器启动这个时刻刚好卡在一些活动运行时间中，需要被开启的活动。
		"""
		self.autoStartList[taskName] = { "mailbox": baseMailBox, "funcName": callbackName }


	def onAutoStartScheme( self ):
		"""
		"""
		for i in self.autoStartList:
			baseMailBox = self.autoStartList[i]["mailbox"]
			callbackName = self.autoStartList[i]["funcName"]
			presistMinute = g_CrondDatas.getTaskPersist( i.lower() )
			
			
			"""
			计算方法：
				1: 把当前时间 T 往前推。推的大小为 持续时间。得到一个时间点 A。
				2: 从时间点A开始计算，看某个活动下一次开启的时间是多少。记录为 R。
				3: 如果R小于 T， 则当前正在活动中。
				4: AUTO_START_CHECK_TIME 的作用主要是避免活动刚开启，就关闭而引起问题。意思是说当前时间如果
					距离结束这个活动的时间比这个值小，那活动就不开启。
			"""
			year, month, day, hour, minute = time.localtime( time.time() - presistMinute * 60 )[:5]
			curTime = time.time()
			for cmd in g_CrondDatas.getTaskCmds( i ):
				scheme = Scheme()
				scheme.init( cmd )
				nextTime = scheme.calculateNext( year, month, day, hour, minute )
				if nextTime < ( curTime - AUTO_START_CHECK_TIME ):
					try:
						callback = getattr( baseMailBox, callbackName )
					except AttributeError, errstr:
						ERROR_MSG( errstr, cmd, callbackName )
						continue
					try:
						callback()
					except:
						EXCEHOOK_MSG( "Crond except" )
						continue


	def recalculateAllSchemeTime( self, year = None, month = None, day = None, hour = None, minute = None ):
		"""
		重新计算所有计划的时间并重新排序。
		如果提供了足够的参数，则以参数指定的时间开始为基础，
		否则使用当前时间为基础。
		注：此接口代码中当前没有使用，主要用于测试
		"""
		if year is None or month is None or day is None or hour is None or minute is None:
			year, month, day, hour, minute = time.localtime()[:5]
		for s in self._schemes:
			s.nextTime = s.schemeInstance.calculateNext( year, month, day, hour, minute )
		self._schemes.sort( key = lambda x: x.nextTime )

	def start( self ):
		"""
		启动一次监控器
		"""
		assert self._timerID == 0
		assert len( self._schemes ) != 0
		assert self._schemes[0].nextTime - time.time() + 1 > 0
		
		# 以最小的任务时间为触发时间
		# 时间计算加上1的偏移是为了避免浮点计算上的误差引起的timer到了但实际时间并没有到的问题
		self._timerID = self.addTimer( self._schemes[0].nextTime - time.time() + 1, 0 )

	def stop( self ):
		"""
		停止监控器，停止时，不改变任何注册的Scheme，仅仅是不再定时检测Scheme。
		"""
		if self._timerID != 0:
			self.delTimer( self._timerID )
			self._timerID = 0

	def onTimer( self, id, userArg ):
		"""
		>>> time.localtime()
		(2009, 2, 2, 11, 49, 59, 0, 33, 0) -> year, month, day, hour, minute, second, wday, yday, isdst
		"""
		if HANDLE_AUTO_START_CBID == userArg:
			self.onAutoStartScheme()
			return
		
		t = time.time()
		year, month, day, hour, minute, second, wday, yday, isdst = time.localtime( t )
		nextMinute = minute + 1
		removedList = []	# 用于记录过期的scheme，以统一清除
		# 检查所有时间计划，并回调符合条件的时间计划任务。
		for index in xrange( len( self._schemes ) ):
			s = self._schemes[index]
			# 因为schemes列表是排过序的，
			# 因此只要第一个时间不匹配就可以中断循环。
			if t < s.nextTime:
				break
			
			try:
				DEBUG_MSG( "crond[%s][%s] : %dyear, %dmonth, %dday, %dhour, %dminute, %dsecond, %dwday, %dyday, %disdst" % ( repr( s.mailbox ), s.callbackName, year, month, day, hour, minute, second, wday, yday, isdst ) )
			except:
				EXCEHOOK_MSG( "Crond log except" )
				# 如果写日志出错了，我们仅仅记录一下，下面继续执行

			# 无论下面的执行结果是什么，
			# 我们都必须先重新计算已处理scheme的下一次触发时间，
			# 以避免因为异常的原因使scheme的nextTime没有重新计算，
			# 而异致整个crond的触发行为在调用self.start()的时候
			# 被“assert self._schemes[0].nextTime - time.time() + 1 > 0”所中断。
			s.nextTime = s.schemeInstance.calculateNext( year, month, day, hour, nextMinute )
			
			# 无论如何，都先把触发次数先处理掉，
			# 以避免因为下面执行失败而触发次数不增长的情况发生。
			if s.activeTimes > 1:
				s.activeTimes -= 1
			if s.activeTimes == 0:
				removedList.append( index )

			try:
				callback = getattr( s.mailbox, s.callbackName )
			except AttributeError, errstr:
				ERROR_MSG( errstr, s.schemeString, s.callbackName )
				continue
			try:
				callback()
			except:
				EXCEHOOK_MSG( "Crond except" )
				continue

		# 清除已经过期的scheme
		removedList.reverse()
		for index in removedList:
			self._schemes.pop( index )

		# 重新以触发的时间由小到大排序
		self._schemes.sort( key = lambda x: x.nextTime )

		self._timerID = 0
		# 重新开始下一个timer
		self.start()
# Crond.py

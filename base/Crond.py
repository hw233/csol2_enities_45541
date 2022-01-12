# -*- coding: gb18030 -*-


import time
import sys
import BigWorld
from bwdebug import *
from CrondScheme import *
import Const
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()


AUTO_START_CHECK_TIME = 60						#��ǰ��������ʱ����Ҫ�����ֵ�󣬲��Զ������
HANDLE_AUTO_START_CBID = 123					#�����Զ������timerID
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
		self.nextTime = 0						# ��һ�δ�����ʱ��
		self.activeTimes = activeTimes			# ����������<= -1 ���޴�����== 0 �����������ã�>= 0 ָ������


class Crond( BigWorld.Base ):
	def __init__( self ):
		"""
		"""
		self._timerID = 0
		# �ƻ��б�like as [ instance of CrondScheme, ... ]
		self._schemes = []
		self.autoStartList = {}
		self.registerGlobally( "Crond", self._onRegisterManager )
		self.addTimer( 300, 0, HANDLE_AUTO_START_CBID )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register Crond Fail!" )
			# again
			self.registerGlobally( "Crond", self._onRegisterManager )
		else:
			BigWorld.globalData["Crond"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("Crond Create Complete!")

	def _addAndSortScheme( self, crondScheme ):
		"""
		����һ��scheme�����Ұ�����ʱ���С����ķ�
		@return: ���ز����λ��
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
		�˽ӿڵĴ�����Ϊ�˼��ݾɵ�ʹ��ģʽ��
		@param timeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		@param baseMailbox: MAILBOX, see also callbackName param
		@param callbackName: string, ��ʱ�䵽��ʱ��ʹ�ô����ִ�baseMailbox�����л�ȡ�ص��ӿڲ����á�
		"""
		self.addSchemeEx( schemeString, baseMailBox, callbackName, -1 )

	def addSchemeEx( self, schemeString, baseMailBox, callbackName, activeTimes ):
		"""
		defined method.
		@param timeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		@param baseMailbox: MAILBOX, see also callbackName param
		@param callbackName: string, ��ʱ�䵽��ʱ��ʹ�ô����ִ�baseMailbox�����л�ȡ�ص��ӿڲ����á�
		@parma activeTimes: int, ִ�м��κ�ʧЧ���꿴self.activeTimes����˵����
		"""
		scheme = Scheme()
		if not scheme.init( schemeString ):
			return

		cs = CrondScheme( schemeString, scheme, baseMailBox, callbackName, activeTimes )
		year,month,day,hour,minute = time.localtime()[:5]
		nextMinute = minute + 1					#��ط���Ҫ����һ���п�ʼ���㣬���������ǰ�����лA�� ���������᷵��A��ʱ�䣬�������
		cs.nextTime = scheme.calculateNext( year,month,day,hour,nextMinute )
		if self._addAndSortScheme( cs ) == 0:
			self.stop()
			self.start()

	def removeScheme( self, schemeString, baseMailBox, callbackName ):
		"""
		defined method.
		�Ƴ�һ��ƥ���ʱ��ƻ���
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
		����һЩ��Ҫ�ڷ������������ʱ�̸պÿ���һЩ�����ʱ���У���Ҫ�������Ļ��
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
			���㷽����
				1: �ѵ�ǰʱ�� T ��ǰ�ơ��ƵĴ�СΪ ����ʱ�䡣�õ�һ��ʱ��� A��
				2: ��ʱ���A��ʼ���㣬��ĳ�����һ�ο�����ʱ���Ƕ��١���¼Ϊ R��
				3: ���RС�� T�� ��ǰ���ڻ�С�
				4: AUTO_START_CHECK_TIME ��������Ҫ�Ǳ����տ������͹رն��������⡣��˼��˵��ǰʱ�����
					�������������ʱ������ֵС���ǻ�Ͳ�������
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
		���¼������мƻ���ʱ�䲢��������
		����ṩ���㹻�Ĳ��������Բ���ָ����ʱ�俪ʼΪ������
		����ʹ�õ�ǰʱ��Ϊ������
		ע���˽ӿڴ����е�ǰû��ʹ�ã���Ҫ���ڲ���
		"""
		if year is None or month is None or day is None or hour is None or minute is None:
			year, month, day, hour, minute = time.localtime()[:5]
		for s in self._schemes:
			s.nextTime = s.schemeInstance.calculateNext( year, month, day, hour, minute )
		self._schemes.sort( key = lambda x: x.nextTime )

	def start( self ):
		"""
		����һ�μ����
		"""
		assert self._timerID == 0
		assert len( self._schemes ) != 0
		assert self._schemes[0].nextTime - time.time() + 1 > 0
		
		# ����С������ʱ��Ϊ����ʱ��
		# ʱ��������1��ƫ����Ϊ�˱��⸡������ϵ���������timer���˵�ʵ��ʱ�䲢û�е�������
		self._timerID = self.addTimer( self._schemes[0].nextTime - time.time() + 1, 0 )

	def stop( self ):
		"""
		ֹͣ�������ֹͣʱ�����ı��κ�ע���Scheme�������ǲ��ٶ�ʱ���Scheme��
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
		removedList = []	# ���ڼ�¼���ڵ�scheme����ͳһ���
		# �������ʱ��ƻ������ص�����������ʱ��ƻ�����
		for index in xrange( len( self._schemes ) ):
			s = self._schemes[index]
			# ��Ϊschemes�б����Ź���ģ�
			# ���ֻҪ��һ��ʱ�䲻ƥ��Ϳ����ж�ѭ����
			if t < s.nextTime:
				break
			
			try:
				DEBUG_MSG( "crond[%s][%s] : %dyear, %dmonth, %dday, %dhour, %dminute, %dsecond, %dwday, %dyday, %disdst" % ( repr( s.mailbox ), s.callbackName, year, month, day, hour, minute, second, wday, yday, isdst ) )
			except:
				EXCEHOOK_MSG( "Crond log except" )
				# ���д��־�����ˣ����ǽ�����¼һ�£��������ִ��

			# ���������ִ�н����ʲô��
			# ���Ƕ����������¼����Ѵ���scheme����һ�δ���ʱ�䣬
			# �Ա�����Ϊ�쳣��ԭ��ʹscheme��nextTimeû�����¼��㣬
			# ����������crond�Ĵ�����Ϊ�ڵ���self.start()��ʱ��
			# ����assert self._schemes[0].nextTime - time.time() + 1 > 0�����жϡ�
			s.nextTime = s.schemeInstance.calculateNext( year, month, day, hour, nextMinute )
			
			# ������Σ����ȰѴ��������ȴ������
			# �Ա�����Ϊ����ִ��ʧ�ܶ��������������������������
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

		# ����Ѿ����ڵ�scheme
		removedList.reverse()
		for index in removedList:
			self._schemes.pop( index )

		# �����Դ�����ʱ����С��������
		self._schemes.sort( key = lambda x: x.nextTime )

		self._timerID = 0
		# ���¿�ʼ��һ��timer
		self.start()
# Crond.py

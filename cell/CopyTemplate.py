# -*- coding: gb18030 -*-

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
from Function import Functor
from bwdebug import WARNING_MSG,ERROR_MSG
# ------------------------------------------------
# from cell
from SpaceCopy import SpaceCopy
import Const

# ------------------------------------------------


class CopyTemplate( SpaceCopy ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.copyUserTimers = {}
		self._delayActionUserArg = Const.SPACE_TIMER_USER_ARG_MAX
		self.getScript().doFirstStage( self )
	
	def addUserTimer( self, start, interval = 0.0, uArg = 0,  params = {} ) :
		"""
		# ����û��Զ���timer
		# �˺�����������ڰ�װ��չ���� addTimer �����Ĺ��ܣ�����ʹ�á�
		# ʹ�ø÷�����ӵ� timer��cancel ʱ��Ҫʹ�� cancelCallbackTimer �������Գ�����
		# ��Ȼʹ����Ҳ���Լ���ʹ�� addTimer ����������ע���Ӧ�޸���Ӧ�� onTimer ������
		# ����������̳�����Ӻͳ��� timer ��Ϊʱʹ�� CopyStageAction12 �� CopyStageAction13������������д�����ű���
		
		@param	start			:	��ʼ��һ�λص�ʱ��
		@type	start			:	FLOAT
		@param	callbackName 	:	�ص����������ƣ�����ʹ�ø÷����� spaceScript �϶��壬��ʽΪ def callbackName( self, selfEntity, params ) :
		@type	callbackName 	:	STRING
		@param	interval		:	�ص�ʱ����
		@type	interval		:	FLOAT
		@param	params			:	�ص������Ĳ���
		@type	params			:	PY_DICT
		
		"""
		if uArg == 0 :
			self._delayActionUserArg += 1
			uArg = self._delayActionUserArg
		
		params["userArg"] = uArg
		timerID =  self.addTimer( start, interval, uArg )
		if interval == 0 :
			params["autoCancel"] = True
		self.copyUserTimers[ uArg ] = ( timerID, params )
		return uArg
	
	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		�˽ӿ�����֪ͨ��ɫ���ص�ͼ��ϣ������ƶ��ˣ�����������������Ϸ���ݽ�����
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		"""
		self.getScript().onTeleportReady( self, baseMailbox )
	
	def onTimer( self, timerID, userArg ):
		"""
		# ���ǵײ��onTimer()�������
		"""
		if userArg in self.copyUserTimers :
			params = self.copyUserTimers[ userArg ][1]
			self.getScript().onTimer( self, timerID, userArg, params )
			if params.has_key( "autoCancel" ) :
				del self.copyUserTimers[ userArg ]
	
	def hasUserTimer( self, uArg ) :
		"""
		�ж��Ƿ���ĳһ�û��Զ���timer
		"""
		return uArg in self.copyUserTimers
	
	def cancelUserTimer( self, uArg ) :
		"""
		�����û��Զ���timer
		"""
		try :
			timerID = self.copyUserTimers[ uArg ][0]
		except :
			ERROR_MSG( "the uArg %s timer cant't found. " % uArg )
			return
		self.cancel( timerID )
		del self.copyUserTimers[ uArg ]
	
	def onDestroy( self ):
		"""
		cell ��ɾ��ʱ����
		"""
		self.copyUserTimers = {}
		SpaceCopy.onDestroy( self )
	
	def getCopyShareTempMapping( self ) :
		return self.copyShareTempMapping
	
	def setCopyShareTemp( self, key, value ) :
		"""
		���һ��������������
		�˴���ӵ� key ��Ҫ�� ObjectScripts.CopyTemplate.py �ļ��ж��壬��������鿴��
		
		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		"""
		self.copyShareTempMapping[ key ] = value
	
	def removeCopyShareTemp( self, key ) :
		"""
		�Ƴ�һ��������������
		"""
		self.copyShareTempMapping.pop( key, None )
	
	def queryCopyShareTemp( self, key, default = None ) :
		"""
		���ݹؼ��ֲ�ѯ������������ copyShareTempMapping ����֮��Ӧ��ֵ
		@return: ����ؼ��ֲ������򷵻� default ֵ
		"""
		try :
			return self.copyShareTempMapping[ key ]
		except KeyError :
			return default
	
	def popCopyShareTemp( self, key, default = None ) :
		"""
		�Ƴ�������һ���ؼ���Ϊ key �ĸ�����������
		@return : ����ؼ��ֲ������򷵻� default ֵ
		"""
		return self.copyShareTempMapping.pop( key, default )
	
	
# -*- coding: gb18030 -*-
#

import BigWorld
import time
import Love3
import Const
from bwdebug import *


class LoginAttemper:
	"""
	��ҵ�¼����ģ��
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert LoginAttemper._instance is None
		
		self.waitQueue = []		# �ȴ�����
		self.loginQueue = []		# ��¼����
		self.loginTimeList = []	# ��¼ʱ���б������������һ�ε�¼�޶�ʱ����(Const.LOGIN_CALCULATE_TIME_INTERVAL)��ʱ��
		
		self.loginAccountCountKey = ""
		self.waitAccountCountKey = ""
		self.playerCountKey = ""
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = LoginAttemper()
		return self._instance
		
	# --------------------------------------------------------------
	# public
	# --------------------------------------------------------------
	def onBaseAppReady( self ):
		"""
		baseApp׼������
		"""
		baseAppIDStr = str( BigWorld.getWatcher( "id" ) )
		self.waitAccountCountKey = Const.PREFIX_GBAE_WAIT_NUM + baseAppIDStr
		self.loginAccountCountKey = Const.PREFIX_GBAE_LOGIN_NUM + baseAppIDStr
		self.playerCountKey = Const.PREFIX_GBAE_PLAYER_NUM + baseAppIDStr
		BigWorld.baseAppData[ self.waitAccountCountKey ] = 0	# ��ǰbaseApp�ʺŵȴ����г���
		BigWorld.baseAppData[ self.loginAccountCountKey ] = 0	# ��ǰbaseApp�ʺŵ�¼���г���
		BigWorld.baseAppData[ self.playerCountKey ] = 0		# ��ǰbaseApp�ʺŽ�ɫ����
		
	def onAccountReady( self, accountEntity ):
		"""
		�˻�����״̬������ȴ�����
		
		@param accountEntity : Account ENTITY
		"""
		order = len( self.waitQueue )
		self.waitQueue.append( accountEntity )
		BigWorld.baseAppData[ self.waitAccountCountKey ] += 1
		if BigWorld.globalData["loginAttemper_count_limit"] >= 0:
			# ÿ��baseapp�еġ���¼���С���ͬʱ�����ɫ��¼������Ϊ��Const.LOGIN_ACCOUNT_LIMIT / ��ǰbaseapp������
			# һ��baseApp��������Role���������������Ѵ��ڵ�¼�����е������С��BigWorld.globalData["baseApp_player_count_limit"]��
			loginPlayerNum = len( self.loginQueue )
			if loginPlayerNum >= BigWorld.globalData["loginAttemper_count_limit"] / Love3.g_baseApp.getBaseAppCount()  or \
				Love3.g_baseApp.getPlayerCount() + loginPlayerNum >= BigWorld.globalData["baseApp_player_count_limit"]:
					self._sendWaitTime( accountEntity, order )
					return
					
		if self._loginAccount():
			self._refleshWaitTime()
		
	def onAccountLogoff( self, accountEntity ):
		"""
		�ʺ�������
		"""
		if accountEntity.grade > 0:
			return
		if accountEntity.loginState == Const.ACCOUNT_GAMMING_STATE:
			return
		elif accountEntity.loginState == Const.ACCOUNT_WAITTING_STATE:
			order = self.waitQueue.index( accountEntity )
			self.waitQueue.pop( order )
			BigWorld.baseAppData[ self.waitAccountCountKey ] -= 1
			self._refleshWaitTime( order )
		elif accountEntity.loginState == Const.ACCOUNT_LOGIN_STATE:
			self.loginQueue.remove( accountEntity )
			BigWorld.baseAppData[ self.loginAccountCountKey ] -= 1
			# һ��baseApp��������Role����������BigWorld.globalData["baseApp_player_count_limit"]
			if Love3.g_baseApp.getPlayerCount() + len( self.loginQueue ) < BigWorld.globalData["baseApp_player_count_limit"]:
				if self._loginAccount():
					self._refleshWaitTime()
					
	def loginComplete( self, accountEntity ):
		"""
		�ʺŵ�¼�ɹ�( �ʺ��µ�ĳ����ɫ�ɹ�������Ϸ )������������Ϊ
		"""
		if accountEntity.grade > 0:
			return
		self.loginTimeList.append( time.time() )	# ��¼���ε�¼�ɹ�ʱ��
		self.loginQueue.remove( accountEntity )
		BigWorld.baseAppData[ self.loginAccountCountKey ] -= 1
		# һ��baseApp��������Role����������С��BigWorld.globalData["baseApp_player_count_limit"]
		if Love3.g_baseApp.getPlayerCount() + len( self.loginQueue ) < BigWorld.globalData["baseApp_player_count_limit"]:
			if self._loginAccount():
				self._refleshWaitTime()
		
	def loginAttempt( self, accountEntity ):
		"""
		�Ѿ���¼��account�ظ���¼
		"""
		if accountEntity.loginState == Const.ACCOUNT_INITIAL_STATE:
			if accountEntity.grade > 0:
				accountEntity.changeLoginState( Const.ACCOUNT_LOGIN_STATE )
			else:
				accountEntity.changeLoginState( Const.ACCOUNT_WAITTING_STATE )
		elif accountEntity.loginState == Const.ACCOUNT_WAITTING_STATE:
			self._refleshWaitTime()
		else:
			accountEntity.queryRoles()
			
	def loginAttemperTrigger( self ):
		"""
		���ȴ���
		"""
		# ÿ��baseapp�еġ���¼���С���ͬʱ�����ɫ��¼������Ϊ��Const.LOGIN_ACCOUNT_LIMIT / ��ǰbaseapp������
		# һ��baseApp��������Role���������������Ѵ��ڵ�¼�����е������С��BigWorld.globalData["baseApp_player_count_limit"]��
		loginPlayerNum = len( self.loginQueue )
		if Love3.g_baseApp.getPlayerCount() + loginPlayerNum < BigWorld.globalData["baseApp_player_count_limit"] and \
			loginPlayerNum < BigWorld.globalData["loginAttemper_count_limit"] / Love3.g_baseApp.getBaseAppCount():
				if self._loginAccount():
					self._refleshWaitTime()
					
	def canLogin( self, accountEntity ):
		"""
		��¼�����Ƿ������¼
		"""
		if accountEntity.grade > 0:
			return True
			
		if len( self.waitQueue ) >= BigWorld.globalData["login_waitQueue_limit"]:
			return False
		return True
		
	# --------------------------------------------------------------
	# private
	# --------------------------------------------------------------
	def _loginAccount( self ):
		"""
		����һ�����ڵȴ���account����¼����
		"""
		try:
			accountEntity = self.waitQueue.pop( 0 )
			BigWorld.baseAppData[ self.waitAccountCountKey ] -= 1
		except IndexError:
			DEBUG_MSG( "�ȴ���������û��Account Entity��" )
			return False
		self.loginQueue.append( accountEntity )
		BigWorld.baseAppData[ self.loginAccountCountKey ] += 1
		accountEntity.changeLoginState( Const.ACCOUNT_LOGIN_STATE )
		return True

	def _isLoginBusy( self ):	# ����Ч�ʿ��ǣ��������߼��򵥣��Ƿ��¼��æ���жϲ�ʹ�ô˺������Խ�ʡ�������õĿ���
		"""
		�Ƿ��¼��æ
		
		�ݶ�ÿ��baseapp�еġ���¼���С���ͬʱ�����ɫ��¼������Ϊ��Const.LOGIN_ACCOUNT_LIMIT / ��ǰbaseapp������
		"""
		return len( self.loginQueue ) >= BigWorld.globalData["loginAttemper_count_limit"] / Love3.g_baseApp.getBaseAppCount()
		
	def _isBaseAppBusy( self ):	# ����Ч�ʿ��ǣ��������߼��򵥣��Ƿ��������æ���жϲ�ʹ�ô˺������Խ�ʡ�������õĿ���
		"""
		һ��baseApp��������Role���������������Ѵ��ڵ�¼�����е������С��BigWorld.globalData["baseApp_player_count_limit"]��
		"""
		return Love3.g_baseApp.getPlayerCount() + len( self.loginQueue ) >= BigWorld.globalData["baseApp_player_count_limit"]
		
	def _sendWaitTime( self, accountEntity, order ):
		"""
		���ʺŷ��͵ȴ���¼��ʱ��
		"""
		waitTime = self._getWaitTime( order )
		
		# ��ʱaccountEntity��client�϶��Ѿ���������
		accountEntity.client.receiveWattingTime( order, waitTime )
		
	def _getWaitTime( self, order ):
		"""
		�����Ҫ�ȴ���ʱ��
		"""
		tempList = self.loginTimeList
		self.loginTimeList = []
		loginCheckTime = time.time() - Const.LOGIN_CALCULATE_TIME_INTERVAL	# ����һ��ʱ���ڵ�¼��������Чʱ��
		for fTime in tempList:
			if loginCheckTime < fTime:
				self.loginTimeList.append( fTime )
		count = len( self.loginTimeList )		# Const.LOGIN_CALCULATE_TIME_INTERVALʱ����ڵ�¼����Ҹ���
		if count == 0:		# �����û�гɹ��ĵ�¼����ô����һ���Ƚϳ���ʱ��
			count = 1
			
		# ��Ҫ�ȴ���ʱ�� = ƽ����¼ʱ����ȴ������
		return Const.LOGIN_CALCULATE_TIME_INTERVAL / count * order
		
	def _refleshWaitTime( self, fromOrder = 0 ):
		"""
		ˢ�µȴ�ʱ��
		
		@param fromOrder : ���ĸ�λ�ÿ�ʼˢ�µȴ�ʱ��
		"""
		waitCount = len( self.waitQueue )
		if waitCount == 0:
			return
			
		# �������һ��ˢ��ʱ�䲻��Const.LOGIN_REFLESH_WAIT_TIME_INTERVAL����ô��ˢ��
		#if len( self.loginTimeList ) and time.time() - self.loginTimeList[-1] < Const.LOGIN_REFLESH_WAIT_TIME_INTERVAL:
		#	return
			
		for i in xrange( waitCount - fromOrder ):
			index = i + fromOrder
			self._sendWaitTime( self.waitQueue[ index ], index )
			
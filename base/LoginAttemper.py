# -*- coding: gb18030 -*-
#

import BigWorld
import time
import Love3
import Const
from bwdebug import *


class LoginAttemper:
	"""
	玩家登录调度模块
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert LoginAttemper._instance is None
		
		self.waitQueue = []		# 等待队列
		self.loginQueue = []		# 登录队列
		self.loginTimeList = []	# 登录时间列表，仅保存离最近一次登录限定时间内(Const.LOGIN_CALCULATE_TIME_INTERVAL)的时刻
		
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
		baseApp准备好了
		"""
		baseAppIDStr = str( BigWorld.getWatcher( "id" ) )
		self.waitAccountCountKey = Const.PREFIX_GBAE_WAIT_NUM + baseAppIDStr
		self.loginAccountCountKey = Const.PREFIX_GBAE_LOGIN_NUM + baseAppIDStr
		self.playerCountKey = Const.PREFIX_GBAE_PLAYER_NUM + baseAppIDStr
		BigWorld.baseAppData[ self.waitAccountCountKey ] = 0	# 当前baseApp帐号等待队列长度
		BigWorld.baseAppData[ self.loginAccountCountKey ] = 0	# 当前baseApp帐号登录队列长度
		BigWorld.baseAppData[ self.playerCountKey ] = 0		# 当前baseApp帐号角色总数
		
	def onAccountReady( self, accountEntity ):
		"""
		账户就绪状态，进入等待队列
		
		@param accountEntity : Account ENTITY
		"""
		order = len( self.waitQueue )
		self.waitQueue.append( accountEntity )
		BigWorld.baseAppData[ self.waitAccountCountKey ] += 1
		if BigWorld.globalData["loginAttemper_count_limit"] >= 0:
			# 每个baseapp中的“登录队列”可同时允许角色登录的数量为“Const.LOGIN_ACCOUNT_LIMIT / 当前baseapp数量”
			# 一个baseApp允许最大的Role在线数量，包括已处于登录队列中的玩家需小于BigWorld.globalData["baseApp_player_count_limit"]。
			loginPlayerNum = len( self.loginQueue )
			if loginPlayerNum >= BigWorld.globalData["loginAttemper_count_limit"] / Love3.g_baseApp.getBaseAppCount()  or \
				Love3.g_baseApp.getPlayerCount() + loginPlayerNum >= BigWorld.globalData["baseApp_player_count_limit"]:
					self._sendWaitTime( accountEntity, order )
					return
					
		if self._loginAccount():
			self._refleshWaitTime()
		
	def onAccountLogoff( self, accountEntity ):
		"""
		帐号下线了
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
			# 一个baseApp允许最大的Role在线数量是BigWorld.globalData["baseApp_player_count_limit"]
			if Love3.g_baseApp.getPlayerCount() + len( self.loginQueue ) < BigWorld.globalData["baseApp_player_count_limit"]:
				if self._loginAccount():
					self._refleshWaitTime()
					
	def loginComplete( self, accountEntity ):
		"""
		帐号登录成功( 帐号下的某个角色成功进入游戏 )，触发调度行为
		"""
		if accountEntity.grade > 0:
			return
		self.loginTimeList.append( time.time() )	# 记录本次登录成功时间
		self.loginQueue.remove( accountEntity )
		BigWorld.baseAppData[ self.loginAccountCountKey ] -= 1
		# 一个baseApp允许最大的Role在线数量需小于BigWorld.globalData["baseApp_player_count_limit"]
		if Love3.g_baseApp.getPlayerCount() + len( self.loginQueue ) < BigWorld.globalData["baseApp_player_count_limit"]:
			if self._loginAccount():
				self._refleshWaitTime()
		
	def loginAttempt( self, accountEntity ):
		"""
		已经登录的account重复登录
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
		调度触发
		"""
		# 每个baseapp中的“登录队列”可同时允许角色登录的数量为“Const.LOGIN_ACCOUNT_LIMIT / 当前baseapp数量”
		# 一个baseApp允许最大的Role在线数量，包括已处于登录队列中的玩家需小于BigWorld.globalData["baseApp_player_count_limit"]。
		loginPlayerNum = len( self.loginQueue )
		if Love3.g_baseApp.getPlayerCount() + loginPlayerNum < BigWorld.globalData["baseApp_player_count_limit"] and \
			loginPlayerNum < BigWorld.globalData["loginAttemper_count_limit"] / Love3.g_baseApp.getBaseAppCount():
				if self._loginAccount():
					self._refleshWaitTime()
					
	def canLogin( self, accountEntity ):
		"""
		登录调度是否允许登录
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
		调度一个正在等待的account到登录队列
		"""
		try:
			accountEntity = self.waitQueue.pop( 0 )
			BigWorld.baseAppData[ self.waitAccountCountKey ] -= 1
		except IndexError:
			DEBUG_MSG( "等待队列中已没有Account Entity。" )
			return False
		self.loginQueue.append( accountEntity )
		BigWorld.baseAppData[ self.loginAccountCountKey ] += 1
		accountEntity.changeLoginState( Const.ACCOUNT_LOGIN_STATE )
		return True

	def _isLoginBusy( self ):	# 基于效率考虑，且由于逻辑简单，是否登录繁忙的判断不使用此函数，以节省函数调用的开销
		"""
		是否登录繁忙
		
		暂定每个baseapp中的“登录队列”可同时允许角色登录的数量为“Const.LOGIN_ACCOUNT_LIMIT / 当前baseapp数量”
		"""
		return len( self.loginQueue ) >= BigWorld.globalData["loginAttemper_count_limit"] / Love3.g_baseApp.getBaseAppCount()
		
	def _isBaseAppBusy( self ):	# 基于效率考虑，且由于逻辑简单，是否服务器繁忙的判断不使用此函数，以节省函数调用的开销
		"""
		一个baseApp允许最大的Role在线数量，包括已处于登录队列中的玩家需小于BigWorld.globalData["baseApp_player_count_limit"]。
		"""
		return Love3.g_baseApp.getPlayerCount() + len( self.loginQueue ) >= BigWorld.globalData["baseApp_player_count_limit"]
		
	def _sendWaitTime( self, accountEntity, order ):
		"""
		给帐号发送等待登录的时间
		"""
		waitTime = self._getWaitTime( order )
		
		# 此时accountEntity的client肯定已经创建好了
		accountEntity.client.receiveWattingTime( order, waitTime )
		
	def _getWaitTime( self, order ):
		"""
		获得需要等待的时间
		"""
		tempList = self.loginTimeList
		self.loginTimeList = []
		loginCheckTime = time.time() - Const.LOGIN_CALCULATE_TIME_INTERVAL	# 计算一段时间内登录个数的有效时刻
		for fTime in tempList:
			if loginCheckTime < fTime:
				self.loginTimeList.append( fTime )
		count = len( self.loginTimeList )		# Const.LOGIN_CALCULATE_TIME_INTERVAL时间段内登录的玩家个数
		if count == 0:		# 最近都没有成功的登录，那么返回一个比较长的时间
			count = 1
			
		# 需要等待的时间 = 平均登录时间×等待的序号
		return Const.LOGIN_CALCULATE_TIME_INTERVAL / count * order
		
	def _refleshWaitTime( self, fromOrder = 0 ):
		"""
		刷新等待时间
		
		@param fromOrder : 从哪个位置开始刷新等待时间
		"""
		waitCount = len( self.waitQueue )
		if waitCount == 0:
			return
			
		# 如果距上一次刷新时间不到Const.LOGIN_REFLESH_WAIT_TIME_INTERVAL，那么不刷新
		#if len( self.loginTimeList ) and time.time() - self.loginTimeList[-1] < Const.LOGIN_REFLESH_WAIT_TIME_INTERVAL:
		#	return
			
		for i in xrange( waitCount - fromOrder ):
			index = i + fromOrder
			self._sendWaitTime( self.waitQueue[ index ], index )
			
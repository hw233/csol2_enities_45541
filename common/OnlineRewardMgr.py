# -*- coding: gb18030 -*-

# $Id: OnlineRewardMgr.py,v 1.1 10:44 2009-10-27 jiangyi Exp $

import Language
from bwdebug import *
import csdefine
from config.skill.FixTimeReward import Datas as rd

class OnlineRewardMgr:
	"""
	在线奖励配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert OnlineRewardMgr._instance is None
		OnlineRewardMgr._instance = self
		
		self._datas = rd
		#key : timer
		#value : { 'rewarduid': 10011,……}

	def rewardKeys( self ):
		"""返回排列好的keys"""
		keyOrderList = self._datas.keys()
		if len( keyOrderList ) == 0:
			ERROR_MSG( "timeTick %s has no data." % ( timeTick ) )
			return None
		keyOrderList.sort()
		return keyOrderList
		
	def getTick( self, timeTick ):
		"""
		获得下一个领奖时刻，
		"""
		keyOrderList = self.rewardKeys()
		for data in keyOrderList:
			if timeTick < data: return data
		return None

	def getRewardTick( self, lifetime ):
		"""
		获取已经到点可以领奖的时刻列表
		"""
		keyOrderList = self.rewardKeys()
		Datas = []
		for data in keyOrderList:
			if lifetime > data:
				Datas.append( data )
		if len( Datas ) == 0:
			return None
		Datas.sort()
		return Datas
		
	def getData( self, timeTick ):
		"""
		获得数据
		@param factionID: 势力id 编号
		@return: [( id, prestige ), ...]
		"""
		try:
			return self._datas[timeTick]
		except KeyError:
			ERROR_MSG( "timeTick %s has no data." % ( timeTick ) )
			return None
			
	def getCount( self ):
		"""获得奖励数量"""
		return len( self._datas )
	
	def getRewardUid( self, timeTick ):
		"""
		获得奖励内容
		"""
		try:
			return self._datas[timeTick]['rewarduid']
		except KeyError:
			ERROR_MSG( "timeTick %s has no item." % ( timeTick ) )
			return None
			
	def getDec( self, timeTick ):
		"""
		获得奖励描述
		"""
		try:
			return self._datas[timeTick]['decInfo']
		except KeyError:
			ERROR_MSG( "timeTick %s has no decInfo." % ( timeTick ) )
			return None
			
	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = OnlineRewardMgr()
		return SELF._instance
		
		
#
# $Log: not supported by cvs2svn $
#
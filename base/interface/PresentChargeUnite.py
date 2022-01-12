# -*- coding: gb18030 -*-

# $Id: PresentChargeUnite.py  hd
# 玩家领取运营活动奖励和充值元宝的模块

from bwdebug import *
from PresentChargeManage import PresentChargeManage
import csdefine
import csstatus

class PresentChargeUnite:
	"""
	玩家领取运营活动奖励和充值元宝的模块
	"""
	def __init__( self ):
		self._dataDBIDs = []			#记录正在处理的DBID
		self._pcu_manager = None		#活动奖励管理器
		self._pcu_addSilverCoinTmp = 0	#记录领取全部奖励时 可以领取的银元宝数量


	def get_pcu_manager( self ):
		"""
		获取活动管理器
		注:通常情况下玩家是不会有这个管理器的，如果调用该接口表示需要管理器，那么如果没有初始化过，就在这里初始化
		"""
		if not self._pcu_manager:
			self._pcu_manager = PresentChargeManage( self )
		return self._pcu_manager

	def pcu_takeThings( self, dataType, item_id ):
		"""
		@define method
		开始领取奖励
		@type  dataType : UINT8
		@param dataType : 操作的类型
		"""
		self.get_pcu_manager().takeThings( dataType, item_id )

	def pcu_getPresentTypes( self ):
		"""
		@define method
		请求获取玩家拥有的奖励类型,cell获取后可以决定让客户端去显示，让玩家可以知道自己是否有奖励，如果有，可以请求获取。而
		不是盲目的去请求
		"""
		self.get_pcu_manager().getPresentTypes( self )

	def pcu_check( self, dbid ):
		"""
		检查要处理的DBID是否在之前正在处理
		@type  dbid : int
		@param dbid : 数据的DBID
		"""
		return dbid in self._dataDBIDs

	def pcu_removeDBID( self, dbid ):
		"""
		删除已经处理了的DBID
		@type  dbid : int
		@param dbid : 数据库中该操作的DBID
		"""
		try:
			self._dataDBIDs.remove( dbid )
			return True
		except:
			ERROR_MSG("can not find dbid %s" % dbid )
			return False

	def pcu_addDBID( self, dbid ):
		"""
		加入一个DBID到正在处理的DBID列表中，以避免在极端情况下可能出现重复处理的问题
		@type  dbid : int
		@param dbid : 数据库中该操作的DBID
		"""
		self._dataDBIDs.append( dbid )

	def takeOverSuccess( self ):
		"""
		@define method
		成功领奖完毕清除数据
		"""
		if self._pcu_addSilverCoinTmp:
			self.gainSilver( self._pcu_addSilverCoinTmp, csdefine.CHANGE_SILVER_CHARGE )	# 之前已经检查过是否能增加银元宝 所以这里不再检查。
			self._pcu_addSilverCoinTmp = 0
		self.get_pcu_manager().takeThingsSuccess()

	def takeOverFailed( self ):
		"""
		@define method
		失败,清除数据
		"""
		self.get_pcu_manager().takeThingsFailed()

	def takeSilverCoins( self, silverCoins ):
		"""
		领取银元宝
		"""
		addSilverCoin = 0
		for silverCoin in silverCoins:
			addSilverCoin += silverCoin
		if not self.accountEntity.testAddSilver( addSilverCoin ):	#表示超过了上限
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_SIlVERCOINS )
			return
		self.gainSilver( addSilverCoin, csdefine.CHANGE_SILVER_SILVERPRESENT )
		self.takeOverSuccess()					#通知清理数据

	def takeChargedMoney( self, silverCoinsList, goldList ):
		"""
		领取充值了的金银元宝
		"""
		m_addSilverCoin   = 0
		m_addGold		  = 0
		for silverCoin in silverCoinsList:
			m_addSilverCoin += silverCoin
		if not self.accountEntity.testAddSilver( m_addSilverCoin ):	#表示超过了上限
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_SIlVERCOINS )
			return
		for gold in goldList:
			m_addGold += gold
		if not self.accountEntity.testAddGold( m_addGold ):	#表示超过了上限
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_GOLD )
			return
		if m_addGold > 0:
			self.gainGold( m_addGold, csdefine.CHANGE_GOLD_CHARGE )
		if m_addSilverCoin > 0:
			self.gainSilver( m_addSilverCoin, csdefine.CHANGE_SILVER_CHARGE )
		self.takeOverSuccess()					#通知清理数据


	def takePresents( self, presentIDs, silverCoins ):
		"""
		领取银元宝和物品
		"""
		self._pcu_addSilverCoinTmp = 0
		for silverCoin in silverCoins:
			self._pcu_addSilverCoinTmp += silverCoin
		if not self.accountEntity.testAddSilver( self._pcu_addSilverCoinTmp ):	#这里检查是否能够增加银元宝
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_SIlVERCOINS )
			return

		self.cell.takePresent( presentIDs )		# 这里到CELL增加物品
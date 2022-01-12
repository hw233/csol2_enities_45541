# -*- coding:gb18030 -*-

import time
import Love3
from bwdebug import *
import BigWorld
import csdefine
import csconst
import ECBExtend
from fishingJoy.BulletClip import BulletClip

HIT_INTERVAL_VALID_COUNT = 10		# 每攻击若干次验证一下玩家的攻击频率是否在合法范围

class Fisher:
	def __init__( self ):
		# BASE_AND_CLENT属性，玩家的捕鱼资金。在玩家离开捕鱼场时或者下次上线时返还到玩家相应的货币属性。
		# self.fishingJoyMoney
		# self.fishingJoySilver
		
		self.fish_bulletType = 1				# 玩家当前子弹类型
		
		self.fish_lastHitTime = time.time()		# 玩家最后一次攻击时间
		self.fish_nHitTotalTime = 0				# 若干次攻击所用时间
		self.fish_nHitCount = 0					# 若干次攻击计数
		
		self.magnification = 1					# 炮弹消耗倍率
		self.fish_itemInUse = -1				# 正在使用的物品
		
		self.fishItems = {}
		self.fish_useItemTimerID = -1
		
		self.bulletClip = BulletClip( 8 )		# 根据捕鱼场大小和炮弹速度预估每个玩家同时会在捕鱼场中拥有多少颗炮弹以便确定弹夹空间
		
		
	def fish_addMagnification( self, value ):
		self.magnification += value
		self.client.fish_setMagnification( self.magnification )
		
	def payFishingJoyMoney( self, value ):
		if self.fishingJoyMoney - value < 0:
			DEBUG_MSG( "there is no bullet( %i ):player( %s)." % ( self.fish_bulletType, self.getName() ) )
			return False
		self.addFishingJoyMoney( -value )
		return True
		
	def gainFishingJoyMoney( self, value ):
		if csconst.ROLE_MONEY_UPPER_LIMIT < value + self.fishingJoyMoney:
			ERROR_MSG( "player( %s )'s fishingJoyMoney overflow." % self.getName() )
			return False
		self.addFishingJoyMoney( value )
		return True
		
	def addFishingJoyMoney( self, value ):
		"""
		增减玩家的捕鱼炮弹游戏币账户值
		"""
		self.fishingJoyMoney += value
		if value > 0:	 	# 仅在增加时同步客户端
			self.client.setFishingJoyMoney( self.fishingJoyMoney )
			
	def payFishingJoySilver( self, value ):
		if self.fishingJoySilver - value < 0:
			DEBUG_MSG( "there is no bullet( %i ):player( %s)." % ( self.fish_bulletType, self.getName ) )
			return False
		self.addFishingJoySilver( -value )
		return True
		
	def gainFishingJoySilver( self, value ):
		if csconst.ROLE_SILVER_UPPER_LIMIT < value + self.fishingJoySilver:
			ERROR_MSG( "player( %s )'s fishingJoySilver overflow." % self.getName() )
			return
		self.addFishingJoySilver( value )
		return True
		
	def addFishingJoySilver( self, value ):
		"""
		增减玩家的捕鱼炮弹元宝账户值
		"""
		self.fishingJoySilver += value
		if value > 0:	# 仅在增加时同步客户端
			self.client.setFishingJoySilver( self.fishingJoySilver )
			
	def fish_checkHitFrequency( self ):
		now = time.time()
		DEBUG_MSG( "now, now - self.fish_lastHitTime", now, now - self.fish_lastHitTime )
		if now - self.fish_lastHitTime < csconst.FISH_HIT_COOLDOWN:
			return False
		self.fish_lastHitTime = now
		return True
		
	def fish_getBulletType( self ):
		return self.fish_bulletType
		
	def fish_getMagnification( self ):
		return self.magnification
		
	def fish_hit( self, positionTuple ):
		"""
		Exposed method.
		玩家向某个位置攻击
		
		需要通知到房间中的其他玩家。
		需要控制玩家的发炮频率。
		每攻击一次就要花费一颗子弹。
		"""
		# 玩家每攻击HIT_INTERVAL_VALID_COUNT次验证一下攻击频率是否太快而存在作弊可能。不允许玩家过快的发射炮弹，会给服务器带来过大负担。
		self.fish_nHitCount += 1
		now = time.time()
		self.fish_nHitTotalTime += now - self.fish_lastHitTime
		self.fish_lastHitTime = now
		if self.fish_nHitCount % HIT_INTERVAL_VALID_COUNT == 0:
			cooldown = self.fish_nHitTotalTime / self.fish_nHitCount
			if cooldown < csconst.FISH_HIT_COOLDOWN:
				HACK_MSG( "player( %s ) hit Frequency too fast.maybe a cheat." % self.getName() )
				# 把玩家踢出捕鱼房间
				return
				
		bulletNumber = self.bulletClip.fisherHit( self )
		if bulletNumber != -1:	# 有效炮弹
			BigWorld.globalData["FishingJoyMgr"].fisherHit( self.id, bulletNumber, positionTuple )
			
	def fish_hitFish( self, bulletNumber, fishNumbers ):
		"""
		Exposed method.
		玩家网住了一些鱼
		"""
		bulletData = self.bulletClip.fisherHitFish( bulletNumber )
		if bulletData is None:
			DEBUG_MSG( "i dont have this bullets( %i ): player(%s)." % ( bulletNumber, self.getName() ) )
			return
			
		BigWorld.globalData["FishingJoyMgr"].fisherHitFish( self.id, bulletNumber, bulletData[1], bulletData[2], fishNumbers )
		
	def fish_changeBullet( self, bulletType ):
		"""
		Exposed method.
		玩家改变所使用的炮弹类型
		"""
		if self.fish_bulletType == bulletType:
			HACK_MSG( "the same current bulletType and target bulletType( %i )." % bulletType )
			return
		if not Love3.g_fishingJoyLoader.hasBulletType( bulletType ):
			HACK_MSG( "player( %i ) change a undefine bulletType( %i )" % ( playerID, bulletType ) )
			return
			
		self.fish_bulletType = bulletType
		BigWorld.globalData["FishingJoyMgr"].fisherChangeBullet( self.id, bulletType )
		
	def fish_buyBulletRequest( self, cost ):
		"""
		Exposed method.
		请求买炮弹
		"""
		if not self.paySilver( cost, csdefine.CHANGE_SILVER_FISHING_JOY ):
			DEBUG_MSG( "player( %s ) dont have enough silver( %i )." % ( self.getName(), cost ) )
			return
		self.fish_buyBullet( csdefine.CURRENCY_TYPE_SILVER, cost )
		
	def fish_buyBullet( self, moneyType, cost ):
		"""
		Define method.
		玩家购买炮弹。客户端根据子弹类型计算出花费。
		"""
		DEBUG_MSG( "player(%s) buy bullet( moneyType:%i ) cost:%i." % ( self.getName(), moneyType, cost ) )
		# 仅在客户端做货币数量上限测试
		if moneyType == csdefine.CURRENCY_TYPE_MONEY:
			self.gainFishingJoyMoney( cost )
		else:
			self.gainFishingJoySilver( cost )
		self.fish_bulletUseOutCount = 0
		
	def fish_gainSilver( self, earnings ):
		"""
		Define method.
		捕鱼获得
		"""
		self.gainSilver( earnings, csdefine.CHANGE_SILVER_FISHING_JOY )
		
	def fish_pickItem( self, itemType, fishNumber ):
		"""
		Define method.
		玩家捕获一条鱼，幸运的获得了捕鱼物品
		
		@param itemType:INT16, 掉落的捕鱼物品类型
		@param fishNumber:INT32, 掉落物品的鱼编号
		"""
		if not self.fishItems.has_key( itemType ):
			self.fishItems[itemType] = 1
		else:
			self.fishItems[itemType] += 1
		self.client.fish_pickFishItem( itemType, fishNumber )
		
	def fish_useItem( self, itemType ):
		"""
		Exposed method.
		"""
		if not self.fishItems.has_key( itemType ):
			ERROR_MSG( "player( %s ) have no item( %i )." % ( self.getName(), itemType ) )
			return
		if self.fish_itemInUse != -1:
			DEBUG_MSG( "player(%s) have item( %i ) using." % ( self.getName(), self.fish_itemInUse ) )
			return
			
		self.fish_itemInUse = itemType
		fishItem = Love3.g_fishingJoyLoader.getFishItem( itemType )
		fishItem.attach( self )
		persistent = fishItem.getPersistent()
		if persistent > 0:
			self.fish_useItemTimerID = self.addTimer( persistent, 0, ECBExtend.FISHING_JOY_ITEM_CBID )
		self.fishItems[itemType] -= 1
		if self.fishItems[itemType] == 0:
			del self.fishItems[itemType]
		BigWorld.globalData["FishingJoyMgr"].fisherUseItem( self.id )
		self.client.fish_useItemSuccess( itemType )
		
	def fish_leaveRoom( self ):
		"""
		Define method.
		"""
		self.fish_itemInUse = -1
		if self.fish_useItemTimerID:
			self.delTimer( self.fish_useItemTimerID )
			self.fish_useItemTimerID = -1
		self.bulletClip.reset()
		self.fish_returnBulletMoney()
		
	def fish_returnBulletMoney( self ):
		"""
		返还没有用完的炮弹金钱和银元宝
		"""
		if self.fishingJoyMoney:
			self.cell.fish_retrunMoneyOnLeaving( self.fishingJoyMoney )	# 安全到无微不至的话需锁定self.fishingJoyMoney，但明显没必要。
		if self.fishingJoySilver:
			self.fish_gainSilver( self.fishingJoyMoney )
			self.fishingJoySilver = 0
			self.client.setFishingJoySilver( 0 )
			
	def fish_returnMoneySuccess( self ):
		"""
		Define method.
		捕鱼金钱返还成功
		"""
		self.fishingJoyMoney = 0
		self.client.setFishingJoyMoney( 0 )
		
	def onClientGetCell( self ):
		self.fish_returnBulletMoney()
		
	def onTimer_fish_useItemTimerOut( self, timerID, cbID ):
		fishItem = Love3.g_fishingJoyLoader.getFishItem( self.fish_itemInUse )
		fishItem.detach( self )
		self.fish_itemInUse = -1
		BigWorld.globalData["FishingJoyMgr"].fisherUseItemOver( self.id )
		
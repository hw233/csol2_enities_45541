# -*- coding:gb18030 -*-

import time
import Love3
from bwdebug import *
import BigWorld
import csdefine
import csconst
import ECBExtend
from fishingJoy.BulletClip import BulletClip

HIT_INTERVAL_VALID_COUNT = 10		# ÿ�������ɴ���֤һ����ҵĹ���Ƶ���Ƿ��ںϷ���Χ

class Fisher:
	def __init__( self ):
		# BASE_AND_CLENT���ԣ���ҵĲ����ʽ�������뿪���㳡ʱ�����´�����ʱ�����������Ӧ�Ļ������ԡ�
		# self.fishingJoyMoney
		# self.fishingJoySilver
		
		self.fish_bulletType = 1				# ��ҵ�ǰ�ӵ�����
		
		self.fish_lastHitTime = time.time()		# ������һ�ι���ʱ��
		self.fish_nHitTotalTime = 0				# ���ɴι�������ʱ��
		self.fish_nHitCount = 0					# ���ɴι�������
		
		self.magnification = 1					# �ڵ����ı���
		self.fish_itemInUse = -1				# ����ʹ�õ���Ʒ
		
		self.fishItems = {}
		self.fish_useItemTimerID = -1
		
		self.bulletClip = BulletClip( 8 )		# ���ݲ��㳡��С���ڵ��ٶ�Ԥ��ÿ�����ͬʱ���ڲ��㳡��ӵ�ж��ٿ��ڵ��Ա�ȷ�����пռ�
		
		
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
		������ҵĲ����ڵ���Ϸ���˻�ֵ
		"""
		self.fishingJoyMoney += value
		if value > 0:	 	# ��������ʱͬ���ͻ���
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
		������ҵĲ����ڵ�Ԫ���˻�ֵ
		"""
		self.fishingJoySilver += value
		if value > 0:	# ��������ʱͬ���ͻ���
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
		�����ĳ��λ�ù���
		
		��Ҫ֪ͨ�������е�������ҡ�
		��Ҫ������ҵķ���Ƶ�ʡ�
		ÿ����һ�ξ�Ҫ����һ���ӵ���
		"""
		# ���ÿ����HIT_INTERVAL_VALID_COUNT����֤һ�¹���Ƶ���Ƿ�̫����������׿��ܡ���������ҹ���ķ����ڵ�������������������󸺵���
		self.fish_nHitCount += 1
		now = time.time()
		self.fish_nHitTotalTime += now - self.fish_lastHitTime
		self.fish_lastHitTime = now
		if self.fish_nHitCount % HIT_INTERVAL_VALID_COUNT == 0:
			cooldown = self.fish_nHitTotalTime / self.fish_nHitCount
			if cooldown < csconst.FISH_HIT_COOLDOWN:
				HACK_MSG( "player( %s ) hit Frequency too fast.maybe a cheat." % self.getName() )
				# ������߳����㷿��
				return
				
		bulletNumber = self.bulletClip.fisherHit( self )
		if bulletNumber != -1:	# ��Ч�ڵ�
			BigWorld.globalData["FishingJoyMgr"].fisherHit( self.id, bulletNumber, positionTuple )
			
	def fish_hitFish( self, bulletNumber, fishNumbers ):
		"""
		Exposed method.
		�����ס��һЩ��
		"""
		bulletData = self.bulletClip.fisherHitFish( bulletNumber )
		if bulletData is None:
			DEBUG_MSG( "i dont have this bullets( %i ): player(%s)." % ( bulletNumber, self.getName() ) )
			return
			
		BigWorld.globalData["FishingJoyMgr"].fisherHitFish( self.id, bulletNumber, bulletData[1], bulletData[2], fishNumbers )
		
	def fish_changeBullet( self, bulletType ):
		"""
		Exposed method.
		��Ҹı���ʹ�õ��ڵ�����
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
		�������ڵ�
		"""
		if not self.paySilver( cost, csdefine.CHANGE_SILVER_FISHING_JOY ):
			DEBUG_MSG( "player( %s ) dont have enough silver( %i )." % ( self.getName(), cost ) )
			return
		self.fish_buyBullet( csdefine.CURRENCY_TYPE_SILVER, cost )
		
	def fish_buyBullet( self, moneyType, cost ):
		"""
		Define method.
		��ҹ����ڵ����ͻ��˸����ӵ����ͼ�������ѡ�
		"""
		DEBUG_MSG( "player(%s) buy bullet( moneyType:%i ) cost:%i." % ( self.getName(), moneyType, cost ) )
		# ���ڿͻ����������������޲���
		if moneyType == csdefine.CURRENCY_TYPE_MONEY:
			self.gainFishingJoyMoney( cost )
		else:
			self.gainFishingJoySilver( cost )
		self.fish_bulletUseOutCount = 0
		
	def fish_gainSilver( self, earnings ):
		"""
		Define method.
		������
		"""
		self.gainSilver( earnings, csdefine.CHANGE_SILVER_FISHING_JOY )
		
	def fish_pickItem( self, itemType, fishNumber ):
		"""
		Define method.
		��Ҳ���һ���㣬���˵Ļ���˲�����Ʒ
		
		@param itemType:INT16, ����Ĳ�����Ʒ����
		@param fishNumber:INT32, ������Ʒ������
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
		����û��������ڵ���Ǯ����Ԫ��
		"""
		if self.fishingJoyMoney:
			self.cell.fish_retrunMoneyOnLeaving( self.fishingJoyMoney )	# ��ȫ����΢�����Ļ�������self.fishingJoyMoney��������û��Ҫ��
		if self.fishingJoySilver:
			self.fish_gainSilver( self.fishingJoyMoney )
			self.fishingJoySilver = 0
			self.client.setFishingJoySilver( 0 )
			
	def fish_returnMoneySuccess( self ):
		"""
		Define method.
		�����Ǯ�����ɹ�
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
		
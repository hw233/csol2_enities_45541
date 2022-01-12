# -*- coding:gb18030 -*-

from AbstractTemplates import Singleton
from FishData import FishData
import Language
from FishSpecies import FishSpecies
from FishSpecies import GroupFishSpecies
from Bullet import MoneyBullet
from Bullet import SilverBullet
from FishItem import MagnificationCard
from FishDropBox import FishDropBox

from bwdebug import *
import csdefine

class FishingJoyDataLoader( Singleton ):
	def __init__( self ):
		self.fishTable = {}
		self.bullets = {}
		self.fishItems = {}
		self.dropBox = FishDropBox()

		self.lossMoneyDistrict = []	# 损失金钱的不同区间，可以取得损失区间从rateAmendTable中取得修正率
		self.lossSilverDistrict = []	# 损失银元宝的不同区间
		self.rateAmendTable = {}	# 损失修正率的映射表，like as { ( fishType, moneyType, district ):rate, ... }
		# 只有少数的鱼死亡时适用损失额带来的命中率修正，设置这两个数据过滤大多数不需要的情况
		self.moneyRateAmendFishTypes = set()	# 金钱损失修正率适用的鱼类型
		self.silverRateAmendFishTypes = set()	# 银元宝损失修正率适用的鱼类型

	def initFishingJoyMgrData( self ):
		self.loadFishData( "config/server/fishingJoy/FishingFishes_server.xml" )
		self.loadItemDropOdds( "config/server/fishingJoy/FishItemDrop.xml" )
		self.loadCaptureRateAmend( "config/server/fishingJoy/CaptureRateAmend.xml" )

	def initFishingJoyCommonData( self ):
		self.loadBulletData( "config/server/fishingJoy/FishingBullets_server.xml" )
		self.loadFishItem( "config/server/fishingJoy/FishingItems_server.xml" )

	def loadFishData( self, xmlConfig ):
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError,"cannot load %s." % xmlConfig
		for index, item in enumerate( section.values() ):
			data = { "index" : index,\
						"type":item.readInt( "type" ), \
						"moneyValue":item.readInt( "moneyValue" ), \
						"silverValue":item.readInt( "silverValue" ), \
						"moveSpeed":item.readFloat( "moveSpeed" ), \
						"catchRate":item.readInt( "catchRate" ), \
						"baseAmount":item.readInt( "baseAmount" ), \
						"supplyDelay":item.readInt( "supplyDelay" ), \
						"memberAmount":item.readInt( "memberAmount" ), \
						"randomMoveRate":item.readInt( "randomMoveRate" ), \
					 }
			self.fishTable[index] = FishData( data )

	def loadBulletData( self, xmlConfig ):
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError,"cannot load %s." % xmlConfig
		for item in section.values():
			valueFlag = item.readString( "valueFlag" )
			value = item.readInt( valueFlag )
			type = item.readInt( "type" )
			if valueFlag == "money":
				self.bullets[type] = MoneyBullet( type, value )
			else:
				self.bullets[type] = SilverBullet( type, value )

	def loadFishItem( self, path ):
		"""
		"""
		section = Language.openConfigSection( path )
		if section is None:
			raise SystemError,"cannot load %s." % path
		successCount = 0
		failedCount = 0
		for sectionItem in section.values():
		#try:
			data = { "persistent":sectionItem.readInt( "persistent" ), \
					"magnification":sectionItem.readInt( "magnification" ), \
					"type":sectionItem.readInt( "type" ), \
					"amount":sectionItem.readInt( "amount" ), \
					}
			item = MagnificationCard( data )
			self.fishItems[item.getType()] = item
		#except Exception, errstr:
			#ERROR_MSG( "itemType:, errstr:%s." %( errstr ) )
			#failedCount += 1
		#successCount += 1
		#INFO_MSG( "complet..success:%i, failed:%i." % ( successCount, failedCount ) )

	def loadItemDropOdds( self, path ):
		section = Language.openConfigSection( path )
		if section is None:
			raise SystemError,"cannot load %s." % path
		dropData = []
		totalRate = 0
		for sectionItem in section.values():
			rate = sectionItem.readInt( "rate" )
			itemType = sectionItem.readInt( "itemType" )
			totalRate += rate
			dropData.append( {"rate":rate, "itemType":itemType} )
		self.dropBox.init( totalRate, dropData )

	def loadCaptureRateAmend( self, path ):
		"""
		加载捕获修正率配置

		"""
		section = Language.openConfigSection( path )
		if section is None:
			raise SystemError,"cannot load %s." % path
		for item in section.values():
			moneyType = item.readInt( "lossType" )
			fishType = item.readInt( "fishType" )
			lossValuePoint = item.readInt( "lossValuePoint" )
			rateAmend = item.readFloat( "rateAmend" )
			self.rateAmendTable[( moneyType, fishType, lossValuePoint )] = rateAmend	# 建立根据货币类型、鱼类型、损失点 到捕获修正率的直接映射。
			if moneyType == csdefine.CURRENCY_TYPE_MONEY:
				self.lossMoneyDistrict.append( lossValuePoint )
				self.moneyRateAmendFishTypes.add( fishType )
			elif moneyType == csdefine.CURRENCY_TYPE_SILVER:
				self.lossSilverDistrict.append( lossValuePoint )
				self.silverRateAmendFishTypes.add( fishType )
			else:
				ERROR_MSG( "money( %i ) type undefine in fishType( %i ), lossValuePoint( %i )." % ( moneyType, fishType, lossValuePoint ) )
		self.lossMoneyDistrict.sort()
		self.lossSilverDistrict.sort()
		DEBUG_MSG( self.lossMoneyDistrict, self.lossSilverDistrict, self.rateAmendTable )

	def getCaptureRateAmend( self, moneyType, fishType, lossValue ):
		if moneyType == csdefine.CURRENCY_TYPE_MONEY:
			lossDistrict = self.lossMoneyDistrict
			if fishType not in self.moneyRateAmendFishTypes:
				return 0
		else:
			lossDistrict = self.lossSilverDistrict
			if fishType not in self.silverRateAmendFishTypes:
				return 0

		if len( lossDistrict ) == 0:
			return 0
		if lossValue < lossDistrict[0]:
			return 0
		if lossValue >= lossDistrict[-1]:
			lossValuePoint = lossDistrict[-1]
		else:# 二分查找法快速定位
			minIdx = 0
			maxIdx = len( lossDistrict ) -1
			while minIdx  <= maxIdx:
				idx = (minIdx + maxIdx) / 2
				if lossDistrict[idx] > lossValue:
					maxIdx = idx - 1
				else:
					minIdx = idx + 1
			lossValuePoint = lossDistrict[minIdx-1]

		key = ( moneyType, fishType, lossValuePoint )
		DEBUG_MSG( moneyType, fishType, lossValue, lossValuePoint )
		if self.rateAmendTable.has_key( key ):
			return self.rateAmendTable[key]
		return 0

	def dropItem( self ):
		return self.dropBox.dropItem()

	def generateSpecies( self, room ):
		"""
		根据鱼的类型生成room的fish类型管理实例
		"""
		speciesList = []
		for index, fishData in self.fishTable.iteritems():
			if fishData.memberAmount > 1:
				speciesList.append( GroupFishSpecies( fishData, room ) )
			else:
				speciesList.append( FishSpecies( fishData, room ) )
		return speciesList

	def getFishMoneyValue( self, index ):
		return self.fishTable[index].getMoneyValue()

	def getFishSilverValue( self, index ):
		return self.fishTable[index].getSilverValue()

	def getFishMoveSpeed( self, index ):
		return self.fishTable[index].getMoveSpeed()

	def getFishBornDelay( self, index ):
		return self.fishTable[index].getSupplyDelay()

	def getFishMemberAmount( self, index ):
		return self.fishTable[index].getMemberAmount()

	def getFishFormation( self, index ):
		return self.fishTable[index].getFormation()

	def hasBulletType( self,bulletType ):
		return self.bullets.has_key( bulletType )

	def getBullet( self, bulletType ):
		return self.bullets[bulletType]

	def getFishItem( self, itemType ):
		return self.fishItems[itemType]

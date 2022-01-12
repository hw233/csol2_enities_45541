# -*- coding:gb18030 -*-

import Language
from bwdebug import ERROR_MSG


class FishingDataMgr:

	_instance = None

	def __init__( self ):
		assert FishingDataMgr._instance is None, "You should invoke the instance method."
		self._fishesData = {}
		self._cannonballsData = {}
		self._multipleCardsData = {}
		self._effectDataMgr = FishingEffectMgr()

	@classmethod
	def instance(self):
		if FishingDataMgr._instance is None:
			FishingDataMgr._instance = FishingDataMgr()
		return FishingDataMgr._instance

	def loadFishData( self, configPath ):
		""""""
		section = Language.openConfigSection(configPath)
		for item in section.values():
			data = {}
			style = item.readInt("style")
			data["name"] = item.readString("name")
			data["coin"] = item.readInt("coinValue")     # 配置里填的以铜为单位
			data["ingot"] = item.readInt("ingotValue")
			data["speed"] = item.readFloat("speed")
			data["model"] = item.readString("modelNumber")
			data["scale"] = item.readFloat("modelScale")
			data["moveEffect"] = item.readInt("moveEffect")
			data["turnEffect"] = item.readInt("turnEffect")
			self._fishesData[style] = data
		Language.purgeConfig(configPath)

	def loadCannonballData( self, configPath ):
		""""""
		section = Language.openConfigSection(configPath)
		for item in section.values():
			data = {}
			level = item.readInt("level")
			data["name"] = item.readString("name")
			currency = item["price"].readString("currency")
			if currency == "money":
				price = CoinPrice(item["price"].readInt("value"))
			elif currency == "silver":
				price = IngotPrice(item["price"].readInt("value"))
			else:
				ERROR_MSG("Unknown price type of %s." % currency)
				continue
			data["price"] = price
			data["coin"] = item.readInt("coinValue")
			data["ingot"] = item.readInt("ingotValue")
			data["speed"] = item.readFloat("speed")
			data["model"] = item.readString("modelNumber")
			data["scale"] = item.readFloat("modelScale")
			data["normalRange"] = item.readFloat("normalRange")
			data["explodeRange"] = item.readFloat("explodeRange")
			data["moveEffect"] = item.readInt("moveEffect")
			self._cannonballsData[level] = data
		Language.purgeConfig(configPath)

	def loadMultipleCardData(self, configPath):
		""""""
		section = Language.openConfigSection(configPath)
		for item in section.values():
			data = {}
			type = item.readInt("type")
			data["speed"] = item.readFloat("speed")
			data["model"] = item.readString("modelNumber")
			data["scale"] = item.readFloat("modelScale")
			data["multiple"] = item.readInt("magnification")
			data["persistent"] = item.readInt("persistent")
			self._multipleCardsData[type] = data
		Language.purgeConfig(configPath)

	def loadEffectData(self, path):
		""""""
		self._effectDataMgr.loadFromXML(path)

	def getFishDataByStyle( self, style ):
		""""""
		return self._fishesData.get(style)

	def getCannonballDataByLevel( self, level ):
		""""""
		return self._cannonballsData.get(level)

	def getCannonballDatas(self):
		""""""
		return self._cannonballsData.copy()

	def getCannonballPriceByLevel(self, level):
		""""""
		return self.getCannonballDataByLevel(level)["price"]

	def getRewardTypeByCannonballLevel(self, level):
		""""""
		return self.getCannonballPriceByLevel(level).type()

	def getMultipleCardDataByType(self, type):
		""""""
		return self._multipleCardsData.get(type)

	def getEffectByID(self, effectID):
		""""""
		return self._effectDataMgr.getEffectByID(effectID)


class Price:

	def __init__(self, value, type):
		self._value = value
		self._type = type

	@property
	def value(self):
		return self._value

	def type(self):
		return self._type

	def checkForPay(self, fisher):
		return False

	def deduct(self, fisher):
		pass

	def unitNumber(self, fisher):
		pass

	def sell(self, fisher, amount):
		pass

	def maxSellTo(self, player):
		return 0

class CoinPrice(Price):

	def __init__(self, value):
		Price.__init__(self, value, "coin")

	def checkForPay(self, fisher):
		return fisher.payCoinCheck(self._value * fisher.magnification())

	def deduct(self, fisher):
		return fisher.payCoin(self._value * fisher.magnification())

	def unitNumber(self, fisher):
		return int(fisher.fishingCoin() / (self._value * fisher.magnification()))

	def sell(self, fisher, amount):
		cost = amount * self._value * fisher.magnification()
		fisher.buyCoinBullet(cost)

	def maxSellTo(self, player):
		return player.money / (self._value * player.magnification)


class IngotPrice(Price):

	def __init__(self, value):
		Price.__init__(self, value, "ingot")

	def checkForPay(self, fisher):
		return fisher.payIngotCheck(self._value * fisher.magnification())

	def deduct(self, fisher):
		return fisher.payIngot(self._value * fisher.magnification())

	def unitNumber(self, fisher):
		return int(fisher.fishingIngot() / (self._value * fisher.magnification()))

	def sell(self, fisher, amount):
		cost = amount * self._value * fisher.magnification()
		fisher.buyIngotBullet(cost)

	def maxSellTo(self, player):
		return player.silver / (self._value * player.magnification)


class FishingEffectMgr:

	def __init__(self):
		self._datas = {}

	def _particlesFromSection(self, section):
		""""""
		particles = []

		e_scale = section.readFloat("scale")
		e_duration = section.readFloat("duration")

		for p_sect in section["particles"].values():
			p_source = p_sect.readString("source")
			p_scale = p_sect.readFloat("scale", e_scale)
			p_duration = p_sect.readFloat("duration", e_duration)
			p_hardPoints = tuple(p_sect.readString("hard_points").split())
			particles.append((p_source, p_scale, p_duration, p_hardPoints))

		return tuple(particles)

	def loadFromXML(self, path):
		""""""
		section = Language.openConfigSection(path)
		for item in section.values():
			e_id = item.readInt("id")
			self._datas[e_id] = self._particlesFromSection(item)

		Language.purgeConfig(path)

	def getEffectByID(self, effectID):
		""""""
		return self._datas.get(effectID)

# -*- coding: gb18030 -*-

#$Id: ItemSystemExp.py,v 1.32 2008-08-18 06:09:38 yangkai Exp $

from bwdebug import *
import Language
import random
import Function
import ItemTypeEnum
import math
import copy
import csdefine
import csconst
from config.item import ItemTypeAmend
from config.item import EquipQualityInfo
from config.item import EquipPrefixInfo

from config.item import EquipMake
from config.item import StuffInfo

from config.item import EquipBind

from config.item import EquipStudded
from config.item import EquipStiletto

from config.item import RemoveCrystal
from config.item import ChangeProperty

from config.item import EquipImproveQuality

from config.item import StuffMerge

from config.item import SpecialCompose

from config.item import IntensifyLuckGem
from config.item import EquipIntensify
from config.item import IntensifyDragonGem

from config.item import PrefixAllot

from config.item import EquipSplit

from config.item import PrefixDistribute as prefixdistribute

from config.item import A_PropertyPrefix

from config.item import TalismanSplit

from config.item import TalismanIntensify

from config.item import EquipGodWeapon

from config.item import GodWeaponSkills

from config.item import SpecialStuffCompose

from config.item.EquipDefenceLevelConfig import Datas as equipDefenceData
from config.item.EquipPriceGeneLevelConfig import Datas as equipPriceGeneData
from config.item.AttrOutputPro import Datas as E_Data
from config.item.ScrollAttrOutputPro import Datas as S_Data
from config.item.LevelAttrOutputPro import Datas as L_Data
import CombatUnitConfig

# ----------------------------------------------------------------------------------------------------
# 神机匣功能
# 材料合成公式
# ----------------------------------------------------------------------------------------------------
class StuffMergeExp:
	"""
	材料合成公式
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：value}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert StuffMergeExp._instance is None, "instance already exist in"
		StuffMergeExp._instance = self
		self._datas = StuffMerge.Datas		# like as { baseAmount : { "srcItemID" : { "odds" : odds, "dstItem" : dstItem }... } ... }
		self._useItemIDs = StuffMerge.UseItemIDs

	@staticmethod
	def instance():
		if StuffMergeExp._instance is None:
			StuffMergeExp._instance = StuffMergeExp()
		return StuffMergeExp._instance

	def getOdds( self, baseAmount, itemID ):
		"""
		通过基数和源材料物品ID，获取成功率
		@param		baseAmount: 合成基数
		@type		baseAmount: Int
		@param		itemID: 物品ID
		@type		itemID: ITEM_ID
		@return		int
		"""
		try:
			return self._datas[ baseAmount ][itemID]["odds"]
		except KeyError:
			ERROR_MSG( "Can't find odds Config by ( baseAmount --> %s) ( itemID -->> %s )" % ( baseAmount, itemID ) )
			return 0

	def getPrice( self, baseAmount, itemID ):
		"""
		通过基数和原来ID获取合成价格 by姜毅
		"""
		try:
			return self._datas[ baseAmount ][ itemID ][ "price" ]
		except KeyError:
			ERROR_MSG( "Can't find price Config by ( baseAmount --> %s) ( itemID -->> %s )" % ( baseAmount, itemID ) )
			return 0

	def getDstItemID( self, baseAmount, itemID ):
		"""
		通过基数和源材料物品ID，获取合成物品ID
		@param		baseAmount: 合成基数
		@type		baseAmount: Int
		@param		itemID: 物品ID
		@type		itemID: ITEM_ID
		@return		int
		"""
		try:
			return self._datas[ baseAmount ][itemID]["dstItemID"]
		except KeyError:
			ERROR_MSG( "Can't find odds Config by ( baseAmount --> %s) ( itemID -->> %s )" % ( baseAmount, itemID ) )
			return 0

	def getAdditiveInfo( self, baseAmount, itemID ):
		"""
		通过基数和原料获取合成所需的添加剂ID和数量 by姜毅
		"""
		try:
			return self._datas[ baseAmount ][itemID]["additive"]
		except KeyError:
			ERROR_MSG( "Can't find additive Config by ( baseAmount --> %s) ( itemID -->> %s )" % ( baseAmount, itemID ) )
			return {}

	def canMerge( self, itemID ):
		"""
		判断该物品是否能合成
		@param		itemID: 物品ID
		@type		itemID: ITEM_ID
		@return		Bool
		"""
		return itemID in self._useItemIDs

# ----------------------------------------------------------------------------------------------------
# 神机匣功能
# 装备强化公式
# ----------------------------------------------------------------------------------------------------
class EquipIntensifyExp:
	"""
	装备强化公式
	@ivar _data: 全局数据字典; key is id, value is dict
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipIntensifyExp._instance is None, "instance already exist in"
		EquipIntensifyExp._instance = self
		self._datas = EquipIntensify.Datas				# like as { intensifyLevel : { "intensifyOdds" : odds...} , ... }
		self._dragonGemDict = IntensifyDragonGem.Datas["intenData"]
		self._dragonLevel = IntensifyDragonGem.Datas["levelData"]
		self._luckGemDict = IntensifyLuckGem.Datas

	@staticmethod
	def instance():
		if EquipIntensifyExp._instance is None:
			EquipIntensifyExp._instance = EquipIntensifyExp()
		return EquipIntensifyExp._instance

	def isDragonGem( self, item ):
		"""
		判断物品是否是强化材料：龙珠
		"""
		return item.id in [ tempKey[0] for tempKey in self._dragonGemDict.keys() ]

	def isLuckGem( self, item ):
		"""
		判断物品是否强化材料：幸运宝石
		"""
		return item.id in self._luckGemDict.keys()

	def getMinLevel( self, itemID ):
		"""
		根据ID获取能强化的最低等级
		"""
		try:
			return self._dragonLevel[itemID]["minLevel"]
		except:
			ERROR_MSG("Can't find %s 's Config By getMinLevel" % itemID )
			return 0

	def getMaxLevel( self, itemID ):
		"""
		根据ID获取能强化的最高等级
		"""
		try:
			return self._dragonLevel[itemID]["maxLevel"]
		except:
			ERROR_MSG("Can't find %s 's Config By getMaxLevel" % itemID )
			return 0

	def getOdds( self, intensifyLevel ):
		"""
		根据强化等级获取成功率
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 	INT32
		"""
		try:
			return self._datas[intensifyLevel]["intensify_odds"]
		except:
			ERROR_MSG("Can't find %s 's Config By getOdds" % intensifyLevel )
			return 0

	def getBaseRate( self, intensifyLevel, quality, prefix ):
		"""
		根据强化等级和品质和前缀获取强化的基础附加属性比率值
		@param		intensifyLevel	: 强化等级
		@type		intensifyLevel	: UINT8
		@param		quality			: 品质
		@type		quality			: UINT8
		@param		prefix			: 前缀
		@type		prefix			: UINT8
		@return						: Float
		"""
		# 这次，装备强化只根据品质来修改基础属性值 by 姜毅 17:03 2009-11-26
		if quality == ItemTypeEnum.CQT_GREEN:
			idata = self._datas.get( intensifyLevel )
			if idata is None: return 0.0
			data = idata.get( "prefix_map" )
			key = prefix
			if data is None: return 0.0
			baseRate = data.get( key )
			if baseRate is None: return data[ItemTypeEnum.CPT_MYTHIC]		# 让无前缀的家伙也能有基础比率提升
			return baseRate
		else:
			idata = self._datas.get( intensifyLevel )
			if idata is None: return 0.0
			data = idata.get( "quality_map" )
			key = quality
			if data is None: return 0.0
			baseRate = data.get( key )
			if baseRate is None: return 0.0
			return baseRate

	def setIntensifyValue( self, equip, dragonGemID, intensifyLevel ):
		"""
		由龙珠的类型和强化级别设置装备强化提升值
		"""
		equipType = equip.getType()
		maskCode = 0xff0000										# 装备类型掩码
		equipLevel = int ( ( equip.getReqLevel()- 1 ) / 10 )
		if equipType & maskCode == ItemTypeEnum.ITEM_WEAPON:	# 提升装备的物理攻击力和法术攻击力
			intensifyValue = equip.getIntensifyValue()			# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			phys_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_damage_inc" ]
			magic_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_damage_inc" ]
			intensifyValue[ 0 ][ 0 ] += phys_damage_inc
			intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType & maskCode == ItemTypeEnum.ITEM_ARMOR:	# 提升装备的防御力
			intensifyValue = equip.getIntensifyValue()			# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			phys_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_defence_inc" ]
			magic_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_defence_inc" ]
			intensifyValue[ 1 ][ 0 ] += phys_defence_inc
			intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_NECKLACE:	# 提升装备的防御力
			intensifyValue = equip.getIntensifyValue()			# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			phys_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_defence_inc" ]
			magic_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_defence_inc" ]
			intensifyValue[ 1 ][ 0 ] += phys_defence_inc
			intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_RING:		# 提升装备的物理攻击力和法术攻击力
			intensifyValue = equip.getIntensifyValue()			# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			phys_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_damage_inc" ]
			magic_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_damage_inc" ]
			intensifyValue[ 0 ][ 0 ] += phys_damage_inc
			intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )


	def setIntensifyFailedValue( self, equip, dragonGemID, intensifyLevel ):
		"""
		强化失败,设置装备数据

		@param equip : 装备
		@type equip : ITEM
		@param dragonGemID : 用于强化的龙珠id
		@type dragonGemID : ITEM_ID
		@param intensifyLevel : 强化级别
		@type intensifyLevel : UINT8
		"""
		equipType = equip.getType()
		maskCode = 0xff0000										# 装备类型掩码
		equipLevel = int ( ( equip.getReqLevel()- 1 ) / 10 )
		if equipType & maskCode == ItemTypeEnum.ITEM_WEAPON:	# 提升装备的物理攻击力和法术攻击力
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_damage_inc" ]
				magic_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_damage_inc" ]
				intensifyValue[ 0 ][ 0 ] += phys_damage_inc
				intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType & maskCode == ItemTypeEnum.ITEM_ARMOR:	# 提升装备的防御力
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_defence_inc" ]
				magic_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_defence_inc" ]
				intensifyValue[ 1 ][ 0 ] += phys_defence_inc
				intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_NECKLACE:	# 提升装备的防御力
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_defence_inc" ]
				magic_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_defence_inc" ]
				intensifyValue[ 1 ][ 0 ] += phys_defence_inc
				intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_RING:		# 提升装备的物理攻击力和法术攻击力
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValue为[ ( 强化的物理攻击力, 强化的魔法攻击力 ), ( 强化的物理防御值, 强化的魔法防御值 ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_damage_inc" ]
				magic_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_damage_inc" ]
				intensifyValue[ 0 ][ 0 ] += phys_damage_inc
				intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )


	def getFiledLevel( self, intensifyLevel ):
		"""
		根据强化等级获取强化失败后掉落到的强化等级
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 	Int
		"""
		try:
			return self._datas[intensifyLevel]["intensify_filedLevel"]
		except:
			ERROR_MSG("Can't find %s 's Config By getFiledLevel" % intensifyLevel )
			return 0

	def getRequirementUpLimit( self, intensifyLevel ):
		"""
		根据强化等级获取强化65级以上装备的原料需求
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 	{ "itemID" ：itemAmount }
		"""
		try:
			data = self._datas[intensifyLevel]
			return { data["intensify_needHigh"] : data["intensify_amountHigh"] }
		except:
			ERROR_MSG("Can't find %s 's Config By getRequirementUpLimit" % intensifyLevel )
			return {}

	def getReqMoney( self, level, intensifyLevel ):
		"""
		根据强化等级获取强化所烧钱 by姜毅
		"""
		return level * intensifyLevel * 10

	def getRequirementDownLimit( self, intensifyLevel ):
		"""
		根据强化等级获取强化65级以下装备的原料需求
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 	{ "itemID" ：itemAmount }
		"""
		try:
			data = self._datas[intensifyLevel]
			return { data["intensify_needLow"] : data["intensify_amountLow"] }
		except:
			ERROR_MSG("Can't find %s 's Config By getRequirementDownLimit" % intensifyLevel )
			return {}

	def getExtraItem( self, intensifyLevel ):
		"""
		根据强化等级获取额外附加物品
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 	ItemID
		"""
		try:
			return self._datas[intensifyLevel]["intensify_extraItem"]
		except:
			ERROR_MSG("Can't find %s 's Config By getExtraItem" % intensifyLevel )
			return ""

	def getExtraPerOdds( self, intensifyLevel ):
		"""
		根据强化等级获取额外附加物品
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 	ItemID
		"""
		try:
			return self._datas[intensifyLevel]["intensify_extraPerOdds"]
		except:
			ERROR_MSG("Can't find %s 's Config By getExtraPerOdds" % intensifyLevel )
			return ""

	def getExtraOdds( self, luckGemID ):
		"""
		根据幸运水晶的id获得强化成功率

		@param luckGemID : 幸运水晶的id
		@type luckGemID : ITEM_ID
		"""
		assert self._luckGemDict.has_key( luckGemID )
		return self._luckGemDict[ luckGemID ]

	def isShine( self, intensifyLevel ):
		"""
		根据强化等级获取该等级是否发光
		@param		intensifyLevel: 强化等级
		@type		intensifyLevel: UINT8
		@return 					Bool
		"""
		try:
			return self._datas[intensifyLevel]["intensify_isShine"]
		except:
			ERROR_MSG("Can't find intensify_isShine config by intensifyLevel(%s)" % intensifyLevel )
			return False

# ----------------------------------------------------------------------------------------------------
# 神机匣功能
# 绿装升品公式
# ----------------------------------------------------------------------------------------------------
class EquipImproveQualityExp:
	"""
	绿装升品公式
	@ivar _data: 全局数据字典; key is id, value is dict
	@type _data: dict
	"""
	_instance = None

	def __init__(self):
		assert EquipImproveQualityExp._instance is None, "instance already exist in"
		EquipImproveQualityExp._instance = self
		self._datas = EquipImproveQuality.Datas
		self._badge = EquipImproveQuality.Datas["itemData"]




	@staticmethod
	def instance():
		if EquipImproveQualityExp._instance is None:
			EquipImproveQualityExp._instance = EquipImproveQualityExp()
		return EquipImproveQualityExp._instance

	def isBadge( self , item ):
		"""
		判断物品是否是升品材料：神话徽章或者逆天徽章
		"""
		return item.id in self._badge

	def getOdds( self, badgeID, prefix ):
		try:
			return self._datas["improveQualityData"][( badgeID, prefix)]["improveQuality_odds"]
		except:
			ERROR_MSG("can't find ( %s, %s) config by getOdds"%( badgeID, prefix))
			return 0

	def setImproveQualityPrefix( self, equip , badgeID):
		"""
		由装备的前缀和徽章的类型设置装备的新的前缀
		"""
		prefix = equip.getPrefix()
		newPrefix=self._datas["improveQualityData"][( badgeID, prefix)]["result_prefix"]
		equip.setPrefix(newPrefix)

	def setImproveQualityFailedPrefix( self, equip , badgeID):
		pass

# ----------------------------------------------------------------------------------------------------
# 神机匣功能
# 装备镶嵌相关公式
# ----------------------------------------------------------------------------------------------------
class EquipStuddedExp:
	"""
	装备镶嵌相关公式
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipStuddedExp._instance is None, "instance already exist in"
		EquipStuddedExp._instance = self
		self._cDatas = EquipStiletto.Datas			# like as { stiletto_amount : stiletto_cost, ... }
		self._sDatas = EquipStudded.Datas			# like as { itemID : itemAmount }
		self._oDatas = EquipStiletto.Odds

	@staticmethod
	def instance():
		if EquipStuddedExp._instance is None:
			EquipStuddedExp._instance = EquipStuddedExp()
		return EquipStuddedExp._instance

	def getCost( self, holeIndex ):
		"""
		根据装备的孔位数数量获取打此孔需要的花费
		@type  holeIndex: UINT8
		@param holeIndex: 需求打孔的位数
		@return			: UINT 32
		"""
		try:
			return self._cDatas[holeIndex]
		except KeyError:
			ERROR_MSG( "Can't find StilettoCost config by %s " % holeIndex )
			return 0

	def getStilettoOdds( self, holes ):
		"""
		根据装备孔数获取成功率 by姜毅
		@type  holes: UINT8
		@param holes: 现有孔数
		@return		: UINT 32
		"""
		try:
			return self._oDatas[ holes ]
		except KeyError:
			ERROR_MSG( "Can't find StilettoOdd config by %s " % holes )
			return 0

	def getStuff( self ):
		"""
		返回装备镶嵌所需材料
		@return	Dic
		"""
		return self._sDatas.values()

# ----------------------------------------------------------------------------------------------------
# 装备品质前缀相关公式
# ----------------------------------------------------------------------------------------------------
class EquipQualityExp:
	"""
	装备品质相关公式
	装备的制造及装备的升级，装备的随机等都会用到，故分开初始化
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipQualityExp._instance is None, "instance already exist in"
		EquipQualityExp._instance = self
		self._datas = EquipQualityInfo.Datas
		self._pDatas = EquipPrefixInfo.Datas
		self.Q_EXCRATE_MAP = {	ItemTypeEnum.CPT_NORMAL			: "excQuaRatePrefix1",
								ItemTypeEnum.CPT_APPLIED		: "excQuaRatePrefix2",
								ItemTypeEnum.CPT_INTENSIFY		: "excQuaRatePrefix3",
								ItemTypeEnum.CPT_EXCELLENT		: "excQuaRatePrefix4",
								ItemTypeEnum.CPT_COSTFULL		: "excQuaRatePrefix5",
								ItemTypeEnum.CPT_FABULOUS		: "excQuaRatePrefix6",
								ItemTypeEnum.CPT_MYTHIC			: "excQuaRatePrefix7",
								ItemTypeEnum.CPT_MYGOD			: "excQuaRatePrefix8",
							}
		self.Q_BASERATE_MAP = { ItemTypeEnum.CPT_NORMAL			: "baseQualityRate",
								ItemTypeEnum.CPT_APPLIED		: "baseQualityRate",
								ItemTypeEnum.CPT_INTENSIFY		: "baseQualityRate",
								ItemTypeEnum.CPT_EXCELLENT		: "baseQualityRate",
								ItemTypeEnum.CPT_COSTFULL		: "baseQualityRate",
								ItemTypeEnum.CPT_FABULOUS		: "baseQualityRate6",
								ItemTypeEnum.CPT_MYTHIC			: "baseQualityRate7",
								ItemTypeEnum.CPT_MYGOD			: "baseQualityRate8",
							}

	@staticmethod
	def instance():
		if EquipQualityExp._instance is None:
			EquipQualityExp._instance = EquipQualityExp()
		return EquipQualityExp._instance

	def getColorByQuality( self, quality ):
		"""
		通过装备品质返回装备颜色值(vector3)
		@type  quality: UNIT8
		@param quality: 装备品质
		@return:        vector3
		"""
		try:
			return tuple( self._datas[quality]["color"] )
		except:
			return ( 255,255,255 )

	def getBaseRateByQuality( self, quality, prefix ):
		"""
		通过装备品质返回装备基础属性品质比率
		@type  quality		: UNIT8
		@param quality		: 装备品质
		@type  prefix		: UNIT8
		@param prefix		: 装备前缀
		@return				: Float
		"""
		# 现在已经去掉了前缀，于是默认都是普通的
		key = self.Q_BASERATE_MAP.get( ItemTypeEnum.CPT_NORMAL )
		if key is None: return 0.0

		qData = self._datas.get( quality )
		if qData is None: return 0.0

		baseRate = qData.get( key )
		if baseRate is None: return 0.0

		return baseRate

	def getRepairRateByQuality( self, quality ):
		"""
		通过装备品质返回装备基础属性品质比率
		@type  quality: UNIT8
		@param quality: 装备品质
		@return:        Float
		"""
		try:
			return self._datas[quality]["repairQualityRate"]
		except:
			return 0.0

	def getexcRateByQandP( self, quality, prefix ):
		"""
		根据装备品质和装备前缀返回附加属性品质比率
		@type  quality: UNIT8
		@param quality: 装备品质
		@type  prefix: UNIT8
		@param prefix: 装备前缀
		@return:        Float
		"""
		key = self.Q_EXCRATE_MAP.get( prefix )
		if key is None: return 0.0

		qData = self._datas.get( quality )
		if qData is None: return 0.0

		excRate = qData.get( key )
		if excRate is None: return 0.0

		return excRate

	def getName( self, prefix ):
		"""
		通过装备前缀返回前缀显示名
		@type  prefix: UNIT8
		@param prefix: 装备前缀
		@return:        String
		"""
		try:
			return self._pDatas[prefix]["name"]
		except:
			return ""

	def getRebuildRate( self, prefix ):
		"""
		通过装备前缀返回改造前缀占的比率
		@type  prefix: UNIT8
		@param prefix: 装备前缀
		@return:        Int
		"""
		try:
			return self._pDatas[prefix]["rebuild_rate"]
		except KeyError:
			ERROR_MSG( "Can't find RebuildRate config by %s" % prefix )
			return 0

	def getMakeRate( self, prefix ):
		"""
		通过装备前缀返回制造中占的前缀比率
		@type  prefix: UNIT8
		@param prefix: 装备前缀
		@return:        Int
		"""
		try:
			return self._pDatas[prefix]["make_rate"]
		except KeyError:
			ERROR_MSG( "Can't find MakeRate config by %s" % prefix )
			return 0

	def getIntensifyColor( self, quality ):
		"""
		通过装备品质返回装备强化发光颜色
		return as ( r, g, b, c ) 前面3个是RGB值，最后一个是透明度
		@type  quality: UNIT8
		@param quality: 装备品质
		@return:        Vector4
		"""
		try:
			return self._datas[quality]["intensifyColor"]
		except:
			ERROR_MSG( "Can't find intensifyColor config by quality(%s)" % quality )
			return ( 1, 1, 1, 1 )

#-----------------------------------------------------------------------------------------------------
#各职业的装备前缀B的生成概率数据加载
#-----------------------------------------------------------------------------------------------------
class PrefixDistribute:
	"""
	各职业的装备前缀B的生成概率数据加载
	"""
	_instance = None

	def __init__(self):
		assert PrefixDistribute._instance is None,"PrefixDistribute instance already exist"
		self.__datas = prefixdistribute.Datas


	def getPrefixs_RC_EQ_EL( self, equipClass, equipQuality, equipLevel ):
		"""
		获取前缀的生成数据
		"""
		try:
			return self.__datas[equipClass][equipQuality][equipLevel]
		except:
			ERROR_MSG("equipClass = %s equipQuality = %s equipLevel = %s has no prefix" % (equipClass, equipQuality, equipLevel) )
			return ()

	def getPrefixs_RC_EQ( self, equipClass, equipQuality ):
		"""
		获取前缀的生成数据
		"""
		try:
			return self.__datas[equipClass][equipQuality]
		except:
			ERROR_MSG("equipClass = %s equipQuality = %s has no prefix" % (equipClass, equipQuality ) )
			return {}

	def __randomPrefix( self, equipType, perfixs ):
		"""
		根据概率随机获取一个前缀
		"""
		if perfixs is None: return 0

		n_odds = random.random()
		for id, odds in perfixs:
			if ( n_odds <= odds ) and ( not PropertyPrefixExp.instance().isLimitType( id, equipType ) ):
				return id

		randomAttrs = random.sample( perfixs, len( perfixs ) )

		for id, odds in randomAttrs:										#当没有找到合适的属性的时候，把原本的列表打乱，在取一个合适属性
			if not PropertyPrefixExp.instance().isLimitType( id, equipType ):
				return id

		return 0

	def randomPrefixID( self, equipClass, equipType, equipQuality, equipLevel ):
		"""
		获取一个前缀
		"""
		prefixs_l = self.getPrefixs_RC_EQ( equipClass, equipQuality)
		if len( prefixs_l ) == 0: return 0

		levelList = sorted(prefixs_l.keys())	#因为字典是无序的所以需要排列
		for level in levelList:
			if equipLevel <= level :
				return self.__randomPrefix( equipType, prefixs_l.get( level ) )

	@staticmethod
	def instance():
		if PrefixDistribute._instance is None:
			PrefixDistribute._instance = PrefixDistribute()
		return PrefixDistribute._instance

#-----------------------------------------------------------------------------------------------------
#装备前缀B的分配和附加属性生成的相关
#-----------------------------------------------------------------------------------------------------
class PrefixAllotExp:
	"""
	加载各种品质的物品的前缀的分布和该品质的各个属性的价值因子分布
	"""
	_instance = None

	def __init__( self ):
		assert PrefixAllotExp._instance is None, "PrefixAllotExp instance already exist"
		self._datas = PrefixAllot.Datas

	@staticmethod
	def instance():
		if PrefixAllotExp._instance is None:
			PrefixAllotExp._instance = PrefixAllotExp()
		return PrefixAllotExp._instance

	def getPreAmountByQuality( self, quality ):
		"""
		获取附加属性的条数
		"""
		try:
			return self._datas[quality]["property"]
		except:
			ERROR_MSG(" quality %s has no propertyNum" % quality)
			return 0

	def getGeneRateDist( self, quality ):
		"""
		获取附加属性 各个属性的分配率
		"""
		try:
			return self._datas[quality]["effect_rate"]
		except:
			ERROR_MSG(" quality %s has no effect_rate" % quality)
			return 0


# ----------------------------------------------------------------------------------------------------
# 属性前缀相关
# ----------------------------------------------------------------------------------------------------
class PropertyPrefixExp:
	"""
	属性前缀相关的信息
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert PropertyPrefixExp._instance is None, "PropertyPrefixExp instance already exist in"
		self._datas = A_PropertyPrefix.Datas

	@staticmethod
	def instance():
		if PropertyPrefixExp._instance is None:
			PropertyPrefixExp._instance = PropertyPrefixExp()
		return PropertyPrefixExp._instance

	def getEffectIDs( self, proPrefixID ):
		"""
		根据属性前缀ID返回该ID包含的效果ID
		"""
		try:
			return self._datas[ proPrefixID ][ "effect_id" ]
		except:
			ERROR_MSG( "PropertyPrefixExp.getEffectIDs  has no PropertyproPrefix id %s" % proPrefixID )
			return []

	def getProPrefixName( self, proPrefixID ):
		"""
		根据属性前缀的ID获取该属性前缀的名称
		"""
		try:
			return self._datas[ proPrefixID ]["prefix_name"]
		except:
			ERROR_MSG( "PropertyPrefixExp.getProPrefixName  has no PropertyproPrefix %s" % proPrefixID )
			return ""

	def getProPrefixLimit( self, proPrefixID ):
		"""
		获取属性前缀限定装备类型列表
		如果为[]则不限制
		return list
		"""
		data = self._datas.get( proPrefixID )
		if data is None: return []

		prefixLimit = data.get( "prefix_limit" )
		if prefixLimit is None: return []

		return prefixLimit

	def isLimitType( self, proPrefixID, type ):
		"""
		判定给定type是否在限定属性ID的产生
		return BOOL
		"""
		limitTypes = self.getProPrefixLimit( proPrefixID )
		if len( limitTypes ) == 0: return False
		if type not in limitTypes: return False
		return True

# ----------------------------------------------------------------------------------------------------
# 装备绑定相关公式
# ----------------------------------------------------------------------------------------------------
class EquipBindExp:
	"""
	装备绑定相关公式
	config/item/EquipBind.xml
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipBindExp._instance is None, "instance already exist in"
		EquipBindExp._instance = self
		self._datas = EquipBind.Datas			# like as { "require" : { itemID : amount }, "perCost" : Money }

	@staticmethod
	def instance():
		if EquipBindExp._instance is None:
			EquipBindExp._instance = EquipBindExp()
		return EquipBindExp._instance

	def getPerCost( self ):
		"""
		获取每等级耗费金钱数
		@return Int
		"""
		try:
			return self._datas["perCost"]
		except:
			ERROR_MSG( "Can't find EquipBindExp config bind_cost" )
			return 0

	def getStuff( self ):
		"""
		获取绑定需求
		@return { itemID : amount }
		"""
		try:
			return self._datas["require"]
		except:
			ERROR_MSG( "Can't find EquipBindExp config bind_require" )
			return {}

# ----------------------------------------------------------------------------------------------------
# 装备制造/改造相关公式
# ----------------------------------------------------------------------------------------------------
class EquipMakeExp:
	"""
	装备制造/改造相关公式
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None
	EQUIP_LEVEL = 70

	def __init__( self ):
		assert EquipMakeExp._instance is None, "instance already exist in"
		EquipMakeExp._instance = self
		self._datas  = EquipMake.Datas			# like as { itemID : { "name" : name, "stuff" : {itemID : amount} },... }
		self._sdatas = StuffInfo.Datas		# like as { itemID : { "stuff_level": lsect.asInt, "stuff_name" : nsect.asString }, ... }
		_pDatas = EquipPrefixInfo.Datas

		rateDict = {}
		rateDict[ItemTypeEnum.CQT_WHITE] = {}
		rateDict[ItemTypeEnum.CQT_BLUE] = {}
		rateDict[ItemTypeEnum.CQT_GOLD] = {}
		rateDict[ItemTypeEnum.CQT_PINK] = {}
		rateDict[ItemTypeEnum.CQT_GREEN] = {}
		for d in _pDatas:
			if d == ItemTypeEnum.CPT_EXCELLENT or d == ItemTypeEnum.CPT_APPLIED:
				continue
			if d < ItemTypeEnum.CPT_FABULOUS:
				rateDict[ItemTypeEnum.CQT_WHITE][_pDatas[d]['rebuild_rate']] = ItemTypeEnum.CPT_NONE
				rateDict[ItemTypeEnum.CQT_BLUE][_pDatas[d]['rebuild_rate']] = d
				rateDict[ItemTypeEnum.CQT_GOLD][_pDatas[d]['rebuild_rate']] = d
				rateDict[ItemTypeEnum.CQT_PINK][_pDatas[d]['rebuild_rate']] = d
			else:
				rateDict[ItemTypeEnum.CQT_GREEN][_pDatas[d]['rebuild_rate']] = d
		self._pDatas = rateDict		# like as { quality:{rate:prefix, rate:prefix, ...}, ... }

	@staticmethod
	def instance():
		if EquipMakeExp._instance is None:
			EquipMakeExp._instance = EquipMakeExp()
		return EquipMakeExp._instance


	def getStuff( self, itemID ):
		"""
		根据物品ID 获取制造/改造该物品ID所需要的材料
		@param itemID	:	物品ID
		@type itemID	:	ITEM_ID
		@return 		:	dic
		"""
		try:
			return self._datas[itemID]["stuff"]
		except KeyError:
			ERROR_MSG( "Can't find EquipMake config by %s" % itemID )
			return {}

	def getAmount( self, itemID ):
		"""
		根据物品ID 获取制造/改造该物品ID所需要的最低材料总数
		@param itemID	:	物品ID
		@type itemID	:	ITEM_ID
		@return 		:	Int
		"""
		amount = 0
		for value in self.getStuff( itemID ).itervalues():
			amount += value
		return amount

	def getLevel( self, itemID ):
		"""
		通过材料ID号获取物品等级
		@param	itemID	: 物品ID
		@type	itemID	: ITEM_ID
		@return			:	int
		"""
		try:
			return self._sdatas[itemID]["stuff_level"]
		except:
			ERROR_MSG( "Can't find EquipMake_Level config by %s" % itemID )
			return 0

	def getEquipLevel( self, equipID ):
		"""
		通过材料ID号获取物品等级
		@param	equipID	: 装备D
		@type	equipID	: String
		@return			:	int
		"""
		try:
			return self._datas[equipID]["level"]
		except:
			ERROR_MSG( "Can't find EquipMake_EquipLevel config by %s" % equipID )
			return 0

	def getClassName( self, itemID ):
		"""
		通过物品ID获取该物品的类名字
		例如 : 080101001 == 原始铁 ，它的系列名字就是 铁
		@param	itemID	: 物品ID
		@type	itemID	: ITEM_ID
		@return 		: String
		"""
		try:
			return self._sdatas[itemID]["stuff_name"]
		except:
			ERROR_MSG( "Can't find EquipMake_Name config by %s" % itemID )
			return ""

	def getSameTypeEquips( self, tag ):
		"""
		通过装备前面位编号获得相同类型装备列表
		"""
		sameTypeEquips = []
		for euipID, euipDict in self._datas.iteritems():
			# 暂时补足9位，防止界面显示问题
			# 将来得改 15:54 2008-8-8 yk
			key = "0" * ( 9 - len( str(euipID) ) ) + str(euipID)
			if key.startswith( tag ):
				sameTypeEquips.append( ( euipID, self._datas[euipID] ) )
		return sameTypeEquips


	def getClassList( self, itemID ):
		"""
		根据原料ID获取该原料类的其他等级高于自身的ID集合
		比如：二级铁的ID是 080101003，这个方法返回的就是铁
		系列的比二级铁等级高的三级铁，四级铁，五级铁 ID集合
		@param	itemID	: 物品ID
		@type	itemID	: ITEM_ID
		@return 		: List
		"""
		itemIDs = []
		itemName = self.getClassName( itemID )
		itemLevel = self.getLevel( itemID )
		for id, data in self._sdatas.iteritems():
			if itemName == self.getClassName( id ) and itemLevel <= self.getLevel( id ):
				itemIDs.append( id )
		return itemIDs

	def isCanMake( self, itemID, itemInfo ):
		"""
		通过物品原料信息判断是否能制造当前itemID
		@param	itemID	: 物品ID
		@type	itemID	: ITEM_ID
		@param	itemInfo: 原料信息
		@type	itemInfo: dic like as {"080101001": 2.......}
		@return 		: Bool
		"""
		# 材料满足规则中，只允许高级材料当级材料匹配
		# 例如：需要2个2级铁，而玩家放入的是10个一级铁，则视为不满足条件(尽管10个一级铁就是2个2级铁)
		# 例如：需要2个2及铁，而玩家放入的是1个2级铁，一个3级铁，则视为满足条件
		dic = self.getStuff( itemID )
		canInStuffs = []
		for id in dic.keys():
			canInStuffs.extend( self.getClassList( id ) )
		if len( canInStuffs ) == 0: return False

		for id, amount in dic.iteritems():
			amountCount = 0
			classItemIDs = self.getClassList( id )
			for id1, amount1 in itemInfo.iteritems():
				if id1 not in canInStuffs: return False
				if id1 in classItemIDs:
					amountCount += amount1
			if amountCount != amount : return False
		return True

	def getOdds( self, equip, itemInfo, quality ):
		"""
		根据物品信息获和制造品质获取成功的概率，白装不计算，如果其他品质的物品不能造出，那么必定能造出白装
		#之前的基数公式：部位折算*材料个数*5^（品质-2）*道具等级/30
		#新公式：p_1=平均材料基数 / 5 ^ [ floor (装备物品等级 / 10)+装备品质系数-7 ]
				p_2=平均材料基数 / 5 ^ (装备品质系数-1)

		@param	dic		: 物品信息 like {"dj1600":2......}
		@type	dic		: dict
		@return	 ( int, float )
		"""
		molecule = 0.0
		totalAmount = self.getAmount( equip.id )
		for itemID, amount in itemInfo.iteritems():
			itemLevel = self.getLevel( itemID )
			molecule += amount * 5**( itemLevel - 1 )

		if equip.getLevel() < EquipMakeExp.EQUIP_LEVEL:		#当装备物品等级<70时，打造成功率=p_1
			return molecule / ( totalAmount * 5 ** ( int( equip.getLevel()/10 ) + quality - 7 ) )

		else:		#当装备物品等级>=70时，打造成功率=p_2
			return molecule / ( totalAmount * 5 ** ( quality - 1 ) )

	def getPrefix( self, quality, rate, rateBase = 0.0 ):
		"""
		根据生成的品质，品质概率，附加品质概率获取前缀
		@param	dic			: 品质
		@type	dic			: int
		@param	dic			: 生成该品质的比率
		@type	dic			: int
		@param	rateBase	: 附加比率
		@type	rateBase	: int
		"""
		#如果计算出制作绿装的几率为80%， 则先判断是否能产出绿装，如果不能那就产出粉装。
		#如果能，则再按80%的几率判断前缀是否为神话（第7个前缀名），如果没有随到，则前缀名为传说（第6个前缀名）。
		#修改随机模块，使用配置EquipPrefixInfo by 姜毅
		rate = (rate + rateBase)*100
		prefixDict = self._pDatas[quality]
		rate_k = prefixDict.keys()
		rate_k.sort()
		odd = random.uniform(0,100)

		for r in rate_k:
			if odd < r:
				return prefixDict[r]

		return ItemTypeEnum.CPT_NONE

# ----------------------------------------------------------------------------------------------------
# 神机匣功能
# 特殊合成公式
# ----------------------------------------------------------------------------------------------------
class SpecialComposeExp:
	"""
	特殊合成公式
	config/item/ArmorAmend.xml
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert SpecialComposeExp._instance is None, "instance already exist in"
		SpecialComposeExp._instance = self
		self._datas = SpecialCompose.Datas # like as { scrollitemID:{"dstItemID" : dstItemID,"amount" : dstAmount,  "srcItems" : [(srcitemID1:amount1),...)] ,} 

	@staticmethod
	def instance():
		if SpecialComposeExp._instance is None:
			SpecialComposeExp._instance = SpecialComposeExp()
		return SpecialComposeExp._instance
		
	def getIsBind( self, scrollID ):
		"""
		根据制作卷ID，获取目标物品是否绑定
		"""
		return False
		
	def getRequireMoney( self, scrollID ):
		"""
		根据制作卷的ID 查找出该制作卷需要多少钱
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return 0
		return scinfo["requireMoney"]
		
	def getMaterials( self , scrollID ):
		"""
		根据制作卷的ID 查找出该制作卷合成需要的其他材料
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return []
		Materials = scinfo["srcItems"]
		return copy.deepcopy( Materials )

	def getDstItemID( self , scrollID ):
		"""
		根据制作卷的ID 查找出该制作卷合成出的物品ID
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return 0
		return scinfo["dstItemID"]
		
	def getDstItemCount( self , scrollID ):
		"""
		根据制作卷的ID 查找出该制作卷合成出的物品的数量
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return 0
		return scinfo["amount"]
		

# ----------------------------------------------------------------------------------------------------
# 神机匣功能
# 特殊材料合成公式
# ----------------------------------------------------------------------------------------------------
class SpecialStuffComposeExp:
	"""
	特殊材料合成公式
	config/item/ArmorAmend.xml
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert SpecialStuffComposeExp._instance is None, "instance already exist in"
		SpecialStuffComposeExp._instance = self
		self._datas = SpecialStuffCompose.Datas # like as { dstItemID : [ { "amount" : dstAmount, "srcItems" : { itemID1:amount1...} } ], [......]  }
		self._scroll= SpecialStuffCompose.Scroll # 存储卷轴对应的合成公式 方便通过卷轴查找合成材料 format like this { scrollid : dstItemID }

	@staticmethod
	def instance():
		if SpecialStuffComposeExp._instance is None:
			SpecialStuffComposeExp._instance = SpecialStuffComposeExp()
		return SpecialStuffComposeExp._instance

	def getDstItemInfo( self, itemInfo ):
		"""
		根据材料获取合成物品ID和数量 和 属性
		"""
		#multiples = []
		dstItemID = 0
		quality = 0
		prefix = 0
		proPrefixID = 0
		for itemID, datas in self._datas.iteritems():
			for data in datas:
				basesItems = data["srcItems"]
				if set( itemInfo.keys() ) != set( basesItems.keys() ): #需要材料id和所给要匹配
					continue
				dstItemID = itemID
				quality = data["quality"]
				prefix = data["prefix"]
				proPrefixID = data["propPrefixID"]
				amount = data["amount"]
				enough = True
				for baseID, baseAmount in basesItems.iteritems():
					itemAmount = itemInfo[baseID]
					if itemAmount < baseAmount:
						enough = False
						break
				if enough:
					return ( ( dstItemID, amount ), ( quality, prefix, proPrefixID ) )
		return ()


	def getMaterials( self , scrollID ):
		"""
		根据制作卷的ID 查找出该制作卷合成需要的其他材料
		"""
		DstItemID = self._scroll.get( scrollID )
		if not DstItemID:
			return
		Materials ={}
		for data in self._datas[ DstItemID ]:
			if data[ "srcItems" ].has_key( scrollID ):
				Materials = copy.copy( data[ "srcItems" ] )
				del Materials[scrollID]
		return Materials

	def getDstItemID( self , scrollID ):
		"""
		根据制作卷的ID 查找出该制作卷合成出的物品ID
		"""
		DstItemID = self._scroll.get( scrollID )
		if not DstItemID:
			return
		return DstItemID

	def getBaseMaterials( self, dstItemID ):
		"""
		根据目标物品ID 查找相应的材料
		"""
		basesItems = []
		if self._datas.has_key( dstItemID ):
			for data in self._datas[dstItemID]:
				basesItems.append( data["srcItems"] )
		return basesItems

	def getEquipQuality( self, dstItemID ):
		"""
		根据制作卷需求 可以指定装备品质 查找相应的品质 by姜毅
		"""
		try:
			if self._datas.has_key( dstItemID ):
				for data in self._datas[dstItemID]:
					return data["quality"]
		except:
			ERROR_MSG( "Can't find quality config" )
			return None

	def getEquipPrefix( self, dstItemID ):
		"""
		根据制作卷需求 可以指定装备前缀 查找相应的前缀 by姜毅
		"""
		try:
			if self._datas.has_key( dstItemID ):
				for data in self._datas[dstItemID]:
					return data["prefix"]
		except:
			ERROR_MSG( "Can't find prefix config" )
			return None

	def getEquipPropPrefix( self, dstItemID ):
		"""
		根据制作卷需求 可以指定装备的属性前缀 查找相应的前缀 by姜毅
		"""
		try:
			if self._datas.has_key( dstItemID ):
				for data in self._datas[dstItemID]:
					return data["propPrefixID"]
		except:
			ERROR_MSG( "Can't find propPrefix config" )
			return None


# ----------------------------------------------------------------------------------------------------
# 防具类型防御值修正公式
# ----------------------------------------------------------------------------------------------------
class ItemTypeAmendExp:
	"""
	物品类型相关修正公式
	config/item/ArmorAmend.xml
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert ItemTypeAmendExp._instance is None, "instance already exist in"
		ItemTypeAmendExp._instance = self
		self._datas = ItemTypeAmend.Datas # like as { itemType : { "dropAmend":dropAmend, "armorAmend" : armorAmend, "priceGeneAmend" : priceGeneAmend } ... }

	@staticmethod
	def instance():
		if ItemTypeAmendExp._instance is None:
			ItemTypeAmendExp._instance = ItemTypeAmendExp()
		return ItemTypeAmendExp._instance

	def getArmorAmend( self, itemType , roleClass ):
		"""
		根据物品类型获取物品防御值修正率
		@type  itemType: Int
		@param itemType: 防具类型
		@type  roleClass : INT
		@param roleClass : 玩家职业
		@return:        Flaot
		"""
		try:
			if roleClass == csdefine.CLASS_FIGHTER:
				return self._datas[itemType]["fighter_armorAmend"]
			if roleClass == csdefine.CLASS_SWORDMAN:
				return self._datas[itemType]["swordman_armorAmend"]
			if roleClass == csdefine.CLASS_ARCHER:
				return self._datas[itemType]["archer_armorAmend"]
			if roleClass == csdefine.CLASS_MAGE:
				return self._datas[itemType]["mage_armorAmend"]
		except KeyError:
			ERROR_MSG( "Can't find ArmorAmend config by %s" % itemType )
			return 0

	def getGeneAmend( self, itemType ):
		"""
		根据物品类型获取物品价值因子修正率
		@type  itemType: Int
		@param itemType: 防具类型
		@return:        Flaot
		"""
		try:
			return self._datas[itemType]["geneAmend"]
		except KeyError:
			ERROR_MSG( "Can't find GeneAmend config by %s" % itemType )
			return 0

	def getDropAmend( self, itemType ):
		"""
		根据物品类型获取物品掉落修正率
		@type  itemType: Int
		@param itemType: 防具类型
		@return:        Flaot
		"""
		try:
			return self._datas[itemType]["DropAmend"]
		except KeyError:
			ERROR_MSG( "Can't find DropAmend config by %s" % itemType )
			return 0

	def getEquipDemageValueWithNombril( self, itemType ):
		"""
		有盾牌的防御分摊系数
		"""
		try:
			return self._datas[itemType]["AbrasionAmend_With_Nombril"]
		except KeyError:
			ERROR_MSG( "Can't find AbrasionAmend config by %s" % itemType )
			return 0


	def getEquipDemageValueWithoutNombril( self, itemType ):
		"""
		有盾牌的防御分摊系数
		"""
		try:
			return self._datas[itemType]["AbrasionAmend_Without_Nombril"]
		except KeyError:
			ERROR_MSG( "Can't find AbrasionAmend config by %s" % itemType )
			return 0


class EquipSplitExp:
	"""
	装备拆分相关
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert EquipSplitExp._instance is None, " EquipSplitExp is  already exist"
		EquipSplitExp._instance = self
		self._Splitdatas = EquipSplit.Splitdatas		#拆分的信息表
		self._SpecifyItem = EquipSplit.SpecifyItem		#指定的物品的拆分信息(用以指定什么物品产出什么材料)
		self._Materialdatas = StuffInfo.MaterialDatas	#材料的数据表

	@staticmethod
	def instance():
		if EquipSplitExp._instance is None:
			EquipSplitExp._instance = EquipSplitExp()
		return EquipSplitExp._instance

	def getSplitInfo( self, level, quality ):
		"""
		根据装备的等级和品质获取该装备的拆分的相关信息 (非特例)
		"""
		try:
			levels = self._Splitdatas.keys()
			levels.sort()
			for key in levels:
				if level <= key:
					return self._Splitdatas[key][quality]
			ERROR_MSG("EquipSplitExp.getSplitInfo equip level %s quality %s can not split---1" % (level,quality) )
			return {}
		except:
			ERROR_MSG("EquipSplitExp.getSplitInfo equip level %s quality %s can not split---2" % (level,quality) )
			return {}

	def getSpecifySplitInfo( self, itemid ):
		"""
		根据物品的ID获取该ID应该拆分的材料(必须是特例的装备)
		"""
		if itemid in self._SpecifyItem.keys():
			return self._SpecifyItem[ itemid ]
		else:
			return []

	def getMaterial( self, level ):
		"""
		根据材料的等级获取该等级的所有材料
		"""
		try:
			return self._Materialdatas[ level ]
		except:
			ERROR_MSG("EquipSplitExp.getMaterial material level %s no exist" % level )
			return []

class RemoveCrystalExp:
	"""
	水晶摘除相关公式
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert RemoveCrystalExp._instance is None, "instance already exist in"
		RemoveCrystalExp._instance = self
		self._sDatas = RemoveCrystal.Datas			# like as { itemID : itemAmount }

	@staticmethod
	def instance():
		if RemoveCrystalExp._instance is None:
			RemoveCrystalExp._instance = RemoveCrystalExp()
		return RemoveCrystalExp._instance

	def getStuff( self ):
		"""
		返回摘除水晶所需材料
		@return	Dic
		"""
		return self._sDatas.values()

class ChangePropertyExp:
	"""
	绿装洗前缀相关公式
	@ivar _data: 全局数据字典;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ChangePropertyExp._instance is None, "instance already exist in"
		ChangePropertyExp._instance = self
		self._sDatas = ChangeProperty.Datas			# like as { itemID : itemAmount }

	@staticmethod
	def instance():
		if ChangePropertyExp._instance is None:
			ChangePropertyExp._instance = ChangePropertyExp()
		return ChangePropertyExp._instance

	def getStuff( self ):
		"""
		返回绿装洗前缀所需材料
		@return	Dic
		"""
		return self._sDatas.values()

class TalismanExp:
	"""
	法宝相关
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert TalismanExp._instance is None, " TalismanExp is  already exist"
		TalismanExp._instance = self
		self._datas = TalismanSplit.Datas
		self._inDatas = TalismanIntensify.Datas
		# TalismanSplit结构	Datas = { grade:{"cost":cost, "oddDatas":{ odd:amount }, "itemIDs":[ itemid, ... ] }, grade2{...}, ... }

	@staticmethod
	def instance():
		if TalismanExp._instance is None:
			TalismanExp._instance = TalismanExp()
		return TalismanExp._instance

	def getSplitInfo( self, grade ):
		"""
		获得法宝分解信息
		@ return [ itemID, ... ]
		"""
		try:
			return self._datas[grade]["splitID"]
		except:
			return 0

	def getSplitCost( self, grade ):
		"""
		获得法宝分解消费额
		"""
		try:
			return self._datas[grade]["cost"]
		except:
			return 0

	def getIntensifyRate( self, grade, intensifyLevel ):
		"""
		获得法宝强化后的属性上升比率
		"""
		try:
			return self._inDatas[grade][intensifyLevel]
		except:
			return 0

class EquipGodWeaponExp:
	"""
	神器相关
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert EquipGodWeaponExp._instance is None, " EquipGodWeaponExp is  already exist"
		EquipGodWeaponExp._instance = self
		self._datas = EquipGodWeapon.Datas
		self._skDatas = GodWeaponSkills.Datas
		self.s_keys = self._datas.keys()
		self.sk_keys = self._skDatas.keys()
		self.s_keys.sort()
		self.s_keys.reverse()
		self.sk_keys.sort()
		self.sk_keys.reverse()
		# EquipGodWeapon结构	Datas = { equipLevel:[itemID, itemID], equipLevel{...}, ... }
		# GodWeaponSkills结构	Datas = { equipLevel:[skillID, skillID, ... ], equipLevel:[ ... ], ... }

	@staticmethod
	def instance():
		if EquipGodWeaponExp._instance is None:
			EquipGodWeaponExp._instance = EquipGodWeaponExp()
		return EquipGodWeaponExp._instance

	def getGodWeaponMaxLevel( self ):
		"""
		获得可打造的神器装备的最高等级
		"""
		return self.s_keys[0]

	def getGodWeaponMinLevel( self ):
		"""
		获得可打造的神器的最低等级
		"""
		return self.s_keys[len(self.s_keys)-1]

	def getGodWeaponStuff( self, equipLevel ):
		"""
		通过装备等级获取炼制神器所需材料
		"""
		for el in self.s_keys:
			if equipLevel >= el:
				return self._datas[el]
		return []

	def getGodWeaponSkill( self, equipLevel ):
		"""
		通过装备等级获取随机技能
		"""
		for el in self.sk_keys:
			if equipLevel >= el:
				return random.choice( self._skDatas[el] )
		return 0

class EquipExp:
	"""
	和装备有关的公式封装，力图做到对公式这样纠结的东西只在一处设计和修改
	此类并非单实例模型，在设计上更加类似于visitor  by mushuang
	"""

	def __init__( self, equipInstance, ownerInstance ):
		self.__equip = equipInstance
		self.__owner = ownerInstance

		self.__initialize()

	def __initialize( self ):
		"""
		计算相关公共数据， 计算需要的个性化数据请在公共方法中初始化
		"""
		g_armorAmend = ItemTypeAmendExp.instance()

		classlist = self.__equip.queryReqClasses()
		itemReqClass = csdefine.CLASS_SWORDMAN
		if len( classlist ) == 1: itemReqClass = classlist[0]

		# 防具修正值
		self.armorAmend = g_armorAmend.getArmorAmend( self.__equip.getType() , itemReqClass)

		# 基础品质比率
		self.baseQualityRate = self.__equip.getBaseRate()
		
		#附加属性比率
		self.excQualityRate = self.__equip.getExcRate()
		
		# 装备及主人级别
		self.equipLevel = self.__equip.getLevel()
		self.ownerLevel = self.__owner.getLevel()

		# 装备水平系数、装备防御等级参数1、装备防御等级参数2、装备防御等级参数3
		self.equipStandardModifier, \
		self.defenceLevelArg1, \
		self.defenceLevelArg2, \
		self.defenceLevelArg3 = equipDefenceData[ self.equipLevel ]

		# 装备总价值因子
		self.statValueStandardModifier = 1.0
		statValueStandardData = equipPriceGeneData.get( self.equipLevel )
		if statValueStandardData and len( statValueStandardData ):
			self.statValueStandardModifier = statValueStandardData[0]

	def __doConfig( self, config ):
		"""
		根据定制初始化一些基本计算量
		"""
		g_equipIntensify = EquipIntensifyExp.instance()

		# 基本属性加成
		self.addBaseRate = 1.0

		# 浮点数放大率
		self.floatZipPercent = 1.0

		# 为佩戴装备做数值调整
		self.doWieldCalc = False

		# 强化物防加值
		self.intensifyArmorInc = 0

		# 强化法防加值
		self.intensifyMagicArmorInc = 0

		# 强化物攻加值
		self.intensifyDamageInc = 0

		# 强化魔攻加值
		self.intensifyMagicDamageInc = 0

		if not config.get( "ignoreObey" ): # 计算认主加成
			if self.__equip.isObey():
				self.addBaseRate += csconst.EQUIP_GHOST_BIND_ADD_BASERATE

		if not config.get( "ignoreIntensify" ): # 计算强化加成
			intensify = self.__equip.getIntensifyLevel()
			if intensify:
				quality = self.__equip.getQuality()
				prefix = self.__equip.getPrefix()
				self.addBaseRate += g_equipIntensify.getBaseRate( intensify, quality, prefix )
				intensifyValue = self.__equip.getIntensifyValue()
				self.intensifyArmorInc = intensifyValue[1][0]
				self.intensifyMagicArmorInc = intensifyValue[1][1]
				self.intensifyDamageInc = intensifyValue[0][0]
				self.intensifyMagicDamageInc = intensifyValue[0][1]

		if not config.get( "ignoreZipPercent" ): # 计算浮点数放大率
			self.floatZipPercent = csconst.FLOAT_ZIP_PERCENT

		if not config.get( "ignoreWieldCalc" ): # 做装备佩戴数值调整
			self.doWieldCalc = True

	@property
	def equip( self ):
		"""
		只读属性
		获取装备引用
		"""
		return self.__equip

	@property
	def owner( self ):
		"""
		只读属性
		获取角色引用
		"""
		return self.__owner

	def getArmorBase( self, **config ):
		"""
		获取此装备提升的物理防御值
		"""
		self.__doConfig( config )

		# 物理防御减伤率
		eq_pDamageLose = self.__equip.query( "eq_pDamageLose", 0.0 )

		# 物理防御值= 防具修正值 * 强化/认主加成 * 基础属性品质比率 * 装备水平系数*(参数_1*物品等级+ 参数_2 ) * 参数_3^ ( 0.1 * 物品等级 - 1) * 物理防御减伤率 / ( 1 - 物理防御减伤率) + 强化加值
		return	int( math.ceil( self.armorAmend * self.addBaseRate * self.baseQualityRate * self.equipStandardModifier * \
				( self.defenceLevelArg1 * self.equipLevel + self.defenceLevelArg2 ) * \
				self.defenceLevelArg3 ** ( 0.1 * self.equipLevel - 1 ) * eq_pDamageLose / ( 1 - eq_pDamageLose ) ) + self.intensifyArmorInc )

	def getMagicArmorBase( self, **config ):
		"""
		获取此防具提升的法术防御值
		"""
		self.__doConfig( config )

		# 法术防御减伤率
		eq_sDamageLose = self.__equip.query( "eq_sDamageLose", 0.0 )

		# 法术防御值= 防具修正值 * 强化/认主加成 * 基础属性品质比率* 装备水平系数* (参数_1*道具等级+ 参数_2 ) * 参数_3^ ( 0.1 * 道具等级 - 1) * 法术防御减伤率 / ( 1 - 法术防御减伤率) + 强化加值
		return	int( math.ceil( self.armorAmend * self.addBaseRate * self.baseQualityRate * self.equipStandardModifier * \
				( self.defenceLevelArg1 * self.equipLevel + self.defenceLevelArg2 ) * \
				self.defenceLevelArg3 ** ( 0.1 * self.equipLevel - 1 ) * eq_sDamageLose / ( 1 - eq_sDamageLose ) ) + self.intensifyMagicArmorInc )


	def getResistMagicHushProb( self, **config ):
		"""
		抵抗沉默概率
		"""
		self.__doConfig( config )

		# 抗魔法沉默因子
		eq_resistMagicHush = self.__equip.query("eq_ResistChenmo", 0 )

		if eq_resistMagicHush and self.doWieldCalc:
			eq_resistMagicHush = CombatUnitConfig.valueToPer( eq_resistMagicHush, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistMagicHush * self.floatZipPercent * self.statValueStandardModifier )

	def getResistGiddyProb( self, **config ):
		"""
		抵抗眩晕概率
		"""
		self.__doConfig( config )

		# 抵抗眩晕因子
		eq_resistGiddy = self.__equip.query("eq_ResistGiddy", 0 )
		if eq_resistGiddy and self.doWieldCalc:
			eq_resistGiddy = CombatUnitConfig.valueToPer( eq_resistGiddy, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistGiddy * self.floatZipPercent * self.statValueStandardModifier )

	def getResistFixProb( self, **config ):
		"""
		抵抗定身概率
		"""
		self.__doConfig( config )

		# 抵抗定身因子
		eq_resistFix = self.__equip.query("eq_ResistFix", 0 )
		if eq_resistFix and self.doWieldCalc:
			eq_resistFix = CombatUnitConfig.valueToPer( eq_resistFix, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistFix * self.floatZipPercent * self.statValueStandardModifier )

	def getReduceTargetHit( self, **config ):
		"""
		降低对方物理命中点数
		"""
		self.__doConfig( config )

		# 降低命中点数
		eq_reduceTargetHit = self.__equip.query( "eq_ReduceTargetHit", 0 )
		return int( self.baseQualityRate * self.addBaseRate * eq_reduceTargetHit * self.statValueStandardModifier )

	def getReduceTargetMagicHit( self, **config ):
		"""
		降低对方法术命中点数
		"""
		self.__doConfig( config )

		eq_reduceTargetMagicHit = self.__equip.query( "eq_ReduceTargetMagicHit", 0 )
		return int( self.baseQualityRate * self.addBaseRate * eq_reduceTargetMagicHit * self.statValueStandardModifier )

	def getResistSleepProb( self, **config ):
		"""
		抵抗昏睡概率
		"""
		self.__doConfig( config )

		# 抵抗昏睡因子
		eq_resistSleep = self.__equip.query( "eq_ResistSleep", 0 )
		if eq_resistSleep and self.doWieldCalc:
			eq_resistSleep = CombatUnitConfig.valueToPer( eq_resistSleep, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistSleep * self.floatZipPercent * self.statValueStandardModifier )

	def getResistHitProb( self, **config ):
		"""
		招架点数概率
		"""
		self.__doConfig( config )

		# 招架点数因子
		eq_resistHit = self.__equip.query( "eq_ResistHit", 0 )
		if eq_resistHit and self.doWieldCalc:
			eq_resistHit = CombatUnitConfig.valueToPer( eq_resistHit, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistHit * self.floatZipPercent * self.statValueStandardModifier )

	def getDodgeProb( self, **config ):
		"""
		闪避概率
		"""
		self.__doConfig( config )

		# 闪避因子
		eq_dodge = self.__equip.query("eq_Dodge", 0 )
		if eq_dodge and self.doWieldCalc:
			eq_dodge = CombatUnitConfig.valueToPer( eq_dodge, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_dodge * self.floatZipPercent * self.statValueStandardModifier )
	
	def getReduceRoleD( self, **config ):
		"""
		御敌值
		"""
		self.__doConfig( config )
		
		eq_reduceRoleD = self.__equip.query("eq_ReduceRoleD", 0.0 )
		
		return int( eq_reduceRoleD * self.floatZipPercent  )

	def getAddRoleD( self, **config ):
		"""
		破敌值
		"""
		self.__doConfig( config )
		
		eq_addRoleD = self.__equip.query("eq_AddRoleD", 0.0 )
		return int( eq_addRoleD * self.floatZipPercent  )
	
	def getIntensifyDamageInc( self, **config ):
		"""
		获取因强化导致的物理攻击加值
		"""
		if not self.__equip.getIntensifyLevel():
			#没有强化直接给0
			return 0

		self.__doConfig( config )

		return int( self.intensifyDamageInc )

	def getIntensifyMagicDamageInc( self, **config ):
		"""
		获取因强化导致的魔法攻击加值
		"""
		if not self.__equip.getIntensifyLevel():
			#没有强化直接给0
			return 0

		self.__doConfig( config )

		return int( self.intensifyMagicDamageInc )

	def getDPSValue( self, **config ):
		"""
		获取DPS加值
		"""
		self.__doConfig( config )
		eq_DPS = self.__equip.query( "eq_DPS", 0.0 )
		return int( eq_DPS * self.baseQualityRate * self.addBaseRate * self.floatZipPercent * self.statValueStandardModifier )

	def getDPSFluctuation( self, **config ):
		"""
		获取DPS波动
		"""
		self.__doConfig( config )
		fluctuation = self.__equip.query( "eq_DPSArea", 0.0 )
		return int( fluctuation * self.floatZipPercent )

	def getDefaultDPSFluctuation( self, **config ):
		"""
		获取空手状态下的DPS波动
		"""
		self.__doConfig( config )
		return int( 0.3 * self.floatZipPercent )

	def getDefaultHitSpeedBase( self, **config ):
		"""
		获取空手状态下的攻速基础值
		"""
		self.__doConfig( config )
		return int( 1.3 * self.floatZipPercent )

	def getDefaultAttackRangeBase( self, **config ):
		"""
		获取空手状态下的攻速基础值
		"""
		self.__doConfig( config )
		return int( 2.0 * self.floatZipPercent )

	def getHitSpeedBase( self, **config ):
		"""
		获取攻击速度基础值
		"""
		self.__doConfig( config )
		hit_speed = self.__equip.query( "eq_delay", 0.0 )
		return int( hit_speed * csconst.FLOAT_ZIP_PERCENT )

	def getAttackRangeBase( self, **config ):
		"""
		获取武器的攻击距离
		"""
		self.__doConfig( config )
		eq_range = self.__equip.query( "eq_range", 0.0 )
		return int( eq_range * csconst.FLOAT_ZIP_PERCENT )

	def getMagicDamageValue( self, **config ):
		"""
		获取武器的魔攻加值
		"""
		self.__doConfig( config )
		eq_magic_damage = self.__equip.query( "eq_magicPower", 0.0 )
		return int( eq_magic_damage * self.baseQualityRate * self.addBaseRate * self.statValueStandardModifier )

class EquipAttrExp:
	"""
	装备各种属性获取
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipAttrExp._instance is None, "instance already exist in"

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipAttrExp()
		return self._instance

	def getItemPriceGene( self, itemID, level, type, quality, prefix ):
		"""
		根据物品的品质前缀获取物品的价值因子
		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@param quality: 物品品质
		@type  quality: Int
		@param prefix: 物品前缀
		@type  prefix: Int
		"""
		# 物品类型修正率 * 1.82*（7.5*（2*等级*附加属性品质比率）^1.54+（等级^1.5*2.5+60）*附加属性品质比率）
		excQualityRate = EquipQualityExp.instance().getexcRateByQandP( quality, prefix )
		priceGeneAmend = ItemTypeAmendExp.instance().getGeneAmend( type )
		
		statValueStandardModifier, \
		arg1, \
		arg2 = equipPriceGeneData[ level ]
		
		#装备总价值因子 = 价值水平系数 * 部位折算 * 附加属性品质比率 * 参数1 * 参数2 ^ ( 0.1 * 道具等级–1 ） 
		priceGene = statValueStandardModifier * priceGeneAmend * excQualityRate * arg1 * arg2 ** ( 0.1 * level - 1 )
		return priceGene
		
	def getRandomAttr( self, itemLevel, attrNum, hasCodes = [] ):
		"""
		获得随机属性
		@param itemLevel: 物品等级
		@type  itemLevel: ITEM_LEVEL
		@param attrNum: 装备的第几个属性
		@type  attrNum: Int
		@param hasCodes:已经随到的属性
		"""
		#1.取得配置中的概率
		newDic = {}  #新的符合条件的属性及其对应概率字典
		sum_pro = 0  #新的符合条件的属性在基础配置中的概率和
		attrs = {}
		if attrNum == 1:
			attrs = copy.deepcopy ( L_Data[ItemTypeEnum.EQUIP_NORMAL_ATTR] )
		elif attrNum == 2 or attrNum == 3:
			copyData = copy.deepcopy(L_Data)
			attrs = copyData[ItemTypeEnum.EQUIP_NORMAL_ATTR]
			attrs.update( copyData[ItemTypeEnum.EQUIP_MIDDLE_ATTR] )
		elif attrNum == 4 or attrNum == 5:
			copyData = copy.deepcopy(L_Data)
			attrs = copyData[ItemTypeEnum.EQUIP_NORMAL_ATTR]
			attrs.update( copyData[ItemTypeEnum.EQUIP_MIDDLE_ATTR] )
			attrs.update( copyData[ItemTypeEnum.EQUIP_TOP_ATTR] )
		
		for code,attr in attrs.iteritems():
			if code not in hasCodes: #去掉已经随到的属性
				for levelRegion,pro in attr.iteritems():
					if  levelRegion[0]  <= itemLevel <= levelRegion[1]:
						newDic[ code ] = pro
						sum_pro += pro
						break
		
		#2.重新计算概率
		codePro = 0
		for code in newDic.keys():
			newDic[code] = ( codePro,codePro+newDic[code]/sum_pro )
			codePro = newDic[code][1]
		
		#3.看随机到哪个属性
		ranV = random.random()
		for code,pro in newDic.iteritems():
			if pro[0] < ranV <= pro[1]:
				return code
		return -1	
		
	def getEquipRandomEffect( self, itemID, itemLevel, equipType, quality ):
		"""
		获取装备的随机属性
		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@param quality: 物品品质
		@type  quality: Int
		"""
		dic = {}
		attrNum = ItemTypeEnum.EQUIP_ATTR_NUM_MAPS[ quality ]
		#检测部位或者卷轴存在不？
		if equipType != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL:
			if equipType not in E_Data.keys():
				return {}
		else:
			if itemID not in S_Data.keys():
				return {}
			
		if attrNum == 0: return {}
		#先随机属性
		if attrNum > 1:
			code1 = self.getRandomAttr( itemLevel, 1 )
			if code1 > 0:
				dic[ code1 ] = 0
			code2 = self.getRandomAttr( itemLevel, 2, dic.keys() )
			if  code2 > 0:
				dic[ code2 ] = 0
		if equipType != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL:
			if attrNum > 2:
				code3 = self.getRandomAttr( itemLevel, 3, dic.keys() )
				if  code3 > 0:
					dic[ code3 ] = 0
			if attrNum > 3:
				code4 = self.getRandomAttr( itemLevel, 4, dic.keys() )
				if code4 > 0:
					dic[ code4 ] = 0
			if attrNum > 4:
				code5 = self.getRandomAttr( itemLevel, 5, dic.keys() )
				if code5 > 0:
					dic[ code5 ] = 0
		#再获得属性具体加多少值
		if len( dic ) > 0:
			if equipType != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL:
				for attrCode in dic.keys():
					fluctuation_range = E_Data[equipType][max( (itemLevel/10)*10, 10 )][attrCode]
					#随机一下看取值区间
					ranV = random.random()
					for info in fluctuation_range: #info的结构是 10,20,2,0.1,0.3
						if info[3] < ranV <= info[4] :
							if int(info[0]) == int(info[1]):
								dic[attrCode] = int(info[0])
							else:	
								dic[attrCode] = random.randrange( int(info[0]), int(info[1]), int(info[2]) )
							if attrCode in ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE:
								dic[attrCode] =  dic[attrCode] / ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE[attrCode]
							break
			else:
				for attrCode in dic.keys():
					fluctuation_range = S_Data[itemID][attrCode]
					#随机一下看取值区间
					ranV = random.random()
					for info in fluctuation_range: #info的结构是 10,20,2,0.1,0.3
						if info[3] < ranV <= info[4] :
							if int(info[0]) == int(info[1]):
								dic[attrCode] = int(info[0])
							else:	
								dic[attrCode] = random.randrange( int(info[0]), int(info[1]), int(info[2]) )
							if attrCode in ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE:
								dic[attrCode] =  dic[attrCode] / ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE[attrCode]
							break
		if ( equipType == ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL and len( dic ) != 2 ) or ( equipType != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL and len( dic ) != attrNum ):
			ERROR_MSG("EquipRandomEffect number not matching!")
			return {}
		result = { "dic" : dic }
		return result
		
		
	def getScrollComposeRandomEffect( self, itemID, itemLevel, sdic, quality ):
		"""
		获得卷轴合成时的随机属性
		"""
		dic = {}
		keyL = sdic.keys()
		attrNum = ItemTypeEnum.EQUIP_ATTR_NUM_MAPS[ quality ]
		#先随机属性
		if attrNum > 2:
			code3 = self.getRandomAttr( itemLevel, 3, keyL )
			if code3 > 0:
				dic[ code3 ] = 0
				keyL.append( code3 )
		if attrNum > 3:
			code4 = self.getRandomAttr( itemLevel, 4, keyL )
			if  code4 > 0:
				dic[ code4 ] = 0
				keyL.append( code4 )
		if attrNum > 4:
			code5 = self.getRandomAttr( itemLevel, 5, keyL )
			if  code5 > 0:
				dic[ code5 ] = 0
		
		for attrCode in dic.keys():
			fluctuation_range = S_Data[itemID][attrCode]
			#随机一下看取值区间
			ranV = random.random()
			for info in fluctuation_range: #info的结构是 10,20,2,0.1,0.3
				if info[3] < ranV <= info[4] :
					if int(info[0]) == int(info[1]):
						dic[attrCode] = int(info[0])
					else:	
						dic[attrCode] = random.randrange( int(info[0]), int(info[1]), int(info[2]) )
					if attrCode in ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE:
						dic[attrCode] =  dic[attrCode] / ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE[attrCode]
					break
		return dic



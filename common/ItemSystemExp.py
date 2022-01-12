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
# ���ϻ����
# ���Ϻϳɹ�ʽ
# ----------------------------------------------------------------------------------------------------
class StuffMergeExp:
	"""
	���Ϻϳɹ�ʽ
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��value}
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
		ͨ��������Դ������ƷID����ȡ�ɹ���
		@param		baseAmount: �ϳɻ���
		@type		baseAmount: Int
		@param		itemID: ��ƷID
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
		ͨ��������ԭ��ID��ȡ�ϳɼ۸� by����
		"""
		try:
			return self._datas[ baseAmount ][ itemID ][ "price" ]
		except KeyError:
			ERROR_MSG( "Can't find price Config by ( baseAmount --> %s) ( itemID -->> %s )" % ( baseAmount, itemID ) )
			return 0

	def getDstItemID( self, baseAmount, itemID ):
		"""
		ͨ��������Դ������ƷID����ȡ�ϳ���ƷID
		@param		baseAmount: �ϳɻ���
		@type		baseAmount: Int
		@param		itemID: ��ƷID
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
		ͨ��������ԭ�ϻ�ȡ�ϳ��������Ӽ�ID������ by����
		"""
		try:
			return self._datas[ baseAmount ][itemID]["additive"]
		except KeyError:
			ERROR_MSG( "Can't find additive Config by ( baseAmount --> %s) ( itemID -->> %s )" % ( baseAmount, itemID ) )
			return {}

	def canMerge( self, itemID ):
		"""
		�жϸ���Ʒ�Ƿ��ܺϳ�
		@param		itemID: ��ƷID
		@type		itemID: ITEM_ID
		@return		Bool
		"""
		return itemID in self._useItemIDs

# ----------------------------------------------------------------------------------------------------
# ���ϻ����
# װ��ǿ����ʽ
# ----------------------------------------------------------------------------------------------------
class EquipIntensifyExp:
	"""
	װ��ǿ����ʽ
	@ivar _data: ȫ�������ֵ�; key is id, value is dict
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
		�ж���Ʒ�Ƿ���ǿ�����ϣ�����
		"""
		return item.id in [ tempKey[0] for tempKey in self._dragonGemDict.keys() ]

	def isLuckGem( self, item ):
		"""
		�ж���Ʒ�Ƿ�ǿ�����ϣ����˱�ʯ
		"""
		return item.id in self._luckGemDict.keys()

	def getMinLevel( self, itemID ):
		"""
		����ID��ȡ��ǿ������͵ȼ�
		"""
		try:
			return self._dragonLevel[itemID]["minLevel"]
		except:
			ERROR_MSG("Can't find %s 's Config By getMinLevel" % itemID )
			return 0

	def getMaxLevel( self, itemID ):
		"""
		����ID��ȡ��ǿ������ߵȼ�
		"""
		try:
			return self._dragonLevel[itemID]["maxLevel"]
		except:
			ERROR_MSG("Can't find %s 's Config By getMaxLevel" % itemID )
			return 0

	def getOdds( self, intensifyLevel ):
		"""
		����ǿ���ȼ���ȡ�ɹ���
		@param		intensifyLevel: ǿ���ȼ�
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
		����ǿ���ȼ���Ʒ�ʺ�ǰ׺��ȡǿ���Ļ����������Ա���ֵ
		@param		intensifyLevel	: ǿ���ȼ�
		@type		intensifyLevel	: UINT8
		@param		quality			: Ʒ��
		@type		quality			: UINT8
		@param		prefix			: ǰ׺
		@type		prefix			: UINT8
		@return						: Float
		"""
		# ��Σ�װ��ǿ��ֻ����Ʒ�����޸Ļ�������ֵ by ���� 17:03 2009-11-26
		if quality == ItemTypeEnum.CQT_GREEN:
			idata = self._datas.get( intensifyLevel )
			if idata is None: return 0.0
			data = idata.get( "prefix_map" )
			key = prefix
			if data is None: return 0.0
			baseRate = data.get( key )
			if baseRate is None: return data[ItemTypeEnum.CPT_MYTHIC]		# ����ǰ׺�ļһ�Ҳ���л�����������
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
		����������ͺ�ǿ����������װ��ǿ������ֵ
		"""
		equipType = equip.getType()
		maskCode = 0xff0000										# װ����������
		equipLevel = int ( ( equip.getReqLevel()- 1 ) / 10 )
		if equipType & maskCode == ItemTypeEnum.ITEM_WEAPON:	# ����װ�������������ͷ���������
			intensifyValue = equip.getIntensifyValue()			# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			phys_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_damage_inc" ]
			magic_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_damage_inc" ]
			intensifyValue[ 0 ][ 0 ] += phys_damage_inc
			intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType & maskCode == ItemTypeEnum.ITEM_ARMOR:	# ����װ���ķ�����
			intensifyValue = equip.getIntensifyValue()			# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			phys_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_defence_inc" ]
			magic_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_defence_inc" ]
			intensifyValue[ 1 ][ 0 ] += phys_defence_inc
			intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_NECKLACE:	# ����װ���ķ�����
			intensifyValue = equip.getIntensifyValue()			# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			phys_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_defence_inc" ]
			magic_defence_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_defence_inc" ]
			intensifyValue[ 1 ][ 0 ] += phys_defence_inc
			intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_RING:		# ����װ�������������ͷ���������
			intensifyValue = equip.getIntensifyValue()			# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			phys_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "phys_damage_inc" ]
			magic_damage_inc = self._dragonGemDict[ ( dragonGemID, intensifyLevel, equipLevel ) ][ "magic_damage_inc" ]
			intensifyValue[ 0 ][ 0 ] += phys_damage_inc
			intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )


	def setIntensifyFailedValue( self, equip, dragonGemID, intensifyLevel ):
		"""
		ǿ��ʧ��,����װ������

		@param equip : װ��
		@type equip : ITEM
		@param dragonGemID : ����ǿ��������id
		@type dragonGemID : ITEM_ID
		@param intensifyLevel : ǿ������
		@type intensifyLevel : UINT8
		"""
		equipType = equip.getType()
		maskCode = 0xff0000										# װ����������
		equipLevel = int ( ( equip.getReqLevel()- 1 ) / 10 )
		if equipType & maskCode == ItemTypeEnum.ITEM_WEAPON:	# ����װ�������������ͷ���������
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_damage_inc" ]
				magic_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_damage_inc" ]
				intensifyValue[ 0 ][ 0 ] += phys_damage_inc
				intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType & maskCode == ItemTypeEnum.ITEM_ARMOR:	# ����װ���ķ�����
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_defence_inc" ]
				magic_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_defence_inc" ]
				intensifyValue[ 1 ][ 0 ] += phys_defence_inc
				intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_NECKLACE:	# ����װ���ķ�����
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_defence_inc" ]
				magic_defence_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_defence_inc" ]
				intensifyValue[ 1 ][ 0 ] += phys_defence_inc
				intensifyValue[ 1 ][ 1 ] += magic_defence_inc
			equip.setIntensifyValue( intensifyValue, None )
		elif equipType == ItemTypeEnum.ITEM_ORNAMENT_RING:		# ����װ�������������ͷ���������
			intensifyValue = [ [ 0, 0 ], [ 0, 0 ] ]		# intensifyValueΪ[ ( ǿ������������, ǿ����ħ�������� ), ( ǿ�����������ֵ, ǿ����ħ������ֵ ) ]
			for count in xrange( 0, intensifyLevel ):
				phys_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "phys_damage_inc" ]
				magic_damage_inc = self._dragonGemDict[ ( dragonGemID, count + 1, equipLevel ) ][ "magic_damage_inc" ]
				intensifyValue[ 0 ][ 0 ] += phys_damage_inc
				intensifyValue[ 0 ][ 1 ] += magic_damage_inc
			equip.setIntensifyValue( intensifyValue, None )


	def getFiledLevel( self, intensifyLevel ):
		"""
		����ǿ���ȼ���ȡǿ��ʧ�ܺ���䵽��ǿ���ȼ�
		@param		intensifyLevel: ǿ���ȼ�
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
		����ǿ���ȼ���ȡǿ��65������װ����ԭ������
		@param		intensifyLevel: ǿ���ȼ�
		@type		intensifyLevel: UINT8
		@return 	{ "itemID" ��itemAmount }
		"""
		try:
			data = self._datas[intensifyLevel]
			return { data["intensify_needHigh"] : data["intensify_amountHigh"] }
		except:
			ERROR_MSG("Can't find %s 's Config By getRequirementUpLimit" % intensifyLevel )
			return {}

	def getReqMoney( self, level, intensifyLevel ):
		"""
		����ǿ���ȼ���ȡǿ������Ǯ by����
		"""
		return level * intensifyLevel * 10

	def getRequirementDownLimit( self, intensifyLevel ):
		"""
		����ǿ���ȼ���ȡǿ��65������װ����ԭ������
		@param		intensifyLevel: ǿ���ȼ�
		@type		intensifyLevel: UINT8
		@return 	{ "itemID" ��itemAmount }
		"""
		try:
			data = self._datas[intensifyLevel]
			return { data["intensify_needLow"] : data["intensify_amountLow"] }
		except:
			ERROR_MSG("Can't find %s 's Config By getRequirementDownLimit" % intensifyLevel )
			return {}

	def getExtraItem( self, intensifyLevel ):
		"""
		����ǿ���ȼ���ȡ���⸽����Ʒ
		@param		intensifyLevel: ǿ���ȼ�
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
		����ǿ���ȼ���ȡ���⸽����Ʒ
		@param		intensifyLevel: ǿ���ȼ�
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
		��������ˮ����id���ǿ���ɹ���

		@param luckGemID : ����ˮ����id
		@type luckGemID : ITEM_ID
		"""
		assert self._luckGemDict.has_key( luckGemID )
		return self._luckGemDict[ luckGemID ]

	def isShine( self, intensifyLevel ):
		"""
		����ǿ���ȼ���ȡ�õȼ��Ƿ񷢹�
		@param		intensifyLevel: ǿ���ȼ�
		@type		intensifyLevel: UINT8
		@return 					Bool
		"""
		try:
			return self._datas[intensifyLevel]["intensify_isShine"]
		except:
			ERROR_MSG("Can't find intensify_isShine config by intensifyLevel(%s)" % intensifyLevel )
			return False

# ----------------------------------------------------------------------------------------------------
# ���ϻ����
# ��װ��Ʒ��ʽ
# ----------------------------------------------------------------------------------------------------
class EquipImproveQualityExp:
	"""
	��װ��Ʒ��ʽ
	@ivar _data: ȫ�������ֵ�; key is id, value is dict
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
		�ж���Ʒ�Ƿ�����Ʒ���ϣ��񻰻��»����������
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
		��װ����ǰ׺�ͻ��µ���������װ�����µ�ǰ׺
		"""
		prefix = equip.getPrefix()
		newPrefix=self._datas["improveQualityData"][( badgeID, prefix)]["result_prefix"]
		equip.setPrefix(newPrefix)

	def setImproveQualityFailedPrefix( self, equip , badgeID):
		pass

# ----------------------------------------------------------------------------------------------------
# ���ϻ����
# װ����Ƕ��ع�ʽ
# ----------------------------------------------------------------------------------------------------
class EquipStuddedExp:
	"""
	װ����Ƕ��ع�ʽ
	@ivar _data: ȫ�������ֵ�;
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
		����װ���Ŀ�λ��������ȡ��˿���Ҫ�Ļ���
		@type  holeIndex: UINT8
		@param holeIndex: �����׵�λ��
		@return			: UINT 32
		"""
		try:
			return self._cDatas[holeIndex]
		except KeyError:
			ERROR_MSG( "Can't find StilettoCost config by %s " % holeIndex )
			return 0

	def getStilettoOdds( self, holes ):
		"""
		����װ��������ȡ�ɹ��� by����
		@type  holes: UINT8
		@param holes: ���п���
		@return		: UINT 32
		"""
		try:
			return self._oDatas[ holes ]
		except KeyError:
			ERROR_MSG( "Can't find StilettoOdd config by %s " % holes )
			return 0

	def getStuff( self ):
		"""
		����װ����Ƕ�������
		@return	Dic
		"""
		return self._sDatas.values()

# ----------------------------------------------------------------------------------------------------
# װ��Ʒ��ǰ׺��ع�ʽ
# ----------------------------------------------------------------------------------------------------
class EquipQualityExp:
	"""
	װ��Ʒ����ع�ʽ
	װ�������켰װ����������װ��������ȶ����õ����ʷֿ���ʼ��
	@ivar _data: ȫ�������ֵ�;
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
		ͨ��װ��Ʒ�ʷ���װ����ɫֵ(vector3)
		@type  quality: UNIT8
		@param quality: װ��Ʒ��
		@return:        vector3
		"""
		try:
			return tuple( self._datas[quality]["color"] )
		except:
			return ( 255,255,255 )

	def getBaseRateByQuality( self, quality, prefix ):
		"""
		ͨ��װ��Ʒ�ʷ���װ����������Ʒ�ʱ���
		@type  quality		: UNIT8
		@param quality		: װ��Ʒ��
		@type  prefix		: UNIT8
		@param prefix		: װ��ǰ׺
		@return				: Float
		"""
		# �����Ѿ�ȥ����ǰ׺������Ĭ�϶�����ͨ��
		key = self.Q_BASERATE_MAP.get( ItemTypeEnum.CPT_NORMAL )
		if key is None: return 0.0

		qData = self._datas.get( quality )
		if qData is None: return 0.0

		baseRate = qData.get( key )
		if baseRate is None: return 0.0

		return baseRate

	def getRepairRateByQuality( self, quality ):
		"""
		ͨ��װ��Ʒ�ʷ���װ����������Ʒ�ʱ���
		@type  quality: UNIT8
		@param quality: װ��Ʒ��
		@return:        Float
		"""
		try:
			return self._datas[quality]["repairQualityRate"]
		except:
			return 0.0

	def getexcRateByQandP( self, quality, prefix ):
		"""
		����װ��Ʒ�ʺ�װ��ǰ׺���ظ�������Ʒ�ʱ���
		@type  quality: UNIT8
		@param quality: װ��Ʒ��
		@type  prefix: UNIT8
		@param prefix: װ��ǰ׺
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
		ͨ��װ��ǰ׺����ǰ׺��ʾ��
		@type  prefix: UNIT8
		@param prefix: װ��ǰ׺
		@return:        String
		"""
		try:
			return self._pDatas[prefix]["name"]
		except:
			return ""

	def getRebuildRate( self, prefix ):
		"""
		ͨ��װ��ǰ׺���ظ���ǰ׺ռ�ı���
		@type  prefix: UNIT8
		@param prefix: װ��ǰ׺
		@return:        Int
		"""
		try:
			return self._pDatas[prefix]["rebuild_rate"]
		except KeyError:
			ERROR_MSG( "Can't find RebuildRate config by %s" % prefix )
			return 0

	def getMakeRate( self, prefix ):
		"""
		ͨ��װ��ǰ׺����������ռ��ǰ׺����
		@type  prefix: UNIT8
		@param prefix: װ��ǰ׺
		@return:        Int
		"""
		try:
			return self._pDatas[prefix]["make_rate"]
		except KeyError:
			ERROR_MSG( "Can't find MakeRate config by %s" % prefix )
			return 0

	def getIntensifyColor( self, quality ):
		"""
		ͨ��װ��Ʒ�ʷ���װ��ǿ��������ɫ
		return as ( r, g, b, c ) ǰ��3����RGBֵ�����һ����͸����
		@type  quality: UNIT8
		@param quality: װ��Ʒ��
		@return:        Vector4
		"""
		try:
			return self._datas[quality]["intensifyColor"]
		except:
			ERROR_MSG( "Can't find intensifyColor config by quality(%s)" % quality )
			return ( 1, 1, 1, 1 )

#-----------------------------------------------------------------------------------------------------
#��ְҵ��װ��ǰ׺B�����ɸ������ݼ���
#-----------------------------------------------------------------------------------------------------
class PrefixDistribute:
	"""
	��ְҵ��װ��ǰ׺B�����ɸ������ݼ���
	"""
	_instance = None

	def __init__(self):
		assert PrefixDistribute._instance is None,"PrefixDistribute instance already exist"
		self.__datas = prefixdistribute.Datas


	def getPrefixs_RC_EQ_EL( self, equipClass, equipQuality, equipLevel ):
		"""
		��ȡǰ׺����������
		"""
		try:
			return self.__datas[equipClass][equipQuality][equipLevel]
		except:
			ERROR_MSG("equipClass = %s equipQuality = %s equipLevel = %s has no prefix" % (equipClass, equipQuality, equipLevel) )
			return ()

	def getPrefixs_RC_EQ( self, equipClass, equipQuality ):
		"""
		��ȡǰ׺����������
		"""
		try:
			return self.__datas[equipClass][equipQuality]
		except:
			ERROR_MSG("equipClass = %s equipQuality = %s has no prefix" % (equipClass, equipQuality ) )
			return {}

	def __randomPrefix( self, equipType, perfixs ):
		"""
		���ݸ��������ȡһ��ǰ׺
		"""
		if perfixs is None: return 0

		n_odds = random.random()
		for id, odds in perfixs:
			if ( n_odds <= odds ) and ( not PropertyPrefixExp.instance().isLimitType( id, equipType ) ):
				return id

		randomAttrs = random.sample( perfixs, len( perfixs ) )

		for id, odds in randomAttrs:										#��û���ҵ����ʵ����Ե�ʱ�򣬰�ԭ�����б���ң���ȡһ����������
			if not PropertyPrefixExp.instance().isLimitType( id, equipType ):
				return id

		return 0

	def randomPrefixID( self, equipClass, equipType, equipQuality, equipLevel ):
		"""
		��ȡһ��ǰ׺
		"""
		prefixs_l = self.getPrefixs_RC_EQ( equipClass, equipQuality)
		if len( prefixs_l ) == 0: return 0

		levelList = sorted(prefixs_l.keys())	#��Ϊ�ֵ��������������Ҫ����
		for level in levelList:
			if equipLevel <= level :
				return self.__randomPrefix( equipType, prefixs_l.get( level ) )

	@staticmethod
	def instance():
		if PrefixDistribute._instance is None:
			PrefixDistribute._instance = PrefixDistribute()
		return PrefixDistribute._instance

#-----------------------------------------------------------------------------------------------------
#װ��ǰ׺B�ķ���͸����������ɵ����
#-----------------------------------------------------------------------------------------------------
class PrefixAllotExp:
	"""
	���ظ���Ʒ�ʵ���Ʒ��ǰ׺�ķֲ��͸�Ʒ�ʵĸ������Եļ�ֵ���ӷֲ�
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
		��ȡ�������Ե�����
		"""
		try:
			return self._datas[quality]["property"]
		except:
			ERROR_MSG(" quality %s has no propertyNum" % quality)
			return 0

	def getGeneRateDist( self, quality ):
		"""
		��ȡ�������� �������Եķ�����
		"""
		try:
			return self._datas[quality]["effect_rate"]
		except:
			ERROR_MSG(" quality %s has no effect_rate" % quality)
			return 0


# ----------------------------------------------------------------------------------------------------
# ����ǰ׺���
# ----------------------------------------------------------------------------------------------------
class PropertyPrefixExp:
	"""
	����ǰ׺��ص���Ϣ
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
		��������ǰ׺ID���ظ�ID������Ч��ID
		"""
		try:
			return self._datas[ proPrefixID ][ "effect_id" ]
		except:
			ERROR_MSG( "PropertyPrefixExp.getEffectIDs  has no PropertyproPrefix id %s" % proPrefixID )
			return []

	def getProPrefixName( self, proPrefixID ):
		"""
		��������ǰ׺��ID��ȡ������ǰ׺������
		"""
		try:
			return self._datas[ proPrefixID ]["prefix_name"]
		except:
			ERROR_MSG( "PropertyPrefixExp.getProPrefixName  has no PropertyproPrefix %s" % proPrefixID )
			return ""

	def getProPrefixLimit( self, proPrefixID ):
		"""
		��ȡ����ǰ׺�޶�װ�������б�
		���Ϊ[]������
		return list
		"""
		data = self._datas.get( proPrefixID )
		if data is None: return []

		prefixLimit = data.get( "prefix_limit" )
		if prefixLimit is None: return []

		return prefixLimit

	def isLimitType( self, proPrefixID, type ):
		"""
		�ж�����type�Ƿ����޶�����ID�Ĳ���
		return BOOL
		"""
		limitTypes = self.getProPrefixLimit( proPrefixID )
		if len( limitTypes ) == 0: return False
		if type not in limitTypes: return False
		return True

# ----------------------------------------------------------------------------------------------------
# װ������ع�ʽ
# ----------------------------------------------------------------------------------------------------
class EquipBindExp:
	"""
	װ������ع�ʽ
	config/item/EquipBind.xml
	@ivar _data: ȫ�������ֵ�;
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
		��ȡÿ�ȼ��ķѽ�Ǯ��
		@return Int
		"""
		try:
			return self._datas["perCost"]
		except:
			ERROR_MSG( "Can't find EquipBindExp config bind_cost" )
			return 0

	def getStuff( self ):
		"""
		��ȡ������
		@return { itemID : amount }
		"""
		try:
			return self._datas["require"]
		except:
			ERROR_MSG( "Can't find EquipBindExp config bind_require" )
			return {}

# ----------------------------------------------------------------------------------------------------
# װ������/������ع�ʽ
# ----------------------------------------------------------------------------------------------------
class EquipMakeExp:
	"""
	װ������/������ع�ʽ
	@ivar _data: ȫ�������ֵ�;
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
		������ƷID ��ȡ����/�������ƷID����Ҫ�Ĳ���
		@param itemID	:	��ƷID
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
		������ƷID ��ȡ����/�������ƷID����Ҫ����Ͳ�������
		@param itemID	:	��ƷID
		@type itemID	:	ITEM_ID
		@return 		:	Int
		"""
		amount = 0
		for value in self.getStuff( itemID ).itervalues():
			amount += value
		return amount

	def getLevel( self, itemID ):
		"""
		ͨ������ID�Ż�ȡ��Ʒ�ȼ�
		@param	itemID	: ��ƷID
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
		ͨ������ID�Ż�ȡ��Ʒ�ȼ�
		@param	equipID	: װ��D
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
		ͨ����ƷID��ȡ����Ʒ��������
		���� : 080101001 == ԭʼ�� ������ϵ�����־��� ��
		@param	itemID	: ��ƷID
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
		ͨ��װ��ǰ��λ��Ż����ͬ����װ���б�
		"""
		sameTypeEquips = []
		for euipID, euipDict in self._datas.iteritems():
			# ��ʱ����9λ����ֹ������ʾ����
			# �����ø� 15:54 2008-8-8 yk
			key = "0" * ( 9 - len( str(euipID) ) ) + str(euipID)
			if key.startswith( tag ):
				sameTypeEquips.append( ( euipID, self._datas[euipID] ) )
		return sameTypeEquips


	def getClassList( self, itemID ):
		"""
		����ԭ��ID��ȡ��ԭ����������ȼ����������ID����
		���磺��������ID�� 080101003������������صľ�����
		ϵ�еıȶ������ȼ��ߵ����������ļ������弶�� ID����
		@param	itemID	: ��ƷID
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
		ͨ����Ʒԭ����Ϣ�ж��Ƿ������쵱ǰitemID
		@param	itemID	: ��ƷID
		@type	itemID	: ITEM_ID
		@param	itemInfo: ԭ����Ϣ
		@type	itemInfo: dic like as {"080101001": 2.......}
		@return 		: Bool
		"""
		# ������������У�ֻ����߼����ϵ�������ƥ��
		# ���磺��Ҫ2��2����������ҷ������10��һ����������Ϊ����������(����10��һ��������2��2����)
		# ���磺��Ҫ2��2����������ҷ������1��2������һ��3����������Ϊ��������
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
		������Ʒ��Ϣ�������Ʒ�ʻ�ȡ�ɹ��ĸ��ʣ���װ�����㣬�������Ʒ�ʵ���Ʒ�����������ô�ض��������װ
		#֮ǰ�Ļ�����ʽ����λ����*���ϸ���*5^��Ʒ��-2��*���ߵȼ�/30
		#�¹�ʽ��p_1=ƽ�����ϻ��� / 5 ^ [ floor (װ����Ʒ�ȼ� / 10)+װ��Ʒ��ϵ��-7 ]
				p_2=ƽ�����ϻ��� / 5 ^ (װ��Ʒ��ϵ��-1)

		@param	dic		: ��Ʒ��Ϣ like {"dj1600":2......}
		@type	dic		: dict
		@return	 ( int, float )
		"""
		molecule = 0.0
		totalAmount = self.getAmount( equip.id )
		for itemID, amount in itemInfo.iteritems():
			itemLevel = self.getLevel( itemID )
			molecule += amount * 5**( itemLevel - 1 )

		if equip.getLevel() < EquipMakeExp.EQUIP_LEVEL:		#��װ����Ʒ�ȼ�<70ʱ������ɹ���=p_1
			return molecule / ( totalAmount * 5 ** ( int( equip.getLevel()/10 ) + quality - 7 ) )

		else:		#��װ����Ʒ�ȼ�>=70ʱ������ɹ���=p_2
			return molecule / ( totalAmount * 5 ** ( quality - 1 ) )

	def getPrefix( self, quality, rate, rateBase = 0.0 ):
		"""
		�������ɵ�Ʒ�ʣ�Ʒ�ʸ��ʣ�����Ʒ�ʸ��ʻ�ȡǰ׺
		@param	dic			: Ʒ��
		@type	dic			: int
		@param	dic			: ���ɸ�Ʒ�ʵı���
		@type	dic			: int
		@param	rateBase	: ���ӱ���
		@type	rateBase	: int
		"""
		#��������������װ�ļ���Ϊ80%�� �����ж��Ƿ��ܲ�����װ����������ǾͲ�����װ��
		#����ܣ����ٰ�80%�ļ����ж�ǰ׺�Ƿ�Ϊ�񻰣���7��ǰ׺���������û���浽����ǰ׺��Ϊ��˵����6��ǰ׺������
		#�޸����ģ�飬ʹ������EquipPrefixInfo by ����
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
# ���ϻ����
# ����ϳɹ�ʽ
# ----------------------------------------------------------------------------------------------------
class SpecialComposeExp:
	"""
	����ϳɹ�ʽ
	config/item/ArmorAmend.xml
	@ivar _data: ȫ�������ֵ�;
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
		����������ID����ȡĿ����Ʒ�Ƿ��
		"""
		return False
		
	def getRequireMoney( self, scrollID ):
		"""
		�����������ID ���ҳ�����������Ҫ����Ǯ
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return 0
		return scinfo["requireMoney"]
		
	def getMaterials( self , scrollID ):
		"""
		�����������ID ���ҳ���������ϳ���Ҫ����������
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return []
		Materials = scinfo["srcItems"]
		return copy.deepcopy( Materials )

	def getDstItemID( self , scrollID ):
		"""
		�����������ID ���ҳ���������ϳɳ�����ƷID
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return 0
		return scinfo["dstItemID"]
		
	def getDstItemCount( self , scrollID ):
		"""
		�����������ID ���ҳ���������ϳɳ�����Ʒ������
		"""
		scinfo = self._datas.get( scrollID )
		if not scinfo:
			return 0
		return scinfo["amount"]
		

# ----------------------------------------------------------------------------------------------------
# ���ϻ����
# ������Ϻϳɹ�ʽ
# ----------------------------------------------------------------------------------------------------
class SpecialStuffComposeExp:
	"""
	������Ϻϳɹ�ʽ
	config/item/ArmorAmend.xml
	@ivar _data: ȫ�������ֵ�;
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert SpecialStuffComposeExp._instance is None, "instance already exist in"
		SpecialStuffComposeExp._instance = self
		self._datas = SpecialStuffCompose.Datas # like as { dstItemID : [ { "amount" : dstAmount, "srcItems" : { itemID1:amount1...} } ], [......]  }
		self._scroll= SpecialStuffCompose.Scroll # �洢�����Ӧ�ĺϳɹ�ʽ ����ͨ��������Һϳɲ��� format like this { scrollid : dstItemID }

	@staticmethod
	def instance():
		if SpecialStuffComposeExp._instance is None:
			SpecialStuffComposeExp._instance = SpecialStuffComposeExp()
		return SpecialStuffComposeExp._instance

	def getDstItemInfo( self, itemInfo ):
		"""
		���ݲ��ϻ�ȡ�ϳ���ƷID������ �� ����
		"""
		#multiples = []
		dstItemID = 0
		quality = 0
		prefix = 0
		proPrefixID = 0
		for itemID, datas in self._datas.iteritems():
			for data in datas:
				basesItems = data["srcItems"]
				if set( itemInfo.keys() ) != set( basesItems.keys() ): #��Ҫ����id������Ҫƥ��
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
		�����������ID ���ҳ���������ϳ���Ҫ����������
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
		�����������ID ���ҳ���������ϳɳ�����ƷID
		"""
		DstItemID = self._scroll.get( scrollID )
		if not DstItemID:
			return
		return DstItemID

	def getBaseMaterials( self, dstItemID ):
		"""
		����Ŀ����ƷID ������Ӧ�Ĳ���
		"""
		basesItems = []
		if self._datas.has_key( dstItemID ):
			for data in self._datas[dstItemID]:
				basesItems.append( data["srcItems"] )
		return basesItems

	def getEquipQuality( self, dstItemID ):
		"""
		�������������� ����ָ��װ��Ʒ�� ������Ӧ��Ʒ�� by����
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
		�������������� ����ָ��װ��ǰ׺ ������Ӧ��ǰ׺ by����
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
		�������������� ����ָ��װ��������ǰ׺ ������Ӧ��ǰ׺ by����
		"""
		try:
			if self._datas.has_key( dstItemID ):
				for data in self._datas[dstItemID]:
					return data["propPrefixID"]
		except:
			ERROR_MSG( "Can't find propPrefix config" )
			return None


# ----------------------------------------------------------------------------------------------------
# �������ͷ���ֵ������ʽ
# ----------------------------------------------------------------------------------------------------
class ItemTypeAmendExp:
	"""
	��Ʒ�������������ʽ
	config/item/ArmorAmend.xml
	@ivar _data: ȫ�������ֵ�;
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
		������Ʒ���ͻ�ȡ��Ʒ����ֵ������
		@type  itemType: Int
		@param itemType: ��������
		@type  roleClass : INT
		@param roleClass : ���ְҵ
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
		������Ʒ���ͻ�ȡ��Ʒ��ֵ����������
		@type  itemType: Int
		@param itemType: ��������
		@return:        Flaot
		"""
		try:
			return self._datas[itemType]["geneAmend"]
		except KeyError:
			ERROR_MSG( "Can't find GeneAmend config by %s" % itemType )
			return 0

	def getDropAmend( self, itemType ):
		"""
		������Ʒ���ͻ�ȡ��Ʒ����������
		@type  itemType: Int
		@param itemType: ��������
		@return:        Flaot
		"""
		try:
			return self._datas[itemType]["DropAmend"]
		except KeyError:
			ERROR_MSG( "Can't find DropAmend config by %s" % itemType )
			return 0

	def getEquipDemageValueWithNombril( self, itemType ):
		"""
		�ж��Ƶķ�����̯ϵ��
		"""
		try:
			return self._datas[itemType]["AbrasionAmend_With_Nombril"]
		except KeyError:
			ERROR_MSG( "Can't find AbrasionAmend config by %s" % itemType )
			return 0


	def getEquipDemageValueWithoutNombril( self, itemType ):
		"""
		�ж��Ƶķ�����̯ϵ��
		"""
		try:
			return self._datas[itemType]["AbrasionAmend_Without_Nombril"]
		except KeyError:
			ERROR_MSG( "Can't find AbrasionAmend config by %s" % itemType )
			return 0


class EquipSplitExp:
	"""
	װ��������
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert EquipSplitExp._instance is None, " EquipSplitExp is  already exist"
		EquipSplitExp._instance = self
		self._Splitdatas = EquipSplit.Splitdatas		#��ֵ���Ϣ��
		self._SpecifyItem = EquipSplit.SpecifyItem		#ָ������Ʒ�Ĳ����Ϣ(����ָ��ʲô��Ʒ����ʲô����)
		self._Materialdatas = StuffInfo.MaterialDatas	#���ϵ����ݱ�

	@staticmethod
	def instance():
		if EquipSplitExp._instance is None:
			EquipSplitExp._instance = EquipSplitExp()
		return EquipSplitExp._instance

	def getSplitInfo( self, level, quality ):
		"""
		����װ���ĵȼ���Ʒ�ʻ�ȡ��װ���Ĳ�ֵ������Ϣ (������)
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
		������Ʒ��ID��ȡ��IDӦ�ò�ֵĲ���(������������װ��)
		"""
		if itemid in self._SpecifyItem.keys():
			return self._SpecifyItem[ itemid ]
		else:
			return []

	def getMaterial( self, level ):
		"""
		���ݲ��ϵĵȼ���ȡ�õȼ������в���
		"""
		try:
			return self._Materialdatas[ level ]
		except:
			ERROR_MSG("EquipSplitExp.getMaterial material level %s no exist" % level )
			return []

class RemoveCrystalExp:
	"""
	ˮ��ժ����ع�ʽ
	@ivar _data: ȫ�������ֵ�;
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
		����ժ��ˮ���������
		@return	Dic
		"""
		return self._sDatas.values()

class ChangePropertyExp:
	"""
	��װϴǰ׺��ع�ʽ
	@ivar _data: ȫ�������ֵ�;
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
		������װϴǰ׺�������
		@return	Dic
		"""
		return self._sDatas.values()

class TalismanExp:
	"""
	�������
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert TalismanExp._instance is None, " TalismanExp is  already exist"
		TalismanExp._instance = self
		self._datas = TalismanSplit.Datas
		self._inDatas = TalismanIntensify.Datas
		# TalismanSplit�ṹ	Datas = { grade:{"cost":cost, "oddDatas":{ odd:amount }, "itemIDs":[ itemid, ... ] }, grade2{...}, ... }

	@staticmethod
	def instance():
		if TalismanExp._instance is None:
			TalismanExp._instance = TalismanExp()
		return TalismanExp._instance

	def getSplitInfo( self, grade ):
		"""
		��÷����ֽ���Ϣ
		@ return [ itemID, ... ]
		"""
		try:
			return self._datas[grade]["splitID"]
		except:
			return 0

	def getSplitCost( self, grade ):
		"""
		��÷����ֽ����Ѷ�
		"""
		try:
			return self._datas[grade]["cost"]
		except:
			return 0

	def getIntensifyRate( self, grade, intensifyLevel ):
		"""
		��÷���ǿ�����������������
		"""
		try:
			return self._inDatas[grade][intensifyLevel]
		except:
			return 0

class EquipGodWeaponExp:
	"""
	�������
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
		# EquipGodWeapon�ṹ	Datas = { equipLevel:[itemID, itemID], equipLevel{...}, ... }
		# GodWeaponSkills�ṹ	Datas = { equipLevel:[skillID, skillID, ... ], equipLevel:[ ... ], ... }

	@staticmethod
	def instance():
		if EquipGodWeaponExp._instance is None:
			EquipGodWeaponExp._instance = EquipGodWeaponExp()
		return EquipGodWeaponExp._instance

	def getGodWeaponMaxLevel( self ):
		"""
		��ÿɴ��������װ������ߵȼ�
		"""
		return self.s_keys[0]

	def getGodWeaponMinLevel( self ):
		"""
		��ÿɴ������������͵ȼ�
		"""
		return self.s_keys[len(self.s_keys)-1]

	def getGodWeaponStuff( self, equipLevel ):
		"""
		ͨ��װ���ȼ���ȡ���������������
		"""
		for el in self.s_keys:
			if equipLevel >= el:
				return self._datas[el]
		return []

	def getGodWeaponSkill( self, equipLevel ):
		"""
		ͨ��װ���ȼ���ȡ�������
		"""
		for el in self.sk_keys:
			if equipLevel >= el:
				return random.choice( self._skDatas[el] )
		return 0

class EquipExp:
	"""
	��װ���йصĹ�ʽ��װ����ͼ�����Թ�ʽ��������Ķ���ֻ��һ����ƺ��޸�
	���ಢ�ǵ�ʵ��ģ�ͣ�������ϸ���������visitor  by mushuang
	"""

	def __init__( self, equipInstance, ownerInstance ):
		self.__equip = equipInstance
		self.__owner = ownerInstance

		self.__initialize()

	def __initialize( self ):
		"""
		������ع������ݣ� ������Ҫ�ĸ��Ի��������ڹ��������г�ʼ��
		"""
		g_armorAmend = ItemTypeAmendExp.instance()

		classlist = self.__equip.queryReqClasses()
		itemReqClass = csdefine.CLASS_SWORDMAN
		if len( classlist ) == 1: itemReqClass = classlist[0]

		# ��������ֵ
		self.armorAmend = g_armorAmend.getArmorAmend( self.__equip.getType() , itemReqClass)

		# ����Ʒ�ʱ���
		self.baseQualityRate = self.__equip.getBaseRate()
		
		#�������Ա���
		self.excQualityRate = self.__equip.getExcRate()
		
		# װ�������˼���
		self.equipLevel = self.__equip.getLevel()
		self.ownerLevel = self.__owner.getLevel()

		# װ��ˮƽϵ����װ�������ȼ�����1��װ�������ȼ�����2��װ�������ȼ�����3
		self.equipStandardModifier, \
		self.defenceLevelArg1, \
		self.defenceLevelArg2, \
		self.defenceLevelArg3 = equipDefenceData[ self.equipLevel ]

		# װ���ܼ�ֵ����
		self.statValueStandardModifier = 1.0
		statValueStandardData = equipPriceGeneData.get( self.equipLevel )
		if statValueStandardData and len( statValueStandardData ):
			self.statValueStandardModifier = statValueStandardData[0]

	def __doConfig( self, config ):
		"""
		���ݶ��Ƴ�ʼ��һЩ����������
		"""
		g_equipIntensify = EquipIntensifyExp.instance()

		# �������Լӳ�
		self.addBaseRate = 1.0

		# �������Ŵ���
		self.floatZipPercent = 1.0

		# Ϊ���װ������ֵ����
		self.doWieldCalc = False

		# ǿ�������ֵ
		self.intensifyArmorInc = 0

		# ǿ��������ֵ
		self.intensifyMagicArmorInc = 0

		# ǿ���﹥��ֵ
		self.intensifyDamageInc = 0

		# ǿ��ħ����ֵ
		self.intensifyMagicDamageInc = 0

		if not config.get( "ignoreObey" ): # ���������ӳ�
			if self.__equip.isObey():
				self.addBaseRate += csconst.EQUIP_GHOST_BIND_ADD_BASERATE

		if not config.get( "ignoreIntensify" ): # ����ǿ���ӳ�
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

		if not config.get( "ignoreZipPercent" ): # ���㸡�����Ŵ���
			self.floatZipPercent = csconst.FLOAT_ZIP_PERCENT

		if not config.get( "ignoreWieldCalc" ): # ��װ�������ֵ����
			self.doWieldCalc = True

	@property
	def equip( self ):
		"""
		ֻ������
		��ȡװ������
		"""
		return self.__equip

	@property
	def owner( self ):
		"""
		ֻ������
		��ȡ��ɫ����
		"""
		return self.__owner

	def getArmorBase( self, **config ):
		"""
		��ȡ��װ���������������ֵ
		"""
		self.__doConfig( config )

		# �������������
		eq_pDamageLose = self.__equip.query( "eq_pDamageLose", 0.0 )

		# �������ֵ= ��������ֵ * ǿ��/�����ӳ� * ��������Ʒ�ʱ��� * װ��ˮƽϵ��*(����_1*��Ʒ�ȼ�+ ����_2 ) * ����_3^ ( 0.1 * ��Ʒ�ȼ� - 1) * ������������� / ( 1 - �������������) + ǿ����ֵ
		return	int( math.ceil( self.armorAmend * self.addBaseRate * self.baseQualityRate * self.equipStandardModifier * \
				( self.defenceLevelArg1 * self.equipLevel + self.defenceLevelArg2 ) * \
				self.defenceLevelArg3 ** ( 0.1 * self.equipLevel - 1 ) * eq_pDamageLose / ( 1 - eq_pDamageLose ) ) + self.intensifyArmorInc )

	def getMagicArmorBase( self, **config ):
		"""
		��ȡ�˷��������ķ�������ֵ
		"""
		self.__doConfig( config )

		# ��������������
		eq_sDamageLose = self.__equip.query( "eq_sDamageLose", 0.0 )

		# ��������ֵ= ��������ֵ * ǿ��/�����ӳ� * ��������Ʒ�ʱ���* װ��ˮƽϵ��* (����_1*���ߵȼ�+ ����_2 ) * ����_3^ ( 0.1 * ���ߵȼ� - 1) * �������������� / ( 1 - ��������������) + ǿ����ֵ
		return	int( math.ceil( self.armorAmend * self.addBaseRate * self.baseQualityRate * self.equipStandardModifier * \
				( self.defenceLevelArg1 * self.equipLevel + self.defenceLevelArg2 ) * \
				self.defenceLevelArg3 ** ( 0.1 * self.equipLevel - 1 ) * eq_sDamageLose / ( 1 - eq_sDamageLose ) ) + self.intensifyMagicArmorInc )


	def getResistMagicHushProb( self, **config ):
		"""
		�ֿ���Ĭ����
		"""
		self.__doConfig( config )

		# ��ħ����Ĭ����
		eq_resistMagicHush = self.__equip.query("eq_ResistChenmo", 0 )

		if eq_resistMagicHush and self.doWieldCalc:
			eq_resistMagicHush = CombatUnitConfig.valueToPer( eq_resistMagicHush, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistMagicHush * self.floatZipPercent * self.statValueStandardModifier )

	def getResistGiddyProb( self, **config ):
		"""
		�ֿ�ѣ�θ���
		"""
		self.__doConfig( config )

		# �ֿ�ѣ������
		eq_resistGiddy = self.__equip.query("eq_ResistGiddy", 0 )
		if eq_resistGiddy and self.doWieldCalc:
			eq_resistGiddy = CombatUnitConfig.valueToPer( eq_resistGiddy, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistGiddy * self.floatZipPercent * self.statValueStandardModifier )

	def getResistFixProb( self, **config ):
		"""
		�ֿ��������
		"""
		self.__doConfig( config )

		# �ֿ���������
		eq_resistFix = self.__equip.query("eq_ResistFix", 0 )
		if eq_resistFix and self.doWieldCalc:
			eq_resistFix = CombatUnitConfig.valueToPer( eq_resistFix, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistFix * self.floatZipPercent * self.statValueStandardModifier )

	def getReduceTargetHit( self, **config ):
		"""
		���ͶԷ��������е���
		"""
		self.__doConfig( config )

		# �������е���
		eq_reduceTargetHit = self.__equip.query( "eq_ReduceTargetHit", 0 )
		return int( self.baseQualityRate * self.addBaseRate * eq_reduceTargetHit * self.statValueStandardModifier )

	def getReduceTargetMagicHit( self, **config ):
		"""
		���ͶԷ��������е���
		"""
		self.__doConfig( config )

		eq_reduceTargetMagicHit = self.__equip.query( "eq_ReduceTargetMagicHit", 0 )
		return int( self.baseQualityRate * self.addBaseRate * eq_reduceTargetMagicHit * self.statValueStandardModifier )

	def getResistSleepProb( self, **config ):
		"""
		�ֿ���˯����
		"""
		self.__doConfig( config )

		# �ֿ���˯����
		eq_resistSleep = self.__equip.query( "eq_ResistSleep", 0 )
		if eq_resistSleep and self.doWieldCalc:
			eq_resistSleep = CombatUnitConfig.valueToPer( eq_resistSleep, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistSleep * self.floatZipPercent * self.statValueStandardModifier )

	def getResistHitProb( self, **config ):
		"""
		�мܵ�������
		"""
		self.__doConfig( config )

		# �мܵ�������
		eq_resistHit = self.__equip.query( "eq_ResistHit", 0 )
		if eq_resistHit and self.doWieldCalc:
			eq_resistHit = CombatUnitConfig.valueToPer( eq_resistHit, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_resistHit * self.floatZipPercent * self.statValueStandardModifier )

	def getDodgeProb( self, **config ):
		"""
		���ܸ���
		"""
		self.__doConfig( config )

		# ��������
		eq_dodge = self.__equip.query("eq_Dodge", 0 )
		if eq_dodge and self.doWieldCalc:
			eq_dodge = CombatUnitConfig.valueToPer( eq_dodge, self.ownerLevel )

		return int( self.baseQualityRate * self.addBaseRate * eq_dodge * self.floatZipPercent * self.statValueStandardModifier )
	
	def getReduceRoleD( self, **config ):
		"""
		����ֵ
		"""
		self.__doConfig( config )
		
		eq_reduceRoleD = self.__equip.query("eq_ReduceRoleD", 0.0 )
		
		return int( eq_reduceRoleD * self.floatZipPercent  )

	def getAddRoleD( self, **config ):
		"""
		�Ƶ�ֵ
		"""
		self.__doConfig( config )
		
		eq_addRoleD = self.__equip.query("eq_AddRoleD", 0.0 )
		return int( eq_addRoleD * self.floatZipPercent  )
	
	def getIntensifyDamageInc( self, **config ):
		"""
		��ȡ��ǿ�����µ���������ֵ
		"""
		if not self.__equip.getIntensifyLevel():
			#û��ǿ��ֱ�Ӹ�0
			return 0

		self.__doConfig( config )

		return int( self.intensifyDamageInc )

	def getIntensifyMagicDamageInc( self, **config ):
		"""
		��ȡ��ǿ�����µ�ħ��������ֵ
		"""
		if not self.__equip.getIntensifyLevel():
			#û��ǿ��ֱ�Ӹ�0
			return 0

		self.__doConfig( config )

		return int( self.intensifyMagicDamageInc )

	def getDPSValue( self, **config ):
		"""
		��ȡDPS��ֵ
		"""
		self.__doConfig( config )
		eq_DPS = self.__equip.query( "eq_DPS", 0.0 )
		return int( eq_DPS * self.baseQualityRate * self.addBaseRate * self.floatZipPercent * self.statValueStandardModifier )

	def getDPSFluctuation( self, **config ):
		"""
		��ȡDPS����
		"""
		self.__doConfig( config )
		fluctuation = self.__equip.query( "eq_DPSArea", 0.0 )
		return int( fluctuation * self.floatZipPercent )

	def getDefaultDPSFluctuation( self, **config ):
		"""
		��ȡ����״̬�µ�DPS����
		"""
		self.__doConfig( config )
		return int( 0.3 * self.floatZipPercent )

	def getDefaultHitSpeedBase( self, **config ):
		"""
		��ȡ����״̬�µĹ��ٻ���ֵ
		"""
		self.__doConfig( config )
		return int( 1.3 * self.floatZipPercent )

	def getDefaultAttackRangeBase( self, **config ):
		"""
		��ȡ����״̬�µĹ��ٻ���ֵ
		"""
		self.__doConfig( config )
		return int( 2.0 * self.floatZipPercent )

	def getHitSpeedBase( self, **config ):
		"""
		��ȡ�����ٶȻ���ֵ
		"""
		self.__doConfig( config )
		hit_speed = self.__equip.query( "eq_delay", 0.0 )
		return int( hit_speed * csconst.FLOAT_ZIP_PERCENT )

	def getAttackRangeBase( self, **config ):
		"""
		��ȡ�����Ĺ�������
		"""
		self.__doConfig( config )
		eq_range = self.__equip.query( "eq_range", 0.0 )
		return int( eq_range * csconst.FLOAT_ZIP_PERCENT )

	def getMagicDamageValue( self, **config ):
		"""
		��ȡ������ħ����ֵ
		"""
		self.__doConfig( config )
		eq_magic_damage = self.__equip.query( "eq_magicPower", 0.0 )
		return int( eq_magic_damage * self.baseQualityRate * self.addBaseRate * self.statValueStandardModifier )

class EquipAttrExp:
	"""
	װ���������Ի�ȡ
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
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
		������Ʒ��Ʒ��ǰ׺��ȡ��Ʒ�ļ�ֵ����
		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@param quality: ��ƷƷ��
		@type  quality: Int
		@param prefix: ��Ʒǰ׺
		@type  prefix: Int
		"""
		# ��Ʒ���������� * 1.82*��7.5*��2*�ȼ�*��������Ʒ�ʱ��ʣ�^1.54+���ȼ�^1.5*2.5+60��*��������Ʒ�ʱ��ʣ�
		excQualityRate = EquipQualityExp.instance().getexcRateByQandP( quality, prefix )
		priceGeneAmend = ItemTypeAmendExp.instance().getGeneAmend( type )
		
		statValueStandardModifier, \
		arg1, \
		arg2 = equipPriceGeneData[ level ]
		
		#װ���ܼ�ֵ���� = ��ֵˮƽϵ�� * ��λ���� * ��������Ʒ�ʱ��� * ����1 * ����2 ^ ( 0.1 * ���ߵȼ��C1 �� 
		priceGene = statValueStandardModifier * priceGeneAmend * excQualityRate * arg1 * arg2 ** ( 0.1 * level - 1 )
		return priceGene
		
	def getRandomAttr( self, itemLevel, attrNum, hasCodes = [] ):
		"""
		����������
		@param itemLevel: ��Ʒ�ȼ�
		@type  itemLevel: ITEM_LEVEL
		@param attrNum: װ���ĵڼ�������
		@type  attrNum: Int
		@param hasCodes:�Ѿ��浽������
		"""
		#1.ȡ�������еĸ���
		newDic = {}  #�µķ������������Լ����Ӧ�����ֵ�
		sum_pro = 0  #�µķ��������������ڻ��������еĸ��ʺ�
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
			if code not in hasCodes: #ȥ���Ѿ��浽������
				for levelRegion,pro in attr.iteritems():
					if  levelRegion[0]  <= itemLevel <= levelRegion[1]:
						newDic[ code ] = pro
						sum_pro += pro
						break
		
		#2.���¼������
		codePro = 0
		for code in newDic.keys():
			newDic[code] = ( codePro,codePro+newDic[code]/sum_pro )
			codePro = newDic[code][1]
		
		#3.��������ĸ�����
		ranV = random.random()
		for code,pro in newDic.iteritems():
			if pro[0] < ranV <= pro[1]:
				return code
		return -1	
		
	def getEquipRandomEffect( self, itemID, itemLevel, equipType, quality ):
		"""
		��ȡװ�����������
		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@param quality: ��ƷƷ��
		@type  quality: Int
		"""
		dic = {}
		attrNum = ItemTypeEnum.EQUIP_ATTR_NUM_MAPS[ quality ]
		#��ⲿλ���߾�����ڲ���
		if equipType != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL:
			if equipType not in E_Data.keys():
				return {}
		else:
			if itemID not in S_Data.keys():
				return {}
			
		if attrNum == 0: return {}
		#���������
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
		#�ٻ�����Ծ���Ӷ���ֵ
		if len( dic ) > 0:
			if equipType != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL:
				for attrCode in dic.keys():
					fluctuation_range = E_Data[equipType][max( (itemLevel/10)*10, 10 )][attrCode]
					#���һ�¿�ȡֵ����
					ranV = random.random()
					for info in fluctuation_range: #info�Ľṹ�� 10,20,2,0.1,0.3
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
					#���һ�¿�ȡֵ����
					ranV = random.random()
					for info in fluctuation_range: #info�Ľṹ�� 10,20,2,0.1,0.3
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
		��þ���ϳ�ʱ���������
		"""
		dic = {}
		keyL = sdic.keys()
		attrNum = ItemTypeEnum.EQUIP_ATTR_NUM_MAPS[ quality ]
		#���������
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
			#���һ�¿�ȡֵ����
			ranV = random.random()
			for info in fluctuation_range: #info�Ľṹ�� 10,20,2,0.1,0.3
				if info[3] < ranV <= info[4] :
					if int(info[0]) == int(info[1]):
						dic[attrCode] = int(info[0])
					else:	
						dic[attrCode] = random.randrange( int(info[0]), int(info[1]), int(info[2]) )
					if attrCode in ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE:
						dic[attrCode] =  dic[attrCode] / ItemTypeEnum.EQUIP_ATTR_MAGNIFY_RATE[attrCode]
					break
		return dic



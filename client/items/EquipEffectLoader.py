# -*- coding: gb18030 -*-

#$Id: EquipEffectLoader.py,v 1.5 2008-08-20 01:51:18 yangkai Exp $

from bwdebug import *
import Language
from SmartImport import smartImport
from config.item import EquipEffects
from ItemSystemExp import EquipQualityExp
from ItemSystemExp import ItemTypeAmendExp
from config.item.EquipPriceGeneLevelConfig import Datas as equipPriceGeneData
import ItemTypeEnum
import items
import csconst
g_items = items.instance()
g_itemTypeAmend = ItemTypeAmendExp.instance()
g_itemQualityExp = EquipQualityExp.instance()




# ----------------------------------------------------------------------------------------------------
# 装备属性加载
# ----------------------------------------------------------------------------------------------------

class EquipEffectLoader:
	"""
	装备属性加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipEffectLoader._instance is None, "instance already exist in"
		self._datas = EquipEffects.Datas
		self._serverDatas = EquipEffects.serverDatas
		for key, value in self._datas.iteritems():
			self._datas[key]["script"] = smartImport( value["script"] )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipEffectLoader()
		return self._instance

	def getEffect( self, effectID ):
		"""
		根据效果ID获取效果对应脚本类
		"""
		try:
			return self._datas[effectID]["script"]
		except:
			ERROR_MSG( "Can't find equipEffect config by %s" % effectID )
			return None

	def getStonEffectType( self, effectID ):
		"""
		根据效果ID获取效果对应水晶类
		"""
		try:
			return self._datas[effectID]["propType"]
		except:
			return None

	def canSmelt( self, effectID ):
		"""
		判断该条属性是否允许炼化
		@param effectID: 效果编号
		@type  effectID: Int
		@return 1 or 0
		"""
		try:
			return self._datas[effectID]["canSmelt"]
		except KeyError:
			ERROR_MSG( "Can't find canSmelt config by %s" % effectID )
			return 0

	def getIcon( self , effectID, value ):
		"""
		根据效果ID获取拥有该效果的宝石的图标
		"""
		try:
			return self._datas[effectID]["effect_icon_mapping"][value]
		except:
			return ""
	
	def getItemPriceGene( self, itemID, quality, prefix ):
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
		itemLevel = g_items.getLevel( itemID )
		excQualityRate = g_itemQualityExp.getexcRateByQandP( quality, prefix )
		priceGeneAmend = g_itemTypeAmend.getGeneAmend( g_items.getType( itemID ) )
		
		#priceGene = priceGeneAmend * 1.82 * ( 7.5 * ( 2 * itemLevel * excQualityRate ) ** 1.54 + ( itemLevel ** 1.5 * 2.5 + 60 ) * excQualityRate )
		
		statValueStandardModifier, 	arg1, 	arg2 = equipPriceGeneData[ itemLevel ]
		
		#装备总价值因子 = 价值水平系数 * 部位折算 * 附加属性品质比率 * 参数1 * 参数2 ^ ( 0.1 * 道具等级–1 ） 
		priceGene = statValueStandardModifier * priceGeneAmend * excQualityRate * arg1 * arg2 ** ( 0.1 * itemLevel - 1 )
		return priceGene

	def getPerGene( self, effectID ):
		"""
		根据效果ID获取每单位该效果所需价值因子数
		"""
		try:
			gene =  self._serverDatas[effectID]["needPerProceGene"]
		except:
			gene = 0
		return gene
	
	def getType( self, effectID ):
		"""
		根据效果ID获取属性类型
		"""
		data = self._datas.get( effectID, None )
		if data is None: return ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD
		return data.get( "type", ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD )	
	
	def getEffectMax( self, equip, effectId) :
		"""
		获取装备某条属性的最大可能取值
		@equip:装备实例
		@effectId:属性id
		"""
		#获取每条属性的价值因子最大值 ( 逆天绿装的价值因子平均到每条属性 )
		priceGeneMax = self.getItemPriceGene( equip.id, ItemTypeEnum.CQT_GREEN,ItemTypeEnum.CPT_MYGOD )
		
		genePerEffect = float (priceGeneMax) * csconst.EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR
	
		genePerPoint = float ( self.getPerGene( effectId ) )
	
		if genePerPoint ==0 : return 0
		
		maxValue = genePerEffect / genePerPoint
		
		#添加属性类型区分，加值向下取整，加成不变 by cxm 2010.10.13
		type = self.getType( effectId )
		if type == ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD:
			maxValue = int( maxValue )
		
		return maxValue
	


#$Log: not supported by cvs2svn $
#Revision 1.4  2008/05/17 11:59:49  huangyongwei
#SmartImport 改为 smartImport
#
#Revision 1.3  2008/04/08 08:20:08  yangkai
#添加接口canSmelt
#
#Revision 1.2  2008/02/29 07:45:52  yangkai
#效果类型ID由String调整为Int
#
#Revision 1.1  2008/02/22 01:29:05  yangkai
#装备效果加载
#
#
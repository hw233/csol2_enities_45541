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
# װ�����Լ���
# ----------------------------------------------------------------------------------------------------

class EquipEffectLoader:
	"""
	װ�����Լ���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
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
		����Ч��ID��ȡЧ����Ӧ�ű���
		"""
		try:
			return self._datas[effectID]["script"]
		except:
			ERROR_MSG( "Can't find equipEffect config by %s" % effectID )
			return None

	def getStonEffectType( self, effectID ):
		"""
		����Ч��ID��ȡЧ����Ӧˮ����
		"""
		try:
			return self._datas[effectID]["propType"]
		except:
			return None

	def canSmelt( self, effectID ):
		"""
		�жϸ��������Ƿ���������
		@param effectID: Ч�����
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
		����Ч��ID��ȡӵ�и�Ч���ı�ʯ��ͼ��
		"""
		try:
			return self._datas[effectID]["effect_icon_mapping"][value]
		except:
			return ""
	
	def getItemPriceGene( self, itemID, quality, prefix ):
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
		itemLevel = g_items.getLevel( itemID )
		excQualityRate = g_itemQualityExp.getexcRateByQandP( quality, prefix )
		priceGeneAmend = g_itemTypeAmend.getGeneAmend( g_items.getType( itemID ) )
		
		#priceGene = priceGeneAmend * 1.82 * ( 7.5 * ( 2 * itemLevel * excQualityRate ) ** 1.54 + ( itemLevel ** 1.5 * 2.5 + 60 ) * excQualityRate )
		
		statValueStandardModifier, 	arg1, 	arg2 = equipPriceGeneData[ itemLevel ]
		
		#װ���ܼ�ֵ���� = ��ֵˮƽϵ�� * ��λ���� * ��������Ʒ�ʱ��� * ����1 * ����2 ^ ( 0.1 * ���ߵȼ��C1 �� 
		priceGene = statValueStandardModifier * priceGeneAmend * excQualityRate * arg1 * arg2 ** ( 0.1 * itemLevel - 1 )
		return priceGene

	def getPerGene( self, effectID ):
		"""
		����Ч��ID��ȡÿ��λ��Ч�������ֵ������
		"""
		try:
			gene =  self._serverDatas[effectID]["needPerProceGene"]
		except:
			gene = 0
		return gene
	
	def getType( self, effectID ):
		"""
		����Ч��ID��ȡ��������
		"""
		data = self._datas.get( effectID, None )
		if data is None: return ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD
		return data.get( "type", ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD )	
	
	def getEffectMax( self, equip, effectId) :
		"""
		��ȡװ��ĳ�����Ե�������ȡֵ
		@equip:װ��ʵ��
		@effectId:����id
		"""
		#��ȡÿ�����Եļ�ֵ�������ֵ ( ������װ�ļ�ֵ����ƽ����ÿ������ )
		priceGeneMax = self.getItemPriceGene( equip.id, ItemTypeEnum.CQT_GREEN,ItemTypeEnum.CPT_MYGOD )
		
		genePerEffect = float (priceGeneMax) * csconst.EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR
	
		genePerPoint = float ( self.getPerGene( effectId ) )
	
		if genePerPoint ==0 : return 0
		
		maxValue = genePerEffect / genePerPoint
		
		#��������������֣���ֵ����ȡ�����ӳɲ��� by cxm 2010.10.13
		type = self.getType( effectId )
		if type == ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD:
			maxValue = int( maxValue )
		
		return maxValue
	


#$Log: not supported by cvs2svn $
#Revision 1.4  2008/05/17 11:59:49  huangyongwei
#SmartImport ��Ϊ smartImport
#
#Revision 1.3  2008/04/08 08:20:08  yangkai
#��ӽӿ�canSmelt
#
#Revision 1.2  2008/02/29 07:45:52  yangkai
#Ч������ID��String����ΪInt
#
#Revision 1.1  2008/02/22 01:29:05  yangkai
#װ��Ч������
#
#
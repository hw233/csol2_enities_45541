# -*- coding: gb18030 -*-

#$Id: ItemDropLoader.py,v 1.16 2008-08-09 09:31:10 wangshufeng Exp $

from bwdebug import *
from MsgLogger import g_logger
import Language
import random
import items
import Const
import ItemTypeEnum
import time
import sys
from SmartImport import smartImport

g_items = items.instance()

from config.server.droppedItem import	eq_wieldType
from config.server.droppedItem import	equip_quality
from config.server.droppedItem import	LuckyBoxItemDropZhaocai
from config.server.droppedItem import	LuckyBoxItemDropJinbao
from config.server.droppedItem import	EquipMakeDropAmend
from config.server.droppedItem import	SpecialDropAmend
from config.server.droppedItem import	lotteryDropAmend
from config.server.droppedItem import	TreasureBoxDrops
from config.server.droppedItem import	HonorItemZhaocai
from config.server.droppedItem import	HonorItemJinbao


# ----------------------------------------------------------------------------------------------------
# ��Ʒ����������
# ----------------------------------------------------------------------------------------------------
class ItemDropInWorldLoader:
	"""
	��Ʒ����������
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ItemDropInWorldLoader._instance is None, "instance already exist in"
		self.tidyDatas = equip_quality.Datas # ���ݲ�ͬ��Ʒ�ʷֿ��洢 like { quality:{ npcLevel : { "items" : [ ( itemID, quality, prefix, dropOdds ),...],"totalDropOdds" : alDropOdds } } ,{ quality: .........} }
		self.specialDatas = eq_wieldType.Datas # ���ݲ�ͬ��Ʒ�ʵȼ��Ͳ�λ�ֿ��洢

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = ItemDropInWorldLoader()
		return self._instance

	def getDropItems( self, npcLevel ):
		"""
		���ݹ���ȼ���ȡ���������Ϣ
		@type  npcLevel: INT
		@param npcLevel: ����ȼ�
		@return [ ( itemID, quality, prefix, dropOdds )... ]
		"""
		try:
			datas = []
			for tidyDatas in self.tidyDatas.itervalues():
				datas.append( ( tidyDatas[npcLevel]["items"], tidyDatas[npcLevel]["totalDropOdds"] ) )		#like ( [��Ʒ��Ϣ], �ܵ���  )
			return datas
		except KeyError:
			return []

	def getDropOdds( self, npcLevel ):
		"""
		��ȡָ���ȼ���װ������
		"""
		odds = 0.0
		for tidyDatas in self.tidyDatas.itervalues():
			odds += tidyDatas[npcLevel]["totalDropOdds"]
		return odds

	def randomValue( self, quality, npcLevel ):
		"""
		���һ���õȼ��ܵ������ڵ�ֵ
		"""
		try:
			return random.random() * self.tidyDatas[ quality ][ npcLevel ][ "totalDropOdds" ]
		except:
			try:
				g_logger.itemDropExceptLog( "in ItemDropInWorldLoader Drop a not exist Item, Info: quality %s, npcLevel %s" % ( quality, npcLevel ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return -1.0


	def getItem( self, quality, npcLevel ):
		"""
		���ݵ���ֵ��ȡ�������Ʒ
		"""
		odds = self.randomValue( quality, npcLevel )
		if odds == -1.0:
			return None
		for item in self.tidyDatas[ quality ][ npcLevel ][ "items" ]:
			if odds <= item[3]:
				return item
		try:
			g_logger.itemDropExceptLog( "in ItemDropInWorldLoader, can not drop this item : odds(%s), quality(%s), npcLevel(%s)" %( odds,quality,npcLevel ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return None

	def specialRandomValue( self, quality, npcLevel, eq_wieldType ):
		"""
		���һ���õȼ��ܵ������ڵ�ֵ������֣�
		"""
		try:
			return random.random() * self.specialDatas[ quality ][ npcLevel ][ eq_wieldType ][ "totalDropOdds" ]
		except:
			try:
				g_logger.itemDropExceptLog( "in ItemDropInWorldLoader Drop a not exist Item, Info: quality %s, npcLevel %s, eq_wieldType %s" % ( quality, npcLevel, eq_wieldType )  )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return -1.0

	def getSpecialItem( self, quality, npcLevel, eq_wieldType ):
		"""
		���ݵ���ֵ��ȡ�������Ʒ������֣�
		"""
		odds = self.specialRandomValue( quality, npcLevel, eq_wieldType )
		if odds == -1.0:
			return None
		for item in self.specialDatas[ quality ][ npcLevel ][ eq_wieldType ][ "items" ]:
			if odds <= item[3]:
				return item
		try:
			g_logger.itemDropExceptLog( "in ItemDropInWorldLoader, can not drop this item : odds(%s), quality(%s), npcLevel(%s), eq_wieldType(%s)" %( odds,quality,npcLevel,eq_wieldType ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return None

	def getSpecialwieldTypeList( self, quality, npcLevel ):
		"""
		����Ʒ�ʺ͵ȼ���ȡ�����װ����λ�б�����֣�
		"""
		try:
			return self.specialDatas[ quality ][ npcLevel ].keys()
		except:
			try:
				g_logger.itemDropExceptLog( "in ItemDropInWorldLoader, can not drop a level items : quality(%s), npcLevel(%s)" % ( quality, npcLevel ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return []

	def getDropItemsEx( self, quality, npcLevel):
		"""
		���ݹ���ȼ���ȡ���������Ϣ�е�ָ��Ʒ�ʵ���Ʒ�ĵ�����Ϣ
		"""
		try:
			return self.tidyDatas[quality][npcLevel]["items"]
		except KeyError:
			return []

	def getItemsTotalOddsEx( self, quality, npcLevel ):
		"""
		���ݹ���ȼ���ȡ���������Ϣ�е�ָ��Ʒ�ʵ���Ʒ�ĸü���ĵ�������ܺ�
		@type  npcLevel: INT
		@param npcLevel: ����ȼ�
		@return [ ( itemID, quality, prefix, dropOdds )... ]
		"""
		try:
			return self.tidyDatas[quality][npcLevel]["totalDropOdds"]
		except KeyError:
			return 0.0

	def getItemByClass( self, quality, npcLevel, playerClass ):
		"""
		��ȡ��ӦƷ�ʡ��ȼ���ְҵ��װ��
		"""
		itemList = []
		for item in self.tidyDatas[ quality ][ npcLevel ][ "items" ]:
			itemID = item[0]
			if g_items[itemID]['reqClasses'] == [ playerClass ] and not itemID in itemList:
				itemList.append( itemID )
		return itemList

# ----------------------------------------------------------------------------------------------------
# ��ͨ��������������
# ----------------------------------------------------------------------------------------------------
class ItemDropSundriesLoader:
	"""
	����������
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
	@type _data: dict
	"""
	def __init__( self, pyconfig ):
		self._datas = pyconfig.Datas # like as { npcID : { itemID : { "odds" : odds, "amount" : amount, "multiOdds" : multiOdds }, ... } }

	def getDropItemInfo( self, monsterID ):
		"""
		��ȡ���������Ϣ
		@type  monsterID: String
		@param monsterID: ��������
		"""
		try:
			return self._datas[monsterID]["items"]
		except:
			WARNING_MSG( "Can't Find SunbriesItemDrop config By %s" % monsterID )
			return []

	def getMaxOdds( self, monsterID ):
		"""
		��ȡ�������е�����Ʒ�����ܺͣ�����Ȩ�ؼ���
		@type  monsterID: String
		@param monsterID: ��������
		@return Float
		"""
		try:
			return self._datas[monsterID]["maxOdds"]
		except:
			WARNING_MSG( "Can't Find MaxOdds config By %s" % monsterID )
			return 0

	def getMultiOdds( self, monsterID, itemID ):
		"""
		��ȡ��������Ʒ�ĵ���������
		@type  monsterID: String
		@param monsterID: ��������
		@type  itemID: ITEM_ID
		@param itemID: ��ƷID
		"""
		try:
			return self._datas[monsterID]["multiOdds"][itemID]
		except:
			WARNING_MSG( "Can't Find modifyOdds config By %s" % monsterID )
			return 0

	def getModifyDropAmount( self, monsterID, amount, itemID ):
		"""
		�����������������1��ʱ����һ���������ڿ��Ƶ�������
		���磺ĳ��������һ������2�����ϣ���ô����һ���������ڿ���
		�ù����������䡣���������һ������ֵ������Ϊ 70% ����ô
		������������������һ��ʱ��100%���ģ���2����70%������
		3����49%��....�Դ�����
		@type  monsterID: String
		@param monsterID: ��������
		@type  amount: Int
		@param amount: ��Ʒ����
		"""
		if amount == 1: return amount
		dropAmount = 0
		multiOdds = self.getMultiOdds( monsterID, itemID )
		r = random.random()
		for index in xrange( 1, amount ):
			if r <= ( multiOdds ** index ):
				dropAmount = index
		return dropAmount + 1

	def getDropItem( self, monster):
		"""
		��ȡ�������Ʒ
		"""
		monsterID = monster.className
		sundriesDropInfo = self.getDropItemInfo( monsterID )
		maxOdds = self.getMaxOdds( monsterID )
		r = random.random() * maxOdds
		for itemID, amount, odds in sundriesDropInfo:
			if r <= odds:
				dropAmount = self.getModifyDropAmount( monsterID, amount, itemID )
				tempItem =  g_items.createDynamicItem( int( itemID ) , dropAmount )
				if tempItem is None:
					continue
				return tempItem
		return None


# ----------------------------------------------------------------------------------------------------
# ��������շѵ�����Ʒ����
# ----------------------------------------------------------------------------------------------------
class ItemDropTreasureBoxLoader:
	"""
	��������շѵ�����Ʒ����
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ItemDropTreasureBoxLoader._instance is None, "instance already exist in"
		self._datas = TreasureBoxDrops.Datas	# like as { npcID : { "items" : [ ( itemID, quality, prefix ),...], "amendOdds" : amendOdds } ,..... }


	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = ItemDropTreasureBoxLoader()
		return self._instance


	def getDropItems( self, boxLevel ):
		"""
		���ݹ���ȼ���ȡ���������Ϣ
		@type  boxLevel: INT
		@param boxLevel: ����ȼ�
		@return [ ( itemID, quality, prefix, dropRate )... ]
		"""
		try:
			return self._datas[boxLevel]
		except KeyError:
			ERROR_MSG("has no item boxLevel = %s" % boxLevel )
			return []

	def randomValue( self, boxLevel ):
		"""
		���һ���õȼ��ܵ������ڵ�ֵ
		"""
		try:
			return random.random() * self._datas[ boxLevel][-1][1]		# format [(id,odds,amount)] -1��ʾ���һ�У�1������䣬���һ�еĵڶ�������ֵΪ�ܵ���
		except:
			ERROR_MSG( "can not find  item  boxLevel(%s)" % boxLevel )
			return -1.0

	def getEquipDropInfo( self , level, quality ):
		"""
		��ȡ���п��ܵ�װ������
		"""
		worldDrop =  ItemDropInWorldLoader.instance()
		data = worldDrop.getItem( quality, level )
		return data

	def getDropItem( self, boxLevel):
		"""
		��ȡ�������Ʒ
		"""
		dropDatas = self.getDropItems( boxLevel )
		if len( dropDatas ) == 0:
			return None
		dropRate  = self.randomValue( boxLevel )
		if dropRate < 0.0:
			return None
		for itemID, dropOdds, dropAmount in dropDatas:
			if dropRate <= dropOdds:
				if itemID.startswith( "equip_quality" ): #�����װ��
					quality = int( itemID[-1] )
					itemInfo = self.getEquipDropInfo( boxLevel, quality ) #itemInfo ��ʽ ( itemID, quality, prefix, odds )
					if not itemInfo:
						ERROR_MSG( "can not get equip level = %s, quality = %s " % (boxLevel, quality) )
						return None
					itemInst = g_items.createDynamicItem( int( itemInfo[0] ) , 1 )		# װ���̶�ֻ��һ�� ����ȡ���ã��������ô���
					if itemInst is None:
						ERR0R_MSG( "Create Equip Error, item id = %s " % itemInfo[0]  )
						return None
					if itemInfo[1] !=0 and itemInfo[2] != 0:
						itemInst.setQuality( itemInfo[1] )
						itemInst.setPrefix( itemInfo[2] )
						if not itemInst.createRandomEffect():
							DEBUG_MSG( "getDropItem createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemInfo[0], itemInfo[1], itemInfo[2] ) )
					return itemInst
				else:
					itemInst = g_items.createDynamicItem( int( itemID ) , dropAmount )
					if itemInst is None:
						ERR0R_MSG( "Create Equip Error, item id = %s " % itemInfo[0]  )
						return None
					return itemInst
		return  None

# --------------------------------------------------------------------------------------------
# �콵���е���.15:59 2009-1-12,wsf
# --------------------------------------------------------------------------------------------
class LuckyBoxDrop:
	"""
	�콵���е������ݻ���
	"""
	def __init__( self, dictDat ):
		"""
		@param		dictDat: ��������
		@type		dictDat: python dictDat
		"""
		self.dtype = dictDat[ "drop_type" ]	# ��������
		self.level = dictDat[ "level" ]		# ��Ӧ���콵���м���
		self.rate = dictDat[ "rate" ]		# �������
		self.rateNode = 0.0							# �������ڽڵ�

	def getDropData( self ):
		"""
		Virtual method.
		��õ������ݣ����������д�˷���
		"""
		try:
			g_logger.itemDropExceptLog( "this is virtual method.-->>>" )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setRateNode( self, rateNode ):
		"""
		���������ĸ���Ʒ�Ĺ����� �ڼ����Ӧ���ܵ��ʷ�Χ���һ����ֵ����ÿһ������ʵ�������Լ����ڵĵ��ʷ�Χ
		������������ĳ������ʵ���ĵ��ʷ�Χ�����������Ľ��Ǵ�ʵ����

		���洢���䷶Χ�����ֵ����Ϊ�жϵ�ʵ�ִ���Сֵ��ʼ�жϣ�ֱ���ҵ����ʵĵ���ʵ����

		@type rateNode : FLOAT
		"""
		self.rateNode = rateNode

	def getRateNode( self ):
		"""
		@type rateNode : FLOAT
		"""
		return self.rateNode


class LuckyBoxDropItem( LuckyBoxDrop ):
	"""
	�콵���е�����Ʒ
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		self.itemID = int( dictDat[ "param" ] )


	def getDropData( self ):
		"""
		"""
		tempItem = items.instance().createDynamicItem( self.itemID )
		return ( self.dtype, tempItem )


class LuckyBoxDropAmount( LuckyBoxDrop ):
	"""
	�콵���е�����ֵ�������ھ��顢Ǳ�ܡ���Ǯ�����ڸ���dtype�������ִ�3�ֵ��䣬���3�ֶ�ʹ�ô��ࡣ
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		self.amount = int( dictDat[ "param" ] )	# ����/Ǳ��/��Ǯ


	def getDropData( self ):
		"""
		"""
		return ( self.dtype, self.amount )


class LuckyBoxDropEquip( LuckyBoxDrop ):
	"""
	�콵���е��䣺a-b��cƷ�ʵ����������磺1-3������װ
	10�����ӵ����Ʒ��2����������ͬ10������ĵ��䣬10:21 2009-1-14��wsf
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		tempList = dictDat["param"].split( "|" )
		self.quality = int( tempList[0] )
		self.lowLevel = int( tempList[1] )
		self.highLevel = int( tempList[2] )


	def getDropData( self ):
		"""
		10�����ӵ����Ʒ��2����������ͬ10������ĵ���10:21 2009-1-14��wsf
		���������ܱ����ṩ�˽ӿڣ���������ķ�ʽ��
		"""
		#level = random.randint( self.lowLevel, self.highLevel )
		itemData = ItemDropInWorldLoader.instance().getItem( self.quality, self.level )	# ( itemID, quality, prefix, dropOdds )
		item = items.instance().createDynamicItem( int( itemData[ 0 ] ) )
		item.set( "quality", itemData[ 1 ] )
		item.set( "prefix", itemData[2] )
		if not item.createRandomEffect():
			DEBUG_MSG( "getDropData createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemData[0], itemData[1], itemData[2] ) )
		return ( self.dtype, item )


class HonorItem( LuckyBoxDrop ):
	"""
	�����ȶһ���Ʒ
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		self.itemID = int( dictDat[ "param" ] )
		self.count	= int( dictDat[ "count" ] )


	def getDropData( self ):
		"""
		"""
		tempItem = items.instance().createDynamicItem( self.itemID, max( self.count, 1 ) )
		return ( self.dtype, tempItem )

# ����һ���������͵���ӳ��
LUCKY_DROP_ITEM_MAP = {	Const.LUCKY_BOX_DROP_NORMAL_ITEM : LuckyBoxDropItem,
						Const.LUCKY_BOX_DROP_EQUIP : LuckyBoxDropEquip,
						Const.LUCKY_BOX_DROP_MONEY : LuckyBoxDropAmount,
						Const.LUCKY_BOX_DROP_POTENTIAL : LuckyBoxDropAmount,
						Const.LUCKY_BOX_DROP_EXP : LuckyBoxDropAmount,
						Const.HONOR_ITEM	: HonorItem,
						}


class ItemDropLuckyBoxZhaocai:
	"""
	�콵����:�вƣ��������ü���
	"""
	_instance = None
	#��config.server.droppedItem.LuckyBoxItemDropZhaocai.Datas ����Դ��ʼ����ʵ��
	_datas		= LuckyBoxItemDropZhaocai.Datas

	def __init__( self ):
		"""
		"""
		assert ItemDropLuckyBoxZhaocai._instance is None,"Just allow only one instance exist!!"

		self._levelMapRate = {}	# �����Ӧ���ܵ��ʣ��������ƻ��������ķ�Χ{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# ��ŵ�����Ʒ����������{ ����1:{ ���ʶ����ֵ1:����ʵ��1,���ʶ����ֵ2:����ʵ��2,...}, ... }

		ItemDropLuckyBoxZhaocai._instance = self
		self.init( )


	@classmethod
	def instance( self ):
		"""
		"""
		if ItemDropLuckyBoxZhaocai._instance is None:
			ItemDropLuckyBoxZhaocai._instance = ItemDropLuckyBoxZhaocai()
		return ItemDropLuckyBoxZhaocai._instance

	def init( self ):
		"""
		"""
		for i in xrange( len( self._datas ) ):
			node = self._datas[ i ]
			dtype = node["drop_type"]
			level = node["level"]
			rate = node["rate"]
			if not self._data.has_key( level ):
				self._data[ level ] = []
			if not self._levelMapRate.has_key( level ):
				self._levelMapRate[ level ] = 0.0
			levelDropTable = self._data[ level ]
			self._levelMapRate[ level ] += rate
			dropInstance = LUCKY_DROP_ITEM_MAP[ dtype ]( node )
			dropInstance.setRateNode( self._levelMapRate[ level ] )
			levelDropTable.append( dropInstance )


	def getDropData( self, level ):
		"""
		���ݱ��еĵȼ���õ�������

		@param level : ���м���
		@type level : UINT16
		@return ( ���е�������, �������� )
		"""
		totalRate = self._levelMapRate[ level ]	# �����Ӧ���ܵ��ʣ����ڴ˵��ʷ�Χ���ȷ������������Ʒ
		dropRate = random.random() * totalRate
		for dropInstace in self._data[ level ]:
			if dropRate < dropInstace.getRateNode():
				return dropInstace.getDropData()


class ItemDropLuckyBoxJinbao:
	"""
	�콵����:�������������ü���
	"""
	_instance 	= None
	#��config.server.droppedItem.LuckyBoxItemDropJinbao.Datas ����Դ��ʼ����ʵ��
	_datas 		= LuckyBoxItemDropJinbao.Datas

	def __init__( self ):
		"""
		"""
		assert ItemDropLuckyBoxJinbao._instance is None,"Just allow only one instace exist!!"
		ItemDropLuckyBoxJinbao._instance = self

		self._levelMapRate = {}	# �����Ӧ���ܵ��ʣ��������ƻ��������ķ�Χ{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# ��ŵ�����Ʒ����������{ ����1:{ ���ʶ����ֵ1:����ʵ��1,���ʶ����ֵ2:����ʵ��2,...}, ... }
		self.init( )

	@classmethod
	def instance( self ):
		"""
		"""
		if ItemDropLuckyBoxJinbao._instance is None:
			ItemDropLuckyBoxJinbao._instance = ItemDropLuckyBoxJinbao()
		return ItemDropLuckyBoxJinbao._instance

	def init( self ):
		"""
		"""
		for i in xrange( len( self._datas ) ):
			node = self._datas[ i ]
			dtype = node["drop_type"]
			level = node["level"]
			rate = node["rate"]
			if not self._data.has_key( level ):
				self._data[ level ] = []
			if not self._levelMapRate.has_key( level ):
				self._levelMapRate[ level ] = 0.0
			levelDropTable = self._data[ level ]
			self._levelMapRate[ level ] += rate
			dropInstance = LUCKY_DROP_ITEM_MAP[ dtype ]( node )
			dropInstance.setRateNode( self._levelMapRate[ level ] )
			levelDropTable.append( dropInstance )


	def getDropData( self, level ):
		"""
		���ݱ��еĵȼ���õ�������

		@param level : ���м���
		@type level : UINT16
		@return ( ���е�������, �������� )
		"""
		totalRate = self._levelMapRate[ level ]	# �����Ӧ���ܵ��ʣ����ڴ˵��ʷ�Χ���ȷ������������Ʒ
		dropRate = random.random() * totalRate
		for dropInstace in self._data[ level ]:
			if dropRate < dropInstace.getRateNode():
				return dropInstace.getDropData()

# ----------------------------------------------------------------------------------------------------
# ���ҵ���Ʒ�������ü���
# ----------------------------------------------------------------------------------------------------
class ItemDropLotteryLoader:

	"""
	���ҵ���Ʒ�������ü���
	"""

	_instance = None

	def __init__( self ):
		"""
		��ʼ�������ص�������
		@type  xmlConfig : STRING
		@param xmlConfig : ���õ�·��
		"""
		assert ItemDropLotteryLoader._instance is None, "instance already exist in"
		self.__datas   = lotteryDropAmend.Datas #�洢��������
		self.totalodds = lotteryDropAmend.Totalodds #��¼�ܵĵ�����

	def getDropDatas( self ):
		"""
		��ȡ�洢�ĵ�������
		"""
		return self.__datas

	def gettotalodds( self, fact ):
		"""
		��ȡ��ʵ���ʻ�����ʾ���ʵ��ܵ���
		"""
		odds = "fact_odds"
		if not fact:
			odds = "falsity_odds"
		return self.totalodds[ odds ]

	def getItemLevel( self, itemID ):
		"""
		������Ʒ��ID����ȡ����Ʒ�ڽ��ҵ����еĵȼ�������Ʒ������ҵ��������Ʒ����Ȼû������
		"""
		for item in self.__datas:
			if item["id"] == str(itemID):
				return item["itemLevel"]
		return 6		#���û���ҵ����ID ˵������װ��(��Ϊ����Ʒ������Ǵӽ��ҵ�������������)

	def randomValue( self, fact, valueLimit = 0 ):
		"""
		���յ��ʵ��������һ������
		"""
		odds = "fact_odds"
		if not fact:
			odds = "falsity_odds"
		if valueLimit == 0:
			limit = self.totalodds[ odds ]
		else:
			limit = valueLimit

		randomValue = random.random()
		randomValue = randomValue * limit

		return randomValue

	def getEquipDropInfo( self , level ):
		"""
		��ȡ����ܵķ�ɫװ���ĵ������Ϣ
		"""
		worldDrop =  ItemDropInWorldLoader.instance()
		data = worldDrop.getItem( 4, level )
		return data

	@classmethod
	def instance( self ):
		"""
		���س����ʵ��
		"""
		if self._instance is None:
			self._instance = ItemDropLotteryLoader()
		return self._instance

# ----------------------------------------------------------------------------------------------------
# ������ĵ������
# ----------------------------------------------------------------------------------------------------
class EquipMakeDropLoader:
	"""
	������ĵ������
	"""
	_instance = None

	def __init__( self ):
		"""
		��ʼ�������ص�������
		@type  xmlConfig : STRING
		@param xmlConfig : ���õ�·��
		"""
		assert EquipMakeDropLoader._instance is None, "instance already exist in"
		self.__datas   = EquipMakeDropAmend.Datas #�洢��������

	def randomValue( self, quality, itemlevel ):
		"""
		���һ���õȼ��ܵ������ڵ�ֵ
		"""
		try:
			return random.random() * self.__datas[ quality ][ itemlevel ][ "totalDropOdds" ]
		except:
			ERROR_MSG( "can not find  item quality(%s) itemlevel(%s)" % (quality, itemlevel) )
			return -1.0

	def getItem( self, quality, itemlevel ):
		"""
		���ݵ���ֵ��ȡ�������Ʒ
		@type  quality   : int
		@param quality   : ���������Ʒ��
		@type  itemlevel : int
		@param itemlevel : ��������ĵȼ�
		"""
		odds = self.randomValue( quality, itemlevel )
		if odds == -1.0:
			return 0
		for item in self.__datas[ quality ][ itemlevel ][ "items" ]:
			if odds <= item["DROP_ODDS"]:
				return item["ITEM_ID"]

	@classmethod
	def instance( self ):
		"""
		���س����ʵ��
		"""
		if self._instance is None:
			self._instance = EquipMakeDropLoader()
		return self._instance


# ----------------------------------------------------------------------------------------------------
# �������ü���
# ----------------------------------------------------------------------------------------------------
class SpecialDropLoader:
	"""
	�������ĵ����ܵ������ü���
	"""
	_instance = None

	def __init__( self, xmlConfig = None ):
		"""
		��ʼ�������ص�������
		@type  xmlConfig : STRING
		@param xmlConfig : ���õ�·��
		"""
		assert SpecialDropLoader._instance is None, "instance already exist in"
		self.__datas   = {}
		for key,value in SpecialDropAmend.Datas.iteritems():
			obj = eval(value['drop_script'])
			config = smartImport( "config.server.droppedItem." + value["drop_config_name"] )
			self.__datas[key] = obj( config )

	def getDropDatas( self ):
		"""
		��ȡ�洢�ĵ�������
		"""
		return self.__datas

	@classmethod
	def instance( self ):
		"""
		���س����ʵ��
		"""
		if self._instance is None:
			self._instance = SpecialDropLoader()
		return self._instance


# ----------------------------------------------------------------------------------------------------
# ������Ʒ�������
# ----------------------------------------------------------------------------------------------------
class SpecialMonsterDropLoader:
	"""
	���������Ʒ������صĻ���
	"""
	def __init__( self, pyconfig ):
		"""
		@param dictDat: ��������
		@type  dictDat: python dict
		"""
		self.__datas   = pyconfig.Datas

	def getClassName( self ):
		"""
		��ȡ�Լ�����������ӡ��Ϣ��
		"""
		return self.__class__.__name__

	def getDropDatas( self ):
		"""
		��ȡ�洢�ĵ�������
		"""
		return self.__datas

	def getDropDatasEx( self, level ):
		"""
		��ȡָ���ȼ�����Ʒ��������
		"""
		try:
			return self.__datas[ level ][ "item" ]
		except KeyError:
			return []

	def gettotalodds( self, level ):
		"""
		��ȡ�õȼ�������ܵ���
		"""
		try:
			return self.__datas[ level ][ "totalodds" ]
		except KeyError:
			return 0.0

	def randomValue( self, level ):
		"""
		���չ���ĵȼ���ȡһ�������
		"""
		limit = self.gettotalodds( level )
		randomValue = random.random()
		randomValue = randomValue * limit
		return randomValue

	def getDropItem( self, monster):
		"""
		��ȡ�������Ʒ
		"""
		level = monster.level
		dropRate  = self.randomValue( level )
		dropDatas = self.getDropDatasEx( level )
		for item in dropDatas:
			if dropRate <= item[ "drop_odds" ]:
				if item[ "item_id" ] == "nothing":							#�����û�� �ͷ���none
					return None
				elif item[ "item_id" ].startswith( "equip_quality" ): #�����װ��
					info = item[ "item_id" ].split("_")
					if len( info ) < 4:		#�ж���д��ʽΪequip_quality_2
						quality = int( info[2] )
						# ��ȡ���䲿λ�б�
						specialDrop = ItemDropInWorldLoader.instance()
						wieldTypeList = specialDrop.getSpecialwieldTypeList( quality, level )
						if not wieldTypeList: return None
						eq_wieldType = random.choice( wieldTypeList )	#���һ�����䲿λ
						itemInfo = self.getEquipDropInfo( quality, level, eq_wieldType )	#itemInfo ��ʽ ( itemID, quality, prefix, odds )
						if not itemInfo:
							return None
						itemInst = g_items.createDynamicItem( int( itemInfo[0] ) , 1 )
						if itemInst is None:
							continue
					elif len( info ) >= 4:		#�ж���д��ʽΪequip_quality_2_2
						quality = int( info[2] )
						eq_wieldType = int( info[3] ) 		#����װ��ָ�����䲿λ
						itemInfo = self.getEquipDropInfo( quality, level, eq_wieldType )	#itemInfo ��ʽ ( itemID, quality, prefix, odds,eq_wieldType )
						if not itemInfo:
							return None
						itemInst = g_items.createDynamicItem( int( itemInfo[0] ) , 1 )
						if itemInst is None:
							continue
					if itemInfo[1] !=0 and itemInfo[2] != 0:
						itemInst.setQuality( itemInfo[1] )
						itemInst.setPrefix( itemInfo[2] )
						if not itemInst.createRandomEffect():
							DEBUG_MSG( "getDropItem createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemInfo[0], itemInfo[1], itemInfo[2] ) )
					return itemInst
				elif item[ "item_id" ].startswith( "equip_make" ): #�����������
					itemLevel = level + random.randint(0,2)
					quality = int( item[ "item_id" ][-1] )
					itemid = self.getEquipMakeDropInfo( itemLevel, quality )	#itemid ��Ϊ�������ID
					if not itemid:
						return None
					itemInst = g_items.createDynamicItem( int( itemid ) , 1 )
					if itemInst is None:
						continue
					return itemInst
				else:
					itemInst = g_items.createDynamicItem( int( item[ "item_id" ] ) , 1 )
					if itemInst is None:
						continue
					return itemInst
		return  None

	def getEquipDropInfo( self, quality, level, eq_wieldType ):
		"""
		���չ���ĵȼ���ȡ����ܵ� װ���ĵ������Ϣ
		"""
		specialDrop = ItemDropInWorldLoader.instance()
		data = specialDrop.getSpecialItem( quality, level, eq_wieldType )
		return data

	def getEquipMakeDropInfo( self , level, quality ):
		"""
		���չ���ĵȼ���ȡ����ܵ� װ���ĵ������Ϣ
		"""
		EquipMakeDrop =  EquipMakeDropLoader.instance()
		data = EquipMakeDrop.getItem( quality, level )
		return data

# ----------------------------------------------------------------------------------------------------
# ������������������ü���
# ----------------------------------------------------------------------------------------------------
class SpecialSundriesLoader:
	"""
	������������������ü���
	"""

	def __init__( self, pyconfig ):
		"""
		��ʼ�������ص�������
		@type  xmlConfig : STRING
		@param xmlConfig : ���õ�·��
		"""
		self.__datas   = pyconfig.Datas #�洢��������

	def getClassName( self ):
		"""
		��ȡ�Լ�����������ӡ��Ϣ��
		"""
		return self.__class__.__name__

	def getDropItem( self, monster):
		"""
		��ȡ�������Ʒ
		"""
		level = monster.level
		for item in self.__datas:
			if level <= item["item_level"]:
				itemInst = g_items.createDynamicItem( int( item[ "item_id" ] ) , 1 )
				if itemInst is None:
					continue
				return itemInst
		return None

#----------------------------------------------------------
#������﹫������Ʒ����(��ر�ͼ)
#----------------------------------------------------------
class CommonItemsLoader:
	"""
	������﹫������Ʒ����
	"""

	def __init__( self, pyconfig ):
		"""
		��ʼ��
		"""
		self.__datas   = pyconfig.Datas #�洢��������

	def getClassName( self ):
		"""
		��ȡ�Լ�����������ӡ��Ϣ��
		"""
		return self.__class__.__name__

	def getDropItem( self, monster ):
		"""
		��ȡ�������Ʒ
		"""
		if len( self.__datas ) == 0:
			try:
				L_logger.itemDropExceptLog( "%s has no Item" % self.getClassName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		odds = random.random() * self.__datas[-1]["drop_odds"]	#���һ����Ʒ�ĵ�����Ǹñ���ܵ���
		for item in self.__datas:
			if odds <= item["drop_odds"]:
				if item[ "item_id" ] == "nothing":							#�����û�� �ͷ���none
					return None
				else:
					dropped_item = g_items.createDynamicItem( int( item[ "item_id" ] ) , 1 )
					if dropped_item is None:
						continue
					item_creat = item["item_creat"]
					if item_creat:
						for key,value in item_creat.iteritems():
							if key == "level":
								if value == "monster":
									dropped_item.set( "level", monster.level )
							else:
								dropped_item.set( key, eval(value) )
						dropped_item.generateLocation( None, monster.level )
					return dropped_item
		return None


#----------------------------------------------------------
#������ʱ��Ĺ�������Ʒ����(���콵����)
#----------------------------------------------------------
class CommonItemsTimeLoader:
	"""
	������﹫������Ʒ����
	"""

	def __init__( self, pyconfig ):
		"""
		��ʼ��
		"""
		self.__datas   = pyconfig.Datas #�洢��������

	def getClassName( self ):
		"""
		��ȡ�Լ�����������ӡ��Ϣ��
		"""
		return self.__class__.__name__

	def getDropItem( self, monster ):
		"""
		��ȡ�������Ʒ
		"""
		if len( self.__datas ) == 0:
			try:
				g_logger.itemDropExceptLog( "%s has no Item" % self.getClassName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		hour = int(time.strftime("%H",time.localtime()))
		dropDatas = self.__datas.get(hour, None)
		if not dropDatas:
			return None
		for item in dropDatas:
			odds = random.random()
			if odds <= item["drop_odds"]:
				dropped_item = g_items.createDynamicItem( int( item[ "item_id" ] ), 1 )
				if dropped_item is None:
					continue
				item_creat = item["item_creat"]
				if item_creat:
					for key,value in item_creat.iteritems():
						if key == "level":
							if value == "monster":
								dropped_item.set( "level", monster.level )
						else:
							dropped_item.set( key, eval(value) )
				return dropped_item
		return None


class HonorItemZhaocai( ItemDropLuckyBoxZhaocai ):
	_datas = HonorItemZhaocai.Datas
	_hinstance = None


	@classmethod
	def instance( self ):
		"""
		"""
		if HonorItemZhaocai._hinstance is None:
			HonorItemZhaocai._hinstance = HonorItemZhaocai()
		return HonorItemZhaocai._hinstance

	def __init__( self ):
		"""
		"""
		assert HonorItemZhaocai._hinstance is None,"Just allow only one instance exist!!"

		self._levelMapRate = {}	# �����Ӧ���ܵ��ʣ��������ƻ��������ķ�Χ{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# ��ŵ�����Ʒ����������{ ����1:{ ���ʶ����ֵ1:����ʵ��1,���ʶ����ֵ2:����ʵ��2,...}, ... }

		HonorItemZhaocai._hinstance = self
		self.init( )


class HonorItemJinbao( ItemDropLuckyBoxJinbao ):
	_datas = HonorItemJinbao.Datas
	_hinstance = None

	@classmethod
	def instance( self ):
		"""
		"""
		if HonorItemJinbao._hinstance is None:
			HonorItemJinbao._hinstance = HonorItemJinbao()
		return HonorItemJinbao._hinstance

	def __init__( self ):
		"""
		"""
		assert HonorItemJinbao._hinstance is None,"Just allow only one instance exist!!"

		self._levelMapRate = {}	# �����Ӧ���ܵ��ʣ��������ƻ��������ķ�Χ{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# ��ŵ�����Ʒ����������{ ����1:{ ���ʶ����ֵ1:����ʵ��1,���ʶ����ֵ2:����ʵ��2,...}, ... }

		HonorItemJinbao._hinstance = self
		self.init( )
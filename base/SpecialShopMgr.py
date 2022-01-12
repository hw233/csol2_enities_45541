# -*- coding: gb18030 -*-
#


from bwdebug import *
import Language
import csdefine
import Language

SUBTYPE_MAPS = { csdefine.SPECIALSHOP_ESPECIAL_GOODS: [
																	csdefine.SPECIALSHOP_SUBTYPE_MOS_CRYSTAL,
																	csdefine.SPECIALSHOP_SUBTYPE_VAL_GOODS
																	],
					csdefine.SPECIALSHOP_CURE_GOODS:			[
																	csdefine.SPECIALSHOP_SUBTYPE_EXP_GOODS,
																	csdefine.SPECIALSHOP_SUBTYPE_REST_GOODS
																	],
					csdefine.SPECIALSHOP_VEHICLE_GOODS:		[
																	csdefine.SPECIALSHOP_SUBTYPE_LAND_VEHICLE,
																	csdefine.SPECIALSHOP_SUBTYPE_SKY_VEHICLE,
																	csdefine.SPECIALSHOP_SUBTYPE_VEHICLE_PROPS
																	],
					csdefine.SPECIALSHOP_PET_GOODS:			[
																	csdefine.SPECIALSHOP_SUBTYPE_PET_BOOK,
																	csdefine.SPECIALSHOP_SUBTYPE_PET_PROPS,
																	csdefine.SPECIALSHOP_SUBTYPE_PET_EGG
																	],
					csdefine.SPECIALSHOP_FASHION_GOODS:		[
																	csdefine.SPECIALSHOP_SUBTYPE_MALE_FASHION,
																	csdefine.SPECIALSHOP_SUBTYPE_FEMALE_FASHION
																	]
				}


class SpecialItem:
	"""
	�����̳���Ʒ
	"""
	def __init__( self, itemID, itemType, goldPrice, silverPrice, description, subType ):
		"""
		itemID : ��Ʒid
		type : ��Ʒ����
		price : �۸�
		"""
		self.itemID = itemID
		self.type = itemType
		self.goldPrice = goldPrice
		self.silverPrice = silverPrice
		self.description = description
		self.subType = subType
		
		
	def getDataList( self, moneyType ):
		"""
		�����Ʒ����
		@return [ self.itemID, self.type, self.price ]
		"""
		dataList = []
		if Language.LANG == Language.LANG_BIG5:
			if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_GOLD and self.goldPrice >= 0:
				dataList = [ self.itemID, self.type, self.goldPrice, self.description, moneyType, self.subType ]
			if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER and self.silverPrice >= 0:
				dataList = [ self.itemID, self.type, self.silverPrice, self.description, moneyType, self.subType ]
		else:
			dataList = [ self.itemID, self.type, self.goldPrice, self.description, self.subType ]
		return dataList
	def getPrice( self, moneyType ):
		"""
		"""
		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:
			return self.goldPrice
		elif moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
			return self.silverPrice
		
		
class SpecialShopMgr:
	"""
	�����̳����ù���
	"""
	_instance = None
	
	def __init__( self ):
		"""
		"""
		assert SpecialShopMgr._instance is None, "there's aready a instance exist!"
		self.data = {}
		self.reconmmentHotGoods = []# �ٷ��Ƽ�������Ʒ
		self.recommentGoods = []	# �Ƽ���Ʒ
		self.especialGoods = []		# ��ŵر�
		self.cureGoods = []			# �鵤��ҩ
		self.rebuildGoods = []		# �������
		self.vehicleGoods = []		# �����̳�
		self.petGoods = []			# �ɳ��̳�
		self.fashionGoods = []		# ʱװ����Ʒ
		self.enhanceGoods = []		# ǿ������
		self.talismanGoods = []		# ��������
		self.crystalGoods = []		# ��Ƕˮ��
		
		self.goodsTypeMap = { csdefine.SPECIALSHOP_RECOMMEND_GOODS : self.recommentGoods,
							csdefine.SPECIALSHOP_ESPECIAL_GOODS  : self.especialGoods,
							csdefine.SPECIALSHOP_CURE_GOODS      : self.cureGoods,
							csdefine.SPECIALSHOP_REBUILD_GOODS   : self.rebuildGoods,
							csdefine.SPECIALSHOP_VEHICLE_GOODS   : self.vehicleGoods,
							csdefine.SPECIALSHOP_PET_GOODS       : self.petGoods,
							csdefine.SPECIALSHOP_FASHION_GOODS   : self.fashionGoods,
							csdefine.SPECIALSHOP_ENHANCE_GOODS   : self.enhanceGoods,
							csdefine.SPECIALSHOP_TALISMAN_GOODS  : self.talismanGoods,
							csdefine.SPECIALSHOP_CRYSTAL_GOODS   : self.crystalGoods,
							}
							
	@classmethod
	def instance( self ):
		if SpecialShopMgr._instance is None:
			SpecialShopMgr._instance = SpecialShopMgr()
		return SpecialShopMgr._instance
		
	def load( self, xmlConfig ):
		"""
		��������
		"""
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError,"cannot load %s." % xmlConfig
			
		for item in section.values():
			itemID = item.readInt( "itemID" )
			tempType = item.readInt( "type" )
			subType = item.readInt( "subType" )
			activate = bool( item.readInt( "activate" ) )
			if not activate: continue
			if itemID in self.data:
				ERROR_MSG( "itemID(%i) has already in data."%( itemID ) )
				continue
			if tempType&csdefine.SPECIALSHOP_GOODS_TYPES != tempType:				#��Ʒ���Ͳ��ڴ�����
				ERROR_MSG( "not exit goods(%i) width type(%i)."%( itemID, tempType) )
				continue
			else: 																	#��Ʒ�����ڴ���
				if tempType in SUBTYPE_MAPS and \
				not subType in SUBTYPE_MAPS[tempType]:						#�����಻���ڴ�������෶Χ
					ERROR_MSG( "goods(%i) subtype(%i) not exit in type(%i)."%( itemID, subType, tempType) )
					continue
			tempItem = SpecialItem( itemID, tempType, item.readInt( "goldPrice" ), item.readInt( "silverPrice" ), item.readString( "description" ), subType )
			self.data[itemID] = tempItem
			
			if tempType & csdefine.SPECIALSHOP_RECOMMEND_GOODS:	# �Ƽ���Ʒ
				self.recommentGoods.append( tempItem )
			if tempType & csdefine.SPECIALSHOP_ESPECIAL_GOODS:	# ��Ƶر�
				self.especialGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_CURE_GOODS:	# �ָ�����Ʒ
				self.cureGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_REBUILD_GOODS:	# �������
				self.rebuildGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_VEHICLE_GOODS:	# �������Ʒ
				self.vehicleGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_PET_GOODS:		# ��������Ʒ
				self.petGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_FASHION_GOODS:	# ʱװ����Ʒ
				self.fashionGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_ENHANCE_GOODS:	# ǿ������
				self.enhanceGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_TALISMAN_GOODS:# ��������
				self.talismanGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_CRYSTAL_GOODS:	# ��Ƕˮ��
				self.crystalGoods.append( tempItem )
				
	def getItemPrice( self, itemID, amount, moneyType ):
		"""
		���ѯ�ۣ�����itemID������Ʒ�۸������������Ʒ�򷵻�-1
		
		@param itemID : ��Ʒid
		@type itemID : ITEM_ID
		@param amount : �����������
		@type amount : INT32
		"""
		try:
			price = self.data[itemID].getPrice( moneyType )
		except KeyError:
			return -1
		else:
			return price * amount if price >= 0 else -1
			
	def requestItemsPrices( self, player, itemIDs, moneyType ) :
		"""
		��������Ʒ�۸�
		"""
		prices = {}
		for itemID in itemIDs :
			state = csdefine.SPECIALSHOP_REQ_FAIL_NOT_EXIST
			prices[itemID] = ( state, 0 )
			if itemID in self.data :
				state = csdefine.SPECIALSHOP_REQ_SUCCESS
				item = self.data[itemID]
				prices[itemID] = ( state, item.getPrice( moneyType ) )
		player.client.spe_onReceiveItemsPrices( prices )
		
	def updateGoods( self, player, queryType, moneyType ):
		"""
		�����������̳���Ʒ��Ϣ
		
		@param player : ��ѯ���
		@type player : ENTITY
		@param queryType : ���������Ͳ�ѯ�̳ǵ���
		@type queryType : UINT32
		"""
		if not self.isOpen():
			player.statusMessage( csstatus.SPECIALSHOP_IS_NOT_OPEN )
			return
		for item in self.goodsTypeMap[ queryType ]:
			goodsData = item.getDataList( moneyType )
			if len( goodsData ) > 0:
				player.client.spe_receiveGoods( goodsData, queryType, moneyType )
			
	def isOpen( self ):
		return True
		
specialShop = SpecialShopMgr.instance()

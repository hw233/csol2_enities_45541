# -*- coding: gb18030 -*-

# $Id: GoodsLoader.py,v 1.3 2008-08-11 07:24:21 huangyongwei Exp $

import Language
from bwdebug import *
import items
import csconst
import csdefine
import InvoiceDataType
import ItemAttrClass

g_items = items.instance()

itemUndefineAttrs = ( "proPrefix", )	# 商品配置中合法的未定义物品属性

class GoodsLoader:
	"""
	商品加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert GoodsLoader._instance is None
		GoodsLoader._instance = self
		# key == 对应的npcID
		# value == [( itemID, amount ), ...]
		# like as { npcID : [(itemID, amount), ...], ...}
		self._datas = {}

	def load( self, configPath ):
		"""
		加载配置表
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			key = node.readString( "npcID" )
			if key not in self._datas:
				self._datas[key] = []
			priceData = {}
			itemID = node.readInt( "itemID" )
			invoiceType = node.readInt( "invoiceType" )
			if not invoiceType:	# 调试用
				invoiceType = csdefine.INVOICE_CLASS_TYPE_NORMAL
			priceType = node.readInt( "priceType" )
			itemAttrs = node.readString( "itemAttrs" )
			itemAttrs = eval( itemAttrs ) if itemAttrs else {}
			for attrName in itemAttrs.iterkeys():	# 初始化阶段检查并把一些未被定义的物品属性输出到日志
				if attrName not in ItemAttrClass.m_itemAttrMap and attrName not in itemUndefineAttrs:
					ERROR_MSG( "undefine property. -->", attrName )

			priceData = []
			if priceType & csdefine.INVOICE_NEED_MONEY:
				priceData.append( { "priceType":csdefine.INVOICE_NEED_MONEY, "price":node.readInt( "price1" ) } )
			if priceType & csdefine.INVOICE_NEED_ITEM:
				itemData = node.readString( "price2" ).split( ":" )
				priceItemID = int( itemData[0] )
				itemCount = int( itemData[1] )
				priceData.append( { "priceType":csdefine.INVOICE_NEED_ITEM, "itemID":priceItemID, "itemCount":itemCount } )
			if priceType & csdefine.INVOICE_NEED_DANCE_POINT:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_DANCE_POINT, "point":node.readInt( "price3" )} )
			if priceType & csdefine.INVOICE_NEED_TONG_CONTRIBUTE:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_TONG_CONTRIBUTE, "tongContribute":node.readInt( "price4" )} )
			if priceType & csdefine.INVOICE_NEED_ROLE_PERSONAL_SCORE:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_ROLE_PERSONAL_SCORE, "personalScore":node.readInt( "price6" )} )
			if priceType & csdefine.INVOICE_NEDD_TEAM_COMPETITION_POINT:
				priceData.append( {"priceType":csdefine.INVOICE_NEDD_TEAM_COMPETITION_POINT, "teamCompetitionPoint":node.readInt("price7" )} )
			if priceType & csdefine.INVOICE_NEED_TONG_SCORE:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_TONG_SCORE, "tongCompetitionScore":node.readInt( "price8" )} )
			if priceType & csdefine.INVOICE_NEED_ROLE_ACCUM_POINT:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_ROLE_ACCUM_POINT, "accumPoint":node.readInt( "price9" )} )
			if priceType & csdefine.INVOICE_NEED_SOUL_COIN:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_SOUL_COIN, "accumPoint":node.readInt( "price10" )} )
			if priceType & csdefine.INVOICE_NEED_CAMP_HONOUR:
				priceData.append( {"priceType":csdefine.INVOICE_NEED_CAMP_HONOUR, "campHonour":node.readInt( "price11" )} )
			if len( priceData ) == 0:	# 暂时兼容旧配置
				priceData.append( { "priceType":csdefine.INVOICE_NEED_MONEY, "price":-1 } )
			self._datas[key].append( ( itemID, node.readInt( "amount" ), invoiceType, node.readInt( "itemType" ), itemAttrs, priceData ) )

		# 清除缓冲
		Language.purgeConfig( configPath )

	def initGoods( self, npcEntity, npcClassName ):
		"""
		初始化npc的商品

		"""
		argIndex = 0
		for itemID, amount, invoiceType, itemType, itemAttrs, priceData in self.get( npcClassName ):
			item = g_items.createDynamicItem( itemID )
			if item is None:
				ERROR_MSG( "%s: no such item." % itemID )
				continue

			for attrString, value in itemAttrs.iteritems():
				item.set( attrString, value )
			if item.isEquip():
				item.fixedCreateRandomEffect( item.getQuality(),  None, False )

			argIndex += 1
			tmpInvData = InvoiceDataType.createInvoiceInstace( invoiceType )
			tmpInvData.setSrcItem( item )
			tmpInvData.setMaxAmount( amount )
			tmpInvData.setAmount( amount )
			tmpInvData.setItemType( itemType )						# 设置商品类型（08.08.09）
			for priceItem in priceData:		# 如果还没设置价格，那么用物品配置中的价格
				if priceItem["priceType"] == csdefine.INVOICE_NEED_MONEY and priceItem["price"] <= 0:
					priceItem["price"] = item.getPrice()
			tmpInvData.initPrice( priceData )
			npcEntity.attrInvoices[argIndex] = tmpInvData

	def get( self, npcID ):
		"""
		根据 NPC ID 取得其对应商品列表

		@param npcID: NPC 编号
		@return: [( itemID, amount ), ...]
		"""
		try:
			return self._datas[npcID]
		except KeyError:
			ERROR_MSG( "npc %s has no goods." % ( npcID ) )
			return []


	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = GoodsLoader()
		return SELF._instance


#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/09 01:50:01  wangshufeng
# 物品id类型调整，STRING -> INT32,相应调整代码。
#
# Revision 1.1  2007/12/08 09:41:51  phw
# no message
#
#
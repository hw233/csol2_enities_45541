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

itemUndefineAttrs = ( "proPrefix", )	# ��Ʒ�����кϷ���δ������Ʒ����

class GoodsLoader:
	"""
	��Ʒ������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert GoodsLoader._instance is None
		GoodsLoader._instance = self
		# key == ��Ӧ��npcID
		# value == [( itemID, amount ), ...]
		# like as { npcID : [(itemID, amount), ...], ...}
		self._datas = {}

	def load( self, configPath ):
		"""
		�������ñ�
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
			if not invoiceType:	# ������
				invoiceType = csdefine.INVOICE_CLASS_TYPE_NORMAL
			priceType = node.readInt( "priceType" )
			itemAttrs = node.readString( "itemAttrs" )
			itemAttrs = eval( itemAttrs ) if itemAttrs else {}
			for attrName in itemAttrs.iterkeys():	# ��ʼ���׶μ�鲢��һЩδ���������Ʒ�����������־
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
			if len( priceData ) == 0:	# ��ʱ���ݾ�����
				priceData.append( { "priceType":csdefine.INVOICE_NEED_MONEY, "price":-1 } )
			self._datas[key].append( ( itemID, node.readInt( "amount" ), invoiceType, node.readInt( "itemType" ), itemAttrs, priceData ) )

		# �������
		Language.purgeConfig( configPath )

	def initGoods( self, npcEntity, npcClassName ):
		"""
		��ʼ��npc����Ʒ

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
			tmpInvData.setItemType( itemType )						# ������Ʒ���ͣ�08.08.09��
			for priceItem in priceData:		# �����û���ü۸���ô����Ʒ�����еļ۸�
				if priceItem["priceType"] == csdefine.INVOICE_NEED_MONEY and priceItem["price"] <= 0:
					priceItem["price"] = item.getPrice()
			tmpInvData.initPrice( priceData )
			npcEntity.attrInvoices[argIndex] = tmpInvData

	def get( self, npcID ):
		"""
		���� NPC ID ȡ�����Ӧ��Ʒ�б�

		@param npcID: NPC ���
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
# ��Ʒid���͵�����STRING -> INT32,��Ӧ�������롣
#
# Revision 1.1  2007/12/08 09:41:51  phw
# no message
#
#
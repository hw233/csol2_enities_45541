# -*- coding: gb18030 -*-
#
# $Id: ItemDataList.py,v 1.12 2008-08-09 08:57:37 wangshufeng Exp $

"""
@var	instance: �Զ������͵��߻���ʵ����Ҳ��ȫ�ֵĵ���ʵ��
@type	instance: dict
"""

import Language
import BigWorld
from bwdebug import *
import Function
import ItemAttrClass
from  config.item import Items


class ItemDataList:
	"""
	�Զ������͵���ʵ������Ҫ���ڼ���ȫ�ֵ�����ʵ���Լ����桢����һЩ���ߵ��ױ����ԣ��Զ������͵��ߵı���ʹ��䣩��

	������
		>>> instance = ItemDataList( )	# ��config.item.Items.Datas����Դ����ʵ��
		a = instance.createDynamicItem( 10502001, 1 )	# �����µ���Ʒ����������
		print a.getPrice()			# ��ȡ�۸�

	@ivar _itemDict: ȫ�ֵ���ʵ���ֵ�
	@type _itemDict: dict
	"""
	_instance = None
	def __init__( self ):
		assert ItemDataList._instance is None, "instance already exist in"
		ItemDataList._instance = self
		self._itemDict = {}
		self._itemData = Items.Datas

	@staticmethod
	def instance():
		if ItemDataList._instance is None:
			ItemDataList._instance = ItemDataList()
		return ItemDataList._instance

	def __getitem__( self, id ):
		"""
		ȡ��ĳ��ȫ�ֵ���ʵ��

		@param id: ����Ψһ��ʶ��
		@type  id: ITEM_ID
		"""
		return self._getItemDict( id )

	def _getItemDict( self, itemID ):
		"""
		��ȡ��Ʒ��������

		@return: item data dict; return None if item not found.
		"""
		if itemID not in self._itemDict:
			try:
				itemData = self._loadItemConf( itemID, self._itemData[ str( itemID ) ] )
			except KeyError:
				ERROR_MSG( "item %i not found." % itemID )
				return None
			if itemData is None: return None
			self._itemDict[itemID] = itemData		# �ɹ����أ�����Ʒ�ŵ�ȫ���ֵ���
		return self._itemDict[itemID]

	def _loadItemConf( self, itemID, configDict ):
		"""
		����һ����Ʒ

		@return: �Ѽ��ص�item����; �������ʧ���򷵻�None
		"""
		item = { "id":itemID, "dynClass":None }
		attrMap = ItemAttrClass.m_itemAttrMap
		for key, e in configDict.iteritems():
			# ���˵�û�����õ�����
			try:
				if len( e ) == 0:
					continue
			except: #���� len( ��ֵ���Ͳ��� ) ���׳��쳣����Ϊ��ֵʱ����ֵ��Ϊ��
				pass
			attrMap[ key ].readFromConfig( item, e )
		return item

	def id2name( self, id ):
		"""
		ת����ƷΨһ���Ϊ��Ʒ����

		@return: ��Ʒ���ƣ�����Ҳ����򷵻ؿ��ַ���""
		@rtype:  ITEM_ID
		"""
		try:
			return self._getItemDict( id )["name"]
		except TypeError:
			return ""

	def getLevel( self, id ):
		"""
		����ID�����Ʒ�ĵȼ�

		@return: ��Ʒ���"
		@rtype:  String
		"""
		try:
			return self._getItemDict( id )["level"]
		except:
			return 0

	def getType( self, id ):
		"""
		ת����ƷID
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

	def createDynamicItem( self, id, amount = 1 ):
		"""
		������̬��Ʒ
		@param id: ��Ʒ�ؼ�������
		@type  id: ITEM_ID
		@return: see GItemBase.createDynamicItem method; if item not found, return None
		"""
		gobj = self._getItemDict( id )
		if gobj is None: return None
		obj = gobj["dynClass"]( gobj )
		obj.setAmount( amount )
		return obj

	def createFromDict( self, valDict ):
		"""
		���ֵ��д�����Ʒʵ��

		@param valDict: ��Ʒ�������ֵ�
		@type  valDict: dict
		@return:        �̳���CItemBase�ĵ���ʵ��; ʧ���򷵻�None
		@rtype:         CItemBase
		"""
		# �˺����������쳣����Ϊ���������ܳ����쳣�����ȷʵ�����ˣ�
		# �Ǿ�Ӧ�ÿ������ǵĴ����ĳЩ�����Ƿ�Ѵ˴���������
		id = valDict["id"]
		obj = self.createDynamicItem( id )			# �����µ���֮��Ӧ�Ķ���
		if obj is None: return None
		obj.loadFromDict( valDict )
		return obj

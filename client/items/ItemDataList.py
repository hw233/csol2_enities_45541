# -*- coding: gb18030 -*-
#
# $Id: ItemDataList.py,v 1.21 2008-08-20 09:03:18 yangkai Exp $

"""
@var	instance: �Զ������͵��߻���ʵ����Ҳ��ȫ�ֵĵ���ʵ��
@type	instance: dict
"""

import sys
import os
import Language
import BigWorld
from bwdebug import *
import Function
import ItemAttrClass
from config.item.Items import Datas as g_ItemsData


class ItemDataList:
	"""
	�Զ������͵���ʵ������Ҫ���ڼ���ȫ�ֵ�����ʵ���Լ����桢����һЩ���ߵ��ױ����ԣ��Զ������͵��ߵı���ʹ��䣩��

	������
		>>> instance = ItemDataList( )	# ��ʼ�������ļ�������ʵ��
		a = instance.createDynamicItem( 10502001, 1 )	# �����µ���Ʒ����������
		print a.getPrice()			# ��ȡ�۸�

	@ivar _itemDict: ȫ�ֵ���ʵ���ֵ�
	@type _itemDict: dict
	"""
	_instance = None
	def __init__( self ):
		assert ItemDataList._instance is None, "instance already exist in"
		ItemDataList._instance = self
		self._itemDict = {}				# �Ѽ��ص���Ʒ�б�

	@staticmethod
	def instance():
		if ItemDataList._instance is None:
			ItemDataList._instance = ItemDataList()
		return ItemDataList._instance

	def _getItemDict( self, itemID ):
		"""
		��ȡ��Ʒ��������
		@return: item data dict; return None if item not found.
		"""
		if itemID not in self._itemDict:
			try:
				itemData = self._loadItemConf( itemID, g_ItemsData[ str( itemID ) ] )
			except KeyError:
				ERROR_MSG( "item %s not found." % itemID )
				return None
			if itemData is None: return None
			self._itemDict[itemID] = itemData		# �ɹ����أ�����Ʒ�ŵ�ȫ���ֵ���
		return self._itemDict[itemID]

	def _loadItemConf( self, itemID, dict ):
		"""
		����һ����Ʒ

		@return: �Ѽ��ص�item����; �������ʧ���򷵻�None
		"""
		item = { "id":itemID, "dynClass":None }
		attrMap = ItemAttrClass.m_itemAttrMap
		errsec = ""
		try :
			for key, dat in dict.iteritems():
				# ���˵�û�����õ�����
			#	if len( dat ) == 0: continue
				errsec = key
				attrMap[key].readFromConfig( item, dat )
		except :
			ERROR_MSG( "item %s read section '%s' error!" % ( str( itemID ), errsec ) )
			return None
		return item

	def id2name( self, id ):
		"""
		ת����ƷΨһ���Ϊ��Ʒ����

		@return: ��Ʒ���ƣ�����Ҳ����򷵻ؿ��ַ���""
		@rtype:  String
		"""
		try:
			return self._getItemDict( id )["name"]
		except TypeError:
			return ""

	def id2model( self, id ):
		"""
		������ƷID��ȡ��Ʒģ�ͱ��
		"""
		try:
			return self._getItemDict( id )["model"]
		except:
			return 0

	def id2particle( self, id ):
		"""
		������ƷID��ȡ��Ʒ��Ч����
		"""
		try:
			return self._getItemDict( id )["particle"]
		except:
			return ""

	def id2type( self, id ):
		"""
		������ƷID��ȡ��Ʒ����
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

	def id2quality( self, id ):
		"""
		������ƷID��ȡ��ƷƷ��
		"""
		try:
			return self._getItemDict( id )["quality"]
		except:
			return 0

	def createDynamicItem( self, id, amount = 1 ):
		"""
		������̬��Ʒ
		@param id: ��Ʒ�ؼ�������
		@type  id: str
		@return: see GItemBase.createDynamicItem method; if item not found, return None
		"""
		gobj = self._getItemDict( id )
		if gobj is None: return None
		try :													# ����쳣������ֹ��Ʒ������ Script ʱ�����ж�ִ�У�2008.09.28��
			obj = gobj["dynClass"]( gobj )
		except TypeError :
			EXCEHOOK_MSG( "item which id is %i has no script!" % id )
			return None
		obj.setAmount( amount )
		return obj

	def createFromDict( self, valDict ):
		"""
		���ֵ��д�����Ʒʵ��

		@param valDict: ��Ʒ�������ֵ�
		@type  valDict: dict
		@return:        �̳���CItemBase�ĵ���ʵ��; ���ʧ���򷵻�None
		@rtype:         CItemBase
		"""
		# �˺����������쳣����Ϊ���������ܳ����쳣�����ȷʵ�����ˣ�
		# �Ǿ�Ӧ�ÿ������ǵĴ����ĳЩ�����Ƿ�Ѵ˴���������
		id = valDict["id"]
		obj = self.createDynamicItem( id )			# �����µ���֮��Ӧ�Ķ���
		if obj is None:
			ERROR_MSG( "can't find item: %i" % id )
			return None
		obj.loadFromDict( valDict )
		return obj
		
	
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
	
	def	getType( self, id ):
		"""
		ת����ƷID
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

# -*- coding: gb18030 -*-
#
# $Id: ItemDataList.py,v 1.16 2008-08-09 08:57:22 wangshufeng Exp $

"""
@var	instance: �Զ������͵��߻���ʵ����Ҳ��ȫ�ֵĵ���ʵ��
@type	instance: dict
"""

import sys
import Language
import BigWorld
from bwdebug import *
import Function
import ItemAttrClass
import Math
from  config.item import Items
import Math


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
		self._itemDict = {}			# �Ѽ��ص���Ʒ����
		self._itemData = Items.Datas		# ��Ʒ������

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
				printStackTrace()
				ERROR_MSG( "item %i not found." % int( itemID ) )
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
			
			# ��������е������ֶΣ��Ը�ֱ�ӵķ�ʽ��ӳ���������� by mushuang
			if not attrMap.has_key( key ):
				ERROR_MSG( "Redundant field in item data, please check configuration! itemID(%s),key(%s)"%(str(itemID),key) )
			else:
				attrMap[ key ].readFromConfig( item, e )
			
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

	def	getType( self, id ):
		"""
		ת����ƷID
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

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

	def getReqClass( self, id ):
		"""
		����ID�����Ʒ��ְҵ����

		@return: ��Ʒ���"
		@rtype:  String
		"""
		try:
			return self._getItemDict( id )["reqClasses"]
		except:
			return []
			
	def getStacCount( self, id ):
		"""
		����ID����ÿɵ��Ӹ���
		"""
		try:
			return self._getItemDict( id )["stackable"]
		except:
			return 0

	def createDynamicItem( self, id, amount = 1 ):
		"""
		������̬��Ʒ
		@param id: ��Ʒ�ؼ�������
		@type  id: int
		@return: see GItemBase.createDynamicItem method; if item not found, return None
		"""
		gobj = self._getItemDict( id )
		if gobj is None: return None
		try :												# ����쳣������ֹ��Ʒ������ Script ʱ�����ж�ִ�У�2008.09.28��
			obj = gobj["dynClass"]( gobj )
		except TypeError :
			msg = "item which id is %i has no script!" % id
			sys.excepthook( Exception, msg, sys.exc_traceback )
			return None
		obj.setAmount( amount )
		return obj

	def createEntity( self, id, spaceID, position, direction, srcDict = None ):
		"""
		����һ��Entity�ӵ���ͼ��

		@param   spaceID: ��ͼID��
		@type    spaceID: INT32
		@param  position: ���߲���������ĸ�λ��
		@type   position: VECTOR3
		@param direction: ���߲�����ŵķ���
		@type  direction: VECTOR3
		@param   srcDict: ���ӵ������ֵ����ݣ��ò���Ĭ��ֵΪNone
		@type    srcDict: CItemBase
		@return:          һ���µĵ���entity��if item not found, return None
		@rtype:           Entity
		"""
		position = Math.Vector3( position )
		if srcDict is None:
			obj = self.createDynamicItem( id, True )
			if obj is None: return None
			tmpDict = { "itemProp" : obj }
		else:
			if not srcDict.has_key( "itemProp" ):
				tmpDict = srcDict.copy()
				obj = self.createDynamicItem( id, True )
				if obj is None: return None
				tmpDict["itemProp"] = obj
			else:
				tmpDict = srcDict
		position = Math.Vector3(position)
		# entity��ر�����ײ��ȷ�����Է��ڵ�����
		position.y += 0.1  #�������õĵ㴦����Ҫ������ʱ��ʰȡ��ʧ�ܵ����
		for amend in [-10, 10]:
			pos = ( position[0], position[1] + amend, position[2] )
			r = BigWorld.collide( spaceID, position, pos )
			if r is not None:
				break
		if r is not None:
			pos = r[0]
		else:
			pos = position
		return BigWorld.createEntity( "DroppedItem", spaceID, pos, direction, tmpDict )

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
		if obj is None: return None
		obj.loadFromDict( valDict )
		return obj



#
# $Log: not supported by cvs2svn $
# Revision 1.15  2008/08/09 01:49:06  wangshufeng
# ��Ʒid���͵�����STRING -> INT32,��Ӧ�������롣
#
# Revision 1.14  2008/04/24 03:20:32  yangkai
# no message
#
# Revision 1.13  2008/04/23 04:22:11  yangkai
# no message
#
# Revision 1.12  2008/04/23 03:58:16  yangkai
# no message
#
# Revision 1.11  2008/02/23 10:27:45  yangkai
# ��ӽӿ� getLevel();getReqClass()
#
# Revision 1.10  2008/01/25 10:06:04  yangkai
# �����ļ�·���޸�
#
# Revision 1.9  2007/11/28 02:08:54  yangkai
# �Ƴ������õ� from ItemTypeEnum import *
#
# Revision 1.8  2007/11/24 03:53:47  yangkai
# no message
#
# Revision 1.7  2007/11/24 03:08:04  yangkai
# ��Ʒϵͳ����
# ������Ʒ���ü��ش���
#
# Revision 1.6  2007/09/28 02:17:49  yangkai
# �����ļ�·������:
# res/server/config  -->  res/config
#
# Revision 1.5  2007/06/23 02:38:37  phw
# method modified: load(), ȡ���˶��ļ����õ�ֱ����������Ϊͨ����һ�����ô��λ���б�������
#
# Revision 1.4  2006/12/21 09:29:02  phw
# ��Ʒ��ʼ��ʱǿ��ת����ƷidΪСд
#
# Revision 1.3  2006/08/18 06:57:02  phw
# �޸Ľӿڣ�
#     load()��CITI_* to CIST_*
#     createFromDict()�����Ӷ�item�Ƿ�None���ж�
#
# Revision 1.2  2006/08/11 02:57:00  phw
# ���Ը������޸�����itemInstance.keyName��itemInstance.id()ΪitemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
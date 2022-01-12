# -*- coding: gb18030 -*-

# $Id: CItemBase.py,v 1.15 2008-07-02 03:41:19 wangshufeng Exp $

"""
�Զ������͵��߻���ģ�顣

"""
import BigWorld
import cPickle
import copy
import ItemTypeEnum
from bwdebug import *
import ItemAttrClass
import ItemDataList
from Function import newUID

g_items = ItemDataList.ItemDataList.instance()

class CItemBase:
	"""
	�Զ������͵���ʵ������Ҫ���ڱ���ʹ���һЩ���ߵ��ױ�����
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: ��Ʒ��ԭʼ����
		"""
		self.uid = newUID()						# ȫ��Ψһ��ID
		self.id = srcData["id"]					# ���Լ���Ӧ��ȫ��ʵ������
		self.srcData = srcData					# ���Լ���Ӧ��ȫ��ʵ�����������ڳ�ʼ��ʱ��������ʱʹ�ò���Ҫ����
		self.kitbag = None						# ��Ʒ�������ĸ�����ʵ����,��һ������
		self.order = -1							# ��Ʒ���õ�λ��
		self.amount = 1							# ��ǰ������Ĭ��ֵΪ1
		self.extra = {}							# ����Ķ�̬���ԣ����е���Ҫ���浽���ݿ��Ǩ��ʱ��Ҫ��������Զ�����������
		self.tmpExtra = {}						# ����Ķ�̬���ԣ�������extra,Ψһ�����Ǳ����ڴ˵����Բ����̣�ֻ������ʱ��Ч


	def name( self ):
		"""
		��ȡ��Ʒ����
		"""
		return self.srcData["name"]

	def icon( self ):
		"""
		��ȡͼ��
		"""
		return self.srcData["icon"]

	def model( self ):
		"""
		��ȡģ��
		"""
		try:
			return self.srcData["model"]
		except:
			return 0

	def credit( self ):
		"""
		��ȡ��Ʒ���������
		"""
		try:
			return self.srcData["credit"]
		except:
			return 0

	def query( self, attrName, default = None ):
		"""
		��ȡһ������

		@param attrName: ��Ҫ��ȡ��ֵ����������
		@type  attrName: String
		@param  default: ���ָ�����Ե�ֵ�����ڣ�����ʲô��ĬΪ����None
		@type   default: any
		"""
		if attrName in self.extra:
			return self.extra[attrName]
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def queryTemp( self, attrName, default = None ):
		"""
		��ȡһ����ʱ����

		@param attrName: ��Ҫ��ȡ��ֵ����������
		@type  attrName: String
		@param  default: ���ָ�����Ե�ֵ�����ڣ�����ʲô��ĬΪ����None
		@type   default: any
		"""
		if attrName in self.tmpExtra:
			return self.tmpExtra[attrName]
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def queryInt( self, attrName ):
		return self.query( attrName, 0 )

	def queryTempInt( self, attrName ):
		return self.queryTemp( attrName, 0 )

	def queryStr( self, attrName ):
		return self.query( attrName, "" )

	def queryTempStr( self, attrName ):
		return self.queryTemp( attrName, "" )

	def set( self, attrName, value, owner = None ):
		"""
		���ö�̬����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		self.extra[attrName] = value
		if owner:
			if attrName not in ItemAttrClass.m_itemAttrMap:
				WARNING_MSG( "set undefine property. -->", attrName, value )
				return
			stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( value )
			owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def setTemp( self, attrName, value, owner = None ):
		"""
		���ö�̬����ʱ����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		self.tmpExtra[attrName] = value
		if owner:
			if attrName not in ItemAttrClass.m_itemAttrMap:
				WARNING_MSG( "set undefine property. -->", attrName, value )
				return
			stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( value )
			owner.client.onItemTempAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def addToDict( self ):
		"""
		ת����ITEM type format.

		@return: dict
		@rtype:  dict
		"""
		return { 	"uid"		: self.uid,
					"id" 		: self.id,
					"amount" 	: self.amount,
					"order"		: self.order,
					"extra" 	: cPickle.dumps( self.extra, 2 ),
					"tmpExtra" 	: cPickle.dumps( self.tmpExtra, 2 ),
				}

	def loadFromDict( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self.uid = valDict["uid"]
		self.amount = valDict["amount"]
		self.order = valDict["order"]
		if valDict.has_key( "extra" ):
			self.extra = cPickle.loads( valDict["extra"] )
		if valDict.has_key( "tmpExtra" ) and len( valDict["tmpExtra"] ):
			self.tmpExtra = cPickle.loads( valDict["tmpExtra"] )

	def setKitbag( self, kitbag ):
		"""
		@param kitbag: ���ø���Ʒ�ı���ʵ��
		@type  kitbag: KitbagBase
		@return:          ��
		"""
		self.kitbag = kitbag

	def getKitbag( self ):
		"""
		��ȡ����Ʒ���ڰ���ʵ��
		"""
		return self.kitbag

	def setOrder( self, order ):
		"""
		@param  order: ����Ʒ�����ĸ�λ��
		@type   order: UINT8
		@return:          ��
		"""
		self.order = order

	def getOrder( self ):
		"""
		��ȡorderID
		"""
		return self.order

	def getuid( self ):
		"""
		��ȡuid
		"""
		return self.uid

	def getType( self ):
		"""
		��ȡ��Ʒ����
		"""
		return self.query( "type" )

	def isType( self, type ):
		"""
		�ж��Լ��Ƿ�Ϊĳ���͵ĵ��ߣ�

		@param type: ���жϵ����ͣ�ֵΪ��ģ���С�CIST_����ͷ�ĳ���֮һ
		@type  type: UINT32
		@return:     True == ��ָ�������ͣ�False == ����ָ��������
		@rtype:      BOOL
		"""
		return self.getType() == type

	def getAmount( self ):
		"""
		ȡ����Ʒ����
		"""
		return self.amount

	def setAmount( self, amount, owner = None ):
		"""
		ȡ����Ʒ����
		"""
		self.amount = amount
		if owner:
			if amount <= 0:
				owner.removeByOrder( self.order )
			else:
				attrName = "amount"
				stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( amount )
				owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def addFlag( self, flags, owner = None ):
		"""
		���ӱ�־

		@param flags: �����ӵı�־����־Ϊ���С�CFE_����ͷ�����
		@type  flags: UINT16
		@return:      ��
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		self.set( "flags", oldFlags | flags, owner )

	def removeFlag( self, flags, owner = None ):
		"""
		�Ƴ���־

		@param flags: ���Ƴ��ı�־����־Ϊ���С�CFE_����ͷ�����
		@type  flags: UINT16
		@return:      ��
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		# ��ȷ��������ֵ�������ȡ����
		self.set( "flags", (oldFlags | flags) ^ flags, owner )

	def hasFlag( self, flags ):
		"""
		�жϱ�־

		@param flags: ���жϵı�־����־Ϊ���С�CFE_����ͷ�����
		@type  flags: UINT16
		@return:      True == ����ָ���ı�־(���)��False == ������ָ���ı�־(���)
		@rtype:       BOOL
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		return flags & oldFlags == flags

	def getStackable( self ):
		"""
		��ȡ����Ʒ�ĵ������ޣ�Ĭ��Ϊ1
		"""
		return self.query( "stackable", 1 )

	def canStore( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ��洢

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_WAREHOUSE )

	def canSell( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_SELL )

	def canDestroy( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_DESTROY )

	def canRepair( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_REPAIR )

	def canConsume( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_WASTAGE )

	def canAbrasion( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�ĥ��

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_ABRASION )

	def canIntensify( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�ǿ��

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_INTENSIFY )

	def canRebuid( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_REBUILD )

	def canStiletto( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_STILETTO )

	def canGive( self ):
		"""
		�ж��Ƿ��ܸ�(��������֮�����Ʒ����)
		������ƷΪ��״̬ʱ������Ʒ���ܽ���

		@return: bool
		@rtype:  bool
		"""
		return not self.isBinded() or self.hasFlag( ItemTypeEnum.CFE_NO_TRADE )

	def canUse( self ):
		"""
		�ж��Լ��Ƿ���Ա�ʹ��

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.query( "spell", 0 ) > 0

	def setBindType( self, type, owner ):	# 11:39 2008-7-2,wsf add
		"""
		���ð�����
		"""
		bit = 1 << type
		bindType = ( bit << 4 ) | bit
		self.set( "bindType", bindType, owner )

	def getBindType( self ):
		"""
		��ȡ������
		"""
		return self.query( "bindType", 0 )

	def isBinded( self ):
		"""
		�жϸ���Ʒ�Ƿ��
		@return Bool
		"""
		return ( self.getBindType() >> 4 ) > 0

	def cancelBindType( self, owner = None ):
		"""
		ȡ������Ʒ�İ󶨣��ָ�����ǰ״̬
		"""
		bindType = self.query( "bindType", 0 )
		if bindType == ItemTypeEnum.CBT_NONE:
			return
		newBindType = bindType >> 4
		self.set( "bindType", newBindType, owner )

	def new( self ):
		"""
		ʹ�õ�ǰ��Ʒ�����ݴ���һ���µ���Ʒʵ����

		@return: �̳���CItemBase���Զ������͵���ʵ��
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		return obj

	def copy( self ):
		"""
		�����Լ���uid��Դ��Ʒһ����

		@return: �̳���CItemBase���Զ������͵���ʵ��
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		obj.uid = self.uid
		return obj

	def updateMe( self, owner ):
		"""
		������Ʒ��ӵ���ߵ�client��

		@return: �����ӵ�����򷵻�Treu, û���򷵻�False
		"""
		raise "I can't support yet."

	def getAddedDescribe1( self ):
		"""
		ȡ�ø��ӵ�����1
		"""
		try:
			return self.srcData["describe1"]
		except KeyError:
			return ""

	def getAddedDescribe2( self ):
		"""
		ȡ�ø��ӵ�����2
		"""
		try:
			return self.srcData["describe2"]
		except KeyError:
			return ""

	def getAddedDescribe3( self ):
		"""
		ȡ�ø��ӵ�����3
		"""
		try:
			return self.srcData["describe3"]
		except KeyError:
			return ""

	def getMaxSpace( self ):
		"""
		"""
		return self.query( "kb_maxSpace", 0 )

	def getPrice( self ):
		"""
		��ȡ��ǰ���߼�ֵ���п��ܻ���Ҫ����ĳЩ���Լ���
		"""
		return self.query( "price" )

	def setPrice( self, value, owner = None ):
		"""
		���ø���Ʒ�ļ۸�
		"""
		assert isinstance( value, int )
		self.set( "price", value, owner )

	def getQuestID( self ):
		"""
		��ø���Ʒ����������ID
		"""
		return self.query( "questID", 0 )

	def getQuality( self ):
		"""
		��ȡ��Ʒ��Ʒ��
		"""
		return self.query( "quality", 1 )

	def isFrozen( self ):
		"""
		�ж��Լ��Ƿ񱻶���
		@return: BOOL
		"""
		return self.queryTemp( "freeze" )

	def freeze( self, owner = None ):
		"""
		�����Լ�
		@return: ����ܶ����򷵻�True, ����Ѿ��������򷵻�False
		@rtype:  bool
		"""
		if self.queryTemp( "freeze", 0 ):
			return False
		self.setTemp( "freeze", 1, owner )
		return True

	def unfreeze( self, owner = None ):
		"""
		�ⶳ�Լ�
		@return: ��
		"""
		self.setTemp( "freeze", 0, owner )

	def getReqLevel( self ):
		"""
		��ȡʹ�õȼ�
		"""
		return self.query( "reqLevel", 0 )

	def getLifeTime( self ):
		"""
		��ȡ��Ʒ���ʱ��
		"""
		return self.query( "lifeTime", 0 )

	def setLevel( self, level, owner = None ):
		"""
		������Ʒ�ĵȼ� by ����
		@param    reqLevel: ʹ�õȼ�
		@type     reqLevel: UINT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		self.set( "level", level, owner )
		
	def getLevel( self ):
		"""
		��ȡ�ȼ�
		"""
		return self.query( "level", 0 )
		
	def isEquip( self ):
		"""
		virtual method.
		�ж��Ƿ���װ��
		"""
		return False

# CItemBase.py

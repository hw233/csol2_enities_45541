# -*- coding: gb18030 -*-

#$Id: EquipSuitLoader.py,v 1.3 2008-08-09 01:48:51 wangshufeng Exp $

from bwdebug import *
import Language
from items.ItemDataList import ItemDataList
from config.item import EquipSuits

g_items = ItemDataList.instance()

# ----------------------------------------------------------------------------------------------------
# װ����װ���ü���
# ----------------------------------------------------------------------------------------------------

class EquipSuitLoader:
	"""
	װ����װ���ü���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipSuitLoader._instance is None, "instance already exist in"
		self._datas = EquipSuits.Datas	# like as { suitID : [itemID, ......], ...}
		self._suitName = EquipSuits.SuitName # like as { suitID : name , ......}	���´洢����Ϊ�������ԭ���Ľṹ,��װ����ʹ�õط����Ǻܶ� hd

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipSuitLoader()
		return self._instance

	def isSuit( self, EquipIDList ):
		"""
		�ж�һ��װ��ID�б��Ƿ�����װ
		@type  EquipIDList: List
		@param EquipIDList: װ��ID�б�
		@return:        Bool
		"""
		return set( EquipIDList ) in [ set( k ) for k in self._datas.itervalues()]

	def getSuit( self, EquipID ):
		"""
		����װ��ID��ȡ��ID��Ӧ��ȫ����װ��ID
		@type  EquitID	:	INT
		@param EquitID	:	����װ����ID
		@return:	List �洢����װ����ID���б� �Լ�����װ������
		@add by hd
		"""
		for suitkey in self._datas:
			if str(EquipID).endswith(str(suitkey)):
				if EquipID in self._datas[suitkey]:
					return ( self.getSuitChildName(suitkey) ,list(self._datas[suitkey]))		#���ظ���װԭʼ���ݵĸ��� ���ⱻ�ⲿ��С���޸�

	def getSuitID( self, EquipID ):
		"""
		����װ��ID��ȡ��ID��Ӧ��ȫ����װ��ID
		@type  EquitID	:	INT
		@param EquitID	:	����װ����ID
		@return:	INT ���ظ���װ������ID
		@add by hd
		"""
		for suitkey in self._datas:
			if str(EquipID).endswith(str(suitkey)):
				if EquipID in self._datas[suitkey]:
					return suitkey

	def getSuitChildID(self, SuitId):
		"""
		������װID ��ȡ��װ�Ĳ���ID
		"""
		if not SuitId:
			return []
		return self._datas.get(SuitId)

	def getSuitChildName( self, SuitId ):
		"""
		������װ��ID ��ȡ����װ������
		@type  SuitId	:	INT
		@param SuitId	:	��װ��ID
		@return:	str ��װ��
		@add by hd
		"""
		if not SuitId or not self._suitName:
			return None
		return self._suitName.get(SuitId)

	def getSuitChildNames( self, SuitId):
		"""
		������װ��ID ��ȡ����װ�����в���������
		@type  SuitId	:	INT
		@param SuitId	:	��װ��ID
		@return:	LIST ��װ�����в�����
		@add by hd
		"""
		equips = self._datas.get(SuitId)
		if not equips:
			return []
		equipNames = []  #�洢����װ�������ֵ��б�
		for equip in equips:
			name = g_items.id2name(equip)
			equipNames.append( name )
		return equipNames


equipsuit = EquipSuitLoader.instance()

#$Log: not supported by cvs2svn $
#Revision 1.2  2008/04/07 02:49:25  yangkai
#no message
#
#Revision 1.1  2008/03/24 02:29:30  yangkai
#��װ�������ü���
#
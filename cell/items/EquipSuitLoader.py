# -*- coding: gb18030 -*-

#$Id: EquipSuitLoader.py,v 1.3 2008-08-09 01:48:51 wangshufeng Exp $

from bwdebug import *
import Language
from config.item.EquipSuits import Datas as g_EquipSuitData

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

	def __init__( self, xmlConf = None ):
		assert EquipSuitLoader._instance is None, "instance already exist in"
		self._datas = g_EquipSuitData	# like as { suitID : [itemID, ......], ...}

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

#$Log: not supported by cvs2svn $
#Revision 1.2  2008/04/07 02:49:25  yangkai
#no message
#
#Revision 1.1  2008/03/24 02:29:30  yangkai
#��װ�������ü���
#
# -*- coding: gb18030 -*-
#
# ����Ʒ����Ʒ�ı������� 2009-01-12 SongPeifang
#

import Language
from bwdebug import *

class PointChapmanGoodsLoader:
	"""
	����Ʒ����Ʒ�ı�������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert PointChapmanGoodsLoader._instance is None
		PointChapmanGoodsLoader._instance = self
		self._datas = {} # key:value = Ҫ������ƷID:����������Ʒ����Ʒ����Ϣ

	def load( self, configPath ):
		"""
		�������ñ�
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			key = node.readString( "itemID" )
			if key not in self._datas:
				self._datas[key] = {}
			self._datas[key]["point"] = node.readInt( "point" )

		# �������
		Language.purgeConfig( configPath )

	def get( self, ID ):
		"""
		���� ID ȡ�����Ӧ��Ʒ�б�

		@param npcID: NPC ���
		@return: [( itemID, amount ), ...]
		"""
		try:
			return self._datas[ID]
		except KeyError:
			ERROR_MSG( "ID %s has no goods." % ( ID ) )
			return None

	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = PointChapmanGoodsLoader()
		return SELF._instance
		
g_PointChapmanGoods = PointChapmanGoodsLoader.instance()
# -*- coding: gb18030 -*-
import copy

import Language
from bwdebug import INFO_MSG

class SpaceCopyDataLoader:
	# ������Ϣ
	_instance = None
	def __init__( self ):
		assert SpaceCopyDataLoader._instance is None
		self.data = {}

	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = SpaceCopyDataLoader()
		return self._instance

	def __getitem__( self, key ):
		"""
		ȡ��Space���ݲ���
		"""
		if self.data.has_key( key ):
			return self.data[key]
		else:
			return None

	def load( self, configPath ):
		spaceCopyInfos = Language.openConfigSection( configPath )
		for node in spaceCopyInfos.values():
			self.data[ node.readString( "spaceClassName" ) ] = {\
				"spaceName": node.readString( "spaceName" ),\
				"birthPos": node.readVector3( "birthPos" ) ,\
				"birthDirection": node.readVector3( "birthDirection" ),\
				}

		Language.purgeConfig( configPath )

	def birthDataOfCopy( self, copyLabel ) :
		"""
		��ȡ�����ĳ���������
		"""
		if copyLabel in self.data :
			return self.data[copyLabel]["birthPos"], self.data[copyLabel]["birthDirection"]
		else :
			INFO_MSG( "Space(%s) birth pos and birth direction not exist." % copyLabel )
			return (0,0,0), (0,0,0)

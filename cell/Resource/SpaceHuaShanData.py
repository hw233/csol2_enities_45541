# -*- coding: gb18030 -*-
import copy

import Language

class SpaceHuaShanData:
	# ��ɽ��/��ս��������������Ϣ
	_instance = None
	def __init__( self ):
		assert SpaceHuaShanData._instance is None
		self.data = {}
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = SpaceHuaShanData()
		return self._instance

	def __getitem__( self, key ):
		"""
		ȡ��Space���ݲ���
		"""
		return self.data[key]
	
	def getMonsterInfos( self, gate, memNum ):
		# ȡ�õ�ǰ������������ gate:�㣬 memNum:��������
		item = self.data[ gate ]
		memNum -= 1
		monsterNum = item[ "monsterNum" ][ memNum ]
		bossNum = item[ "bossNum" ][ memNum ]
		bbossNum = item[ "bbossNum" ][ memNum ]
		return ( monsterNum, bossNum, bbossNum )
	
	def load( self, configPath ):
		spawnConfigFile = Language.openConfigSection( configPath )
		for node in spawnConfigFile.values():
			self.data[ node.readInt( "gate" ) ] = {\
				"monsterNum":eval( node.readString( "monsterNum" ) ),\
				"bossNum":eval( node.readString( "bossNum" ) ),\
				"bbossNum":eval( node.readString( "bbossNum" )),\
				}
		
		Language.purgeConfig( configPath )
		self.initConfigData()
	
	def initConfigData( self ):
		datacopy = copy.deepcopy( self.data )
		for gate, infos in datacopy.iteritems():
			for key, values in infos.iteritems():
				count = 0
				newList = []
				for value in values:
					count += value
					newList.append( count )
					
				self.data[ gate ][ key ] = newList
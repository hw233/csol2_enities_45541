# -*- coding: gb18030 -*-


from bwdebug import *
import csdefine
import csconst
import Language
import random
import items


class TongFeteDataLoader:
	"""
	���������ݼ���
	"""
	_instance = None
	def __init__( self ):
		assert self._instance is None,"Just allow one instance exist!"
		TongFeteDataLoader._instance = self
		
		self._data = {}	# �洢��������{ ( ����, Ʒ�� ):[ �﹩, [ itemID, ��ø��� ] ] }
		
		
	def load( self, xmlPath = "" ):
		"""
		����xml�ļ�����
		"""
		section = Language.openConfigSection( xmlPath )
		assert section is not None,"open file( path:%s ) error:not exist!" % xmlPath
		
		successCount = 0
		failedCount = 0
		for node in section.values():
			level = node.readInt( "equip_level" )
			quality = node.readInt( "quality" )
			offer = node.readInt( "tong_offer" )
			rate = node.readInt( "rate" )
			itemID = node.readInt( "itemID" )
			if level is None or quality is None or offer is None or rate is None or itemID is None:
				ERROR_MSG( "--->>>read data,when failedCount:%i,successCount:%i." % ( failedCount, successCount ) )
				failedCount += 1
				continue
			self._data[ ( level, quality ) ] = [ offer, [ itemID, rate/100.0 ] ]
			successCount += 1
		INFO_MSG( "------>>>successCount:%i;failedCount:%i." % ( successCount, failedCount ) )
		
		
	def getTongOffer( self, equipLevel, equipQuality ):
		"""
		����װ�������װ��Ʒ�ʻ����Ӧ�İ﹩
		
		@param equipLevel : װ������
		@type equipLevel : UINT16
		@param equipQuality : װ��Ʒ��
		@type equipQuality : UINT8
		"""
		try:
			return self._data[ ( equipLevel, equipQuality ) ][ 0 ]
		except:
			ERROR_MSG( "-------->>>equeipLevel:%i;equipQuality:%i." % ( equipLevel, equipQuality ) )
			
			
	def getFeteItem( self, equipLevel, equipQuality ):
		"""
		����װ�������Ʒ��Ҫ������Ʒ
		
		@param equipLevel : װ������
		@type equipLevel : UINT16
		@param equipQuality : װ��Ʒ��
		@type equipQuality : UINT8
		"""
		rate = self._data[ ( equipLevel, equipQuality ) ][ 1 ][ 1 ]
		if random.random() > rate:
			return None
		return items.instance().createDynamicItem( self._data[ ( equipLevel, equipQuality ) ][ 1 ][ 0 ] )
		
		
	@classmethod
	def instance( self ):
		"""
		"""
		if TongFeteDataLoader._instance is None:
			TongFeteDataLoader._instance = TongFeteDataLoader()
		return TongFeteDataLoader._instance
		
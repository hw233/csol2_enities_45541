# -*- coding: gb18030 -*-


from bwdebug import *
import csdefine
import csconst
import Language
import random
import items


class TongFeteDataLoader:
	"""
	帮会祭祀活动数据加载
	"""
	_instance = None
	def __init__( self ):
		assert self._instance is None,"Just allow one instance exist!"
		TongFeteDataLoader._instance = self
		
		self._data = {}	# 存储奖励数据{ ( 级别, 品质 ):[ 帮供, [ itemID, 获得概率 ] ] }
		
		
	def load( self, xmlPath = "" ):
		"""
		加载xml文件配置
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
		根据装备级别和装备品质获得相应的帮供
		
		@param equipLevel : 装备级别
		@type equipLevel : UINT16
		@param equipQuality : 装备品质
		@type equipQuality : UINT8
		"""
		try:
			return self._data[ ( equipLevel, equipQuality ) ][ 0 ]
		except:
			ERROR_MSG( "-------->>>equeipLevel:%i;equipQuality:%i." % ( equipLevel, equipQuality ) )
			
			
	def getFeteItem( self, equipLevel, equipQuality ):
		"""
		根据装备级别和品质要求获得物品
		
		@param equipLevel : 装备级别
		@type equipLevel : UINT16
		@param equipQuality : 装备品质
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
		
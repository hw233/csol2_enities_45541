# -*- coding: gb18030 -*-

class PlanesSpaceItem( object ):
	def __init__( self ):
		super( PlanesSpaceItem, self ).__init__()
		self.spaceNumber = -1
		self.isFull = False
	
class ImpPlanesSpaceDomain( object ):
	#位面的domain接口
	def __init__( self ):
		super( ImpPlanesSpaceDomain, self ).__init__()
		self._planesSpaceItemInfos = {}
	
	def createPlanesSpaceItem( self, params ):
		"""
		virtual method.
		模板方法；使用params参数创建新的spaceItem
		@return: instance of SpaceItem，如果达到了最大数量，则返回None
		"""
		spaceItem = self.createSpaceItem( params )
		newItem = PlanesSpaceItem()
		newItem.spaceNumber = spaceItem.spaceNumber
		
		self._planesSpaceItemInfos[ spaceItem.spaceNumber ] = newItem
		return spaceItem
			
	def setPlanesSpaceNotFull( self, spaceNumber ):
		"""
		define method.
		设置位面空间的space当前没满，为可进入状态
		"""
		if self._planesSpaceItemInfos.has_key( spaceNumber ):
			self._planesSpaceItemInfos[ spaceNumber ].isFull = False

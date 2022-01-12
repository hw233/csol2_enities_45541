# -*- coding: gb18030 -*-

class PlanesSpaceItem( object ):
	def __init__( self ):
		super( PlanesSpaceItem, self ).__init__()
		self.spaceNumber = -1
		self.isFull = False
	
class ImpPlanesSpaceDomain( object ):
	#λ���domain�ӿ�
	def __init__( self ):
		super( ImpPlanesSpaceDomain, self ).__init__()
		self._planesSpaceItemInfos = {}
	
	def createPlanesSpaceItem( self, params ):
		"""
		virtual method.
		ģ�巽����ʹ��params���������µ�spaceItem
		@return: instance of SpaceItem������ﵽ������������򷵻�None
		"""
		spaceItem = self.createSpaceItem( params )
		newItem = PlanesSpaceItem()
		newItem.spaceNumber = spaceItem.spaceNumber
		
		self._planesSpaceItemInfos[ spaceItem.spaceNumber ] = newItem
		return spaceItem
			
	def setPlanesSpaceNotFull( self, spaceNumber ):
		"""
		define method.
		����λ��ռ��space��ǰû����Ϊ�ɽ���״̬
		"""
		if self._planesSpaceItemInfos.has_key( spaceNumber ):
			self._planesSpaceItemInfos[ spaceNumber ].isFull = False

# -*- coding: gb18030 -*-
#
#�չ���Ʒʵ��

import BigWorld
from config import CollectionItems

def getValidItemIDs():
	"""
	"""
	ids = []
	for name, itemData in CollectionItems.Datas.items():
		if name == "index":continue
		for subName, subData in itemData.items():
			if subName == "index":continue
			for id in subData.keys():
				if id == "index":continue
				ids.append( int(id) )
	return ids

g_validIDs = getValidItemIDs()

class CollectionItem:
	def __init__( self ):
		"""
		"""
		self.itemID 			= 0
		self.price		 		= 0
		self.collectAmount 		= 0
		self.collectedAmount	= 0
		self.collectorDBID		= 0
		self.uid				= 0

	def isEmpty( self ):
		"""
		"""
		return self.collectedAmount == 0

	def isFull( self ):
		"""
		"""
		return self.collectedAmount == self.collectAmount

	def onTake( self ):
		"""
		"""
		self.collectAmount -= self.collectedAmount
		self.collectedAmount = 0
	
	def isValid( self ):
		"""
		���ڼ���չ����ݵĺϷ���
		"""
		return self.itemID in g_validIDs
	
	def check( self, collectionItem ):
		"""
		���ڼ�⽻����Ʒ�ĺϷ���
		"""
		return self.price == collectionItem.price and self.collectAmount - self.collectedAmount >= collectionItem.collectAmount
		
	def onSell( self, collectionItem ):
		"""
		��Ʒ�������ص�
		"""
		self.collectedAmount += collectionItem.collectAmount
		
	def getTotalPrice( self ):
		"""
		��ȡ��Ʒ���չ��ܼ۸�
		"""
		return self.price * ( self.collectAmount - self.collectedAmount )
		
	##################################################################
	# BigWorld �Ľӿ�												#
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "itemID" 			:   obj.itemID,
				 "price" 			:	obj.price,
				 "collectAmount" 	:	obj.collectAmount,
				 "collectedAmount" 	:	obj.collectedAmount,
				 "collectorDBID" 	:	obj.collectorDBID,
				 "uid"				:	obj.uid,
			}

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = CollectionItem()
		obj.itemID 			= dict["itemID"]
		obj.price 			= dict["price"]
		obj.collectAmount	= dict["collectAmount"]
		obj.collectedAmount	= dict["collectedAmount"]
		obj.collectorDBID	= dict["collectorDBID"]
		obj.uid				= dict["uid"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, CollectionItem )


instance = CollectionItem()


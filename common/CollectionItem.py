# -*- coding: gb18030 -*-
#
#收购物品实例

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
		用于检测收购数据的合法性
		"""
		return self.itemID in g_validIDs
	
	def check( self, collectionItem ):
		"""
		用于检测交易物品的合法性
		"""
		return self.price == collectionItem.price and self.collectAmount - self.collectedAmount >= collectionItem.collectAmount
		
	def onSell( self, collectionItem ):
		"""
		物品被卖出回调
		"""
		self.collectedAmount += collectionItem.collectAmount
		
	def getTotalPrice( self ):
		"""
		获取物品的收购总价格
		"""
		return self.price * ( self.collectAmount - self.collectedAmount )
		
	##################################################################
	# BigWorld 的接口												#
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


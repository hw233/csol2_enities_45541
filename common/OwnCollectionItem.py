# -*- coding: gb18030 -*-
#
#收购物品实例

import BigWorld
#import items
#g_items = items.instance()
import CollectionItem

class OwnCollectionItem:
	def __init__( self ):
		"""
		"""
		self.itemID 			= 0
		self.price		 		= 0
		self.collectAmount 		= 0
		self.uid				= 0

	def isValid( self ):
		"""
		用于检测收购数据的合法性
		"""
		return self.itemID in CollectionItem.g_validIDs
	
	def check( self, collectionItem ):
		"""
		用于检测交易物品的合法性
		"""
		return self.price == collectionItem.price and self.collectAmount >= collectionItem.collectAmount
		
	
	def getTotalPrice( self ):
		"""
		"""
		return self.price * self.collectAmount


	def removeTotal( self, amount ):
		"""
		"""
		self.collectAmount -= amount


	#def getItem( self ):
	#	"""
	#	"""
	#	return g_items.createDynamicItem( self.itemID, self.collectAmount )
	
	def getPrice( self ):
		"""
		"""
		return self.price
	
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
				 "uid"				:	obj.uid,
			}

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = OwnCollectionItem()
		obj.itemID 			= dict["itemID"]
		obj.price 			= dict["price"]
		obj.collectAmount	= dict["collectAmount"]
		obj.uid				= dict["uid"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, OwnCollectionItem )
		
instance = OwnCollectionItem()

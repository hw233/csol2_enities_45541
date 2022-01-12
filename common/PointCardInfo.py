# -*- coding: gb18030 -*-
#
#�㿨ʵ��

import BigWorld

class PointCardInfo:
	def __init__( self ):
		self.isSelling 		= False	#�Ƿ���������״̬
		self.buyerName		= ""	#�������
		self.buyerAccount	= ""	#����˺�
		self.price			= 0 	#�㿨�۸�
		self.cardNo			= ""	#����
		self.passWord		= ""	#����
		self.orderID		= ""	#��ţ����������һ��20λ����
		self.serverName		= ""	#����������
		self.salesName		= ""	#��������
		self.salesAccount	= ""	#����ʺ�
		self.salesIP		= 0		#����IP
		self.result			= -1	#�忨���
		self.overTimeResult = -1	#��ʱ���
		self.parValue		= ""	#
		self.sellTime		= 0		#����ʱ��
		
		
	##################################################################
	# BigWorld �Ľӿ�												#
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return getDictFromObj( obj )

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		return createObjFromDict( dict )

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, PointCardInfo )


instance = PointCardInfo()

if BigWorld.component in [ "db", "base", "cell" ]:
	def getDictFromObj( obj ):
		"""
		"""
		return { "isSelling" 	:   obj.isSelling, 			
				 "buyerName" 	:	obj.buyerName,		
				 "buyerAccount" :	obj.buyerAccount,	
				 "price" 		:	obj.price,			
				 "cardNo" 		:	obj.cardNo,			
				 "passWord" 	:	obj.passWord,		
				 "orderID" 		:	obj.orderID,		
				 "serverName" 	:	obj.serverName,		
				 "salesName" 	:	obj.salesName,		
				 "salesIP" 		:	obj.salesIP,		
				 "result"		:	obj.result,			
				 "overTimeResult":	obj.overTimeResult,	
				 "parValue"		:	obj.parValue,
				 "sellTime"		:	obj.sellTime,
				 "salesAccount"	:	obj.salesAccount,		
			}
	def createObjFromDict( dict ):
		"""
		"""
		obj = PointCardInfo()
		obj.price 		= dict["price"]
		obj.buyerName 	= dict["buyerName"]
		obj.buyerAccount= dict["buyerAccount"]
		obj.cardNo		= dict["cardNo"]
		obj.passWord	= dict["passWord"]
		obj.orderID		= dict["orderID"]
		obj.serverName	= dict["serverName"]
		obj.salesName	= dict["salesName"]
		obj.salesIP		= dict["salesIP"]
		obj.result		= dict["result"]
		obj.overTimeResult = dict["overTimeResult"]
		obj.parValue	= dict["parValue"]
		obj.sellTime	= dict["sellTime"]
		obj.salesAccount	= dict["salesAccount"]
		return obj
else:
	def getDictFromObj( obj ):
		"""
		"""
		return { 	
				"isSelling" 	:   0, 			
				 "buyerName" 	:	"",		
				 "buyerAccount" :	"",	
				 "price" 		:	obj.price,			
				 "cardNo" 		:	obj.cardNo,			
				 "passWord" 	:	"",		
				 "orderID" 		:	"",		
				 "serverName" 	:	"",		
				 "salesName" 	:	obj.salesName,		
				 "salesIP" 		:	"",		
				 "result"		:	0,			
				 "overTimeResult":	0,	
				 "parValue"		:	obj.parValue,
				 "sellTime"		:	obj.sellTime,
				 "salesAccount"	:	"",
			}
	def createObjFromDict( dict ):
		"""
		"""
		obj = PointCardInfo()
		obj.price 		= dict["price"]
		obj.cardNo		= dict["cardNo"]
		obj.salesName	= dict["salesName"]
		obj.parValue	= dict["parValue"]
		obj.sellTime	= dict["sellTime"]
		return obj
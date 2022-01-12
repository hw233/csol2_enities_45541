# -*- coding: gb18030 -*-
#
#点卡实例

import BigWorld

class PointCardInfo:
	def __init__( self ):
		self.isSelling 		= False	#是否正在销售状态
		self.buyerName		= ""	#买家名字
		self.buyerAccount	= ""	#买家账号
		self.price			= 0 	#点卡价格
		self.cardNo			= ""	#卡号
		self.passWord		= ""	#密码
		self.orderID		= ""	#序号（随机产生的一个20位数）
		self.serverName		= ""	#服务器名字
		self.salesName		= ""	#卖家名字
		self.salesAccount	= ""	#买家帐号
		self.salesIP		= 0		#卖家IP
		self.result			= -1	#冲卡结果
		self.overTimeResult = -1	#超时结果
		self.parValue		= ""	#
		self.sellTime		= 0		#出售时间
		
		
	##################################################################
	# BigWorld 的接口												#
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
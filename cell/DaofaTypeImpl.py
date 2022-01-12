# -*- coding: gb18030 -*-
from items.CDaoFa import CDaoFa

class DaofaTypeImpl:
	"""
	道法基础数据类型
	"""
	def getDictFromObj( self, obj ):
		dict = {
			"uid"		: obj.uid,
			"type" 		: obj.type,
			"level"		: obj.level,
			"exp"		: obj.exp,
			"quality" 	: obj.quality,
			"order"		: obj.order,
			"daoXinID"	: obj.daoXinID,
			"isLocked"	: obj.isLocked,
		}
		return dict
	
	def createObjFromDict( self, dict ):
		obj = CDaoFa()
		obj.initData( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, CDaoFa )

instance = DaofaTypeImpl()
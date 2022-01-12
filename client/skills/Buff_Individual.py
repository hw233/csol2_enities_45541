# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpellBase import Buff
from Function import newUID

class Buff_Individual ( Buff ):
	"""
	玩家个体相关的buff，如果某个buff中需要保存一些针对每个玩家的个性化数据，那么请继承此buff
	不继承此buff且也不采取其他措施就直接处理玩家个性化数据会产生“单实例”问题，详见：CSOL-10239
	by mushuang
	"""
	def __init__( self ):
		"""
		"""
		self._packedIndividualData = {}
	
	def __clone( self ):
		"""
		克隆自身
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		return obj
		
	
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		
		
		注意:理论上client数据没有什么数据需要打包运输，但是跟踪结果表明此方法仍然被BigWorld调用至少一次，所以保险起见，
		还是按照正确的步骤进行打包。如果你明白BigWorld为什么需要在客户端调用此方法以及此方法打包的数据被用在了哪里，请
		将在这里备注一下，谢谢！ by mushuang
		"""
		DEBUG_MSG( "client addToDict called!"  )
		
		
		# 数据漂流瓶，用来监测数据的流动，没有什么实际意义，原因见此方法的注释
		if isDebuged:
			 self._packedIndividualData[ "debug2011-1-17 16:15" ] = \
			 "If you saw this data somewhere else, it means BigWorld spreads data using this method!"
		
		return { "param" : self._packedIndividualData }
	
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		注意:如果你继承了“Buff_Individual”类，一定不要覆盖这个方法。
		
		@type data: dict
		"""
		obj = self.__clone()
		
		DEBUG_MSG( "Restoreing object of class: %s"%obj.__class__ )
		
		# 将打包运输的“不同玩家相关数据”正确设置到各个字段中去
		for key,val in data["param"].iteritems():
			assert hasattr( obj, key ),"Can't find attribute: %s in this object!"%key
			DEBUG_MSG( "Setting attr:%s to %s"%( key, val ) )
			setattr( obj, key, val )		
			
		return obj
	

	
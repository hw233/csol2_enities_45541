# -*- coding: gb18030 -*-

"""
此模块只在cellApp和baseApp下使用，client不需要此模块。

使用时cellApp和baseApp下必须有TimeSave模块。cellApp和baseApp下的TimeSave模块有不同的处理方式。
"""
# $Id: CooldownFlyweight.py,v 1.3 2006-05-26 10:20:50 phw Exp $

import TimeSave
from bwdebug import *
import Language

class CooldownFlyweight:
	_instance = None
	
	def __init__( self ):
		assert CooldownFlyweight._instance is None, "instance already exist in"
		self._datas = {}
	
	@staticmethod
	def instance():
		if CooldownFlyweight._instance is None:
			CooldownFlyweight._instance = CooldownFlyweight()
		return CooldownFlyweight._instance
	
	def __getitem__( self, typeID ):
		"""
		取得某个全局道具实例
		
		@param typeID: cooldown 类型标识
		@type  typeID: INT16
		"""
		return self._datas[typeID]
		
	def load( self, xmlConf ):
		"""
		加载数据
		"""
		section = Language.openConfigSection( xmlConf )
		assert section is not None, "can't open config."
		
		count = 0
		for sec in section.values():
			instance = TimeSave.TimeSave( sec )
			self._datas[instance.getID()] = instance
			count += 1
			
		Language.purgeConfig( xmlConf )
		INFO_MSG( "cooldown type config read", count )
		
# end of class: CooldownFlyweight

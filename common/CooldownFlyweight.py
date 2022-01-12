# -*- coding: gb18030 -*-

"""
��ģ��ֻ��cellApp��baseApp��ʹ�ã�client����Ҫ��ģ�顣

ʹ��ʱcellApp��baseApp�±�����TimeSaveģ�顣cellApp��baseApp�µ�TimeSaveģ���в�ͬ�Ĵ���ʽ��
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
		ȡ��ĳ��ȫ�ֵ���ʵ��
		
		@param typeID: cooldown ���ͱ�ʶ
		@type  typeID: INT16
		"""
		return self._datas[typeID]
		
	def load( self, xmlConf ):
		"""
		��������
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

# -*- coding: gb18030 -*-
"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine
import Function
from ProximityTransducer import ProximityTransducer
import random

class RandomProximityTransducer( ProximityTransducer ):
	"""
	����������һ���������壬��������һ�����ʴ��������崥����Ҫ��һ�ο�����ʱ���ٿɴ���
	���ã�����һ�������ƶ���entity������entity����ĳһλ��ʱ���������õļ��ʣ�ִ��һ������
	"""
	def __init__( self ):
		"""
		"""
		ProximityTransducer.__init__( self )		
		self.enterTime = 0.0
		
	def onEnterTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		script = self.getScript()
		if script is not None and hasattr( script, "onEnterTrapExt" ):
			if random.random() <= self.triggerRate and self.radius > 0.0:									# ���ݴ������ʣ������Ƿ񴥷���������
				if BigWorld.time() - self.enterTime < self.triggerInterval:									# ������������ʱ��С�ڴ���������򲻴�������
					return 
				self.enterTime = BigWorld.time()																# ��¼���������ʱ��
				script.onEnterTrapExt( self, entity, range, userData )
	
# end of RandomProximityTransducer.py

# -*- coding: gb18030 -*-
#
# $Id: BoundingBoxLoader.py,v 1.1 2008-03-29 08:47:09 phw Exp $

"""
"""

import sys
from bwdebug import *
import Language
import Math
from config import NPCBoundingBox

class BoundingBoxLoader:
	"""
	��NPCģ�����ñ��е�ģ�ͱ��Ϊkey���ṩ��Ӧ��ģ�͵�bounding box.
	"""
	_instance = None
	def __init__( self ):
		assert BoundingBoxLoader._instance is None, "instance already exist in"
		self._default = ( 0, 0, 0 )
		self._bounds = NPCBoundingBox.Datas		# key == modelNumber; value == Vector3

	@staticmethod
	def instance():
		if BoundingBoxLoader._instance is None:
			BoundingBoxLoader._instance = BoundingBoxLoader()
		return BoundingBoxLoader._instance


	def get( self, modelNumber ):
		"""
		ͨ��modelNumberȡ����Ӧ��bounding box�ĳ����ߡ���
		
		@return: Vector3; (x,y,z) �ֱ��Ӧ�����ߡ���
		"""
		return Math.Vector3( self._bounds.get( modelNumber, self._default ) )


#
# $Log: not supported by cvs2svn $
#
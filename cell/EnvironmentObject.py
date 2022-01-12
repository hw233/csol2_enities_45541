# -*- coding: gb18030 -*-
#

"""
环境物件基类
"""
from interface.GameObject import GameObject
import csdefine
import BigWorld


class EnvironmentObject(GameObject):
	"""
	场景物件基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		GameObject.__init__( self )

		self.setEntityType( csdefine.ENTITY_TYPE_MISC )
		self.visible = True

	def setModelNumber( self, modelNumber ):
		"""
		define method.
		设置模型编号
		"""
		self.modelNumber = modelNumber

	def setModelScale( self, modelScale ):
		"""
		define method.
		设置模型尺寸
		"""
		self.modelScale = modelScale

	def setVisible( self, visible ):
		"""
		define method.
		设置模型尺寸
		"""
		self.visible = visible

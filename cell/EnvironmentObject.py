# -*- coding: gb18030 -*-
#

"""
�����������
"""
from interface.GameObject import GameObject
import csdefine
import BigWorld


class EnvironmentObject(GameObject):
	"""
	�����������
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		GameObject.__init__( self )

		self.setEntityType( csdefine.ENTITY_TYPE_MISC )
		self.visible = True

	def setModelNumber( self, modelNumber ):
		"""
		define method.
		����ģ�ͱ��
		"""
		self.modelNumber = modelNumber

	def setModelScale( self, modelScale ):
		"""
		define method.
		����ģ�ͳߴ�
		"""
		self.modelScale = modelScale

	def setVisible( self, visible ):
		"""
		define method.
		����ģ�ͳߴ�
		"""
		self.visible = visible

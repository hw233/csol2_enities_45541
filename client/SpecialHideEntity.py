# -*- coding: gb18030 -*-
# ����������Entity 2009-01-09 SongPeifang & LinQing
#

from NPCObject import NPCObject
import Define

class SpecialHideEntity( NPCObject ):
	"""
	����������Entity��
	������Ŀ�ģ�������ҵ����á�
	��ҵ���ʱ����Ҫ֪���Ƿ������ں��ߵ�������ר�Ź��������������Entity
	���Entity��Ҫ�ɲ߻�����Ĳ���һ���ں���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )
		self.setSelectable( False )
		self.__canSelect = False
		self.state = 0

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		self.model = None	# ģ�Ϳͻ��˲��ɼ�

	def canSelect( self ):
		return False
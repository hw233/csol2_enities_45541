# -*- coding: gb18030 -*-

# ------------------------------------------------
# from cell
from Resource.CopyStage.CopyStageBase import CopyStageBase

# ------------------------------------------------

class CopyStageInterface :
	"""
	�����ؿ��ӿ�
	"""
	def __init__( self ) :
		self._stages = []
	
	def addStage( self, stage ) :
		"""
		��Ӹ����ؿ�
		"""
		self._stages.append( stage )
	
	def doFirstStage( self, selfEntity ) :
		"""
		��ʼ��һ�������ؿ�
		"""
		if self._stages :
			selfEntity.setTemp( "stageIndex", 0 )
			self._stages[ 0 ].beginStage( selfEntity )
	
	def doNextStage( self, selfEntity ) :
		"""
		��ʼ��һ�������ؿ�
		"""
		index = selfEntity.queryTemp( "stageIndex", -1 )
		index += 1
		if index < len( self._stages ) :
			selfEntity.setTemp( "stageIndex", index )
			self._stages[ index ].beginStage( selfEntity )
	
	def getCurrentStage( self, selfEntity ) :
		"""
		��õ�ǰ�����ؿ�
		"""
		index = selfEntity.queryTemp( "stageIndex", -1 )
		if index != -1 :
			return self._stages[ index ]
		else :
			return None
	
	def getCurrentStageIndex( self, selfEntity ) :
		"""
		��õ�ǰ�����ؿ��������������㸱����ǰ���ڵڼ���
		"""
		return selfEntity.queryTemp( "stageIndex", -1 )


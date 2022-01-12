# -*- coding: gb18030 -*-

# ------------------------------------------------
# from cell
from Resource.CopyStage.CopyStageBase import CopyStageBase

# ------------------------------------------------

class CopyStageInterface :
	"""
	副本关卡接口
	"""
	def __init__( self ) :
		self._stages = []
	
	def addStage( self, stage ) :
		"""
		添加副本关卡
		"""
		self._stages.append( stage )
	
	def doFirstStage( self, selfEntity ) :
		"""
		开始第一个副本关卡
		"""
		if self._stages :
			selfEntity.setTemp( "stageIndex", 0 )
			self._stages[ 0 ].beginStage( selfEntity )
	
	def doNextStage( self, selfEntity ) :
		"""
		开始下一个副本关卡
		"""
		index = selfEntity.queryTemp( "stageIndex", -1 )
		index += 1
		if index < len( self._stages ) :
			selfEntity.setTemp( "stageIndex", index )
			self._stages[ index ].beginStage( selfEntity )
	
	def getCurrentStage( self, selfEntity ) :
		"""
		获得当前副本关卡
		"""
		index = selfEntity.queryTemp( "stageIndex", -1 )
		if index != -1 :
			return self._stages[ index ]
		else :
			return None
	
	def getCurrentStageIndex( self, selfEntity ) :
		"""
		获得当前副本关卡索引，用来计算副本当前处于第几关
		"""
		return selfEntity.queryTemp( "stageIndex", -1 )


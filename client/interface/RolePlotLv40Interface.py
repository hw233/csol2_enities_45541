# -*- coding: gb18030 -*-
import BigWorld
import event.EventCenter as ECenter

class RolePlotLv40Interface:
	"""
	40级剧情副本相关
	"""
	def __init__( self ):
		pass
		
	def plotLv40_showNpcHP( self ):
		"""
		define method
		显示炉鼎和保护罩的HP
		"""
		ECenter.fireEvent( "EVT_ON_STONE_AND_COVER_SHOW" )
	
	def plotLv40_hideNpcHP( self ):
		"""
		define method
		隐藏炉鼎和保护罩的HP
		"""
		ECenter.fireEvent( "EVT_ON_STONE_AND_COVER_HIDE" )
		
	def plotLv40_stoveHPChange( self ,HP, HP_Max ):
		"""
		define method
		炉鼎血量改变回调
		
		@param HP: INT32
		"""
		ECenter.fireEvent( "EVT_ON_STONE_UPDATE", HP, HP_Max )
	
	def plotLv40_protectCoverHPChange( self ,HP, HP_Max ):
		"""
		保护罩血量改变回调
		
		@param HP: INT32
		"""
		ECenter.fireEvent( "EVT_ON_COVER_UPDATE", HP, HP_Max )
	
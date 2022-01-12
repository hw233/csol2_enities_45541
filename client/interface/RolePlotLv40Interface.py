# -*- coding: gb18030 -*-
import BigWorld
import event.EventCenter as ECenter

class RolePlotLv40Interface:
	"""
	40�����鸱�����
	"""
	def __init__( self ):
		pass
		
	def plotLv40_showNpcHP( self ):
		"""
		define method
		��ʾ¯���ͱ����ֵ�HP
		"""
		ECenter.fireEvent( "EVT_ON_STONE_AND_COVER_SHOW" )
	
	def plotLv40_hideNpcHP( self ):
		"""
		define method
		����¯���ͱ����ֵ�HP
		"""
		ECenter.fireEvent( "EVT_ON_STONE_AND_COVER_HIDE" )
		
	def plotLv40_stoveHPChange( self ,HP, HP_Max ):
		"""
		define method
		¯��Ѫ���ı�ص�
		
		@param HP: INT32
		"""
		ECenter.fireEvent( "EVT_ON_STONE_UPDATE", HP, HP_Max )
	
	def plotLv40_protectCoverHPChange( self ,HP, HP_Max ):
		"""
		������Ѫ���ı�ص�
		
		@param HP: INT32
		"""
		ECenter.fireEvent( "EVT_ON_COVER_UPDATE", HP, HP_Max )
	
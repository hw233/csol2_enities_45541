# -*- coding: gb18030 -*-

import event.EventCenter as ECenter
class TDBattleInterface:
	"""
	��ħ��ս�ӿ�
	"""
	def __init__( self ):
		pass
	
	def onCacheCompleted( self ):
		"""
		"""
		self.cell.TDB_onPlayerLogin()

	def TDB_receiveReslut( self, dict ):
		"""
		define method
		���յ�����
		"""
		ECenter.fireEvent("EVT_ON_TBBATTLE_SHOW_RANKLIST", dict )

	def TDB_showTransWindow( self, buttonFlag ):
		"""
		define method
		��ʾ���ͽ���
		
		@buttonFlag: ������ʾ�İ�ť��1Ϊ���밴ť��2Ϊ�ش���ť
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TBBATTLE_TRANS_WINDOW", buttonFlag )

	def TDB_showActButton( self ):
		"""
		define method
		��ʾ�ͼ��
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TBBATTLE_TRANS" )

	def TDB_hideActButton( self ):
		"""
		define method
		���ػͼ��
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_TBBATTLE_TRANS" )

	def TDB_showActTip( self ):
		"""
		define method
		������ʾ����ؽ���
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TBBATTLE_TRANS_TIP" )

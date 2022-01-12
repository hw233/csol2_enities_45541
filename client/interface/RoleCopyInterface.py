# -*- coding: gb18030 -*-
from gbref import rds
import event.EventCenter as ECenter

class RoleCopyInterface:
	"""
	�����Ĺ��ýӿ�
	"""
	def __init__( self ):
		self.pickAnima_maxContinuousPick = 0 #���������
		self.pickAnima_maxZhadan = 0 #ը����
	
	#---------------------------------------------------
	# ʰȡ�����淨
	#---------------------------------------------------
	def pickAnima_enterSpace( self ):
		"""
		define method
		����ص�
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_START" )
		
	def pickAnima_reqStart( self ):
		"""
		������������淨��ʼ
		"""
		self.cell.pickAnima_reqStart()
	
	def pickAnima_start( self ):
		"""
		ʰȡ����淨��ʼ
		"""
		self.changeWorldCamHandler( 2, 1.532, 3.2 )
		self.pickAnima_maxContinuousPick = 0
		self.pickAnima_maxZhadan = 0
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_ONGOING" )
		
	def pickAnima_stop( self ):
		"""
		ʰȡ��⸱������
		"""
		self.changeWorldCamHandler( 1 )
#		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_END" )
		
	
	def pickAnima_upPickInfos( self, allPickNum, continuousPickNum ):
		"""
		define method
		allPickNum �ܹ��������
		continuousPickNum ��ǰ��������
		"""
		if self.pickAnima_maxContinuousPick < continuousPickNum:
			self.pickAnima_maxContinuousPick = continuousPickNum
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_PICKNUM_CHANGED", allPickNum, continuousPickNum )
	
	def pickAnima_triggerZhaDan( self ):
		"""
		define method.
		����ը��
		"""
		self.pickAnima_maxZhadan += 1
	
	def pickAnima_overReport( self, allPickNum, potentialCount ):
		"""
		define method
		ʰȡ�����淨���
		allPickNum һ��ʰȡ����
		potentialCount һ����õ�Ǳ�ܵ���
		"""
		#self.pickAnima_maxContinuousPick ���������
		#self.pickAnima_maxZhadan ը����
		#������JIRA�ϵ��㷨��һ��
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_OVER_REPORT", allPickNum, potentialCount )
	
	def pickAnima_confirmQuitSpace( self ):
		"""
		���ȷ���˳�λ��
		"""
		self.cell.pickAnima_confirmQuitSpace()

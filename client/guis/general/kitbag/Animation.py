# -*- coding: gb18030 -*-
#

"""
implement Animation
"""

from guis.common.RootGUI import RootGUI
import GUI
import BigWorld

class Animation( RootGUI ):
	"""
	��������
	"""
	def __init__( self, gui = None ):
		"""
		��ʼ��
		"""
		RootGUI.__init__( self, gui )
		
		self.visible = False							# ��ʾ
		self.playTime = 1								# ����ʱ��
		self.__playCBID = 0								# CBID
		self.focus = False								# ���⶯���ڲ���ʱ���ƶ�
		
	def initAnimation( self, name, time = 1 ):
		"""
		�趨����
		name	��ӵ���������
		time 	����ʱ��
		"""
		self.addToMgr( name )							# ��ӵ�������
		self.playTime = time
		self.getGui().stopAt = 0
	
	def playAnimation( self, pos = ( 0, 0 ), pyOwner = None ):
		"""
		���Ŷ���
		pos		λ��
		pyOwner	������
		"""
		if self.__playCBID != 0:
			return
			
		self.left = pos[0]
		self.top = pos[1]
		self.__beginAnimation( pyOwner )
		self.__playCBID = BigWorld.callback( self.playTime, self.__endAnimation )
		
	def __beginAnimation( self, pos, pyOwner = None ):
		"""
		��ʼ����
		pos 		λ��
		pyOwner		������
		"""
		RootGUI.show( self, pyOwner )
		self.getGui().stopAt = -1
		
	def __endAnimation( self ):
		"""
		��������
		"""
		RootGUI.hide( self )
		self.getGui().stopAt = 0
		self.__playCBID = 0
# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import cschannel_msgs
import ShareTexts as ST
import time
import BigWorld
import csconst

SPACE_LAST_TIME = 3600 		#�������ʱ��һСʱ

"""
���л��縱���߼��������⴦��
"""


class SpaceCopyHundun( SpaceCopy ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		if "HD_%i"%self.params["teamID"] in BigWorld.cellAppData.keys():
			del BigWorld.cellAppData["HD_%i"%self.params["teamID"]]
	
	def onEnter( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.copyDataInit( baseMailbox, params )
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnter( self, baseMailbox, params )


	def copyDataInit( self, baseMailbox, params ):
		"""
		�������ݷ���ĳ�ʼ��
		"""
		BigWorld.globalData['Hundun_%i' % params['teamID'] ] = True
		self.setTemp('globalkey','Hundun_%i' % params['teamID'])
		
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_MONSTERACTIVITY )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
		
	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
		]
		"""
		# ��ʾʣ��С�֣�ʣ��BOSS�� 
		return [ 1, 3 ]
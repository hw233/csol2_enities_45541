# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import cschannel_msgs
import ShareTexts as ST
import time
import BigWorld
import csconst

SPACE_LAST_TIME = 3600 		#混沌持续时间一小时

"""
所有混沌副本逻辑集中在这处理
"""


class SpaceCopyHundun( SpaceCopy ):
	
	def __init__(self):
		"""
		构造函数。
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
		副本数据方面的初始化
		"""
		BigWorld.globalData['Hundun_%i' % params['teamID'] ] = True
		self.setTemp('globalkey','Hundun_%i' % params['teamID'])
		
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_MONSTERACTIVITY )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
		
	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
		]
		"""
		# 显示剩余小怪，剩余BOSS。 
		return [ 1, 3 ]
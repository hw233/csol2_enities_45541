# -*- coding: gb18030 -*-
#
# $Id: TeamSystem.py

"""
implement quest list class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather
from guis.common.Window import Window
from AbstractTemplates import Singleton
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.StaticText import StaticText
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.TreeView import TreeNode
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from Time import Time
import Timer
import csdefine

DUTY_MAPPINGS = {csdefine.COPY_DUTY_MT:(1,2),
				csdefine.COPY_DUTY_HEALER:(2,1),
				csdefine.COPY_DUTY_DPS:(2,2),
				}

class CopyTeamMatch( Singleton, Window ):
	"""
	队伍匹配界面
	"""
	__triggers = {}
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/copyteam/teammatch.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		self.__matchTime = 0.0
		self.__matchcbid = 0
		self.__avgTime = 0 
		self.__initialize( wnd )
		self.addToMgr( "copyTeamMatch" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ):
		self.__pyPosts = {}
		for name, item in wnd.children:
			if not name.startswith( "post_" ):continue
			postTag = int( name.split( "_" )[1] )
			pyPost = MatchPost( item, postTag )
			if postTag == csdefine.COPY_DUTY_DPS:
				index = int( name.split( "_" )[-1] )
				if self.__pyPosts.has_key( postTag ):
					self.__pyPosts[postTag][index] = pyPost
				else:
					self.__pyPosts[postTag] = {index:pyPost}
			else:
				self.__pyPosts[postTag] = pyPost
		
		self.__pyRtAverTime = CSRichText( wnd.rtAverTime )
		self.__pyRtAverTime.text = ""
		self.__pyRtAverTime.align = "C"
		
		self.__pyRtTeamTime = CSRichText( wnd.rtTeamTime )
		self.__pyRtTeamTime.text = ""
		self.__pyRtTeamTime.align = "C"
		
		self.__pyPostIcon = PyGUI( wnd.post )
		
		self.__pyBtnQuit = HButtonEx( wnd.btnQuit )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.onLClick.bind( self.__onLeaveCopy )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "copyteam:TeamMatch", "quitcopyteam" )
		
		self.__pyBtnClose = HButtonEx( wnd.btnClose )
		self.__pyBtnClose.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnClose.onLClick.bind( self.__onClose )
		labelGather.setPyBgLabel( self.__pyBtnClose, "copyteam:TeamSystem", "close" )
		
		labelGather.setPyLabel( self.pyLbTitle_, "copyteam:TeamMatch", "title_match" )
		labelGather.setLabel( wnd.postText, "copyteam:TeamMatch", "postText" )
	
	@classmethod
	def __onTroogleMatchingWnd( SELF ):
		"""
		触发显示
		"""
		player = BigWorld.player()
		self = SELF.inst
		mins = int( self.__avgTime/60 )
		secs = int( self.__avgTime%60 )
		averTimeStr = labelGather.getText( "copyteam:TeamMatch","avertime" )%( mins, secs )
		teamTimeStr = labelGather.getText( "copyteam:TeamMatch","teamtime" )%(0,0)
		self.__pyRtAverTime.text = PL_Font.getSource( averTimeStr, fc = ( 231, 213, 155, 255 ) )
		membersDuties = player.matchedMembersDuty
		self.__resetDutyState()
		if len( membersDuties ):
			self.__setDutiesInfo( membersDuties )
		else:
			queueingDuties = player.queueingDuties
			index = 0
			for duty in queueingDuties:
				if duty == csdefine.COPY_DUTY_DPS:
					postInfos = self.__pyPosts.get( duty )
					postInfo = postInfos.get( index )
					if postInfo is None:continue
					postInfo.setMaterialFX( "BLEND" )
					index += 1
				else:
					self.__pyPosts[duty].setMaterialFX( "BLEND" )
		self.__pyBtnQuit.enable = not player.isInTeam() or player.isCaptain()
		self.show()
		
	@classmethod
	def __onUpdateMatchInfo( SELF, copyLabel, copyLevel, memberToDuty ):
		"""
		更新匹配信息
		"""
		self = SELF.inst
		if not self.visible:return
		self.__setDutiesInfo( memberToDuty )
	
	@classmethod
	def __onUpdateAvgTime( SELF, avgTime ):
		"""
		平均等待时间
		"""
		self = SELF.inst
		self.__avgTime = avgTime
		mins = int( self.__avgTime/60 )
		secs = int( self.__avgTime%60 )
		averTimeStr = labelGather.getText( "copyteam:TeamMatch","avertime" )%( mins, secs )
		self.__pyRtAverTime.text = PL_Font.getSource( averTimeStr, fc = ( 231, 213, 155, 255 ) )
	
	@classmethod
	def __onStatusChange( SELF, oldStatus, newStatus ):
		"""
		状态改变
		"""
		self = SELF.inst
		if oldStatus == csdefine.MATCH_STATUS_PERSONAL_MATCHING and \
		newStatus in [csdefine.MATCH_STATUS_PERSONAL_NORMAL, \
		csdefine.MATCH_STATUS_PERSONAL_CONFIRMING]:
			if self.__matchcbid > 0:
				Timer.cancel( self.__matchcbid )
			self.hide()
		if newStatus == csdefine.MATCH_STATUS_PERSONAL_MATCHING:
			self.__matchTime = Time.time()
			if self.__matchcbid > 0:
				Timer.cancel( self.__matchcbid )
			self.__matchcbid = Timer.addTimer( 0, 1, self.__updateWaitTime )
			
	@classmethod
	def __onFlashQueueDuties( SELF, duties ):
		"""
		刷新队伍职务
		"""
		self = SELF.inst
		self.__resetDutyState()
		index = 0
		for duty in duties:
			if duty == csdefine.COPY_DUTY_DPS:
				dpsDuties = self.__pyPosts[duty]
				dpsDuty = dpsDuties.get( index )
				if dpsDuty is None:continue
				dpsDuty.setMaterialFX( "BLEND" )
				index += 1
			else:
				self.__pyPosts[duty].setMaterialFX( "BLEND" )

	def __setDutiesInfo( self, duties ):
		"""
		设置每个职务信息
		"""
		index = 0
		player = BigWorld.player()
		if len( duties ) <= 0:return
		for memberID, duty in duties.items():
			if duty == csdefine.COPY_DUTY_DPS:
				postInfos = self.__pyPosts.get( duty )
				postInfo = postInfos.get( index )
				if postInfo is None:continue
				postInfo.setDutyInfo( memberID )
				index += 1
			else:
				self.__pyPosts[duty].setDutyInfo( memberID )
	
	def __resetDutyState( self ):
		"""
		重置职务图标状态
		"""
		for duty, postInfos in self.__pyPosts.items():
			if duty == csdefine.COPY_DUTY_DPS:
				for postInfo in postInfos.values():
					postInfo.setMaterialFX( "COLOUR_EFF" )
			else:
				postInfos.setMaterialFX( "COLOUR_EFF" )
	
	def __onLeaveCopy( self, pyBtn ):
		"""
		离开副本组队
		"""
		if pyBtn is None:return
		BigWorld.player().leaveCopyMatcherQueue()
	
	def __updateWaitTime( self ):
		"""
		更新等待时间
		"""
		waitTime = Time.time() - self.__matchTime
		mins = int( waitTime/60 )
		secs = int( waitTime%60 )
		teamTimeStr = labelGather.getText( "copyteam:TeamMatch","teamtime" )%( mins,secs )
		self.__pyRtTeamTime.text = PL_Font.getSource( teamTimeStr, fc = ( 231, 213, 155, 255 ) )
	
	def __onClose( self, pyBtn ):
		"""
		关闭窗口
		"""
		if pyBtn is None:return
		self.hide()

	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_TOGGLE_TEAMCOPY_MATCHING_WND"] = SELF.__onTroogleMatchingWnd
		SELF.__triggers["EVT_ON_COPYMATCHER_UPDATE_MATCHED_COPYINFO"] = SELF.__onUpdateMatchInfo
		SELF.__triggers["EVT_ON_COPYMATCHER_UPDATE_AVG_QUEUE_TIME"] = SELF.__onUpdateAvgTime
		SELF.__triggers["EVT_ON_COPYMATCHER_STATUS_CHANGE"] = SELF.__onStatusChange
		SELF.__triggers["EVT_ON_COPYMATCHER_FLASH_QUEUE_DUTIES"] = SELF.__onFlashQueueDuties
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )
			
	def show( self ):
		"""
		显示
		"""
		self.r_center = 0
		self.r_middle = 0
		pyPost = self.__pyPosts[csdefine.COPY_DUTY_DPS][2]
		pyPost.setMaterialFX( "BLEND" )
		Window.show( self )
	
	def hide( self ):
		"""
		隐藏
		"""
		for postTag, pyPosts in self.__pyPosts.items():
			if postTag == csdefine.COPY_DUTY_DPS:
				for pyPost in pyPosts.values():
					pyPost.materialFX = "COLOUR_EFF"
			else:
				pyPosts.materialFX = "COLOUR_EFF"
		Window.hide( self )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

# -----------------------------------------------------------------------------
class MatchPost( Control ):
	"""
	匹配职务
	"""
	def __init__( self, item, postTag ):
		Control.__init__( self, item )
		self.__pyPstIcon = PyGUI( item.icon )
		self.__pyCaptain = PyGUI( item.captain )
		self.__pyCaptain.visible = False
		mapping = DUTY_MAPPINGS.get( postTag, (1,2) )
		util.setGuiState( self.__pyPstIcon.getGui(), (2,2), mapping )
		self.setMaterialFX( "COLOUR_EFF" )
		self.__memberID = 0
	
	def setIsCaptain( self, isCaptain ):
		"""
		是否为队长
		"""
		self.__pyCaptain.visible = isCaptain
	
	def setDutyInfo( self, memberID ):
		"""
		设置对应职务的玩家id
		"""
		if memberID > 0:
			player = BigWorld.player()
			self.__memberID = memberID
			self.setMaterialFX( "BLEND" )
			self.__pyCaptain.visible = memberID == player.captainID
	
	def setMaterialFX( self, style ):
		"""
		设置materialFX
		"""
		for name, item in self.getGui().children:
			item.materialFX = style
	
	def _setMemberID( self, teammateID ):
		self.__memberID = teammateID
	
	def _getMemberID( self ):
		return self.__memberID

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	memberID = property( _getMemberID, _setMemberID )

CopyTeamMatch.registerTriggers()
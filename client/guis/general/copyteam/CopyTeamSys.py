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
from guis.controls.Icon import Icon
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.ODListPanel import ODListPanel
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.StaticText import StaticText
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.TreeView import TreeNode
from guis.controls.RichText import RichText
from guis.tooluis.CSRichText import CSRichText
from config.client.msgboxtexts import Datas as mbmsgs
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from Function import Functor
import event.EventCenter as ECenter
import GUIFacade
import csdefine
import csconst
from Time import Time
import Language

CONTINUED_COPY_TYPE = 0		#持续开启副本类型
TIMING_COPY_TYPE = 1		#定时开启副本类型


class CopyTeamSys( Window ):
	"""
	副本组队界面
	"""
	_copy_types = { CONTINUED_COPY_TYPE: labelGather.getText( "copyteam:TeamSystem", "continued" ),
					TIMING_COPY_TYPE: labelGather.getText( "copyteam:TeamSystem", "timing" ),
				}
	_copy_invad_buff = 106001
	
	_copy_cnf = "config/matchablecopies.xml"
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/copyteam/teamsystem/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		self.__isCopyGuider = False
		self.__pyCapCheck = None
		self.__myCDCBID = 0
		self.__teamCDID = 0
		self.__punishCBID = 0
		self.__pyTypeNodes = {}
		self.__copies = {}
		self.__loadCopyConfig()
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		
		self.__changedPyNodes = { 'typeNodes' : [], 'copyNodes' : [] }
	
	def __loadCopyConfig( self ):
		sect = Language.openConfigSection( self._copy_cnf )
		if sect is None :
			ERROR_MSG( "Can't open config of path: %s." % self._copy_cnf )
			return
		for copySect in sect.values() :
			copyFlag = copySect.readInt("copyFlag")
			copyLabel = copySect.readString( "spaceClassName" )
			mode = copySect.readInt("mode")
			if self.__copies.has_key( copyFlag ):
				self.__copies[copyFlag].update( {copyLabel:mode} )
			else:
				self.__copies[copyFlag] = {copyLabel:mode }
		Language.purgeConfig( self._copy_cnf )
	
	def __initialize( self, wnd ):
		self.__pyTVCopys = TreeView( wnd.copyPanel.tvCopys, wnd.copyPanel.vSBCopys )
		self.__pyTVCopys.nodeOffset = 29.0
		self.__pyTVCopys.onTreeNodeSelected.bind( self.__onCopyNodeSelected )
		for copyType, typeName in self._copy_types.items():
			pyTypeNode = TypeNode( copyType )
			pyTypeNode.text = typeName
			self.__pyTypeNodes[copyType] = pyTypeNode
			self.__pyTVCopys.pyNodes.add( pyTypeNode )
			self.__pyTVCopys.pyNodes.sort( key = lambda pyNode : pyNode.copyType )
		self.__initCopiesTree()
	
		infoPanel = wnd.copyPanel.infoPanel
		self.__pyInfoPanel = PyGUI( infoPanel )
		self.__pyInfoPanel.visible = False
		self.__pyRtWarning = CSRichText( infoPanel.rtWarning )
		self.__pyRtWarning.align = "C"
		self.__pyRtWarning.text = ""
		
		self.__pyRtTime = CSRichText( infoPanel.rtTime )
		self.__pyRtTime.align = "C"
		self.__pyRtTime.text = ""
		
		self.__pyListPanel = ODListPanel( infoPanel.listPanel, infoPanel.listBar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 23.0
		self.__pyListPanel.autoSelect = True
		
		self.__pyBtnsPanel = PyGUI( infoPanel.btnsPanel )
		self.__pyBtnsPanel.visible = False
		
		self.__pyBtnOK = HButtonEx( infoPanel.btnsPanel.btnOK )
		self.__pyBtnOK.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOK.onLClick.bind( self.__onRecruit )
		labelGather.setPyBgLabel( self.__pyBtnOK, "copyteam:TeamSystem", "recruit" )
		
		self.__pyBtnCancel = HButtonEx( infoPanel.btnsPanel.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onHide )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "copyteam:TeamSystem", "hide" )
		
		self.__pyPosts = {}
		self.__pyCapCheck = None
		for name, item in wnd.postPanel.children:
			if not name.startswith( "post_" ):continue
			postTag = int( name.split( "_" )[1] )
			pyCKPost = CheckBoxEx( item )
			pyCKPost.postTag = postTag
			pyCKPost.checked = False
			pyCKPost.crossFocus = True
			pyCKPost.onMouseEnter.bind( self.__onShowPostDsp )
			pyCKPost.onMouseLeave.bind( self.__onHidePostDsp )
			pyCKPost.onLMouseDown.bind( self.__onHidePostDsp )
			if postTag == 0:
				self.__pyCapCheck = pyCKPost
				self.__pyCapCheck.onCheckChanged.bind( self.__onCaptainCheck )
			else:
				pyCKPost.onCheckChanged.bind( self.__onPostChange )
				self.__pyPosts[postTag] = pyCKPost
		
		self.__pyBtnInjoy = HButtonEx( wnd.btnInjoy )
		self.__pyBtnInjoy.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnInjoy, "copyteam:TeamSystem", "injoyTeam" )
		self.__pyBtnInjoy.onLClick.bind( self.__onInjoyTeam )
		self.__pyBtnInjoy.enable = False
		
		self.__pyBtnClose = HButtonEx( wnd.btnClose )
		self.__pyBtnClose.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnClose.onLClick.bind( self.__onCloseWnd )
		labelGather.setPyBgLabel( self.__pyBtnClose, "copyteam:TeamSystem", "close" )
		
		self.__pyBtnAbandon = HButtonEx( wnd.btnAbandon )
		self.__pyBtnAbandon.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnAbandon, "copyteam:TeamSystem", "abandon" )
		self.__pyBtnAbandon.onLClick.bind( self.__onAbandon )
		self.__pyBtnAbandon.visible = False
		
		labelGather.setPyLabel( self.pyLbTitle_, "copyteam:TeamSystem", "lbTitle" )
		labelGather.setLabel( wnd.postPanel.bgTitle.stTitle,"copyteam:TeamSystem", "postChose" )
		labelGather.setLabel( wnd.copyPanel.bgTitle.stTitle,"copyteam:TeamSystem", "copyChose" )
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TEAMCOPY_SYSTEM_WND"] = self.__toggleTeamSysWnd
		self.__triggers["EVT_ON_COPYMATCHER_STATUS_CHANGE"] = self.__onCopyMatchStatusChange
		self.__triggers["EVT_ON_COPYMATCHER_COPYNODE_CHECKED"] = self.__onCopyNodeChecked
		self.__triggers["EVT_ON_COPYMATCHER_TEAMMATE_LEAVE"] = self.__onTeammateLeave
		self.__triggers["EVT_ON_COPYMATCHER_TEAMMATE_JOIN"] = self.__onTeammateJion
		self.__triggers["EVT_ON_COPYMATCHER_TEAMMATE_LOGOUT"] = self.__onTeammateLogOut
		self.__triggers["EVT_ON_TEAM_DISBANDED"] = self.__onTeamDisbanded
		self.__triggers["EVT_ON_CHANGE_SELECTING_DUTY_STATUS"] = self.__onChangeSelectingDutyStatus
		self.__triggers["EVT_ON_CANCEL_SELECTING_DUTY_STATUS"] = self.__onCancelSelectingDutyStatus
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
	# -----------------------------------------------------------------
	def __initListItem( self, pyViewItem ) :
		item = GUI.load( "guis/general/copyteam/teamsystem/matestatus.gui" )
		uiFixer.firstLoadFix( item )
		pyMateStatus = MateStatus( item )
		pyViewItem.addPyChild( pyMateStatus )
		pyViewItem.crossFocus = False
		pyMateStatus.pos = 1.0, 1
		pyViewItem.pyItem = pyMateStatus

	def __drawListItem( self, pyViewItem ) :
		pyMateStatus = pyViewItem.pyItem
		pyMateStatus.setStatus( pyViewItem )

	def __initCopiesTree( self ):
		"""
		初始化树视图
		"""
		copyFormulas = rds.spaceCopyFormulas
		copiesSummary = copyFormulas.getCopiesSummary()
		for copyLabel, copySummary in copiesSummary.items():
			copyFlag = copySummary["copyFlag"]
			if copyFlag in self.__copies:
				copies = self.__copies[copyFlag]
				copyNode = None
				if len( copies ) > 1:
					if self.__pyTypeNodes.has_key( copyFlag ):
						copyNode = self.__pyTypeNodes[copyFlag]
					else:
						copyNode = TypeNode( copyFlag )
						copyNode.minLevel = copySummary["minEnterLevel"]
						copyNode.text = copySummary["copyName"]
						self.__pyTypeNodes[copyFlag] = copyNode
					mode = copies[copyLabel]
					subCopyNode = CopyNode( copySummary, mode )
					subCopyNode.text = "%d人难度"%mode
					copyNode.pyNodes.add( subCopyNode )
					copyNode.pyNodes.sort( key = lambda pyNode : pyNode.mode )
				else:
					mode = copies.values()[0]
					copyNode = CopyNode( copySummary, mode )
					copyNode.text = "%s(%d人难度)"%( copySummary["copyName"], mode )
				pyTypeNode = self.__pyTypeNodes[CONTINUED_COPY_TYPE]
				if copySummary["unit"] == "week" or copySummary["unit"] == "day" :   #刷新周期不为空					
					pyTypeNode = self.__pyTypeNodes[TIMING_COPY_TYPE]
				pyTypeNode.pyNodes.add( copyNode )
				pyTypeNode.pyNodes.sort( key = lambda pyNode : pyNode.minLevel )
		
	def __toggleTeamSysWnd( self, isRecruit = False ):
		player = BigWorld.player()
		pClass = player.getClass()
		fitDuties = csconst.CLASS_TO_COPY_DUTIES.get( pClass, () )
		for postTag, pyPost in self.__pyPosts.items():
			pyPost.focus = postTag in fitDuties
			if postTag in fitDuties:
				materialFX = "BLEND"
			else:
				materialFX = "COLOUR_EFF"
			pyPost.materialFX = materialFX
		matchStatus = player.matchStatus
		isCanEnter = not player.isInTeam() or player.isCaptain()
		isPunish = self._copy_invad_buff in player.buffEffect		#是否在惩罚状态
		isCooldown = self.__isTeamCooldown()					# 队伍是否处于15分钟冷却状态
		isAllow =  not isPunish and not isCooldown
		isShowCopy = isAllow and not isRecruit
		self.__pyTVCopys.visible = isShowCopy
		self.__pyInfoPanel.visible = not isShowCopy
		self.__pyBtnInjoy.enable = False
		if isShowCopy:
			print 111
			for pyTypeNode in self.__pyTypeNodes.values():
				pyTypeNode.enable = isCanEnter
				pyTypeNode.setEnterStatus()
				for pyNode in pyTypeNode.pyNodes:
					pyNode.setEnterStatus()
					if hasattr( pyNode, "copyLabel" ):
						pyNode.checked = False
						pyNode.setEnterStatus()

		else: #冷却状态
			warningText = ""
			if isRecruit:	#招募状态
				print 222
				warningText = labelGather.getText( "copyteam:TeamSystem","recruitWarn" )
			if isCooldown:
				print 333
				warningText = labelGather.getText( "copyteam:TeamSystem", "cooldown" )
				self.__myCDCBID = BigWorld.callback( 0.0, self.__flashMyCDTime )
				self.__teamCDID = BigWorld.callback( 0.0, self.__flashTeamCDStatus )
				for teammateID in player.teammatesMatchInfo:
					self.__pyListPanel.addItem( teammateID )
			if isPunish:
				print 444
				warningText = labelGather.getText( "copyteam:TeamSystem", "punish" )
				self.__punishCBID = BigWorld.callback( 1.0, self.__flashPunishTime )
			self.__pyRtWarning.text = warningText
		self.visible = not self.visible
				
	def __flashMyCDTime( self ):
		"""
		刷新自己的15分钟冷却时间
		"""
		player = BigWorld.player()
		time = player.timeTillCooldown()
		if time >0:
			mins = time/60
			secds = time%60
			timeText = ""
			if mins:
				if secds:
					timeText = labelGather.getText("copyteam:TeamSystem","minsAndsecs")%( mins, secds )
				else:
					timeText = labelGather.getText("copyteam:TeamSystem","minus")%mins
			else:
				timeText = labelGather.getText("copyteam:TeamSystem","secds")%secds
			self.__myCDCBID = BigWorld.callback( 1.0, self.__flashMyCDTime )
		else:
			BigWorld.cancelCallback( self.__myCDCBID )
			self.__myCDCBID = 0
			timeText = labelGather.getText("copyteam:TeamSystem","ready")
		self.__pyRtTime.text = timeText
	
	def __flashTeamCDStatus( self ):
		if not self.__isTeamCooldown():
			player = BigWorld.player()
			BigWorld.cancelCallback( self.__teamCDID )
			self.__teamCDID = 0
			self.__pyTVCopys.visible = True
			self.__pyInfoPanel.visible = False
			isCanEnter = not player.isInTeam() or player.isCaptain()
			for pyTypeNode in self.__pyTypeNodes.values():
				pyTypeNode.enable = isCanEnter
				pyTypeNode.setEnterStatus()
				for pyNode in pyTypeNode.pyNodes:
					if hasattr( pyNode, "copyLabel" ):
						pyNode.checked = False
						pyNode.setEnterStatus()
		else:
			self.__teamCDID = BigWorld.callback( 1.0, self.__flashTeamCDStatus )
	
	def __flashPunishTime( self ):
		"""
		刷新惩罚buff状态时间
		"""
		pass
		
	def __isTeamCooldown( self ):
		"""
		获取队伍全部冷却状态,包括角色自己
		"""
		player = BigWorld.player()
		isMateCooldown = False							#队友是否cooldown状态
		for teammateID in player.teammatesMatchInfo:
			if not player.teammateIsCooldown( teammateID ):
				isMateCooldown = True
				break
		return  isMateCooldown or not player.matchIsCooldown()
		
	def __onCopyMatchStatusChange( self, oldStatus, newStatus ):
		"""
		副本组队状态改变
		"""
		player = BigWorld.player()
		if newStatus == csdefine.MATCH_STATUS_PERSONAL_NORMAL: #切换到普通状态
			for pyTypeNode in self.__pyTypeNodes.values():
				pyTypeNode.enable = not player.isInTeam() or player.isCaptain()
	
	def __onChangeSelectingDutyStatus( self, selectedCopies ) :
		"""
		切换到职责选择状态
		"""
		# 切换按钮“关闭”到“放弃”
		self.__pyBtnAbandon.visible = True
		self.__pyBtnClose.visible = False
		# 清空已勾选的职责
		for checkBox in self.__pyPosts.values() :
			checkBox.checked = False
		# 设置所有副本不可见
		self.__setAllCopiesVisible( False )
		# 设置被选中的副本可见
		self.__setSelectedCopiesVisibleTrue( selectedCopies )
		if not self.visible :
			self.show()


	def __onCancelSelectingDutyStatus( self ) :
		"""
		撤销职责选择状态
		"""
		# 切换按钮“放弃”到“关闭”
		self.__pyBtnAbandon.visible = False
		self.__pyBtnClose.visible = True
		# 设置所有副本可见
		self.__setAllCopiesVisible( True )
		self.__restoreChangedPyNodes()
		if self.visible :
			self.hide()

	
	def __setAllCopiesVisible( self, visible ) :
		"""
		设置所有副本的可见性
		"""
		twoTypeNodes = ( self.__pyTypeNodes[CONTINUED_COPY_TYPE], self.__pyTypeNodes[TIMING_COPY_TYPE] )
		for pyTypeNode in twoTypeNodes :
			pyTypeNode.visible = visible
			for pyNode in pyTypeNode.pyNodes:
				pyNode.visible = visible
				if hasattr( pyNode, "copyLabel" ) :
					pyNode.visible = visible
				else:
					for subNode in pyNode.pyNodes:
						subNode.visible = visible

	
	def __setSelectedCopiesVisibleTrue( self, selectedCopies ) :
		"""
		设置被选中副本为打钩可见,但不可勾选
		"""
		twoTypeNodes = ( self.__pyTypeNodes[CONTINUED_COPY_TYPE], self.__pyTypeNodes[TIMING_COPY_TYPE] )
		for typeNode in twoTypeNodes :
			for pyNode in typeNode.pyNodes :
				if hasattr( pyNode, "copyLabel" ) :
					if pyNode.copyLabel in selectedCopies :
						typeNode.extend()
						typeNode.enable = False
						typeNode.visible = True
						self.__changedPyNodes['typeNodes'].append( typeNode )
						pyNode.checked = True
						pyNode.enable = False
						pyNode.visible = True
						self.__changedPyNodes['copyNodes'].append( pyNode )
				else :
					for copyNode in pyNode.pyNodes :
						if copyNode.copyLabel in selectedCopies :
							typeNode.extend()
							typeNode.enable = False
							typeNode.visible = True
							self.__changedPyNodes['typeNodes'].append( typeNode )
							pyNode.extend()
							pyNode.enable = False
							pyNode.visible = True
							self.__changedPyNodes['typeNodes'].append( pyNode )
							copyNode.checked = True
							copyNode.enable = False
							copyNode.visible = True
							self.__changedPyNodes['copyNodes'].append( copyNode )

	def __restoreChangedPyNodes( self ) :
		"""
		恢复职责选择状态下的改动，在撤销职责选择时调用
		"""
		for typeNode in self.__changedPyNodes['typeNodes'] :
			typeNode.enable = True
			typeNode.collapse()
		self.__changedPyNodes['typeNodes'] = []
		
		for copyNode in self.__changedPyNodes['copyNodes'] :
			copyNode.enable = True
			copyNode.checked = False
		self.__changedPyNodes['copyNodes'] = []

	
	def __onCopyNodeChecked( self, checked ):
		"""
		选择副本节点的回调
		"""
		copies = self.__getCheckCopies()
		duties = self.__getCheckDuties()
		player = BigWorld.player()
		matchStatus = player.matchStatus
		if not player.isInTeam() or player.isCaptain():
			self.__pyBtnInjoy.enable = len( copies ) and len( duties )
		else:
			self.__pyBtnInjoy.enable = len( duties ) > 0 and \
			matchStatus == csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY
	
	def __onTeammateLeave( self, teammateID ):
		"""
		队友离队
		"""
		player = BigWorld.player()
		for item in self.__pyListPanel.items:
			if item == teammateID:
				self.__pyListPanel.removeItem( item )
		if not player.isCaptain(): return
		if not player.insideMatchedCopy:return
		self.__pyInfoPanel.visible = True
		self.__pyBtnsPanel.visible = True
		copyName = player.labelOfMatchedCopy
		if player.getSpaceLabel() == player.labelOfMatchedCopy:
			copyName = player.getCurrWholeArea().name
		leaveWarn = labelGather.getText( "copyteam:TeamSystem", "leaveWarn" )%copyName
		self.__pyRtWarning.text = leaveWarn
		self.show()
	
	def __onTeammateJion( self, teammateID ):
		"""
		队友进队
		"""
		pass
	
	def __onTeammateLogOut( self ):
		"""
		队友下线
		"""
		pass
	
	def __onTeamDisbanded( self ):
		"""
		队伍解散
		"""
		for pyViewItem in self.__pyListPanel.pyViewItems:
			pyMateStatus = pyViewItem.pyItem
			pyMateStatus.cancelStatus()
		self.__pyListPanel.clearItems()
	
	def __onCopyNodeSelected( self, pyNode ):
		"""
		选取树节点
		"""
		if pyNode is None:return
	
	def __onRecruit( self, pyBtn ):
		"""
		招募队员
		"""
		if pyBtn is None:return
		teamID = BigWorld.player().teamID
		camp = BigWorld.player().getCamp()
		BigWorld.player().resumeHaltedRaid( teamID, camp )
	
	def __onHide( self, pyBtn ):
		"""
		隐藏
		"""
		self.hide()
	
	def __onCaptainCheck( self, checked ):
		"""
		是否为副本指引人
		"""
		self.__isCopyGuider = checked
	
	def __onPostChange( self, checked ):
		"""
		职务选择
		"""
		copies = self.__getCheckCopies()
		duties = self.__getCheckDuties()
		player = BigWorld.player()
		matchStatus = player.matchStatus
		if not player.isInTeam() or player.isCaptain():
			self.__pyBtnInjoy.enable = len( copies ) and len( duties )
		else:
			self.__pyBtnInjoy.enable = len( duties ) > 0 and \
			matchStatus == csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY
	
	def __getCheckDuties( self ):
		duties = set()
		for postTag, pyPost in self.__pyPosts.items():
			if pyPost.checked:
				duties.add( postTag )
		return duties
		
	def __onInjoyTeam( self, pyBtn ):
		"""
		进入队伍匹配
		"""
		if pyBtn is None:return
		player = BigWorld.player()
		copies = self.__getCheckCopies()
		duties = self.__getCheckDuties()
		isCanReqEnter = not player.isInTeam() or player.isCaptain()
		if len( duties ) <= 0:
			showMessage( mbmsgs[0x0f11], "", MB_OK, None, self )
			return
		if len( copies ) <= 0 and isCanReqEnter:
			showMessage( mbmsgs[0x0f12], "", MB_OK, None, self )
			return
		if isCanReqEnter:
			player.requestEnterCopyMatcherQueue( tuple( duties ), tuple( copies ), player.getCamp(), self.__isCopyGuider )
		else:
			player.selectDutiesOf( tuple( duties ), self.__isCopyGuider )
		self.hide()
		
	
	def __onCloseWnd( self, pyBtn ):
		"""
		关闭窗口
		"""
		self.hide()
	
	def __onAbandon( self, pyBtn ):
		"""
		放弃窗口
		"""
		self.__pyBtnAbandon.visible = False
		self.__pyBtnClose.visible = True
		BigWorld.player().refuseToUndertakeAnyDuty()
		self.hide()
	
	def __onShowPostDsp( self, pyPost ):
		"""
		显示职务说明
		"""
		player = BigWorld.player()
		if pyPost is None:return
		postTag = pyPost.postTag
		postInfo = labelGather.getText( "copyteam:TeamSystem", "post_%d"%postTag )
		if postTag != 0:
			pClass = player.getClass()
			fitDuties = csconst.CLASS_TO_COPY_DUTIES.get( pClass, () )
			if not postTag in fitDuties:
				postInfo += labelGather.getText( "copyteam:TeamSystem", "noFit" )
		toolbox.infoTip.showToolTips( self, postInfo )

	def __onHidePostDsp( self ):
		"""
		隐藏职务说明
		"""
		toolbox.infoTip.hide()
	
	def __getCheckCopies( self ):
		copies = set()
		for pyTypeNode in self.__pyTypeNodes.values():
			for pyNode in pyTypeNode.pyNodes:
				if hasattr( pyNode, "copyLabel" ):
					if not pyNode.checked:continue
					copies.add( pyNode.copyLabel )
				else:
					for subNode in pyNode.pyNodes:
						if not subNode.checked:continue
						copies.add( subNode.copyLabel )
		return copies

	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
	
	def onLeaveWorld( self ):
		for pyTypeNode in self.__pyTypeNodes.values():
			pyTypeNode.checked = False
		self.__pyCapCheck.checked = False
		for pyPost in self.__pyPosts.values():
			pyPost.checked = False
		self.hide()
	
	def onEnterWorld( self ):
		pass

	def show( self ):
		self.r_center = 0
		self.r_middle = 0
		Window.show( self )
	
	def hide( self ):
		for pyViewItem in self.__pyListPanel.pyViewItems:
			pyMateStatus = pyViewItem.pyItem
			pyMateStatus.cancelStatus()
		self.__pyListPanel.clearItems()
		self.__pyCapCheck.checked = False
		self.__pyPosts[csdefine.COPY_DUTY_DPS].checked = False
		BigWorld.cancelCallback( self.__myCDCBID )
		self.__myCDCBID = 0
		BigWorld.cancelCallback( self.__teamCDID )
		self.__teamCDID = 0
		BigWorld.cancelCallback( self.__punishCBID )
		self.__punishCBID = 0
		Window.hide( self )

# -------------------------------------------------------------------------
# 副本节点
class TypeNode( TreeNode ):
	def __init__( self, copyType ):
		node = GUI.load( "guis/general/copyteam/teamsystem/typenode.gui")
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node )
		self.autoWidth = False
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.__copyType = copyType
		self.__copies = {}				#子副本
		self.__pyChecker = CheckBoxEx( node.checker )
		self.__pyChecker.onCheckChanged.bind( self.__onCheck )
		self.__pyLock = PyGUI( node.lock )
		self.__pyLock.visible = False		
		self.minLevel = 0

	def dispose( self ):
		TreeNode.dispose( self )
	
	def __onCheck( self, checked ):
		"""
		选取全部可以进入的副本
		"""
		oncheck = True
		for pyCopyNode in self.pyNodes:
			pyCopyNode.checked = pyCopyNode.isCanEnter() and checked
		for pyCopyNode in self.pyNodes:	
			if not pyCopyNode.checked:
				oncheck = False
		if oncheck and hasattr( self.pyParentNode, "CONTINUED_COPY_TYPE" or "TIMING_COPY_TYPE"):
			self.pyParentNode.checked = checked 
	# ------------------------------------------------
	# public
	# ------------------------------------------------
	def addCopy( self, copy ):
		"""
		增加子副本节点
		"""
		if copy is None:return
	
	def isCanEnter( self ):
		canEnter = False
		if self.minLevel > 0:
			for pySubNode in self.pyNodes:
				if pySubNode.isCanEnter():
					canEnter = True
					break
		return canEnter

	def setEnterStatus( self ):
		"""
		设置锁的状态
		"""
		isCanEnter = False
		for pyCopyNode in self.pyNodes:
			if pyCopyNode.isCanEnter():
				isCanEnter = True
		self.__pyChecker.enable = isCanEnter
		self.__pyLock.visible = not isCanEnter
		if not isCanEnter:
			util.setGuiState( self.__pyLock.getGui(), ( 1, 2 ), ( 1, 2 ) )

	
	def onSubNodeChecked( self, checked ):
		checkNum = len( [pySubNode for pySubNode in self.pyNodes if (pySubNode.checked or (not pySubNode.isCanEnter()))] )
		self.__pyChecker.txelems["checker"].visible = checkNum >= len( self.pyNodes )

	#	 ---------------------------------------------
	#	 property methods
	#	 ---------------------------------------------
	def _setForeColor( self, color ) : #根据类型决定颜色
		TreeNode._setForeColor( self, color )

	def _getForeColor( self ):
		return TreeNode._getForeColor( self )

	def _setCopyType( self, copyType ):
		self.__copyType = copyType

	def _getCopyType( self ):
		return self.__copyType
	
	def _getChecked( self ):
		return self.__pyChecker.checked
	
	def _setChecked( self, checked ):
		self.__pyChecker.checked = checked

	foreColor = property( _getForeColor, _setForeColor )
	copyType = property( _getCopyType, _setCopyType )
	checked = property( _getChecked, _setChecked )

# -----------------------------------------------------------------------
# 副本节点
# -----------------------------------------------------------------------
class CopyNode( TreeNode ):
	def __init__( self, copySummary, mode ):
		node = GUI.load( "guis/general/copyteam/teamsystem/copynode.gui")
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node )
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.__copyInfo = None
		self.__isChecked = False
		self.mode = mode
		self.showPlusMinus = False
		self.__pyChecker = CheckBoxEx( node.checker )
		self.__pyChecker.onCheckChanged.bind( self.__onCheck )

		self.__pyStLevel = StaticText( node.node.stLevel )
		self.__pyStLevel.text = ""

		self.__pyLock = PyGUI( node.lock )
		self.__pyLock.visible = False
		self.minLevel = copySummary["minEnterLevel"]
		self.copyFlag =  copySummary["copyFlag"]
		self.copyLabel =  copySummary["copyLabel"]
		self.consumedFlag = copySummary["consumedFlag"]
		self.copySummary = copySummary
		self.__limits = { "flagLimit":[],"lvLimit":[]}
		self.__timeLimit = True
		self.__triggers = {}
		self.__registerTriggers()

	def dispose( self ):
		TreeNode.dispose( self )

	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		for eventMacro in self.__triggers :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers :
			ECenter.unregisterEvent( eventMacro, self )
	
	def __onCheck( self, checked ):
		"""
		是否被选中
		"""
		self.__isChecked = checked
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_COPYNODE_CHECKED", checked )
		self.pyParentNode.onSubNodeChecked( checked )
		if isinstance( self.pyParentNode.pyParentNode, TypeNode ):
			self.pyParentNode.pyParentNode.onSubNodeChecked( checked )
				
	def onMouseEnter__( self ):
		"""
		不能进入的副本，显示原因
		"""
		TreeNode.onMouseEnter__( self )
		if self.isCanEnter():return
		player = BigWorld.player()
		warnText = ""
		if not self.__timeLimit:
			warnText = labelGather.getText("copyteam:TeamSystem", "timeLimit")
		flagLimits = self.__limits["flagLimit"]
		lvLimits = self.__limits["lvLimit"]
		lvLimit = len( lvLimits ) <= 0 and player.level >= self.minLevel
		if not lvLimit:
			warnText = labelGather.getText("copyteam:TeamSystem", "selfLvLimit") + PL_NewLine.getSource()
		flagLimit = len( self.__limits["flagLimit"] ) <= 0 and \
		not ( player.activityFlags& ( 1 << self.consumedFlag ) )
		if not flagLimit:
			warnText = labelGather.getText("copyteam:TeamSystem", "selfFlagLimit")%self.copySummary["copyName"] + PL_NewLine.getSource()
		if len( flagLimits ): #队员有副本标记
			wText = ""
			for teammateID in flagLimits:
				teammate = player.teamMember.get( teammateID, None )
				if teammate is None:continue
				wText += labelGather.getText( "copyteam:TeamSystem", "flagLimit" )%( teammate.name,self.copySummary["copyName"] ) + PL_NewLine.getSource()
			warnText += wText
		if len( lvLimits ):
			wText = ""
			for teammateID in lvLimits:
				teammate = player.teamMember.get( teammateID, None )
				if teammate is None:continue
				wText += labelGather.getText( "copyteam:TeamSystem", "lvLimit" )%teammate.name + PL_NewLine.getSource()
			warnText += wText
		toolbox.infoTip.showToolTips( self, warnText )
		return True
	
	def setEnterStatus( self ):
		"""
		设置锁的状态
		"""
		isCanEnter = self.isCanEnter()
		self.__pyChecker.enable = isCanEnter
		self.__pyLock.visible = not isCanEnter
		if not isCanEnter:
			util.setGuiState( self.__pyLock.getGui(), ( 1, 2 ), ( 1, 2 ) )
	
	def isCanEnter( self ):
		"""
		获取玩家状态
		"""
		player = BigWorld.player()
		sevTime = Time.localtime()
		curDate = sevTime[6]
		curHour = sevTime[3]
		curMin = sevTime[4]/60.0
		curTime = curHour + curMin
		self.__limits = { "flagLimit":[],"lvLimit":[] }
		for teammateID in player.teammatesMatchInfo:
			teamMember = player.teamMember.get( teammateID, None )
			if teamMember is None:continue
			if teamMember.level < self.minLevel:
				if teammateID in self.__limits["lvLimit"]:continue
				self.__limits["lvLimit"].append( teammateID )
		lvLimit = len( self.__limits["lvLimit"] ) <= 0 and player.level >= self.minLevel
		flagLimit = True
		for teammateID in player.teammatesMatchInfo:	#判断队友身上标记
			if player.teammateHasConsumedAct( teammateID, self.consumedFlag ):
				if teammateID in self.__limits["flagLimit"]:continue
				self.__limits["flagLimit"].append( teammateID )
		flagLimit = len( self.__limits["flagLimit"] ) <= 0 and \
			not ( player.activityFlags& ( 1 << self.consumedFlag ) )	
		durations = { "time1":self.copySummary["time1"], "time2":self.copySummary["time2"], "time3":self.copySummary["time3"] }	
		if self.copySummary["unit"] == "week" or self.copySummary["unit"] == "day" :  #定时开启的副本
			if self.copySummary["unit"] == "week" :  #每周某天进行
				if self.copySummary["day"] - 1 == curDate:
					self.__timeLimit = True
				else:
					self.__timeLimit = False
			else: #每天进行
				self.__timeLimit = self._timeCheck( durations, curTime )	
		return lvLimit and self.__timeLimit and flagLimit

	
	def _timeCheck( self, durations, curTime ):
		"""
		timeCheck 表示是否在开放时间段内，True表示是，False表示不在开放时间段内
		"""
		if durations["time1"] == durations["time2"] == durations["time3"] == "" :  #没有指定开放时间，则认为全天开放
			return True			
		for duration in durations.values():
			if duration == "":continue
			periods = duration.split( "-" )
			durats = []  #len(periods) == 2
			for period in periods:
				times = period.split( ":" )
				hour = int( times[0] )
				mins = int( times[1] )/60.0
				time = hour + mins
				durats.append(time)
			if curTime >= durats[0] and curTime <= durats[1]:
				return True
		return False
		
			
	def _getChecked( self ):
		return self.__isChecked
	
	def _setChecked( self, checked ):
		self.__pyChecker.checked = checked

	checked = property( _getChecked, _setChecked )

# ---------------------------------------------------------------------------------------
class MateStatus( PyGUI ):
	"""
	队员状态信息条
	"""
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyRtName = CSRichText( item.rtName )
		self.__pyRtName.align = "C"
		self.__pyRtName.text = ""
		
		self.__pyRtStatus = CSRichText( item.rtStatus )
		self.__pyRtStatus.align = "C"
		self.__pyRtStatus.text = ""
		
		self.__statusCBID = 0
	
	def setStatus( self, pyViewItem ):
		if pyViewItem is None:return
		player = BigWorld.player()
		teammateID = pyViewItem.listItem
		teamMember = player.teamMember.get( teammateID, None )
		if teamMember is None:return
		self.__pyRtName.text = teamMember.getName()
		self.__statusCBID = BigWorld.callback( 0.0, Functor( self.__flashMatchStatus, teammateID ) )
		
	def __flashMatchStatus( self, teammateID ):
		"""
		刷新状态
		"""
		player = BigWorld.player()
		statusText = ""
		self.cancelStatus()
		if not player.teammateIsCooldown( teammateID ):		#冷却状态
			statusText = labelGather.getText("copyteam:TeamSystem","cooldowning")
			self.__statusCBID = BigWorld.callback( 1.0, Functor( self.__flashMatchStatus, teammateID ) )
		else:
			self.cancelStatus()
			statusText = labelGather.getText("copyteam:TeamSystem","ready")
		self.__pyRtStatus.text = statusText
	
	def cancelStatus( self ):
		BigWorld.cancelCallback( self.__statusCBID )
		self.__statusCBID = 0
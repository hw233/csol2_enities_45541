# -*- coding: gb18030 -*-
#
# $Id: TeamSystem.py

"""
implement quest list class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather
from AbstractTemplates import Singleton
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.StaticText import StaticText
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.TreeView import TreeNode
from guis.tooluis.CSRichText import CSRichText
import csdefine
import GUIFacade

class RandomTeamNotify( Singleton, Window ):
	"""
	����ƥ��ȷ�ϴ���
	"""
	__instance = None
	
	def __init__( self, wnd = None ):
		if wnd is None:
			wnd = GUI.load( "guis/general/copyteam/fixedteam.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = False
		self.h_dockStyle = "CENTER"							# ˮƽ������ʾ
		self.v_dockStyle = "MIDDLE"							# ��ֱ������ʾ
		self.__initialize( wnd )
		self.triggers_ = {}
		self.registerTriggers_()
	
	def __initialize( self, wnd ):
		self.pyRtPost_ = CSRichText( wnd.rtPost )
		self.pyRtPost_.text = ""
		self.pyRtPost_.align = "C"
		
		self.pyBtnEnter_ = HButtonEx( wnd.btnEnter )
		self.pyBtnEnter_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnEnter_, "copyteam:TeamConfirm", "enterCopy" )
		self.pyBtnEnter_.onLClick.bind( self.onEnterCopy_ )
	
		self.pyBtnLeave_ = HButtonEx( wnd.btnLeave )
		self.pyBtnLeave_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnLeave_, "copyteam:TeamConfirm", "leaveCopy" )
		self.pyBtnLeave_.onLClick.bind( self.onLeaveCopy_ )
		
		self.pyPostIcon_ = PyGUI( wnd.postIcon.icon )
		
		self.pyCaptain_ = PyGUI( wnd.postIcon.captain )
		self.pyCaptain_.visible = False
	
		labelGather.setPyLabel( self.pyLbTitle_, "copyteam:TeamConfirm", "title_random" )
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_NOTIFY_CONFIRM_COPYMATCHED"] = self.__onNotifyConfirm
		for key in self.triggers_ :
			GUIFacade.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		for key in self.triggers_ :
			GUIFacade.unregisterEvent( key, self )
	# --------------------------------------------------------------
	def __onNotifyConfirm( self, duty, copyLabel, copyLevel, bossesTotal, bossesKilled ):
		"""
		ְ��ȷ��
		"""
		pass
		
	def onEnterCopy_( self, pyEnter ):
		"""
		���븱��
		"""
		pass
	
	def onLeaveCopy_( self, pyLeave ):
		"""
		�뿪����
		"""
		pass

	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.triggers_[macroName]( *args )
	
	def show( self ):
		self.r_center = 0
		self.r_middle = 0
		Window.show( self )
	
	def hide( self ):
		Window.hide( self )
	
# -------------------------------------------------------------------------------
class FixedTeamNotify( RandomTeamNotify ):
	"""
	�̶�����
	"""
	_duties_map = { csdefine.COPY_DUTY_MT: ( labelGather.getText( "copyteam:TeamConfirm", "tank" ),(1,2) ),
					csdefine.COPY_DUTY_HEALER: ( labelGather.getText( "copyteam:TeamConfirm", "nurse" ),(2,1) ),
					csdefine.COPY_DUTY_DPS: ( labelGather.getText( "copyteam:TeamConfirm", "dps" ),(2,2) ),
			}
	def __init__( self ):
		wnd = GUI.load( "guis/general/copyteam/fixedteam.gui" )
		uiFixer.firstLoadFix( wnd )
		RandomTeamNotify.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = False
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.pyBtnEnter_.onLClick.bind( self.onEnterCopy_ )
		
		self.pyBtnLeave_.onLClick.bind( self.onLeaveCopy_ )
		
		self.__pyRtCopyInfo = CSRichText( wnd.rtCopyInfo )
		self.__pyRtCopyInfo.text = ""
		self.__pyRtCopyInfo.align = "C"
		
		self.__pyRtBossInfo = CSRichText( wnd.rtBossInfo )
		self.__pyRtBossInfo.text = ""
		self.__pyRtBossInfo.align = "C"
		
		labelGather.setPyLabel( self.pyLbTitle_, "copyteam:TeamConfirm", "title_fixed" )
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_COPYMATCHER_NOTIFY_CONFIRM"] = self.__onNotifyConfirm
		self.triggers_["EVT_ON_COPYMATCHER_CONFIRM_TIMEOUT"] = self.__onConfirmTimeOut
		self.triggers_["EVT_ON_COPYMATCHER_RECEIVE_MATCHED_INFO"] = self.__onRecMatchInfo
		RandomTeamNotify.registerTriggers_( self )

	def deregisterTriggers_( self ) :
		RandomTeamNotify.deregisterTriggers_( self )
	# --------------------------------------------------------------
	
	def __onNotifyConfirm( self, duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies ):
		"""
		����ȷ����Ϣ
		������Ҫ���3����5�˸��������������3�ˣ��͵���3�˵ģ�5�˵ľ͵���5�˵ģ�
		����len(copies)�ж���ָ����������δ֪����
		"""
		copyFormulas = rds.spaceCopyFormulas
		copiesSummary = copyFormulas.getCopiesSummary()
		
		dutyInfo = self._duties_map.get( duty )
		if dutyInfo is None:return
		postInfo = labelGather.getText( "copyteam:TeamConfirm", "duty" )%dutyInfo[0]
		util.setGuiState( self.pyPostIcon_.getGui(),(2,2),dutyInfo[1] )
		self.pyRtPost_.text = postInfo
		summary = copiesSummary.get( copyLabel, None )
		copyName = labelGather.getText( "copyteam:TeamConfirm", "unkownCopy" )
		if summary and len( copies ) == 1:
			copyName = labelGather.getText( "copyteam:TeamConfirm", "copyInfo" )%( summary["mode"], summary["copyName"], copyLevel )
		bosskill = labelGather.getText( "copyteam:TeamConfirm", "bosskill" )%( bossesKilled, bossesTotal )
		bossInfo = labelGather.getText( "copyteam:TeamConfirm", "bossInfo" )%bosskill
		self.__pyRtCopyInfo.text = copyName
		self.__pyRtBossInfo.text = bossInfo
		self.show()
	
	def __onConfirmTimeOut( self ):
		"""
		ȷ�ϳ�ʱ
		"""
		self.hide()
	
	def __onRecMatchInfo( self, matchInfo, copyLabelNum ):
		"""
		ƥ����Ϣ
		"""
		self.hide()

	def onEnterCopy_( self, pyEnter ):
		"""
		ȷ�Ͻ��븱��
		"""
		if pyEnter is None:return
		BigWorld.player().confirmCopyMatched( True )
		self.hide()
	
	def onLeaveCopy_( self, pyLeave ):
		"""
		�뿪����
		"""
		if pyLeave is None:return
		BigWorld.player().confirmCopyMatched( False )
		self.hide()
		
	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.triggers_[macroName]( *args )
	
	def show( self ):
		"""
		��ʾ
		"""
		RandomTeamNotify.show( self )
	
	def hide( self ):
		"""
		����
		"""
		RandomTeamNotify.hide( self )
	
	def onLeaveWorld( self ):
		"""
		�뿪��Ϸ����
		"""
		self.hide()
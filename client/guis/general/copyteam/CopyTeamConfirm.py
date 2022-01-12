# -*- coding: gb18030 -*-
#
# $Id: TeamConfirm.py

"""
implement quest list class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather
from AbstractTemplates import Singleton
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.Icon import Icon
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.RichText import RichText
import csdefine

class CopyTeamConfirm( Singleton, Window ):
	"""
	��λȷ�ϴ���
	"""
	__triggers = {}
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/copyteam/teamconfirm.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True
		self.h_dockStyle = "CENTER"							# ˮƽ������ʾ
		self.v_dockStyle = "MIDDLE"							# ��ֱ������ʾ
		self.__matchInfos = []
		self.__needconfirmlen = 0							# ��Ҫȷ�ϵ�����
		self.__initialize( wnd )
		self.addToMgr( "copyTeamConfirm" )
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ):
		self.__pyPosts = {}
		for name, item in wnd.children:
			if not name.startswith( "post_" ):continue
			postTag = int( name.split( "_" )[1] )
			pyPost = ConfirmPost( item )
			if postTag == csdefine.COPY_DUTY_DPS:
				index = int( name.split( "_" )[-1] )
				if self.__pyPosts.has_key( postTag ):
					self.__pyPosts[postTag][index] = pyPost
				else:
					self.__pyPosts[postTag] = {index:pyPost}
			else:
				self.__pyPosts[postTag] = pyPost
		labelGather.setPyLabel( self.pyLbTitle_, "copyteam:TeamMatch", "title_confirm" )

	# ----------------------------------------------------------------
	@classmethod
	def __onRecMatchedInfo( SELF, infos, copyLabelNum ):
		"""
		����ְ��ȷ����Ϣ����ʾ��,3�˵ľ�������self.__pyPosts[postTag]��1��3�������������ر���
		"""
		self = SELF.inst
		index = 0
		self.__matchInfos = infos
		self.__pyPosts[csdefine.COPY_DUTY_DPS][1].visible = (not (copyLabelNum == 3))
		self.__pyPosts[csdefine.COPY_DUTY_DPS][3].visible = (not (copyLabelNum == 3))	
		pyPosts = self.__pyPosts[csdefine.COPY_DUTY_DPS]
		for (memberID, confirm) in infos:
			pyPost = pyPosts.get( index )
			if pyPost is None:continue
			pyPost.setConfirm( memberID, confirm )
			if copyLabelNum == 3:
				index += 2
			elif copyLabelNum == 5:
				index += 1
			else:
				print "ERROR!No this copy with copyLabelNum = ",copyLabelNum
		self.show()	
		if len( infos ) == self.__needconfirmlen:
			self.__matchInfos = []
			self.hide()			
				
	@classmethod
	def __onUpdateConfirmInfo( SELF, teammateID, lenConfirms, infos, copyLabelNum ):
		"""
		����ְ��ȷ����Ϣ,3�˵ľ�������self.__pyPosts[postTag]��1��3�������������ر���
		"""
		"""
		self = SELF.inst
		self.__needconfirmlen = lenConfirms
		self.__matchInfos = confirms
		pyPosts = self.__pyPosts[csdefine.COPY_DUTY_DPS]
		self.__pyPosts[csdefine.COPY_DUTY_DPS][1].visible = (not (copyLabelNum == 3))
		self.__pyPosts[csdefine.COPY_DUTY_DPS][3].visible = (not (copyLabelNum == 3))
		#self.__matchInfos.keys() = [matchinfo[0] for matchinfo in self.__matchInfos]
		#self.__matchInfos.values() = [matchinfo[1] for matchinfo in self.__matchInfos]
		#confirms[teammateID] = confirms[L.index(teammateID)][1]
		L = [matchinfo[0] for matchinfo in self.__matchInfos]
		if teammateID in L:
			for index, pyPost in pyPosts.items():
				if copyLabelNum == 3 and (index == (1 or 3)):continue
				if pyPost.teammateID == teammateID:			
					pyPost.updateConfirm( confirms[L.index(teammateID)][1] )
		else:
			for index, pyPost in pyPosts.items():
				if copyLabelNum == 3 and (index == (1 or 3)):continue
				#if pyPost.teammateID > 0:continue
				pyPost.setConfirm( teammateID, confirms[L.index(teammateID)][1] )
				break
		if len( confirms ) == lenConfirms:
			self.__matchInfos = []
			self.hide()
		"""
		self = SELF.inst
		index = 0
		self.__needconfirmlen = lenConfirms
		self.__matchInfos = infos
		self.__pyPosts[csdefine.COPY_DUTY_DPS][1].visible = (not (copyLabelNum == 3))
		self.__pyPosts[csdefine.COPY_DUTY_DPS][3].visible = (not (copyLabelNum == 3))	
		pyPosts = self.__pyPosts[csdefine.COPY_DUTY_DPS]
		for (memberID, confirm) in infos:
			pyPost = pyPosts.get( index )
			if pyPost is None:continue
			pyPost.setConfirm( memberID, confirm )
			if copyLabelNum == 3:
				index += 2
			elif copyLabelNum == 5:
				index += 1
			else:
				print "ERROR!No this copy with copyLabelNum = ",copyLabelNum
	

	@classmethod
	def __onShowTeamConfirm( SELF ):
		"""
		��ʾ���
		"""
		self = SELF.inst
		index = 0
		pyPosts = self.__pyPosts[csdefine.COPY_DUTY_DPS]
		for (memberID, confirm) in self.__matchInfos:
			pyPost = pyPosts.get( index )
			#if pyPost is None:continue
			pyPost.setConfirm( memberID, confirm )
			index += 1
		self.show()
		
	@classmethod
	def __onInsideCopyChange( SELF, oldValue, newValue ):
		"""
		���븱�����������
		"""
		self = SELF.inst
		if not oldValue and newValue:
			pyPosts = self.__pyPosts[csdefine.COPY_DUTY_DPS]
			for index, pyPost in pyPosts.items():			#���ȷ����Ϣ
				pyPost.setConfirm( 0, csdefine.MATCHED_CONFIRM_STATUS_PENDING )
			self.__matchInfos = []
			self.hide()
	
	@classmethod
	def __hide(SELF):
		self = SELF.inst
		self.hide()
	
	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_TOGGLE_TEAMCOPY_CONFIRMING_WND"] = SELF.__onShowTeamConfirm
		SELF.__triggers["EVT_ON_COPYMATCHER_RECEIVE_MATCHED_INFO"] = SELF.__onRecMatchedInfo
		SELF.__triggers["EVT_ON_COPYMATCHER_UPDATE_CONFIRM_INFO"] = SELF.__onUpdateConfirmInfo
		SELF.__triggers["EVT_ON_COPYMATCHER_INSIDECOPY_CHANGE"] 	= SELF.__onInsideCopyChange
		SELF.__triggers["EVT_ON_COPYMATCHER_HIDE_WINDOW"] = SELF.__hide
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )
	
	def show( self ):
		"""
		��ʾ
		"""
		self.r_center = 0
		self.r_middle = 0
		Window.show( self )
			
	def hide( self ):
		"""
		����
		"""
		self.__matchInfos = []
		pyPosts = self.__pyPosts[csdefine.COPY_DUTY_DPS]
		for index, pyPost in pyPosts.items():			#���ȷ����Ϣ
			pyPost.setConfirm( 0, csdefine.MATCHED_CONFIRM_STATUS_PENDING )
		Window.hide( self )
		
	
	def onLeaveWorld( self ):
		self.__matchInfos = []
		self.hide()

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

CopyTeamConfirm.registerTriggers()

# --------------------------------------------------------------------------------
class ConfirmPost( Control ):
	"""
	ְ��ȷ��
	"""
	_confirm_mappings = { csdefine.MATCHED_CONFIRM_STATUS_ACCEPT: (1,1),
				csdefine.MATCHED_CONFIRM_STATUS_ABANDON: (1,2),
				csdefine.MATCHED_CONFIRM_STATUS_PENDING: (1,3),
			}
	def __init__( self, item ):
		Control.__init__( self, item )
		self.__pyConfirm = PyGUI( item.confirm )
		self.__teammateID = 0
		util.setGuiState( self.__pyConfirm.getGui(),( 1, 3 ),( 1, 3 ) )
	
	def setConfirm( self, playerID, confirm ):
		"""
		����ȷ�ϱ�־
		"""
		self.__teammateID = playerID
		mapping = self._confirm_mappings.get( confirm, (1,3) )
		util.setGuiState( self.__pyConfirm.getGui(), ( 1, 3 ), mapping )
	
	def updateConfirm( self, confirm ):
		"""
		����ȷ�ϱ�־
		"""
		mapping = self._confirm_mappings.get( confirm, (1,3) )
		util.setGuiState( self.__pyConfirm.getGui(), ( 1, 3 ), mapping )

	def _setTeammateID( self, teammateID ):
		self.__teammateID = teammateID
	
	def _getTeammate( self ):
		return self.__teammateID

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	teammateID = property( _getTeammate, _setTeammateID )
# -*- coding: gb18030 -*-
#
# $Id: MsgBox.py,v 1.9 2008-08-26 02:22:08 huangyongwei Exp $

"""
implement messagebox class
-- 2006/05/10: writen by huangyongwei
"""

import weakref
import MessageBox
from guis import *
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.FrameEx import HVFrameEx
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from AbstractTemplates import Singleton
from LabelGather import labelGather
import event.EventCenter as ECenter
from guis.OpIndicatorObj import OpIndicatorObj
import Font

class MsgBox( HVFlexExWindow ) :
	__cg_boxes		   = []									# �������е���Ϣ��
	__cg_preshow_boxes = {}									# ������ĳ��״̬�½�Ҫ��ʾ�Ĵ���
	__cg_tmphide_boxes = []									# ��תʱ����ʱ���浱ǰ������ʾ״̬�µ���Ϣ��ʾ��

	__cc_text_spacing		= 4

	def __init__( self, box ) :
		HVFlexExWindow.__init__( self, box )
		self.__initialize( box )							# ��ʼ��
		self.posZSegment = ZSegs.L2							# ����Ĭ��Ϊ�ڶ���
		self.escHide_ = True								# ���԰� esc ���ر�
		self.activable_ = True								# ���Ա�����
		self.addToMgr( "messageBox" )						# ��ӵ�������
		self.h_dockStyle = "CENTER"							# ˮƽ������ʾ
		self.v_dockStyle = "MIDDLE"							# ��ֱ������ʾ
		self.minHeight_ = 151.0								# ������С�߶�

		self.__pyBinder = None
		self.__callback = None								# �ص�
		self.defRes_ = MessageBox.RS_OK						# Ĭ�Ϸ��ؽ��

		MsgBox.__cg_boxes.append( self )					# ��ӵ�ȫ���б�

	def dispose( self ) :
		"""
		release resource
		"""
		self.__pyBinder = None
		self.__callback = None										# ɾ���� callback ������
		if self in MsgBox.__cg_boxes :
			MsgBox.__cg_boxes.remove( self )						# ��ȫ���б����
		for state, pyBoxes in MsgBox.__cg_preshow_boxes.items() :	# ��Ԥ��ʾ�б���ɾ��
			pyBoxes = MsgBox.__cg_preshow_boxes[state]
			if self in pyBoxes :
				pyBoxes.remove( self )
			if len( pyBoxes ) == 0 :
				MsgBox.__cg_preshow_boxes.pop( state )
		if self in MsgBox.__cg_tmphide_boxes :
			MsgBox.__cg_tmphide_boxes.remove( self )
		HVFlexExWindow.dispose( self )


	def __del__( self ) :
		HVFlexExWindow.__del__( self )
		if Debug.output_del_MessageBox :
			INFO_MSG( str( self ) )

	# -------------------------------------------------
	def __initialize( self, box ) :
		if box is None : return
		self.__pyLbMsg = StaticText( box.lbMsg )						# ����Ϣ�ı�
		self.__pyLbMsg.text = ""
		maxWidth = box.msgPanel.width
		self.pyMsgPanel_ = CSRichText( box.msgPanel )					# ����Ϣ�ı�����
		self.pyMsgPanel_.opGBLink = True
		self.pyMsgPanel_.maxWidth = maxWidth
		self.pyMsgPanel_.font = "MSYHBD.TTF"
		self.pyMsgPanel_.fontSize = 14.0
		self.pyMsgPanel_.foreColor = ( 51, 76, 97, 255 )
		self.pyMsgPanel_.limning = Font.LIMN_NONE
		self.pyMsgPanel_.opGBLink = True
		self.pyBgPanel_ = None
		if hasattr( box, "panel" ):
			self.pyBgPanel_ = HVFrameEx( box.panel )
			self.pyBgPanel_.center = self.width/2.0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notifyCallback_( self, resultID ) :
		"""
		�ص� callback
		"""
		if self.__callback is not None :
			try :
				self.__callback( resultID )
			except :
				EXCEHOOK_MSG()

	def reposition_( self ) :
		"""
		�������ô���λ��
		"""
		self.r_center = 0
		self.r_middle = 0


	# ----------------------------------------------------------------
	# callbacks
	# ---------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		ע��������д onLeaveWorld ������������ǲ��Եģ���Ϊ MessageBox ���Ƿ��������У��޹ء�
		    ������ôд��Ϊ�˽�ɫ�˳���Ϸʱ���������ص�������
		"""
		if self.pyOwner is None :						# ����и����ڵĻ���leave world ʱ�����ᱻ������ dispose��������ﲻ��Ҫ�ٵ���һ��
			self.notifyCallback_( self.defRes_ )		# ��Ĭ�ϵ�����֪ͨ
			self.dispose()

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		����Ϸ״̬�ı�ʱ������
		@param					onStatus  : �ı�ǰ��״̬���� Define.py �ж��壩
		@param					newStatus : �ı���״̬���� Define.py �ж��壩
		"""
		if oldStatus == newStatus : return
		if newStatus == Define.GST_SPACE_LOADING :
			for pyBox in MsgBox.__cg_boxes :
				if pyBox.gui.visible :
					pyBox.gui.visible = False
					self.__cg_tmphide_boxes.append( pyBox )
		elif newStatus == Define.GST_BACKTO_ROLESELECT_LOADING:
			for pyBox in MsgBox.__cg_boxes :
				if pyBox.gui.visible :
					pyBox.gui.visible = False
		else :
			for pyBox in MsgBox.__cg_tmphide_boxes :
				pyBox.gui.visible = True

		pyBoxes = MsgBox.__cg_preshow_boxes.get( newStatus, None )
		if pyBoxes is not None :
			for pyBox in pyBoxes :
				HVFlexExWindow.show( pyBox )
			MsgBox.__cg_preshow_boxes.pop( newStatus )


	# ----------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		if pyOwner :												# ����ֻ��ʾһ����ʾ��
			for pyBox in self.__cg_boxes :
				if pyBox == self :
					continue
				if pyBox.__class__ != self.__class__ :
					continue
				if pyBox.pyBinder is None :
					continue
				if pyBox.pyBinder == pyOwner :
					pyBox.hide()
		self.title = title
		self.setMessage( msg )
		self.__callback = callback
		self.reposition_()
		if pyOwner :
			self.__pyBinder = weakref.ref( pyOwner )

		currStatus = rds.statusMgr.currStatus()
		if gstStatus is None or currStatus == gstStatus :
			HVFlexExWindow.show( self, pyOwner )
		elif gstStatus in MsgBox.__cg_preshow_boxes :
			MsgBox.__cg_preshow_boxes[gstStatus].append( self )
		else :
			MsgBox.__cg_preshow_boxes[gstStatus] = [self]

	def hide( self ) :
		"""
		���ش���
		"""
		self.notifyCallback_( self.defRes_ )			# ��Ĭ�ϵ�����֪ͨ
		self.setOkButton( None ) #add by wuxo 2012-5-17
		self.setCancelButton( None ) #add by wuxo 2012-5-17
		self.dispose()

	def setMessage( self, msg ) :
		"""
		������Ϣ�ı�
		"""
		self.pyMsgPanel_.text = msg
		lineCount = self.pyMsgPanel_.lineCount
		if lineCount == 1 :
			self.pyMsgPanel_.align = "C"
			self.pyMsgPanel_.bottom = self.height/2.0
			if self.pyBgPanel_:
				self.pyMsgPanel_.middle = self.pyBgPanel_.middle
		else:
			self.pyMsgPanel_.align = "L"
			if lineCount >= 4:
				self.pyMsgPanel_.top = 45.0
			else:
				self.pyMsgPanel_.top = 55.0
			if self.pyBgPanel_:
				disHeight = self.pyMsgPanel_.height + ( self.pyMsgPanel_.top - self.pyBgPanel_.top )*2
				if disHeight > self.pyBgPanel_.height:
					self.pyBgPanel_.height =  disHeight
				self.height =  self.pyBgPanel_.bottom + 30.0# ��Ϣ����ʱ�Զ�����������Ѿ�����minHeight_��������

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	def _setVisible( self, visible ) :
		if visible :
			HVFlexExWindow._setVisible( self, visible )
		else :
			self.hide()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )
	visible = property( HVFlexExWindow._getVisible, _setVisible )


# --------------------------------------------------------------------
# implement ok messagebox class
# --------------------------------------------------------------------
class OkBox( MsgBox ) :
	"""
	ȷ����Ϣ��
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/okbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# ok ��ť
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.hide )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"
		self.setOkButton( self.__pyOkBtn )

		self.defRes_ = MessageBox.RS_OK

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:oBox", "btnOk" )

	def dispose( self ) :
		self.__pyOkBtn.dispose()
		MsgBox.dispose( self )
	
	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyOkBtn.top = self.pyBgPanel_.bottom - 2.0

# --------------------------------------------------------------------
# implement cancel messagebox class
# --------------------------------------------------------------------
class CancelBox( MsgBox ) :
	"""
	ȡ����Ϣ��	20089-01-13 SongPeifang
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/cancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )					# cancel ��ť
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"
		self.setCancelButton( self.__pyCancelBtn )

		self.defRes_ = MessageBox.RS_CANCEL

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:cBox", "btnCancel" )

	def dispose( self ) :
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom

# --------------------------------------------------------------------
# implement special cancel messagebox class
# --------------------------------------------------------------------
class SpecialCancelBox( MsgBox ) :
	"""
	�����ȡ����Ϣ��	20089-01-13 SongPeifang
	���������Ϊ���߻�Ҫ������ʱ����һ������ȡ������
	��������������CancelBox������ȫһ����ֻ�Ǽ��ص�gui��һ��
	��������ȡ����ť�����Ҳ߻�Ҫ�������Ϣ��Ҫ�ǳ�С
	���һ�����Ϣ�����Զ����������ġ�...��
	"""
	def __init__( self ) :
		box = GUI.load( "guis/tooluis/messagebox/specialCancelBox.gui" )
		uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyCancelBtn = Button( box.cancelBtn, self )	# cancel ��ť
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.setCancelButton( self.__pyCancelBtn )
		self.defRes_ = MessageBox.RS_SPE_CANCEL

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:scBox", "btnCancel" )

	def reposition_( self ) :
		"""
		�������ô���λ��
		���õ��������������
		"""
		MsgBox.reposition_( self )
		self.r_top = -0.31
		self.r_left = -0.09

	def dispose( self ) :
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

# --------------------------------------------------------------------
# implement ok-cancel messagebox class
# --------------------------------------------------------------------
class OkCancelBox( MsgBox, OpIndicatorObj ) :
	"""
	ȷ��/ȡ����Ϣ��
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/okcancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		OpIndicatorObj.__init__( self )
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# ȷ����ť
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.onOk_ )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )			# ȡ����ť
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyOkBtn )							# ����Ĭ�ϵĻس���ť
		self.setCancelButton( self.__pyCancelBtn )					# ����Ĭ�ϵ� esc ��ť

		self.defRes_ = MessageBox.RS_CANCEL							# Ĭ�Ͻ��Ϊ cancel

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:ocBox", "btnOk" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:ocBox", "btnCancel" )
		
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","okCancelBox" )
		condition = ( "quest_uncompleted","checkNotHasVehicle" )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showIndication
	
	def __showIndication( self, idtId ):
		pyBtn = self.__pyOkBtn
		toolbox.infoTip.showHelpTips( idtId, pyBtn )
		self.addVisibleOpIdt( idtId )

	def dispose( self ) :
		self.__pyOkBtn.dispose()
		self.__pyCancelBtn.dispose()
		if hasattr(rds.ruisMgr,"okCancelBox"):
			del rds.ruisMgr.okCancelBox
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyOkBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom - 2.0
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onOk_( self ) :
		"""
		��ȷ����ť�����ʱ����
		"""
		self.notifyCallback_( MessageBox.RS_OK )
		self.dispose()
		
	def onMove_( self, dx, dy ) :
		self.relocateIndications()

# --------------------------------------------------------------------
# implement yes-no messagebox class
# --------------------------------------------------------------------
class YesNoBox( MsgBox ) :
	"""
	��/����Ϣ��
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/yesnobox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyYesBtn = HButtonEx( box.yesBtn, self )					# �� ��ť
		self.__pyYesBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyYesBtn.onLClick.bind( self.onYes_ )
		self.__pyYesBtn.v_dockStyle = "BOTTOM"
		self.setOkButton( self.__pyYesBtn )

		self.__pyNoBtn = HButtonEx( box.noBtn, self )						# �� ��ť
		self.__pyNoBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNoBtn.onLClick.bind( self.hide )
		self.__pyNoBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyYesBtn )								# ����Ĭ�ϵĻس���ť
		self.setCancelButton( self.__pyNoBtn )							# ����Ĭ�ϵ� esc ��ť

		self.defRes_ = MessageBox.RS_NO									# Ĭ�Ϸ��ؽ��Ϊ��

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyYesBtn, "MsgBox:ynBox", "btnYes" )
		labelGather.setPyBgLabel( self.__pyNoBtn, "MsgBox:ynBox", "btnNo" )

	def dispose( self ) :
		self.__pyYesBtn.dispose()
		self.__pyNoBtn.dispose()
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyYesBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyNoBtn.top = self.pyBgPanel_.bottom - 2.0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onYes_( self ) :
		"""
		�ǰ�ť�����ʱ����
		"""
		self.notifyCallback_( MessageBox.RS_YES )
		self.dispose()


# --------------------------------------------------------------------
# implement yes-no messagebox class
# --------------------------------------------------------------------
class YesNoCancelBox( MsgBox ) :
	"""
	��/��ȡ����Ϣ��
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/yesnocancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyYesBtn = HButtonEx( box.yesBtn, self )					# �� ��ť
		self.__pyYesBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyYesBtn.onLClick.bind( self.onYes_ )
		self.__pyYesBtn.v_dockStyle = "BOTTOM"
		self.setOkButton( self.__pyYesBtn )

		self.__pyNoBtn = HButtonEx( box.noBtn, self )						# �� ��ť
		self.__pyNoBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNoBtn.onLClick.bind( self.onNo_ )
		self.__pyNoBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )				# �� ��ť
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyYesBtn )								# ����Ĭ�ϵĻس���ť
		self.setCancelButton( self.__pyNoBtn )							# ����Ĭ�ϵ� esc ��ť

		self.defRes_ = MessageBox.RS_CANCEL								# Ĭ�Ͻ��Ϊȡ��

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyYesBtn, "MsgBox:yncBox", "btnYes" )
		labelGather.setPyBgLabel( self.__pyNoBtn, "MsgBox:yncBox", "btnNo" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:yncBox", "btnCancel" )

	def dispose( self ) :
		self.__pyYesBtn.dispose()
		self.__pyNoBtn.dispose()
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )


	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyYesBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyNoBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom - 2.0
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onYes_( self ) :
		"""
		�ǰ�ť�����ʱ����
		"""
		self.notifyCallback_( MessageBox.RS_YES )
		self.dispose()

	def onNo_( self ) :
		"""
		��ť�����ʱ����
		"""
		self.notifyCallback_( MessageBox.RS_NO )
		self.dispose()

# --------------------------------------------------------------------
# implement special ok-cancel messagebox class
# --------------------------------------------------------------------
class SpecialOkCancelBox( MsgBox ) :
	"""
	����ȷ��/ȡ����Ϣ����Ҫ�����ӳٴ��ͣ�
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/specialokcancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# ���̴��Ͱ�ť
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.onOk_ )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )			# ȡ�����Ͱ�ť
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyOkBtn )							# ����Ĭ�ϵĻس���ť
		self.setCancelButton( self.__pyCancelBtn )					# ����Ĭ�ϵ� esc ��ť

		self.defRes_ = MessageBox.RS_SPE_CAN						# Ĭ�Ͻ��Ϊ cancel
		player = BigWorld.player()
		self.delayTime = player.delayTeleportTime

		self.__triggers = {}
		self.__registerTriggers()

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:speOCBox", "btnOk", self.delayTime )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:speOCBox", "btnCancel" )

	def dispose( self ) :
		self.delayTime = 0
		self.__pyOkBtn.dispose()
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		��ʾ��Ϣ��
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyOkBtn.top = self.pyBgPanel_.bottom + 2.0
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom + 2.0

		BigWorld.callback( 1.0, self.delayTimeChanged_ )

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def setMessage( self, msg ) :
		"""
		������Ϣ�ı�
		"""
		self.pyMsgPanel_.text = msg
		lineCount = self.pyMsgPanel_.lineCount
		if lineCount == 1 :
			self.pyMsgPanel_.align = "C"
			self.pyMsgPanel_.bottom = self.height/2.0
			if self.pyBgPanel_:
				self.pyMsgPanel_.middle = self.pyBgPanel_.middle
		else:
			self.pyMsgPanel_.align = "L"
			if lineCount >= 4:
				self.pyMsgPanel_.top = 55.0
			else:
				self.pyMsgPanel_.top = 65.0
			if self.pyBgPanel_:
				disHeight = self.pyMsgPanel_.height + ( self.pyMsgPanel_.top - self.pyBgPanel_.top )*2
				if disHeight > self.pyBgPanel_.height:
					self.pyBgPanel_.height =  disHeight
				self.pyBgPanel_.gui.elements["light_effect"].size.y = self.pyBgPanel_.height - 2.0
				self.height =  self.pyBgPanel_.bottom +50.0# ��Ϣ����ʱ�Զ�����������Ѿ�����minHeight_��������

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		ע���¼�
		"""
		self.__triggers["EVT_ON_HIDE_SPE_OCBOX"]	 =  self.__onHide	 # ���ؽ���
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def onOk_( self ) :
		"""
		��ȷ����ť�����ʱ����
		"""
		self.notifyCallback_( MessageBox.RS_SPE_OK )
		self.dispose()

	# ----------------------------------------------------------------
	def delayTimeChanged_( self ):
		"""
		�ӳ�ʱ��ı�
		"""
		if self.delayTime < 0: return
#		if not self.visible: return
		self.delayTime -= 1
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:speOCBox", "btnOk", self.delayTime )
		BigWorld.callback( 1.0, self.delayTimeChanged_ )

	def __onHide( self ):
		"""
		���ؽ��棬�жϴ���
		"""
		if self.delayTime < 0: return
		self.hide()
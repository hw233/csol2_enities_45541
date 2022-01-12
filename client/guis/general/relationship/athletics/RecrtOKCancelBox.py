# -*- coding: gb18030 -*-
#
from guis import *
from guis.controls.ButtonEx import HButtonEx
from LabelGather import labelGather
from guis.tooluis.messagebox.MsgBox import MsgBox
import MessageBox

class RecrtOKCancelBox( MsgBox ):
		
	__instance = None
		
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/okcancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )

		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# ȷ����ť
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.onOk_ )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )			# ȡ����ť
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide_ )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyOkBtn )							# ����Ĭ�ϵĻس���ť
		self.setCancelButton( self.__pyCancelBtn )					# ����Ĭ�ϵ� esc ��ť

		self.defRes_ = MessageBox.RS_CANCEL							# Ĭ�Ͻ��Ϊ cancel
		self.__delaycbid = 0

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:ocBox", "btnOk" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:ocBox", "btnCancel" )

	def dispose( self ) :
		self.__pyOkBtn.dispose()
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

	@staticmethod
	def instance():
		"""
		to get the exclusive instance of TongCancelOkBox
		"""
		if RecrtOKCancelBox.__instance is None:
			RecrtOKCancelBox.__instance = RecrtOKCancelBox()
		return RecrtOKCancelBox.__instance
		
	@staticmethod
	def getInstance():
		"""
		return None or the exclusive instance of TongCancelOkBox
		"""
		return RecrtOKCancelBox.__instance


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onOk_( self ) :
		"""
		��ȷ����ť�����ʱ����
		"""
		self.notifyCallback_( MessageBox.RS_OK )
	
	def hide_( self ):
		self.notifyCallback_( MessageBox.RS_CANCEL )
		self.hide()
		
	def __del__(self):
		"""
		"""
		pass
	
	def __agentCallback( self, callback, resID ):
		callback( resID )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, lastTime, msg, title, callback, pyOwner = None ) :
		BigWorld.cancelCallback( self.__delaycbid )
		agentCallback = Functor( self.__agentCallback, callback )
		MsgBox.show( self, msg, title, agentCallback, pyOwner )
		self.__delaycbid = BigWorld.callback( lastTime, self.hide )
		return self
	
	def hide( self, succ = False ):
		if succ:
			self.dispose()
		else:
			MsgBox.hide( self )
		BigWorld.cancelCallback( self.__delaycbid )

def show( lastTime, msg, title, callback, pyOwner = None ) :
	RecrtOKCancelBox().show( lastTime, msg, title, callback, pyOwner )
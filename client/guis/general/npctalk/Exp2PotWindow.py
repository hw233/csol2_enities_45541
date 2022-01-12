# -*- coding: gb18030 -*-

"""
implement Exp2PotWindow window
"""

import csstatus
import csconst
import GUIFacade
from guis import *
from AbstractTemplates import Singleton
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from guis.controls.TrackBar import HTrackBar
from guis.controls.ProgressBar import HProgressBar
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather

class Exp2PotWindow( Singleton, Window ) :
	"""
	���黻Ǳ�ܽ���
	"""
	__triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/npctalk/exp2pot.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.posZSegment = ZSegs.L2												# ����Ĭ��Ϊ�ڶ���
		self.h_dockStyle = "CENTER"												# ˮƽ������ʾ
		self.v_dockStyle = "MIDDLE"												# ��ֱ������ʾ
		self.addToMgr( "Exp2PotWindow" )
		self.__trapID = 0

		self.__initialize( wnd )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_Exp2Potential :
			INFO_MSG( str( self ) )

	def __initialize( self, wnd ) :
		self.__stNeedExp = StaticText( wnd.stExp )										# ��ȡǱ����Ҫ�ľ���
		self.__stNeedExp.text = "0"
		self.__stMinVal = StaticText( wnd.stMinVal )									# �϶�����Сֵ
		self.__stMinVal.text = "0"
		self.__stMaxVal = StaticText( wnd.stMaxVal )									# �϶������ֵ
		self.__stMaxVal.text = BigWorld.player().EXP
		self.__maxVal = int( BigWorld.player().EXP / csconst.ROLE_EXP2POT_MULTIPLE )	# ��ǰ������Ի������Ǳ��

		self.__pyPotBox = TextBox( wnd.potentialBox.box )								# Ǳ�����������
		self.__pyPotBox.inputMode = InputMode.NATURALNUM
		self.__pyPotBox.maxLength = 10
		self.__pyPotBox.text = ""
		self.__pyPotBox.onTextChanged.bind( self.__onInputTextChanged )

		self.__pyBtnOk = Button( wnd.btnOk )
		self.__pyBtnOk.visible = True
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onEnter )

		self.__pyBtnCancel = Button( wnd.btnCancel )
		self.__pyBtnCancel.visible = True
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )

		self.__pyTBPot = HTrackBar( wnd.pot_trackBar )		# ������
		self.__pyTBPot.stepCount = -1
		self.__pyTBPot.onSlide.bind( self.__onPotSlided )
		
		self.__pyHBar = HProgressBar( wnd.pot_trackBar.trackBar )
		self.__pyHBar.clipMode = "RIGHT"
		self.__pyHBar.value = 0.0

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnCancel, "NPCTalkWnd:exp2pot", "cancelBtn" )
		labelGather.setPyBgLabel( self.__pyBtnOk, "NPCTalkWnd:exp2pot", "okBtn" )
		labelGather.setLabel( wnd.lbExp, "NPCTalkWnd:exp2pot", "lbExp" )
		labelGather.setLabel( wnd.lbPotential, "NPCTalkWnd:exp2pot", "lbPotential" )
		labelGather.setLabel( wnd.lbTitle, "NPCTalkWnd:exp2pot", "lbTitle" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __onShow( SELF ) :
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		SELF.inst.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, SELF.inst.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����
		SELF.inst.show()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#ɾ����ҵĶԻ�����
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		player = BigWorld.player()
		gossiptarget = GUIFacade.getGossipTarget()						#��ȡ��ǰ�Ի�NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#���NPC�뿪��ҶԻ�����
			self.hide()														#���ص�ǰ����
			self.__delTrap()

	def __onEnter( self ) :
		player = BigWorld.player()
		if self.__pyPotBox.text != "" and self.__pyPotBox.text != "0":
			potVal = int( self.__pyPotBox.text )
			if potVal > self.__maxVal :
				player.statusMessage( csstatus.POTENTIAL_NOT_ENOUGH_EXP_TO_CHANGE )
				return
			if player.potential + potVal > csconst.ROLE_POTENTIAL_UPPER :
				player.statusMessage( csstatus.POTENTIAL_WILL_RUN_OVER )
				return
			def query( rs_id ):
				if rs_id == RS_OK:
					player.cell.onExp2PotFC( potVal )
					self.hide()
			# "ȷ��Ҫ��%d�㾭��һ���%d��Ǳ����?"
			showMessage( mbmsgs[0x0481] % ( potVal * csconst.ROLE_EXP2POT_MULTIPLE, potVal ), "", MB_OK_CANCEL, query, pyOwner = self )

	def __onCancel( self ) :
		self.hide()

	def __onPotSlided( self, pySlider, value ) :
		"""
		��������ʱ������
		"""
		self.__pyPotBox.onTextChanged.shield()
		self.__pyPotBox.text = str( int( value * self.__maxVal ) )
		self.__pyPotBox.onTextChanged.unshield()
		self.__stNeedExp.text = str( int( self.__pyPotBox.text ) * csconst.ROLE_EXP2POT_MULTIPLE )
		self.__pyHBar.value = value

	def __onInputTextChanged( self, pyBox ) :
		"""
		�ı��ı�ʱ������
		"""
		text = pyBox.text
		if int( text ) > self.__maxVal: # ����ֵ���ڵ�ǰ�ɶһ���Ǳ��ֵʱ��ֻ��ʾ��ǰ�ɶһ������ֵ��
			text = str( self.__maxVal )
			self.__pyTBPot.value = 1
			self.__stNeedExp.text = str( self.__maxVal * csconst.ROLE_EXP2POT_MULTIPLE )
			return
		value = 0
		if text.strip() != "" :
			value = min( self.__maxVal, int( text ) )
		self.__pyTBPot.onSlide.shield()
		self.__pyTBPot.value = float( value ) / self.__maxVal
		self.__pyTBPot.onSlide.unshield()
		self.__stNeedExp.text = str( value * csconst.ROLE_EXP2POT_MULTIPLE )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers["EVT_ON_SHOW_Exp2PotWindow"] = SELF.__onShow
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[ evtMacro ]( *args )

	def show( self ) :
		Window.show( self )
		self.__pyPotBox.tabStop = True

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	def hide( self ) :
		Window.hide( self )
		self.dispose()

	def onLeaveWorld( self ) :
		self.hide()

Exp2PotWindow.registerEvents()
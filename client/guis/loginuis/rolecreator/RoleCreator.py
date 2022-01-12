# -*- coding: gb18030 -*-
#
# $Id: RoleCreator.py,v 1.33 2008-08-26 02:20:43 huangyongwei Exp $

"""
implement role creator class
"""

import csdefine
import csconst
import event.EventCenter as ECenter
from cscollections import CycleList
from LoginMgr import roleCreator
from guis import *
from guis.loginuis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.TextBox import TextBox
from guis.controls.ODComboBox import ODComboBox
from config.client.HairFaceConfig import Datas as HFDatas
from config.client.roleHeadTexture import Datas as HEDatas
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
import random

class RoleCreator( RootGUI ) :
	__cc_fade_speed = 0.2

	__cc_name_max_length = 16
	
	__profession_maps = { csdefine.CLASS_FIGHTER: ( ( 1, 1 ), labelGather.getText( "LoginDialog:RoleCreator", "btnFighter" ) ),
						csdefine.CLASS_SWORDMAN: ( ( 1, 2 ), labelGather.getText( "LoginDialog:RoleCreator", "btnSword" ) ),
						csdefine.CLASS_MAGE: ( ( 2, 2 ), labelGather.getText( "LoginDialog:RoleCreator", "btnMage" ) ),
						csdefine.CLASS_ARCHER: ( ( 2, 1 ), labelGather.getText( "LoginDialog:RoleCreator", "btnArcher" ) ),
						}
						
	__camp_maps = { csdefine.ENTITY_CAMP_NONE: labelGather.getText( "LoginDialog:RoleCreator", "noCamp" ),
					csdefine.ENTITY_CAMP_TAOISM: labelGather.getText( "LoginDialog:RoleCreator", "taoism" ),
					csdefine.ENTITY_CAMP_DEMON: labelGather.getText( "LoginDialog:RoleCreator", "demon" ),
				}
	
	def __init__( self ) :
		wnd = GUI.load( "guis/loginuis/rolecreator/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.focus = False
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = False
		self.__initialize( wnd )

		self.hairData = {}
		self.faceData = {}
		self.__curHeadIndex = 0
		self.__maxHeadIndex = 0
		self.__selFaceIndex = 0
		self.__selHairIndex = 0
		self.__selProIndex = 1
		self.__pyMsgBox = None

		self.__triggers = {}
		self.__registerTriggers()
		self.__onHeadSelected( self.__curHeadIndex )
		self.__onHairSelected( self.__selHairIndex )
		self.__onFaceSelected( self.__selFaceIndex )

		shortcutMgr.setHandler( "ROLE_CREATOR_BACK", self.__onBackClick )

	def __initialize( self, wnd ) :
		self.__fader = wnd.fader
		self.__fader.speed = self.__cc_fade_speed
		self.__fader.value = 1
		self.__fader.reset()

		# -----------------------------------
		self.__pyTitle = PyGUI( wnd.title )
		self.__pyTitle.h_dockStyle = "CENTER"
		self.__pyTitle.v_dockStyle = "S_TOP"
		
		self.__pySetPanel = PyGUI( wnd.setPanel )										# Ԥ�����ð���
		self.__pySetPanel.h_dockStyle = "S_LEFT"
		self.__pySetPanel.v_dockStyle = "S_TOP"

		pyBtnMale = SelectableButton( wnd.setPanel.btnMale )							# ����ѡ��ť
		labelGather.setPyBgLabel( pyBtnMale, "LoginDialog:RoleCreator", "btnMale" )
		pyBtnMale.foreColor = 255.0, 255.0, 255.0
		pyBtnFemale = SelectableButton( wnd.setPanel.btnFemale )						# Ů��ѡ��ť
		labelGather.setPyBgLabel( pyBtnFemale, "LoginDialog:RoleCreator", "btnFemale" )
		pyBtnFemale.foreColor = 255.0, 255.0, 255.0
		self.__pyGenderGroup = SelectorGroup( pyBtnMale, pyBtnFemale )
		self.__pyGenderBtns = {}
		self.__pyGenderBtns[csdefine.GENDER_MALE] = pyBtnMale
		self.__pyGenderBtns[csdefine.GENDER_FEMALE] = pyBtnFemale
		
		for gender, pyGender in self.__pyGenderBtns.iteritems() :
			pyGender.mapGender = gender
			pyGender.setStatesMapping( UIState.MODE_R2C2 )
			pyGender.autoSelect = False
			pyGender.onLClick.bind( self.__onGenderClick )

		self.__pyProPanel = PyGUI( wnd.proPanel )
		self.__pyProPanel.h_dockStyle = "CENTER"
		self.__pyProPanel.v_dockStyle = "S_TOP"
		
		self.__pySelProFlag = PyGUI( wnd.proPanel.proFlag )
		util.setGuiState( self.__pySelProFlag.getGui(), ( 2, 2 ), ( 1, 1 ))
		
		self.__pyProName = StaticText( wnd.proPanel.lbText )
		self.__pyProName.text = ""
		
		self.__pyFrontPro = Button( wnd.proPanel.btnFront )
		self.__pyFrontPro.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyFrontPro.onLClick.bind( self.__ChosePro )
		
		self.__pyNextPro = Button( wnd.proPanel.btnNext )
		self.__pyNextPro.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNextPro.onLClick.bind( self.__ChosePro )
		
		self.__pyFrontFace = Button( wnd.setPanel.chFace.btnFront )							# ����ѡ��
		self.__pyFrontFace.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyFrontFace.onLClick.bind( self.__ChoseFace )
		
		self.__pyNextFace = Button( wnd.setPanel.chFace.btnNext )
		self.__pyNextFace.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNextFace.onLClick.bind( self.__ChoseFace )
		
		self.__pyStFace = StaticText( wnd.setPanel.chFace.lbText )
		self.__pyStFace.color = 255.0, 255.0, 255.0
		self.__pyStFace.text = ""
		
		self.__pyFrontHair = Button( wnd.setPanel.chHair.btnFront )
		self.__pyFrontHair.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyFrontHair.onLClick.bind( self.__ChoseHair )
		
		self.__pyNextHair = Button( wnd.setPanel.chHair.btnNext )
		self.__pyNextHair.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNextHair.onLClick.bind( self.__ChoseHair )
		
		self.__pyStHair = StaticText( wnd.setPanel.chHair.lbText )
		self.__pyStHair.color = 255.0, 255.0, 255.0
		self.__pyStHair.text = ""

		self.__pyFrontBtn = Button( wnd.setPanel.frontBtn )
		self.__pyFrontBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyFrontBtn.onLClick.bind( self.__onForeHead )
		self.__pyNextBtn = Button( wnd.setPanel.nextBtn )
		self.__pyNextBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNextBtn.onLClick.bind( self.__onNextHead )
		self.__pyHead = PyGUI( wnd.setPanel.head )
		
		self.__pyDspPanel = PyGUI( wnd.dspPanel )										# ְҵ����
		self.__pyDspPanel.h_dockStyle = "S_RIGHT"
		self.__pyDspPanel.v_dockStyle = "S_TOP"
		
		self.__pyStPro = StaticText( wnd.dspPanel.stPro )
		self.__pyStPro.text = ""
		
		self.__pyProFlag = PyGUI( wnd.dspPanel.proFlag )
		util.setGuiState( self.__pyProFlag.getGui(), ( 2, 2 ), ( 1, 1 ))
		
		self.__pyTPDsp = CSTextPanel( wnd.dspPanel.tpDsp, wnd.dspPanel.sbar )		# ְҵ����

		# -----------------------------------
		self.__pyCtrlPanel = PyGUI( wnd.ctrlPanel )									# ��ɫ���ư���
		self.__pyCtrlPanel.h_dockStyle = "HFILL"
		self.__pyCtrlPanel.v_dockStyle = "S_BOTTOM"

		self.__pyBtnLRotate = Button( wnd.ctrlPanel.btnLRotate )					# ��ת��ť
		self.__pyBtnLRotate.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnLRotate.onLMouseDown.bind( self.__onRotateBtnMouseDown )
		self.__pyBtnLRotate.onLMouseUp.bind( self.__onRotateBtnMouseUp )

		self.__pyBtnRRotate = Button( wnd.ctrlPanel.btnRRotate )					# ��ת��ť
		self.__pyBtnRRotate.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnRRotate.h_dockStyle = "RIGHT"
		self.__pyBtnRRotate.onLMouseDown.bind( self.__onRotateBtnMouseDown )
		self.__pyBtnRRotate.onLMouseUp.bind( self.__onRotateBtnMouseUp )

		self.__pyBtnClose = Button( wnd.ctrlPanel.btnClose )						# ������ť
		self.__pyBtnClose.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnClose.h_dockStyle = "CENTER"
		self.__pyBtnClose.v_dockStyle = "BOTTOM"
		self.__pyBtnClose.onLClick.bind( self.__onViewClose )

		self.__pyBtnFar = Button( wnd.ctrlPanel.btnFar )							# Զ�밴ť
		self.__pyBtnFar.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnFar.h_dockStyle = "CENTER"
		self.__pyBtnFar.v_dockStyle = "BOTTOM"
		self.__pyBtnFar.onLClick.bind( self.__onViewFar )

		# -----------------------------------
		self.__pyNamePanel = PyGUI( wnd.namePanel )									# ������
		self.__pyNamePanel.h_dockStyle = "CENTER"
		self.__pyNamePanel.v_dockStyle = "S_BOTTOM"

		self.__pyTBName = TextBox( wnd.namePanel.tbName )							# ���������
		self.__pyTBName.maxLength = self.__cc_name_max_length

		self.__pyOkBtn = HButtonEx( wnd.namePanel.btnOk )								# ȷ����ť
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onOKClick )
		self.setOkButton( self.__pyOkBtn )

		self.__pyBackBtn = HButtonEx( wnd.btnBack )									# ���ذ�ť
		self.__pyBackBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBackBtn.onLClick.bind( self.__onBackClick )
		self.__pyBackBtn.h_dockStyle = "S_RIGHT"
		self.__pyBackBtn.v_dockStyle = "S_BOTTOM"
		
		self.__pyBtnQuit = HButtonEx( wnd.btnQuit )									# �˳���ť
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.onLClick.bind( self.__onQuit )
		self.__pyBtnQuit.h_dockStyle = "S_RIGHT"
		self.__pyBtnQuit.v_dockStyle = "S_BOTTOM"

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "LoginDialog:RoleCreator", "btnOk" )
		labelGather.setPyBgLabel( self.__pyBackBtn, "LoginDialog:RoleCreator", "btnBack" )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "LoginDialog:CampSelector", "btnQuit" )
		labelGather.setLabel( wnd.title.stTitle, "LoginDialog:RoleCreator", "stCreateTitle" )
		labelGather.setLabel( wnd.setPanel.stHead, "LoginDialog:RoleCreator", "stHead" )
		labelGather.setLabel( wnd.setPanel.stHair, "LoginDialog:RoleCreator", "stHair" )
		labelGather.setLabel( wnd.setPanel.stFace, "LoginDialog:RoleCreator", "stFace" )
		labelGather.setLabel( wnd.setPanel.stGender, "LoginDialog:RoleCreator", "stGender" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_CREATOR_COMPLETE_SHOW"] = self.__onShow
		self.__triggers["EVT_ON_CAMP_SELECTOR_SHOW"] = self.__onHide
		self.__triggers["EVT_ON_ROLECREATOR_GENDER_CHANGED"] = self.__onGenderChanged			# �Ա�ı�ʱ������
		self.__triggers["EVT_ON_ROLECREATOR_PROFESSION_CHANGED"] = self.__onProfessionChanged	# ְҵ�ı�ʱ������
		self.__triggers["EVT_ON_ROLECREATOR_OK"] = self.__onCreateCB  #�����ɹ���ص�
#		self.__triggers["EVT_ON_ROLECREATOR_CAMP_CHANGED"] = self.__onCampChanged	# ְҵ�ı�ʱ������
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __createRole( self ) :
		"""
		������ɫ
		"""
		name = self.__pyTBName.text.strip()
		if name == "" :
			# "�������ɫ����"
			showAutoHideMessage( 3.0, 0x0e21, "", pyOwner = self )
			return
		roleCreator.createRole( name )
		return True

	def __cancel( self ) :
		"""
		ȡ�������ؽ�ɫѡ��
		"""
		roleCreator.cancel()
		self.__pyTBName.text = ""
		self.hide()

	def __onQuit( self, pyBtn ):
		"""
		�˳�
		"""
		def query( id ) :
			if id == RS_OK:
				if self.visible :
					roleCreator.onEnterSelectCamp()
					self.visible = False
		msg = mbmsgs[0x0e24]
		if self.__pyMsgBox:
			self.__pyMsgBox.visible = False
			self.__pyMsgBox = None
		self.__pyMsgBox = showMessage( msg, "", MB_OK_CANCEL, query )

	# -------------------------------------------------
	def __onCampClick( self, pyCamp ):
		"""
		�����Ӫ��ť��ѡ����Ӫ��
		"""
		roleCreator.resetCamp( pyCamp.mapCamp )
		
	def __onGenderClick( self, pyGender ) :
		"""
		����Ա�ť��ѡ���Ա�
		"""
		roleCreator.resetGender( pyGender.mapGender )

	def __onProfessionClick( self, pyProfession ) :
		"""
		���ְҵ��ť��ѡ��ְҵ��
		"""
		roleCreator.selectProfession( pyProfession.mapProfession )

	def __onFaceSelected( self, selIndex ) :
		"""
		����ѡ��
		"""
		profession = self.__selProIndex*csdefine.CLASS_FIGHTER
		currGenSe = self.__pyGenderGroup.pyCurrSelector
		if currGenSe is None: return
		gender = currGenSe.mapGender
		key = gender | profession
		data = HFDatas.get( key )
		if data is None: return
		faceNameData = data.get( "faceName" )
		if faceNameData is None: return
		self.__pyStFace.text = faceNameData[selIndex]
		faceNum = self.faceData.get( selIndex )
		if faceNum is None: return
		roleCreator.selectFace( faceNum )

	def __onHairSelected( self, selIndex ) :
		"""
		����ѡ��
		"""
		profession = self.__selProIndex*csdefine.CLASS_FIGHTER
		currGenSe = self.__pyGenderGroup.pyCurrSelector
		if currGenSe is None: return
		gender = currGenSe.mapGender
		key = gender | profession
		data = HFDatas.get( key )
		if data is None: return
		hairNameData = data.get( "hairName" )
		if hairNameData is None: return
		self.__pyStHair.text = hairNameData[selIndex]
		hairNum = self.hairData.get( selIndex )
		if hairNum is None: return
		roleCreator.selectHair( hairNum )

	def __onHeadSelected( self, index ) :
		"""
		ͷ��ѡ��
		"""
		selIndex = index + 1
		currGenSe = self.__pyGenderGroup.pyCurrSelector
		if currGenSe is None: return
		gender = currGenSe.mapGender
		if gender == csdefine.GENDER_MALE: # ����
			self.__pyHead.texture = "maps/role_headers/tou_xiang_m_%03i.tga" % selIndex
			headIndex = int( "1000" + str( selIndex ) )
			roleCreator.selectHead( headIndex )
		else: # ʣ�µĿ�����Ϊ��Ů��
			self.__pyHead.texture = "maps/role_headers/tou_xiang_w_%03i.tga" % selIndex
			headIndex = int( "2000" + str( selIndex ) )
			roleCreator.selectHead( headIndex )
	
	def __onProSelected( self, index ):
		"""
		ְҵѡ��
		"""
		pro = csdefine.CLASS_FIGHTER *index
		proInfo = self.__profession_maps.get( pro, None )
		if proInfo is None:return
		util.setGuiState( self.__pySelProFlag.getGui(), ( 2, 2 ), proInfo[0])
		util.setGuiState( self.__pyProFlag.getGui(), ( 2, 2 ), proInfo[0] )
		self.__pyProName.text = proInfo[1]
		roleCreator.selectProfession( pro )

	# -------------------------------------------------
	def __onRotateBtnMouseDown( self, pyBtn ) :
		"""
		��ת��ɫ
		"""
		if pyBtn == self.__pyBtnLRotate :
			rds.roleCreator.turnRole( 1 )
		else :
			rds.roleCreator.turnRole( -1 )

	def __onRotateBtnMouseUp( self ) :
		"""
		ֹͣ��ת��ɫ
		"""
		rds.roleCreator.turnRole( 0 )

	def __onViewClose( self ) :
		"""
		��ͷ����
		"""
		rds.roleCreator.viewClose()

	def __onViewFar( self ) :
		"""
		��ͷ��Զ
		"""
		rds.roleCreator.viewFar()
	
	def __ChoseFace( self, pyBtn ):
		if pyBtn == self.__pyFrontFace:
			self.__selFaceIndex -= 1
			if self.__selFaceIndex < 0:
				self.__selFaceIndex = len( self.faceData ) - 1
		else:
			self.__selFaceIndex += 1
			if self.__selFaceIndex > len( self.faceData ) - 1:
				self.__selFaceIndex = 0
		self.__onFaceSelected( self.__selFaceIndex )

	def __ChoseHair( self, pyBtn ):
		if pyBtn == self.__pyFrontHair:
			self.__selHairIndex -= 1
			if self.__selHairIndex < 0:
				self.__selHairIndex = len( self.hairData ) - 1
		else:
			self.__selHairIndex += 1
			if self.__selHairIndex > len( self.hairData )- 1:
				self.__selHairIndex =0
		self.__onHairSelected( self.__selHairIndex )

	# ---------------------------------------
	def __onOKClick( self ) :
		"""
		ȷ��������ɫ
		"""
		self.__createRole()

	def __onBackClick( self ) :
		"""
		����ѡ��Ҫ�����Ľ�ɫ����
		"""
		if self.visible :
			rds.roleCreator.onBackRoleCreate()
			self.visible = False
			return True
		return False

	# -------------------------------------------------
	def __onShow( self ):
		"""
		��ʾ
		"""
		self.show()
		
	def __onCreateCB( self ):
		"""
		������ɫ�ɹ���ص�
		"""
		self.hide()
		
	def __onHide( self ):
		"""
		����
		"""
		self.hide()
		
	def __onGenderChanged( self, gender ) :
		"""
		�Ա�ı�ʱ������
		"""
		self.__pyGenderBtns[gender].selected = True
		self.__resetHairChoice()
		self.__resetFaceChoice()
		self.__curHeadIndex = 0
		self.__onHeadSelected( self.__curHeadIndex )

	def __resetFaceChoice( self ):
		"""
		��������
		"""
		profession = self.__selProIndex*csdefine.CLASS_FIGHTER
		currGenSelect = self.__pyGenderGroup.pyCurrSelector
		if currGenSelect is None: return
		gender = currGenSelect.mapGender
		key = gender | profession
		data = HFDatas.get( key )
		if data is None: return
		faceData = data.get( "faceNum" )
		if faceData is None: return
		faceNameData = data.get( "faceName" )
		if faceNameData is None: return
		if len( faceData ) != len( faceNameData ): return
		self.faceData = {}
		for index, data in enumerate( faceData ):
			self.faceData[index] = data
		self.__selFaceIndex = 0
		self.__pyStFace.text = faceNameData[self.__selFaceIndex]

	def __resetHairChoice( self ):
		"""
		���跢��
		"""
		profession = self.__selProIndex*csdefine.CLASS_FIGHTER
		currGenSe = self.__pyGenderGroup.pyCurrSelector
		if currGenSe is None: return
		gender = currGenSe.mapGender
		key = gender | profession
		data = HFDatas.get( key )
		if data is None: return
		hairData = data.get( "hairNum" )
		if hairData is None: return
		hairNameData = data.get( "hairName" )
		if hairNameData is None: return
		if len( hairData ) != len( hairNameData ): return
		self.hairData = {}
		for index, data in enumerate( hairData ):
			self.hairData[index] = data
		self.__selHairIndex = 0
		self.__pyStHair.text = hairNameData[self.__selHairIndex]

	def __onProfessionChanged( self, profession ) :
		"""
		ְҵ�ı�ʱ������
		"""
		self.__selProIndex = profession / csdefine.CLASS_FIGHTER
		self.__pyTPDsp.text = roleCreator.getDescription( profession )
		info = self.__profession_maps.get( profession )
		if info is None:return
		util.setGuiState( self.__pySelProFlag.getGui(), ( 2, 2 ), info[0])
		util.setGuiState( self.__pyProFlag.getGui(), ( 2, 2 ), info[0] )
		self.__pyProName.text = info[1]
		self.__pyStPro.text = info[1]
		self.__resetHairChoice()
		self.__resetFaceChoice()
	
	def __onCampChanged( self, camp ):
		"""
		��Ӫ�ı�ʱ����
		"""
		self.__pyCampDsp.text = roleCreator.getCampDesp( camp )
		self.__pyCampBtns[camp].selected = True
		campName = self.__camp_maps.get( camp, "" )
		self.__pyStCamp.text = campName
		self.__resetHairChoice()
		self.__resetFaceChoice()

	def __keepTab( self ) : # �߻�Ҫ�������������������Ӱ�죬����֮�٣�
		self.__pyTBName.tabStop = True

	def __onForeHead( self ):
		"""
		��ʾ��һ��ͷ��
		"""
		self.__getMaxHeadIndex()
		self.__curHeadIndex -= 1
		if self.__curHeadIndex < 0:
			self.__curHeadIndex = self.__maxHeadIndex
		self.__onHeadSelected( self.__curHeadIndex )

	def __onNextHead( self ):
		"""
		��ʾ��һ��ͷ��
		"""
		self.__getMaxHeadIndex()
		self.__curHeadIndex += 1
		if self.__curHeadIndex > self.__maxHeadIndex:
			self.__curHeadIndex = 0
		self.__onHeadSelected( self.__curHeadIndex )
	
	def __ChosePro( self, pyBtn ):
		"""
		ְҵѡ��
		"""
		if pyBtn == self.__pyFrontPro:
			self.__selProIndex -= 1
			if self.__selProIndex < 1:
				self.__selProIndex = len( self.__profession_maps )
		else:
			self.__selProIndex += 1
			if self.__selProIndex > len( self.__profession_maps ):
				self.__selProIndex = 1
		self.__onProSelected( self.__selProIndex )

	def __getMaxHeadIndex( self ):
		"""
		���õ�ǰѡ����Ա��ͷ������index
		"""
		currGenSe = self.__pyGenderGroup.pyCurrSelector
		if currGenSe is None: return
		gender = currGenSe.mapGender
		index = 0
		if gender == csdefine.GENDER_MALE:
			genderNum = "1000"
		else:
			genderNum = "2000"
		for key in HEDatas.keys():
			if genderNum in str( key ):
				index += 1
		self.__maxHeadIndex =  index - 1

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		��Ϸ״̬�ı�ʱ������
		"""
		if newStatus == Define.GST_ROLE_CREATE :
			self.visible = not rds.ruisMgr.campSelector.visible
		elif self.visible and newStatus != Define.GST_OFFLINE :
			self.hide()

	def onActivated( self ) :
		"""
		�����ڼ���ʱ������
		"""
		RootGUI.onActivated( self )
		self.__pyTBName.tabStop = True

	def show( self ) :
		self.__fader.value = 1
		RootGUI.show( self )

	def hide( self ) :
		self.__fader.value = 0
		func = Functor( RootGUI.hide, self )
		BigWorld.callback( self.__cc_fade_speed, func )
		self.__pyTBName.text = ""

	# ---------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def isMouseHit( self ) :
		BigWorld.callback( 0.2, self.__keepTab )
		return self.__pySetPanel.isMouseHit()
# -*- coding: gb18030 -*-

# һ����װ����

from guis import *
from guis.common.GUIBaseObject import GUIBaseObject
from guis.tooluis.inputbox.InputBox import InputBox
from guis.controls.Button import Button
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.SelectableButton import SelectableButton

import Time
import Const
import csdefine
import csstatus
import ItemTypeEnum
from LabelGather import labelGather
from config.client.msgboxtexts import Datas as mbmsgs

SUIT_ORDER = (															# ����װ��UID�Ĵ洢˳��
	ItemTypeEnum.CEL_HEAD, ItemTypeEnum.CEL_NECK, ItemTypeEnum.CEL_BODY,
	ItemTypeEnum.CEL_BREECH, ItemTypeEnum.CEL_VOLA, ItemTypeEnum.CEL_HAUNCH,
	ItemTypeEnum.CEL_CUFF, ItemTypeEnum.CEL_LEFTHAND, ItemTypeEnum.CEL_RIGHTHAND,
	ItemTypeEnum.CEL_FEET, ItemTypeEnum.CEL_LEFTFINGER, ItemTypeEnum.CEL_RIGHTFINGER,
	ItemTypeEnum.CEL_TALISMAN,
	)

class SwitchEQPanel( GUIBaseObject ) :

	def __init__( self, panel ) :
		GUIBaseObject.__init__( self, panel )

		self.__swLockCBID = 0											# ��װCD����
		self.__initialize( panel )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		"""
		"""
		btnHandlers = {
			"btn_save" : ( self.__onSave, "dspSave" ),
			"btn_help" : ( self.__onHelp, "dspHelp" ),
			}
		self.__pyBtns = {}
		self.__pySelector = SelectorGroup()								# ������ѡ���
		for label, child in panel.children :
			if "btn_no" in label :										# ������ѡ��ť
				suitIdx = int( label.split( "btn_no" )[1] )
				pyBtnSuit = self.__createButton( SelectableButton, child, self.__onSuitSelected )
				pyBtnSuit.onRClick.bind( self.__onSuitRClicked )
				pyBtnSuit.suitIdx = suitIdx								# ��װ���
				pyBtnSuit.suitName = ""									# ��װ����
				pyBtnSuit.autoSelect = False
				pyBtnSuit.selectedForeColor = ( 0, 250, 102, 255 )
				pyBtnSuit.pressedForeColor = pyBtnSuit.commonForeColor
				pressedMapping = pyBtnSuit.pressedMapping
				pyBtnSuit.selectedMapping = pyBtnSuit.highlightMapping
				pyBtnSuit.pressedMapping = pressedMapping
				self.__pySelector.addSelector( pyBtnSuit )
			elif "btn_" in label :										# ������ͨ��ť
				handler, lbText = btnHandlers[ label ]
				pyBtn = self.__createButton( Button, child, handler )
				pyBtn.dsp = labelGather.getText( "PlayerInfo:main", lbText )
				self.__pyBtns[ label ] = pyBtn

	def __createButton( self, CLS, btn, handler ) :
		"""
		������ť
		"""
		pyBtn = CLS( btn )
		pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		pyBtn.onMouseEnter.bind( self.__onBtnMouseEnter )
		pyBtn.onMouseLeave.bind( self.__onBtnMouseLeave )
		pyBtn.dsp = ""													# ������ʾ�ı�
		if handler :
			pyBtn.onLClick.bind( handler )
		return pyBtn

	# -------------------------------------------------
	def __onSave( self ) :
		"""
		������װ
		"""
		pySelSuit = self.__pySelector.pyCurrSelector
		if pySelSuit is None : return
		self.__lockSuitBtns( True )										# ������װ���水ť

		def saveSuit( success, suitName ) :
			"""
			������װ
			"""
			if success :
				self.__updateSuitBtn( pySelSuit, suitName )
				BigWorld.player().saveSuit( pySelSuit.suitIdx, suitName )
			self.__lockSuitBtns( False )								# ������װ���水ť

		def confirmCB( res ) :
			"""
			δ���������װȷ��
			"""
			if res == RS_YES :
				self.__requestInput( pySelSuit, saveSuit )
			else :
				self.__lockSuitBtns( False )							# ������װ���水ť

		suitName = pySelSuit.suitName
		if suitName == "" :
			# "��ȷ���½�װ����ϣ��������ڴ��ŵ�װ����ϱ�������ô��"
			showMessage( 0x0ec1, "", MB_YES_NO, confirmCB, self )
		else :
			self.__requestInput( pySelSuit, saveSuit )

	def __onHelp( self ) :
		"""
		�鿴����
		"""
		topic = labelGather.getText( "PlayerInfo:main", "helpTopic" )
		ECenter.fireEvent( "EVT_ON_HELP_SEARCH", topic )				# ������������

	def __onSuitSelected( self, pyBtnSuit ) :
		"""
		ѡ��ĳ����װ
		"""
		#if pyBtnSuit.selected == True : return							# ����֮ǰѡ�����װ��������
		if BigWorld.isKeyDown( KEY_LALT ) or \
			BigWorld.isKeyDown( KEY_RALT ) :							# ��סAlt��������ֻ����ѡ��
				pyBtnSuit.selected = True
				return
		if pyBtnSuit.suitName != "" : 									# δ���������ϲ�����
			player = BigWorld.player()
			if player.state == csdefine.ENTITY_STATE_FIGHT : 			# ս��״̬���ܽ��л�װ
				player.statusMessage( csstatus.OKS_FORBIDDEN_IN_FIGHTING )
				return
			if player.isDead() : 										# ����״̬���ܽ��л�װ
				player.statusMessage( csstatus.OKS_FORBIDDEN_WHEN_DEAD )
				return
			if player.state != csdefine.ENTITY_STATE_FREE :				# ����������״̬��ͳһ��ʾ
				player.statusMessage( csstatus.OKS_SWITCH_IN_ERROR_STATE )
				return
			if self.__isSwitchLocked() :								# ��װ����CD��
				player.statusMessage( csstatus.OKS_COOL_DOWN )
				return
			if player.iskitbagsLocked() :								# �����ѱ�����
				player.statusMessage( csstatus.OKS_KIGBAG_LOCKED )
				return
			#self.__lockSwitch()
			INFO_MSG( "switch to suit %i" % pyBtnSuit.suitIdx )
			player.switchSuit( pyBtnSuit.suitIdx )
			pyBtnSuit.selected = True									# ѡ�����װ
		else :
			pyBtnSuit.selected = True									# ѡ�����װ
			self.__onSave()

	def __onSuitRClicked( self, pySuitBtn ) :
		"""
		�Ҽ������װ��ť����������ť
		"""
		if not ( BigWorld.isKeyDown( KEY_LALT ) or \
			BigWorld.isKeyDown( KEY_RALT ) ) :							# ֻ����סAlt���һ������
				return

		def renameCB( success, suitName ) :
			"""
			"""
			if success :
				self.__updateSuitBtn( pySuitBtn, suitName )
				BigWorld.player().renameSuit( pySuitBtn.suitIdx, suitName )

		suitName = pySuitBtn.suitName
		if suitName == "" :
			# "ֻ�ܶ��Ѿ���������������������"
			showMessage( 0x0ec3, "", MB_OK, pyOwner = self )
		else :
			self.__requestInput( pySuitBtn, renameCB )

	# -------------------------------------------------
	def __onBtnMouseEnter( self, pyBtn ) :
		"""
		�����밴ť
		"""
		toolbox.infoTip.showToolTips( pyBtn, pyBtn.dsp )

	def __onBtnMouseLeave( self ) :
		"""
		����뿪��ť
		"""
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def __requestInput( self, pySuitBtn, callback ) :
		"""
		����������װ����
		"""
		def inputNameCB( res, text ) :
			"""
			��������ص�
			"""
			success = False
			if res == DialogResult.OK :
				text = text.strip()
				if len( text ) > 14 :
					# ����������ƹ���
					showAutoHideMessage( 3.0, 0x0ec2, mbmsgs[0x0c22] )
				#elif not rds.wordsProfanity.isPureString( text ) :
				#	# "���Ʋ��Ϸ���"
				#	showAutoHideMessage( 3.0, 0x0e08, mbmsgs[0x0c22] )
				elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
					# "����������н��ôʻ�!"
					showAutoHideMessage( 3.0, 0x0e09, mbmsgs[0x0c22] )
				else :
					if text == "" :
						# û��������ʹ��Ĭ������
						text = labelGather.getText( "PlayerInfo:main", "dspDefSuit", pySuitBtn.suitIdx )
					success = True
			callback( success, text )

		suitName = pySuitBtn.suitName
		if suitName == "" :
			suitName = labelGather.getText( "PlayerInfo:main", "dspDefSuit", pySuitBtn.suitIdx )
		title = labelGather.getText( "PlayerInfo:main", "clewInput" )
		pyIPBox = InputBox()
		pyIPBox.show( title, inputNameCB, self )
		pyIPBox.maxLength = 14
		pyIPBox.text = suitName

	def __updateSuitBtn( self, pyBtnSuit, suitName ) :
		"""
		������װ��ť
		"""
		if suitName == "" :												# ���û�б������װ
			pyBtnSuit.text = ""											# ��ʹ��Ĭ�ϵĸ�����ʾ�ı�
			pyBtnSuit.dsp = labelGather.getText( "PlayerInfo:main", "dspUnused" )
		else :
			pyBtnSuit.text = pyBtnSuit.suitIdx
			pyBtnSuit.dsp = suitName
		pyBtnSuit.suitName = suitName

	def __lockSuitBtns( self, locked ) :
		"""
		����/������װ�ͱ��水ť
		"""
		enable = not locked
		self.__pyBtns["btn_save"].enable = enable
		for pySuitBtn in self.__pySelector.pySelectors :
			if pySuitBtn.selected : continue							# ���ı䵱ǰѡ�����װ��ť
			pySuitBtn.enable = enable

	# -------------------------------------------------
	def __lockSwitch( self ) :
		"""
		������װ����
		"""
		if self.__isSwitchLocked() : return								# ����ǰ״̬��ͬ��������������
		self.__swLockCBID = BigWorld.callback( Const.ONE_KEY_SUIT_CD_TIME, self.__unlockSwitch )

	def __unlockSwitch( self ) :
		"""
		������װ����
		"""
		if not self.__isSwitchLocked() : return							# ����ǰ״̬��ͬ��������������
		BigWorld.cancelCallback( self.__swLockCBID )
		self.__swLockCBID = 0

	def __isSwitchLocked( self ) :
		"""
		��鵱ǰ��װ����������״̬
		"""
		player = BigWorld.player()
		cdid = Const.ONE_KEY_SUIT_CD_ID
		endTime = player.getCooldown( cdid )[3]
		return endTime > Time.Time.time()

	# -------------------------------------------------
	def __getSuitDatas( self ) :
		"""
		��ȡ��ɫ���ϵ�װ��UID
		"""
		kitbag = BigWorld.player().itemsBag
		uidFetcher = lambda eq : eq and eq.uid or 0
		suitDatas = [ uidFetcher( kitbag.getByOrder( order ) ) for order in SUIT_ORDER ]
		return suitDatas


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initSuits( self, selIndex, suitDatas ) :
		"""
		������֪ͨ��ʼ����װ
		"""
		for pyBtnSuit in self.__pySelector.pySelectors :
			suitData = suitDatas.get( pyBtnSuit.suitIdx, {} )
			suitName = suitData.get( "suitName", "" )
			self.__updateSuitBtn( pyBtnSuit, suitName )
			if pyBtnSuit.suitIdx == selIndex :
				pyBtnSuit.selected = True

	def updateSuit( self, suitIdx, suitName ) :
		"""
		������װ
		"""
		for pyBtnSuit in self.__pySelector.pySelectors :
			if pyBtnSuit.suitIdx == suitIdx :
				self.__updateSuitBtn( pyBtnSuit, suitName )
				break

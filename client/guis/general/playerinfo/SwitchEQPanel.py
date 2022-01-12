# -*- coding: gb18030 -*-

# 一键换装板面

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

SUIT_ORDER = (															# 定义装备UID的存储顺序
	ItemTypeEnum.CEL_HEAD, ItemTypeEnum.CEL_NECK, ItemTypeEnum.CEL_BODY,
	ItemTypeEnum.CEL_BREECH, ItemTypeEnum.CEL_VOLA, ItemTypeEnum.CEL_HAUNCH,
	ItemTypeEnum.CEL_CUFF, ItemTypeEnum.CEL_LEFTHAND, ItemTypeEnum.CEL_RIGHTHAND,
	ItemTypeEnum.CEL_FEET, ItemTypeEnum.CEL_LEFTFINGER, ItemTypeEnum.CEL_RIGHTFINGER,
	ItemTypeEnum.CEL_TALISMAN,
	)

class SwitchEQPanel( GUIBaseObject ) :

	def __init__( self, panel ) :
		GUIBaseObject.__init__( self, panel )

		self.__swLockCBID = 0											# 换装CD限制
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
		self.__pySelector = SelectorGroup()								# 创建单选组合
		for label, child in panel.children :
			if "btn_no" in label :										# 创建单选按钮
				suitIdx = int( label.split( "btn_no" )[1] )
				pyBtnSuit = self.__createButton( SelectableButton, child, self.__onSuitSelected )
				pyBtnSuit.onRClick.bind( self.__onSuitRClicked )
				pyBtnSuit.suitIdx = suitIdx								# 套装编号
				pyBtnSuit.suitName = ""									# 套装名称
				pyBtnSuit.autoSelect = False
				pyBtnSuit.selectedForeColor = ( 0, 250, 102, 255 )
				pyBtnSuit.pressedForeColor = pyBtnSuit.commonForeColor
				pressedMapping = pyBtnSuit.pressedMapping
				pyBtnSuit.selectedMapping = pyBtnSuit.highlightMapping
				pyBtnSuit.pressedMapping = pressedMapping
				self.__pySelector.addSelector( pyBtnSuit )
			elif "btn_" in label :										# 创建普通按钮
				handler, lbText = btnHandlers[ label ]
				pyBtn = self.__createButton( Button, child, handler )
				pyBtn.dsp = labelGather.getText( "PlayerInfo:main", lbText )
				self.__pyBtns[ label ] = pyBtn

	def __createButton( self, CLS, btn, handler ) :
		"""
		创建按钮
		"""
		pyBtn = CLS( btn )
		pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		pyBtn.onMouseEnter.bind( self.__onBtnMouseEnter )
		pyBtn.onMouseLeave.bind( self.__onBtnMouseLeave )
		pyBtn.dsp = ""													# 浮动提示文本
		if handler :
			pyBtn.onLClick.bind( handler )
		return pyBtn

	# -------------------------------------------------
	def __onSave( self ) :
		"""
		保存套装
		"""
		pySelSuit = self.__pySelector.pyCurrSelector
		if pySelSuit is None : return
		self.__lockSuitBtns( True )										# 锁定换装保存按钮

		def saveSuit( success, suitName ) :
			"""
			保存套装
			"""
			if success :
				self.__updateSuitBtn( pySelSuit, suitName )
				BigWorld.player().saveSuit( pySelSuit.suitIdx, suitName )
			self.__lockSuitBtns( False )								# 解锁换装保存按钮

		def confirmCB( res ) :
			"""
			未保存过的套装确认
			"""
			if res == RS_YES :
				self.__requestInput( pySelSuit, saveSuit )
			else :
				self.__lockSuitBtns( False )							# 解锁换装保存按钮

		suitName = pySelSuit.suitName
		if suitName == "" :
			# "您确定新建装备组合，并将现在穿着的装备组合保存其中么？"
			showMessage( 0x0ec1, "", MB_YES_NO, confirmCB, self )
		else :
			self.__requestInput( pySelSuit, saveSuit )

	def __onHelp( self ) :
		"""
		查看帮助
		"""
		topic = labelGather.getText( "PlayerInfo:main", "helpTopic" )
		ECenter.fireEvent( "EVT_ON_HELP_SEARCH", topic )				# 搜索帮助主题

	def __onSuitSelected( self, pyBtnSuit ) :
		"""
		选择某个套装
		"""
		#if pyBtnSuit.selected == True : return							# 还是之前选择的套装，不处理
		if BigWorld.isKeyDown( KEY_LALT ) or \
			BigWorld.isKeyDown( KEY_RALT ) :							# 按住Alt键单击，只更换选择
				pyBtnSuit.selected = True
				return
		if pyBtnSuit.suitName != "" : 									# 未保存过的组合不处理
			player = BigWorld.player()
			if player.state == csdefine.ENTITY_STATE_FIGHT : 			# 战斗状态不能进行换装
				player.statusMessage( csstatus.OKS_FORBIDDEN_IN_FIGHTING )
				return
			if player.isDead() : 										# 死亡状态不能进行换装
				player.statusMessage( csstatus.OKS_FORBIDDEN_WHEN_DEAD )
				return
			if player.state != csdefine.ENTITY_STATE_FREE :				# 其他非自由状态，统一提示
				player.statusMessage( csstatus.OKS_SWITCH_IN_ERROR_STATE )
				return
			if self.__isSwitchLocked() :								# 换装操作CD中
				player.statusMessage( csstatus.OKS_COOL_DOWN )
				return
			if player.iskitbagsLocked() :								# 背包已被上锁
				player.statusMessage( csstatus.OKS_KIGBAG_LOCKED )
				return
			#self.__lockSwitch()
			INFO_MSG( "switch to suit %i" % pyBtnSuit.suitIdx )
			player.switchSuit( pyBtnSuit.suitIdx )
			pyBtnSuit.selected = True									# 选择该套装
		else :
			pyBtnSuit.selected = True									# 选择该套装
			self.__onSave()

	def __onSuitRClicked( self, pySuitBtn ) :
		"""
		右键点击套装按钮，重命名按钮
		"""
		if not ( BigWorld.isKeyDown( KEY_LALT ) or \
			BigWorld.isKeyDown( KEY_RALT ) ) :							# 只处理按住Alt键右击的情况
				return

		def renameCB( success, suitName ) :
			"""
			"""
			if success :
				self.__updateSuitBtn( pySuitBtn, suitName )
				BigWorld.player().renameSuit( pySuitBtn.suitIdx, suitName )

		suitName = pySuitBtn.suitName
		if suitName == "" :
			# "只能对已经保存过的组合重新命名。"
			showMessage( 0x0ec3, "", MB_OK, pyOwner = self )
		else :
			self.__requestInput( pySuitBtn, renameCB )

	# -------------------------------------------------
	def __onBtnMouseEnter( self, pyBtn ) :
		"""
		鼠标进入按钮
		"""
		toolbox.infoTip.showToolTips( pyBtn, pyBtn.dsp )

	def __onBtnMouseLeave( self ) :
		"""
		鼠标离开按钮
		"""
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def __requestInput( self, pySuitBtn, callback ) :
		"""
		请求输入套装名称
		"""
		def inputNameCB( res, text ) :
			"""
			名称输入回调
			"""
			success = False
			if res == DialogResult.OK :
				text = text.strip()
				if len( text ) > 14 :
					# 您输入的名称过长
					showAutoHideMessage( 3.0, 0x0ec2, mbmsgs[0x0c22] )
				#elif not rds.wordsProfanity.isPureString( text ) :
				#	# "名称不合法！"
				#	showAutoHideMessage( 3.0, 0x0e08, mbmsgs[0x0c22] )
				elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
					# "输入的名称有禁用词汇!"
					showAutoHideMessage( 3.0, 0x0e09, mbmsgs[0x0c22] )
				else :
					if text == "" :
						# 没有输入则使用默认名称
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
		更新套装按钮
		"""
		if suitName == "" :												# 如果没有保存过套装
			pyBtnSuit.text = ""											# 则使用默认的浮动提示文本
			pyBtnSuit.dsp = labelGather.getText( "PlayerInfo:main", "dspUnused" )
		else :
			pyBtnSuit.text = pyBtnSuit.suitIdx
			pyBtnSuit.dsp = suitName
		pyBtnSuit.suitName = suitName

	def __lockSuitBtns( self, locked ) :
		"""
		锁定/解锁换装和保存按钮
		"""
		enable = not locked
		self.__pyBtns["btn_save"].enable = enable
		for pySuitBtn in self.__pySelector.pySelectors :
			if pySuitBtn.selected : continue							# 不改变当前选择的套装按钮
			pySuitBtn.enable = enable

	# -------------------------------------------------
	def __lockSwitch( self ) :
		"""
		锁定换装操作
		"""
		if self.__isSwitchLocked() : return								# 跟当前状态相同，不需重新设置
		self.__swLockCBID = BigWorld.callback( Const.ONE_KEY_SUIT_CD_TIME, self.__unlockSwitch )

	def __unlockSwitch( self ) :
		"""
		解锁换装操作
		"""
		if not self.__isSwitchLocked() : return							# 跟当前状态相同，不需重新设置
		BigWorld.cancelCallback( self.__swLockCBID )
		self.__swLockCBID = 0

	def __isSwitchLocked( self ) :
		"""
		检查当前换装操作的锁定状态
		"""
		player = BigWorld.player()
		cdid = Const.ONE_KEY_SUIT_CD_ID
		endTime = player.getCooldown( cdid )[3]
		return endTime > Time.Time.time()

	# -------------------------------------------------
	def __getSuitDatas( self ) :
		"""
		获取角色身上的装备UID
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
		服务器通知初始化套装
		"""
		for pyBtnSuit in self.__pySelector.pySelectors :
			suitData = suitDatas.get( pyBtnSuit.suitIdx, {} )
			suitName = suitData.get( "suitName", "" )
			self.__updateSuitBtn( pyBtnSuit, suitName )
			if pyBtnSuit.suitIdx == selIndex :
				pyBtnSuit.selected = True

	def updateSuit( self, suitIdx, suitName ) :
		"""
		更新套装
		"""
		for pyBtnSuit in self.__pySelector.pySelectors :
			if pyBtnSuit.suitIdx == suitIdx :
				self.__updateSuitBtn( pyBtnSuit, suitName )
				break

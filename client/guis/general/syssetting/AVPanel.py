# -*- coding: gb18030 -*-
# implement Audio and Video setting panel
# written by ganjinxing 2009-9-28

import csol
from bwdebug import *
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.ODComboBox import ODComboBox
from guis.controls.RichText import RichText
from guis.controls.ODComboBox import InputBox
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.TrackBar import HTrackBar
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.common.GUIBaseObject import GUIBaseObject
from LabelGather import labelGather
import ResMgr
from MapMgr import mapMgr
import Language
import event.EventCenter as ECenter

class AVPanel( TabPanel ):

	_CKBOX = ResMgr.openSection( "guis_v2/controls/checkbox/medium/leftbox.gui" )

	__TERRAIN_SPECULAR		=	"TERRAIN_SPECULAR"								# 地形泛光	[('ON', True), ('OFF', True)]
	__SKY_LIGHT_MAP			=	"SKY_LIGHT_MAP"									# 天空扭曲 	[('ON', True), ('OFF', True)]
	__SHADER_VERSION_CAP	=	"SHADER_VERSION_CAP"							# 高级光照 [('ON', True), ('OFF', True)]
	__TEXTURE_QUALITY		=	"TEXTURE_QUALITY"								# 贴图精度	[('HIGH', True), ('MEDIUM', True), ('LOW', True)]
	__TEXTURE_COMPRESSION	=	"TEXTURE_COMPRESSION"							# 贴图压缩	[('OFF', True), ('ON', True)]
	__MORPH_VERTICES		=	"MORPH_VERTICES"								# [('OFF', True), ('ON', True)]
	__SHADOWS_QUALITY		=	"REALTIME_SHADOWS_QUALITY"								# 阴影精度	[('HIGH', True), ('MEDIUM', True), ('LOW', True), ('OFF', True)]
	__SHADOWS_COUNT			=	"SHADOWS_COUNT"									# 阴影数量	[('64', True), ('32', True), ('16', True), ('8', True), ('4', True), ('2', True), ('1', True), ('0', True)]
	__HEAT_SHIMMER			=	"HEAT_SHIMMER"									# 热扭曲	[('ON', True), ('OFF', True)]
	__BLOOM_FILTER			=	"BLOOM_FILTER"									# 全屏泛光	[('ON', True), ('OFF', True)]
	__FOOT_PRINTS			=	"FOOT_PRINTS"									# 脚印		[('ON', True), ('OFF', True)]
	__WATER_QUALITY			=	"WATER_QUALITY"									# 水面精度	[('HIGH', True), ('MEDIUM', True), ('LOW', True), ('LOWEST', True), ('ORDINARY', True)]
	__WATER_SIMULATION		=	"WATER_SIMULATION"								# [('HIGH', True), ('LOW', True), ('OFF', True)]
	__FAR_PLANE				=	"FAR_PLANE"										# 游戏视距 	[('FAR', True), ('MEDIUM', True), ('NEAR', True)]
	__FLORA_DENSITY			=	"FLORA_DENSITY"									# 花草数量	[('VERY_HIGH', True), ('HIGH', True), ('MEDIUM', True), ('LOW', True), ('OFF', True)]
	__FXAA_PRESET			=   "FXAA_PRESET"									# 抗锯齿  [('1', True), ('2', True), ('3', True), ('4', True), ('5', True), ('6', True)]
	__PARTICLES_COUNT		= 	"PARTICLES_COUNT"								# 粒子数量 [1000, 100, 30]
	__PRE_DIY				= 	"PRE_DIY"										# 预设定义效果[高、中、低、自定义]
	__REALTIME_SHADOW		= 	"REALTIME_SHADOW"								# 实时阴影 [('ON', True), ('OFF', True)]

	__GRAPHICS_PREFS = {	"TEXTURE_QUALITY":[labelGather.getText( "gamesetting:avPl", "high" ),
											labelGather.getText( "gamesetting:avPl", "medium" ),
											labelGather.getText( "gamesetting:avPl", "low" )],
							"REALTIME_SHADOWS_QUALITY":[labelGather.getText( "gamesetting:avPl", "high" ),
											labelGather.getText( "gamesetting:avPl", "medium" ),
											labelGather.getText( "gamesetting:avPl", "low" ),],
							"SHADOWS_COUNT":['x64','x32','x16','x8','x4','x2','x1',labelGather.getText( "gamesetting:avPl", "off" )],
							"WATER_QUALITY"	:[labelGather.getText( "gamesetting:avPl", "very_high"),
											labelGather.getText( "gamesetting:avPl", "high" ),
											labelGather.getText( "gamesetting:avPl", "medium" ),
											labelGather.getText( "gamesetting:avPl", "low" ),
											labelGather.getText( "gamesetting:avPl", "lowest" )],
							"FAR_PLANE"		:[labelGather.getText( "gamesetting:avPl", "far"),
											labelGather.getText( "gamesetting:avPl", "medium"),
											labelGather.getText( "gamesetting:avPl", "near"),
											labelGather.getText( "gamesetting:avPl", "setbymap")],
							"FLORA_DENSITY"	:[labelGather.getText( "gamesetting:avPl", "very_high"),
											labelGather.getText( "gamesetting:avPl", "high"),
											labelGather.getText( "gamesetting:avPl", "medium"),
											labelGather.getText( "gamesetting:avPl", "low"),
											labelGather.getText( "gamesetting:avPl", "lowest")],
							"FXAA_PRESET"	:[labelGather.getText( "gamesetting:avPl", "off" ), "x2","x4", "x8", "x16", "x32"],
							"PARTICLES_COUNT":[labelGather.getText( "gamesetting:avPl", "high"),
											labelGather.getText( "gamesetting:avPl", "medium"),
											labelGather.getText( "gamesetting:avPl", "low")],
							"PRE_DIY"		:[labelGather.getText( "gamesetting:avPl", "high"),
											labelGather.getText( "gamesetting:avPl", "medium"),
											labelGather.getText( "gamesetting:avPl", "low"),
											labelGather.getText( "gamesetting:avPl", "diy")]
							}
	__FOG_DISTANCE = { 0:( 250, 380 ), 1:( 150, 230 ), 2:( 70, 130 ) }
	__PART_COUNTS = { 0: 1000, 1:100, 2:30}

	__GRAPHICS_DIYS = { __SKY_LIGHT_MAP			:( "ckbox0_cloudShadow", [0, 0, 1] ),
					__BLOOM_FILTER 				:( "ckbox0_wndFLight", [0, 0, 0] ),
					__TERRAIN_SPECULAR 			:( "ckbox0_groundFLight", [0, 1, 1] ),
					__TEXTURE_QUALITY  			:( "odcbox0_txQA", [0, 1, 2] ),
					__FLORA_DENSITY				:( "odcbox0_gfDS", [0, 2, 4] ),
					__WATER_QUALITY			  	:( "odcbox0_wtPRE", [0, 1, 4] ),
					__SHADOWS_COUNT				:( "odcbox0_sdCT", [0, 2, 7] ),
					__SHADOWS_QUALITY			:( "odcbox0_sdPRE", [0, 1, 2] ),
					__SHADER_VERSION_CAP		:( "ckbox0_rmPRE", [0, 1, 1] ),
					__FXAA_PRESET				:( "odcbox0_fpRET", [5, 2, 0] ),
					__FAR_PLANE					:( "odcbox0_frPLT", [0, 1, 2] ),
					__PARTICLES_COUNT			:( "odcbox0_psCUT", [0, 1, 2] ),
					__REALTIME_SHADOW			:( "ckbox0_rtSAW",[0, 1, 1] ),
				}

	__cc_space_path	 =  "universes/%s/space.settings"

	def __init__( self, panel, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/avPanel.gui" )
		uiFixer.firstLoadFix( panel )
		TabPanel.__init__( self, panel, pyBinder )
		self.__tempDataDict = {}												# 临时保存玩家的更改需求

		self.__audioSect = rds.userPreferences["audiosetting"]
		self.__cfgPath = ""
		self.__cfgSect = None
		self.__accountName = ""
		self.__oldSect = {}

		self.__stCKBoxs = {}
		self.__dynCKBoxs = {}
		self.__stTKBars = {}
		self.__dynTKBars = {}
		self.__dynODBoxs = {}
		self.__pyRtWarn = None
		self.__pySpliter = None

		self.changed = False
		self.__initialize( panel )


	#-----------------------------------------------------------------
	# pravite
	#-----------------------------------------------------------------
	def __initialize( self, panel ):
		self.__defSettingSect = Language.openConfigSection( "config/client/avpanelsetting.xml" )
		assert self.__defSettingSect is not None, "can't find avpanel default setting in world setting config file!"
		# 分辨率
		self.__pyCMBResolution = ODComboBox( panel.cmb_Resl, ODInputBox )
		self.__pyCMBResolution.onItemSelectChanged.bind( self.__onResolutionSelected )
		self.__pyCMBResolution.ownerDraw = True
		self.__pyCMBResolution.onViewItemInitialized.bind( self.__initCBItem )
		self.__pyCMBResolution.onDrawItem.bind( self.__onCBItemDraw )
		self.__pyCMBResolution.autoSelect = False

		self.__initElements()										# 初始化其他界面元素
		self.__resetResolution()
		self.__refurbishAudio()

		# 背景音效默认打开
		self.__audioSect.writeFloat( "bgeffectvolume", 1.0 )
		self.__audioSect.writeBool( "switchbgeffect", True )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.stResl, "gamesetting:avPl", "stResl" )
		labelGather.setLabel( panel.frame_video.bgTitle.stTitle, "gamesetting:avPl", "stVideoTitle" )
		labelGather.setLabel( panel.frame_audio.bgTitle.stTitle, "gamesetting:avPl", "stAudioTitle" )

	def __initElements( self ) :
		elmsMap = {
			( 20, 50, 232, 24, 2 ) : [
				( "ckbox1_wndMode", ( "wndMode", BigWorld.isVideoWindowed(), self.__onWndModeChecked ) ),
				( "ckbox1_vSyn", ( "vSyn", BigWorld.isVideoVSync(), self.__onSyncChecked ) ),
				],
			( 10, 80, 0, 32, 1) : [( "odcbox0_peDiy", ( "peDiy",  "PRE_DIY" ) )],
			( 70, 110, 0, 24, 1) : [( "uispt_spliter", ( "spliter",  "guis/general/questlist/spliter.gui" ) )],
			( 20, 115, 237, 24, 2 ):[
				( "ckbox0_wndFLight", ( "wndFLight", "BLOOM_FILTER" ) ),
				( "ckbox0_groundFLight", ( "groundFLight", "TERRAIN_SPECULAR" ) ),
				( "ckbox0_cloudShadow", ( "cloudShadow", "SKY_LIGHT_MAP" ) ),
				( "ckbox0_rmPRE", ("rmPRE", "SHADER_VERSION_CAP") ),
				( "ckbox0_rtSAW", ("rtSAW", "REALTIME_SHADOW") ),
			],# ( 42,60 )
			( 15, 185, 180, 28, 2 ) : [	# name, ltext, rtext, stepCount, type
				( "odcbox0_txQA", ( "txQA", "TEXTURE_QUALITY" ) ),
				( "odcbox0_gfDS", ("gfDS", "FLORA_DENSITY") ),
				( "odcbox0_wtPRE", ("wtPRE", "WATER_QUALITY") ),
				( "odcbox0_sdCT", ("sdCT", "SHADOWS_COUNT") ),
				( "odcbox0_sdPRE", ("sdPRE", "REALTIME_SHADOWS_QUALITY") ),
				( "odcbox0_fpRET", ("fpRET", "FXAA_PRESET") ),
				( "odcbox0_frPLT", ("frPLT", "FAR_PLANE") ),
				( "odcbox0_psCUT", ( "psCUT", "PARTICLES_COUNT") ),
			],# ( 34, 140 )
			( 15, 315, 0, 28, 1 ): [( "rtext0_warRT", ( "warRT",  ) )],
			( 18, 362, 0, 28, 1 ) : [			# name, ltext, rtext, stepCount, value, handler
				( "tkbar1_bgMU", ( "bgMU", "stLeft1", "stRight1", 20, rds.soundMgr.bgVol, self.__onVolSlided ) ),
				( "tkbar1_sceneMU", ( "sceneMU", "stLeft1", "stRight1", 20, rds.soundMgr.effVol, self.__onEffSlided ) ),
				( "tkbar1_totalMU", ( "totalMU", "stLeft1", "stRight1", 20, rds.soundMgr.masterVol, self.__onTotalSlided ) ),
			],# ( 26,364 )
		}
		elmFactory = {
			"tkbar0" : self.__createDynHTBar,
			"tkbar1" : self.__createStHTBar,
			"ckbox0" : self.__createDynCKBox,
			"ckbox1" : self.__createStCKBox,
			"odcbox0": self.__creatODCBox,
			"rtext0" : self.__creatRichText,
			"uispt"  : self.__creatUISplit,
		}
		for ( posX, posY, h_space, v_space, colCount ), elmsList in elmsMap.iteritems() :
			currRow = 0
			for index, ( keyStr, info ) in enumerate( elmsList ) :
				currCol = index % colCount
				elmInfo = keyStr.split( "_" )
				pyElm = elmFactory[ elmInfo[0] ]( keyStr, *info )
				if pyElm is None:continue
				self.addPyChild( pyElm, keyStr )
				pyElm.left = posX + currCol * h_space
				pyElm.top = posY + currRow * v_space
				currRow += currCol == colCount - 1 and 1 or 0

	def __resetResolution( self ) :
		"""
		初始化分辨率
		"""
		self.__pyCMBResolution.clearItems()
		listModes = self.__getSupportVedioMode()
		curIndex = BigWorld.videoModeIndex()
		for mode in listModes:
			self.__pyCMBResolution.addItem( mode )
			if curIndex == mode[0] :
				self.__pyCMBResolution.selItem = mode

	def __selCurrResolution( self ) :
		"""
		重新选择当前的屏幕分辨率
		"""
		currIndex = BigWorld.videoModeIndex()
		for mode in self.__pyCMBResolution.items :
			if currIndex == mode[0] :
				self.__pyCMBResolution.selItem = mode
				break
		else :
			ERROR_MSG( "Can't find corresponding resolution in combobox!" )

	def __createDynCKBox( self, uiName, text, type ) :
		"""
		用此方法来创建一些需要根据实际情况设置是否有效的checkBox
		"""
		activeIndex = self.__getActiveIndex( type )
		ckGui = GUI.load( "guis_v2/controls/checkbox/medium/leftbox.gui" )
		uiFixer.firstLoadFix( ckGui )
		pyCheckBox = CheckBoxEx( ckGui )
		ckGui.textureName = ""
		pyCheckBox.envLabel = type
		pyCheckBox.checked = not activeIndex
		self.__tempDataDict[type] = not activeIndex and 1 or 0
		pyCheckBox.text = labelGather.getText( "gamesetting:avPl", text )
		pyCheckBox.enable = activeIndex is not None
		pyCheckBox.onCheckChanged.bind( self.__onCBChecked )
		self.__dynCKBoxs[ uiName ] = pyCheckBox
		if type == self.__REALTIME_SHADOW:
			self.__dynCKBoxs[ "ckbox0_rtSAW" ].focus = False
			BigWorld.setGraphicsSetting( "REALTIME_SHADOW", activeIndex )
		elif type == self.__SHADER_VERSION_CAP:
			BigWorld.setGraphicsSetting( "SHADER_VERSION_CAP", activeIndex )
		return pyCheckBox

	def __createStCKBox( self, uiName, text, checked, handler ) :
		ckGui = GUI.load( "guis_v2/controls/checkbox/medium/leftbox.gui" )
		uiFixer.firstLoadFix( ckGui )
		ckGui.textureName = ""
		pyCheckBox = CheckBoxEx( ckGui )
		pyCheckBox.checked = checked
		pyCheckBox.text = labelGather.getText( "gamesetting:avPl", text )
		pyCheckBox.onCheckChanged.bind( handler )
		self.__stCKBoxs[ uiName ] = pyCheckBox
		return pyCheckBox

	def __createDynHTBar( self, uiName, text, ltext, rtext, stepCount, type ) :
		"""
		"""
		activeIndex = self.__getActiveIndex( type )
		pyTrackBar = MTrackBar()
		pyTrackBar.stepCount = stepCount
		pyTrackBar.setLabel = type
		value = 0
		if activeIndex is not None :
			value = float( ( stepCount - activeIndex ) ) / stepCount
		pyTrackBar.value = value
		pyTrackBar.dsp = labelGather.getText( "gamesetting:avPl", text )
		pyTrackBar.ltext = labelGather.getText( "gamesetting:avPl", ltext )
		pyTrackBar.rtext = labelGather.getText( "gamesetting:avPl", rtext )
		pyTrackBar.pyBar_.enable = activeIndex is not None
		pyTrackBar.pyBar_.onSlide.bind( self.__onTBSlided )
		self.__dynTKBars[ uiName ] = pyTrackBar
		return pyTrackBar

	def __createStHTBar( self, uiName, text, ltext, rtext, stepCount, value, handler  ) :
		"""
		"""
		pyTrackBar = MTrackBar()
		pyTrackBar.markVisible = False
		pyTrackBar.stepCount = stepCount
		pyTrackBar.value = value
		pyTrackBar.dsp = labelGather.getText( "gamesetting:avPl", text )
		pyTrackBar.ltext = labelGather.getText( "gamesetting:avPl", ltext )
		pyTrackBar.rtext = labelGather.getText( "gamesetting:avPl", rtext )
		pyTrackBar.pyBar_.onSlide.bind( handler )
		self.__stTKBars[ uiName ] = pyTrackBar
		return pyTrackBar

	def __creatODCBox( self, uiName, text, label ):
		"""
		创建下拉框控件
		"""
		activeIndex = self.__getActiveIndex( label )
		options = self.__GRAPHICS_PREFS.get( label, [] )
		if len( options ):
			pyODCBox = TextODCBox( label, self )
			pyODCBox.title = labelGather.getText( "gamesetting:avPl", text )
			pyODCBox.addOptions( options )
			if activeIndex is not None:
				pyODCBox.selOption = activeIndex
			self.__dynODBoxs[uiName] = pyODCBox
			return pyODCBox

	def __creatRichText( self, uiName, text ):
		self.__pyRtWarn = RichText()
		self.__pyRtWarn.text = labelGather.getText( "gamesetting:avPl", text )
		self.__pyRtWarn.foreColor = 252.0, 235.0, 179.0
		return self.__pyRtWarn

	def __creatUISplit( self, uiName, text, path ):
		spliter = GUI.load( path )
		uiFixer.firstLoadFix( spliter )
		self.__pySpliter = PyGUI( spliter )
		return self.__pySpliter

	def __initCBItem( self, pyViewItem ) :
		"""
		"""
		pyText = StaticText()
		pyViewItem.addPyChild( pyText )
		pyText.left = 3.0
		pyText.middle = pyViewItem.height / 2
		pyViewItem.pyText = pyText

	def __onCBItemDraw( self, pyViewItem ) :
		pyPanel = pyViewItem.pyPanel
		pyViewItem.pyText.font = pyPanel.font
		pyViewItem.pyText.text = pyViewItem.listItem[4]
		if pyViewItem.selected :
			pyViewItem.pyText.color = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyText.color = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyText.color = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor

	# -------------------------------------------------
	# audio about
	# -------------------------------------------------
	def __onVolSlided( self, value ) :
		rds.soundMgr.setBgVol( value )
		self.__audioSect.writeFloat( "vocalityvolume", value )
		bgPlay = value > 0.001
		if bgPlay != rds.soundMgr.getAudioval( "switchvocality" ) :
			rds.soundMgr.setBgPlay( bgPlay )
			self.__audioSect.writeBool( "switchvocality", bgPlay )
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __onEffSlided( self, value ) :
		rds.soundMgr.setVocalityVol( value )
		self.__audioSect.writeFloat( "effectvolume", value )
		effPlay = value > 0.001
		if effPlay != rds.soundMgr.getAudioval( "switcheffect" ) :
			rds.soundMgr.setEffPlay( effPlay )
			self.__audioSect.writeBool( "switcheffect", effPlay )
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __onTotalSlided( self, value ) :
		rds.soundMgr.setMasterVol( value )
		self.__audioSect.writeFloat( "mastervolume", value )
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __refurbishAudio( self ):
		for tag in self.__audioSect.keys() :
			audioVal = rds.soundMgr.getAudioval( tag )
			self.__oldSect[tag] = audioVal

	def hide(self):
		pass

	def __rollBackAudioSet( self ):
		"""
		撤销此次对音频的修改
		"""
		value = self.__oldSect["vocalityvolume"]
		self.__stTKBars["tkbar1_bgMU"].value = value
		rds.soundMgr.setBgVol( value )
		bgPlay = value > 0.001
		if bgPlay != rds.soundMgr.getAudioval( "switchvocality" ) :
			rds.soundMgr.setBgPlay( bgPlay )

		value = self.__oldSect["effectvolume"]
		self.__stTKBars["tkbar1_sceneMU"].value = value
		rds.soundMgr.setVocalityVol( value )
		effPlay = value > 0.001
		if effPlay != rds.soundMgr.getAudioval( "switcheffect" ) :
			rds.soundMgr.setEffPlay( effPlay )

		value = self.__oldSect["mastervolume"]
		self.__stTKBars["tkbar1_totalMU"].value = value
		rds.soundMgr.setMasterVol( value )

		for tag, value in self.__oldSect.iteritems():
			rds.soundMgr.rollBackSect( tag, value )

	# -------------------------------------------------
	# video about
	# -------------------------------------------------
	def __onResolutionSelected( self, index ):
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __onWndModeChecked( self, checked ):
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __setPreDiy( self, index ):
		for label, tuples in self.__GRAPHICS_DIYS.items():
			activeIndex = 0
			tempData = self.__tempDataDict.get( label, None )
			if tempData is None:continue
			if index < 3:						#高中低
				activeIndex = tuples[1][index]
			else:								#自定义
				activeIndex = self.__getDiyActiveIndex( label )		#从账号下的配置读取
				if activeIndex < 0:
					activeIndex = self.__getActiveIndex( label )		#从option下读取
			self.__tempDataDict[label] = activeIndex
			dynCKBox = self.__dynCKBoxs.get( tuples[0], None )
			if dynCKBox:
				dynCKBox.checked = not bool( activeIndex )
				dynCKBox.enable = index >= 3
			dynODBox = self.__dynODBoxs.get( tuples[0], None )
			if dynODBox:
				dynODBox.selOption = activeIndex
				dynODBox.pyODCBox.enable = index >= 3

	def __onCBChecked( self, pyCBox, checked ):
		optionLabel = pyCBox.envLabel
		self.__tempDataDict[ optionLabel ] = not checked and 1 or 0
		if optionLabel == self.__SHADER_VERSION_CAP:
			self.__dynCKBoxs["ckbox0_rtSAW"].checked = checked
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __onTBSlided( self, pyTrackBar, value ):
		count = pyTrackBar.stepCount
		index = int( round( count*( 1.0-value ) ) )
		setLabel = pyTrackBar.pyBinder.setLabel
		if setLabel == self.__SHADOWS_COUNT :
			index = { 0:0, 1:1, 2:2, 3:3, 4:6 }[index]
		self.__tempDataDict[ pyTrackBar.pyBinder.setLabel ] = index
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __onSyncChecked( self, checked ):
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	def __getSupportVedioMode( self ) :
		"""
		获取当前的屏幕分辨率
		"""
		listModes = BigWorld.listVideoModes()
		curMode = csol.getCurrentDisplayModes() 						# 当前系统的分辨率
		isWindowed = BigWorld.isVideoWindowed() 						# 是否为窗口模式
		removeList = []
		if isWindowed: 													# 窗口模式
			for iMod in listModes:
				if iMod[1] < 1024 or iMod[1] > curMode[0]:
					removeList.append( iMod )
		else: 															# 全屏模式
			for iMod in listModes:
				if iMod[1] < 1024:
					removeList.append( iMod )
		for iRemove in removeList:
			listModes.remove( iRemove )
		return listModes

	def __setWndMode( self ) :
		"""
		设置窗口/全屏模式及分辨率
		"""
		expectVideoMode = self.__pyCMBResolution.selItem								# 欲设置的分辨率
		if expectVideoMode is None : return
		currVideoIndex = BigWorld.videoModeIndex()
		currVideoMode = BigWorld.listVideoModes()[currVideoIndex]						# 当前分辨率
		currWndMode = BigWorld.isVideoWindowed()										# 当前的窗口模式
		expectWndMode  = self.__stCKBoxs["ckbox1_wndMode"].checked						# 欲设置的窗口模式
		if expectVideoMode[0] != currVideoMode[0] or currWndMode != expectWndMode :
			BigWorld.changeVideoMode( expectVideoMode[0], expectWndMode )
			if expectWndMode :															# 如果设置为窗口模式
				BigWorld.resizeWindow( expectVideoMode[1], expectVideoMode[2] )			# 则重设窗口尺寸
			self.__resetResolution()

	def __setSyncStatus( self ) :
		"""
		设置帧同步状态
		"""
		expectStatus = self.__stCKBoxs["ckbox1_vSyn"].checked
		if expectStatus != BigWorld.isVideoVSync():						# 帧同步状态如果有改变
			BigWorld.setVideoVSync( expectStatus )

	def __checkPending( self ):
		if BigWorld.hasPendingGraphicsSettings():
			BigWorld.callback( 0.1, BigWorld.commitPendingGraphicsSettings )

	def __resetVideoOptions( self ):
		"""
		重设所有视频选项
		"""
		self.__stCKBoxs["ckbox1_vSyn"].checked = BigWorld.isVideoVSync()

		self.__stCKBoxs["ckbox1_wndMode"].checked = BigWorld.isVideoWindowed()

		for pyCKBox in self.__dynCKBoxs.itervalues() :
			if pyCKBox.enable :
				pyCKBox.checked = not self.__getActiveIndex( pyCKBox.envLabel )

		for pyTKBar in self.__dynTKBars.itervalues() :
			if pyTKBar.enable :
				stepCount = pyTKBar.stepCount
				pyTKBar.value = ( stepCount - self.__getActiveIndex( pyTKBar.setLabel ) ) * ( 1.0 / stepCount )

		self.__tempDataDict = {}
		self.__selCurrResolution()													# 重新选中当前的分辨率

	def __getActiveIndex( self, setLabel ):
		for label, active, options in BigWorld.graphicsSettings():
			if label == setLabel:
				return active
		if setLabel == self.__PARTICLES_COUNT:
			psCount = 100 #BigWorld.getWatcher( "Chunks/Particles Lod/MAX pixie count" )
			for index, count in self.__PART_COUNTS.items():
				if int( psCount ) == count:
					return index
		return None
	
	def __getDiyActiveIndex( self, setLabel ):
		"""
		从角色账号下配置读取
		"""
		if not self.__cfgSect: return -1
		grapSect = self.__cfgSect["diyGraphicsPreferences"]
		if not grapSect: return -1
		for label, subSect in grapSect.items():
			if label == setLabel:
				return subSect.asInt
		return -1

	def __setAvDiy( self ):
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		self.__accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		self.__cfgPath = "account/%s/AvDiy.xml"%self.__accountName
		self.__cfgSect = ResMgr.openSection( self.__cfgPath )
		if self.__cfgSect:
			diyIndex = self.__dynODBoxs["odcbox0_peDiy"].selOption
			self.__cfgSect.writeInt( "diyIndex", diyIndex )
			self.__cfgSect.save()
		ResMgr.purge( self.__cfgPath )

	def __getMapFogScales( self ):
		try:
			curWholeArea = BigWorld.player().getCurrWholeArea()
			mapFolder = curWholeArea.spaceFolder
			spaceConfig = self.__cc_space_path % mapFolder
			spSect = ResMgr.openSection( spaceConfig )
			if spSect is None :
				ERROR_MSG( "get space bound error:", spaceConfig )
			skyPath = spSect.readString( "timeOfDay" )
			skyCfg = ResMgr.openSection( skyPath )
			if skyCfg:
				fogNearScale = skyCfg["fog"].readInt( "fogNearScale" )
				fogFarScale = skyCfg["fog"].readInt( "fogFarScale" )
				return ( fogNearScale, fogFarScale )
		except:
			return None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setDefault( self ) :
		"""
		"""
		self.__stCKBoxs["ckbox1_wndMode"].checked = bool( self.__defSettingSect.readInt( "wndMode" ) )   #窗口模式
		resolutionSect = self.__defSettingSect["resolution"]
		modeIndex = resolutionSect.readInt( "modeIndex" )
		modeWidth = resolutionSect.readInt( "windowWidth" )
		modeHeight = resolutionSect.readInt( "windowHeight" )
		modeRoot = resolutionSect.readInt( "windowRoot" )
		mode = str( modeWidth ) + 'x' + str( modeHeight ) + 'x' + str( modeRoot )
		self.__pyCMBResolution.selItem = ( modeIndex, modeWidth, modeHeight, modeRoot, mode )   		 #分辨率
		self.__stCKBoxs["ckbox1_vSyn"].checked = bool( self.__defSettingSect.readInt( "vSyn" ) )         #垂直同步
		self.__dynODBoxs["odcbox0_peDiy"].selOption = self.__defSettingSect.readInt( "peDiy" )
		self.__setPreDiy( self.__defSettingSect.readInt( "peDiy" ) )  		 					 		 #预定义效果
		self.__stTKBars["tkbar1_bgMU"].value = self.__defSettingSect.readFloat( "bgMU" )
		self.__onVolSlided( self.__defSettingSect.readFloat( "bgMU" ) )    						 		 #背景音乐
		self.__stTKBars["tkbar1_sceneMU"].value = self.__defSettingSect.readFloat( "sceneMU" )
		self.__onEffSlided( self.__defSettingSect.readFloat( "sceneMU" ) )   							 #场景音效
		self.__stTKBars["tkbar1_totalMU"].value = self.__defSettingSect.readFloat( "totalMU" )
		self.__onTotalSlided( self.__defSettingSect.readFloat( "totalMU" ) ) 						 	 #音效音量
		self.onOK()

	def onApplied( self ) :
		self.onOK()

	def checkLabelInGraphicsSetting( self, optionType ):
		graphicsSettings = BigWorld.graphicsSettings()
		isChecked = False
		for settings in graphicsSettings:
			if settings[0] == optionType:
				isChecked = True
				break
		return isChecked

	def setGraphicsSetting( self ):
		diyIndex = self.__dynODBoxs["odcbox0_peDiy"].selOption
		graphSect = None
		isCreateDiySect = diyIndex == 3 and self.__cfgSect
		for optionType, value in self.__tempDataDict.iteritems() :
			if optionType == self.__PARTICLES_COUNT: #设置粒子数量
				psCount = self.__PART_COUNTS.get( value, 100 )
#				BigWorld.setWatcher( "Chunks/Particles Lod/MAX pixie count", psCount )
			elif optionType == self.__BLOOM_FILTER:
				try:
					BigWorld.setWatcher( "Client Settings/fx/Bloom/colour attenuation", 0.95 )
				except:	
					ERROR_MSG( "exe not have colour attenuation" )
					continue
			elif optionType == self.__PRE_DIY:
				continue
			else:
				if optionType == self.__FAR_PLANE : #雾化距离与裁剪距离绑定
					dstTuple = self.__FOG_DISTANCE.get( value, None )
					setByMap = BigWorld.getWatcher( "Client Settings/std fog/fogProfileFromMap" ) == "true" and True or False
					if value == 3: #获取当前地图配置数据
						setByMap = True
						dstTuple = self.__getMapFogScales()
						if dstTuple is None:
							dstTuple = self.__FOG_DISTANCE.get( 1, None )
					if dstTuple:
						csol.setFogScale( dstTuple[0], dstTuple[1], setByMap )
			if not self.checkLabelInGraphicsSetting( optionType ):
				ERROR_MSG( "graphics label %s not in graphicsSetting"%optionType )
				continue
			try:
				BigWorld.setGraphicsSetting( optionType, value )
			except ValueError, ve:
				ERROR_MSG( "GraphicsSetting (%s, %d) error!" % (optionType, value) )
			if isCreateDiySect:
				if self.__cfgSect["diyGraphicsPreferences"]:
					self.__cfgSect.writeInt( "diyGraphicsPreferences/%s"%optionType, value )
				else:
					self.__cfgSect.createSection( "diyGraphicsPreferences/%s"%optionType )
					self.__cfgSect.writeInt( "diyGraphicsPreferences/%s"%optionType, value )
			self.__cfgSect.save()

	def onOK( self ) :
		self.__setSyncStatus()
		self.setGraphicsSetting()
		BigWorld.savePreferences()							# 保存系统选项设置
		self.__refurbishAudio()								# 保存新的音频设置
		if BigWorld.graphicsSettingsNeedRestart():			# 需要重启
			# "部分图形设置需要重新启动，将于下次客户端运行时生效。"
			showMessage( 0x0881, "", MB_OK )
		self.__setWndMode()									# 设置窗口模式
		self.__checkPending()
		self.__setAvDiy()
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", False )

	def onCancel( self ) :
		self.__resetVideoOptions()
		self.__rollBackAudioSet()
	
	def onEnterWorld( self ):
		pass

	def onActivated( self ) :
		"""
		所属窗口激活时被调用
		"""
		pass

	def onInactivated( self ) :
		pass

	def setTempGraphics( self, label, index ):
		self.__tempDataDict[label] = index
		if label == self.__PRE_DIY:
			self.__setPreDiy( index )
		else:
			for pyODBox in self.__dynODBoxs.itervalues():
				if pyODBox.label == label:
					pyODBox.selOption = index

	def onShow( self ):
		TabPanel.onShow( self )
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		printStackTrace()
		self.__accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		self.__cfgPath = "account/%s/AvDiy.xml"%self.__accountName
		self.__cfgSect = ResMgr.openSection( self.__cfgPath )
		diyIndex = 1
		if self.__cfgSect is None:
			self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
			self.__cfgSect.createSection( "diyIndex" )
			self.__cfgSect.writeInt( "diyIndex", diyIndex )
			self.__cfgSect.save()
		else:
			diyIndex = self.__cfgSect.readInt( "diyIndex" )
		ResMgr.purge( self.__cfgPath )
		self.__dynODBoxs["odcbox0_peDiy"].selOption = diyIndex
		isByMap = BigWorld.getWatcher( "Client Settings/std fog/fogProfileFromMap" )
		if isByMap == "true": #由地图指定
			self.__dynODBoxs["odcbox0_frPLT"].selOption = 3
		self.__setPreDiy( diyIndex )
		self.__setSyncStatus()
		self.setGraphicsSetting()
		BigWorld.savePreferences()							# 保存系统选项设置
		self.__setWndMode()									# 设置窗口模式

	def onResolutionChanged( self, preReso ):
		"""
		分辨率改变
		"""
		curIndex = BigWorld.videoModeIndex()
		for mode in self.__pyCMBResolution.items:
			if curIndex == mode[0] :
				self.__pyCMBResolution.selItem = mode

class ODInputBox( InputBox ) :

	def __init__( self, box, pyCombo ) :
		InputBox.__init__( self, box, pyCombo )
		self.__viewItem = None

	def getViewItem_ ( self ) :
		"""
		获取当前 Box 中的内容（如果 readOnly 为 True，则它等于 selItem ）
		"""
		return self.__viewItem

	def setViewItem_( self, viewItem ) :
		"""
		设置当前 Box 中的内容（如果 readOnly 为 True，则它应该引起一个
		"""
		self.__viewItem = viewItem
		self.text = viewItem[4]

	def onItemSelectChanged_( self, index ) :
		"""
		选项改变时被调用
		"""
		if index < 0 :
			self.text = ""
			self.__viewItem = None
		else :
			self.__viewItem = self.pyComboBox.items[index]
			self.text = self.__viewItem[4]
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

class MTrackBar( GUIBaseObject ) :

	_dummy_section = ResMgr.openSection( "guis/general/syssetting/trackbar.gui" )

	def __init__( self, bar = None ) :
		if bar is None :
			bar = GUI.load( "guis/general/syssetting/trackbar.gui" )
			uiFixer.firstLoadFix( bar )
		GUIBaseObject.__init__( self, bar )
		self.__markVisible = True
		self.pyBar_ = HTrackBar( bar.trackBar, self )
		self.pyDsp_ = StaticText( bar.stDsp )
		self.pyDsp_.color = 252.0, 235.0, 179.0
		self.pyLST_ = StaticText( bar.stLSite )
		self.pyRST_ = StaticText( bar.stRSite )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearMarkers( self ) :
		for elmName, elm in self.gui.elements.items() :
			if "frm_mk_" in elmName :
				self.gui.removeElement( elm )

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getValue( self ) :
		return self.pyBar_.value

	def _setValue( self, value ) :
		self.pyBar_.value = value

	def _getMarkVisible( self ) :
		return self.__markVisible

	def _setMarkVisible( self, visible ) :
		self.__markVisible = visible
		for elmName, elm in self.gui.elements.items() :
			if "frm_mk_" in elmName :
				elm.visible = visible

	def _getStepCount( self ) :
		return self.pyBar_.stepCount

	def _setStepCount( self, count ) :
		self.pyBar_.stepCount = count
		if self.__markVisible :
			self.__clearMarkers()
			if count < 1 : return
			posX = self.pyBar_.pySlider_.width / 2.0
			maxLen = self.pyBar_.width - self.pyBar_.pySlider_.width
			perLen = maxLen / count
			for i in xrange( count + 1 ) :
				mark = GUI.Texture( "guis/general/syssetting/marker.dds" )
				mark.tileSize = 8, 8
				mark.size = 8, 4
				if i == count :
					mark.mapping = util.getGuiMapping( mark.tileSize, 0, 8, 4, 8 )
				else :
					mark.mapping = util.getGuiMapping( mark.tileSize, 0, 8, 0, 4 )
				self.gui.addElement( mark, "frm_mk_%i" % i )
				s_util.setFElemCenter( mark, self.pyBar_.left + posX + i * perLen )
				s_util.setFElemTop( mark, self.pyBar_.bottom + 1 )
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )

	value = property( _getValue, _setValue )
	stepCount = property( _getStepCount, _setStepCount )
	markVisible = property( _getMarkVisible, _setMarkVisible )
	dsp = property( lambda self : self.pyDsp_._getText(), lambda self, text : self.pyDsp_._setText( text ) )
	ltext = property( lambda self : self.pyLST_._getText(), lambda self, text : self.pyLST_._setText( text ) )
	rtext = property( lambda self : self.pyRST_._getText(), lambda self, text : self.pyRST_._setText( text ) )
	enable = property( lambda self : self.pyBar_.enable, lambda self, v : self.pyBar_._setEnable( v ) )

# --------------------------------------------------------------------------------
from guis.controls.StaticLabel import StaticLabel

class TextODCBox( PyGUI ):

	def __init__( self, label, pyBinder = None ) :
		box = GUI.load( "guis/general/syssetting/odcbox_short.gui" )
		if label == "PRE_DIY":
			box = GUI.load( "guis/general/syssetting/odcbox_long.gui" )
		uiFixer.firstLoadFix( box )
		PyGUI.__init__( self, box )
		self.label = label
		self.pyBinder = pyBinder
		self.__pyStTitle = StaticText( box.stTitle )
		self.__pyStTitle.text = ""
		self.__pyODCBox = ODComboBox( box.odcBox )
		self.__pyODCBox.onItemSelectChanged.bind( self.__onOptionSelected )
		self.__pyODCBox.ownerDraw = True
		self.__pyODCBox.onViewItemInitialized.bind( self.__onInitialized )
		self.__pyODCBox.onDrawItem.bind( self.__onDrawItem )
		self.__pyODCBox.autoSelect = False

	def __onInitialized( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.foreColor = 236, 218, 157
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel

	def __onDrawItem( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyLabel.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		pyLabel.text = pyViewItem.listItem

	def __onOptionSelected( self, index ):
		if index < 0:return
		self.pyBinder.setTempGraphics( self.label, index )
		self.__pyODCBox.pyBox_.text = self.__pyODCBox.items[index]
		ECenter.fireEvent( "EVT_ON_AVPANEL_CHANGED", True )


	def addOptions( self, options ):
		"""
		添加选择项
		"""
		self.__pyODCBox.addItems( options )

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTitle( self ) :
		return self.__pyStTitle.text

	def _setTitle( self, title ) :
		self.__pyStTitle.text = title

	def _getSelOption( self ):
		return self.__pyODCBox.selIndex

	def _setSelOption( self, index ):
		self.__pyODCBox.selIndex = index
		self.__pyODCBox.pyBox_.text = self.__pyODCBox.items[index]

	def _getPyODCBox( self ):
		return self.__pyODCBox

	title = property( _getTitle, _setTitle )
	selOption = property( _getSelOption, _setSelOption )
	pyODCBox = property( _getPyODCBox, )


# -*- coding: gb18030 -*-
#
# $Id: PropertyPanel.py,v 1.12 2008-06-27 03:18:55 huangyongwei Exp $

from bwdebug import *
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import ListItem
from config.Title import Datas as g_TitleData
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
import csdefine
import csconst
import Font

class TitlesPanel( TabPanel ):
	def __init__( self, titlePanel, pyBinder = None ):
		TabPanel.__init__( self, titlePanel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyTitles = {}
		self.__itemHeight = 0
		self.firstLog = True	#是为了区别是关闭窗口后第一次选择称号面板，还是在称号面板和其他面板之间切换
		self.__initPanel( titlePanel )

	def __initPanel( self, titlePanel ):
		labelGather.setLabel( titlePanel.selectedFrm.bgTitle.stTitle, "PlayerProperty:TitlePanel", "curSelTitle" )
		labelGather.setLabel( titlePanel.usedFrm.bgTitle.stTitle, "PlayerProperty:TitlePanel", "curUseTitle" )
		self.__pyTitlesList = ListPanel( titlePanel.titlesPanel.clipPanel, titlePanel.titlesPanel.sbar )
		self.__pyTitlesList.autoSelect = False
		self.__pyTitlesList.onItemSelectChanged.bind( self.__onTitleSelected )

		noTitle = GUI.load( "guis/general/playerprowindow/titlespanel/titleitem.gui" )
		pyNoTitle = TitleItem( noTitle ) #不使用称号
		self.__itemHeight = pyNoTitle.height
		pyNoTitle.text = labelGather.getText( "PlayerProperty:TitlePanel", "noTitle" )
		pyNoTitle.titleID = 0
		pyNoTitle.order = 0
		self.__pyTitles[0] = pyNoTitle
		pyNoTitle.active = True
		self.__pyTitlesList.addItem( pyNoTitle )

		for key, title in g_TitleData.iteritems():
			item = GUI.load( "guis/general/playerprowindow/titlespanel/titleitem.gui" )
			pyTitleItem = TitleItem( item )
			pyTitleItem.text = labelGather.getText( "PlayerProperty:TitlePanel", "notGetTitle" )
			pyTitleItem.titleID = key
			pyTitleItem.order = title["order"]
			self.__pyTitles[key] = pyTitleItem
			pyTitleItem.active = False
			self.__pyTitlesList.addItem( pyTitleItem )
		self.__pyTitlesList.sort( key = lambda pyTitle: pyTitle.order, reverse = False ) #按titleID排序

		self.__pyStTitleName = StaticText( titlePanel.stTitleName )
		self.__pyStTitleName.h_anchor = "CENTER"
		self.__pyStTitleName.text = ""

		self.__pySelTitleInfo = InfoPanel( titlePanel.selTitle )

		self.__pyUseTitleInfo = InfoPanel( titlePanel.curTitle )

		self.__pyBtnChange = Button( titlePanel.btnChange )
		self.__pyBtnChange.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnChange.enable = False
		self.__pyBtnChange.onLClick.bind( self.__onChangeTitle )
		labelGather.setPyBgLabel( self.__pyBtnChange, "PlayerProperty:TitlePanel", "btnChange" )

	# --------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_TITLE_ADD"] = self.__onRoleAddTitle #添加称号
		self.__triggers["EVT_ON_MASTER_INFO_UDATE"] = self.__onMasterTitleUpdate	# 更新师父称号
		self.__triggers["EVT_ON_ROLE_TITLE_REMOVE"] = self.__onRoleRemoveTitle #移除称号
		self.__triggers["EVT_ON_ENTITY_TITLE_CHANGED"] = self.__onRoleChangeTitle #称号改变
		self.__triggers["EVT_ON_ROLE_UPDATE_RELATION"] = self.__onRoleRelationUpdate
		self.__triggers["EVT_ON_ROLE_ALLY_TITLE_CHANGED"] = self.__onRoleAllyTitleChanged
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------------
	def __onRoleAddTitle( self, titleID, title ): #初始化已有称号
		player = BigWorld.player()
		if titleID in [csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]: #夫妻称号
			if player.couple_lover is None:return
			title = title%player.couple_lover.playerName
		elif titleID == csdefine.TITLE_TEACH_PRENTICE_ID:
			title = title%player.getMasterName()
		pyTitle = self.__pyTitles.get( titleID, None )
		if pyTitle is None:return
		pyTitle.active = True
		pyTitle.text = title
		self.__pyTitlesList.removeItem( pyTitle )
		self.__pyTitlesList.addItem( pyTitle, 1 )

	def __onRoleAllyTitleChanged( self, titleID, titleName ):
		"""
		玩家的结拜称号改变
		"""
		pyTitle = self.__pyTitles.get( titleID, None )
		if pyTitle is None:return
		pyTitle.active = True
		pyTitle.text = titleName

	def __onMasterTitleUpdate( self, masterName, masterDBID ):
		"""
		师父的数据更新
		"""
		for pyTitle in self.__pyTitlesList.pyItems:
			if pyTitle.titleID == csdefine.TITLE_TEACH_PRENTICE_ID:
				pyTitle.text = BigWorld.player().getAddTitle( csdefine.TITLE_TEACH_PRENTICE_ID ) % masterName
				break

	def __onRoleRelationUpdate( self, relationUID, relationStatus ):
		if relationStatus & csdefine.ROLE_RELATION_PRENTICE:
			for pyTitle in self.__pyTitlesList.pyItems:
				if pyTitle.titleID == csdefine.TITLE_TEACH_PRENTICE_ID:
					player = BigWorld.player()
					pyTitle.text = player.getAddTitle( csdefine.TITLE_TEACH_PRENTICE_ID ) % player.getMasterName()
					break

	def __onRoleRemoveTitle( self, titleID ):
		selPyTitle = self.__pyTitlesList.pySelItem
		for pyTitle in self.__pyTitlesList.pyItems:
			if pyTitle.titleID == titleID:
				pyTitle.active = False
				pyTitle.text = labelGather.getText( "PlayerProperty:TitlePanel", "notGetTitle" )
			if selPyTitle is not None and pyTitle.titleID == selPyTitle.titleID:
				self.__pyBtnChange.enable = False
				self.__pySelTitleInfo.onRemoveTitle()
		self.onEnterWorld()		# 刷新TitlesPanle

	def __onRoleChangeTitle( self, entity, oldTitle, titleName, titleColor = None ):
		if entity.id != BigWorld.player().id:return
		for titleID, pyTitle in self.__pyTitles.iteritems():
			if not pyTitle.active:continue
			if pyTitle.titleID != BigWorld.player().title: #已激活但没使用
				pyTitle.commonForeColor = ( 255, 255, 255, 255 )
				pyTitle.selectedForeColor = ( 255, 235, 143, 255 )
				pyTitle.highlightForeColor = ( 255, 235, 143, 255 )
			else: #使用
				pyTitle.commonForeColor = ( 99, 238, 85, 255 )
				pyTitle.selectedForeColor = ( 99, 238, 85, 255 )
				pyTitle.highlightForeColor = ( 99, 238, 85, 255 )
				self.__pyTitlesList.pySelItem = pyTitle
				self.__pyUseTitleInfo.setUseTitleInfo( titleID )
		if titleName == "":
			titleName = labelGather.getText( "PlayerProperty:TitlePanel", "noTitle" )
			self.__pyUseTitleInfo.setUseTitleInfo( 0 )
		self.__pyStTitleName.text = titleName

	def __onTitleSelected( self, pyTitle ):
		if pyTitle is None: return
		titleID = pyTitle.titleID
		self.__pyBtnChange.enable = pyTitle.active and BigWorld.player().title != titleID
		self.__pySelTitleInfo.setSelTitleInfo( pyTitle ) #设置选择的称号信息
		self.__setUsedTitleColor()
		
	def __setUsedTitleColor( self ):
		for title in self.__pyTitles.itervalues() :
			if title.titleID == BigWorld.player().title:
				title.commonForeColor = ( 99, 238, 85, 255 )
				title.selectedForeColor = ( 99, 238, 85, 255 )
				title.highlightForeColor = ( 99, 238, 85, 255 )

	def __onChangeTitle( self ):
		pySelTitle = self.__pyTitlesList.pySelItem
		if pySelTitle is None:return
		titleID = pySelTitle.titleID
		BigWorld.player().cell.selectTitle( titleID )

	# -------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def reset( self ):
		self.__pyBtnChange.enable = False
		for pyTitle in self.__pyTitlesList.pyItems:
			if pyTitle.titleID == 0:
				pyTitle.text = labelGather.getText( "PlayerProperty:TitlePanel", "noTitle" )
				pyTitle.active = True
			else:
				pyTitle.text = labelGather.getText( "PlayerProperty:TitlePanel", "notGetTitle" )
				pyTitle.active = False
		self.__pySelTitleInfo.onRemoveTitle()
		self.__pyUseTitleInfo.onRemoveTitle()
		self.__pyTitlesList.pySelIndex = 0
		self.firstLog = True
		self.__pyTitlesList.scroll = 0
		
	def onShow( self ):
		TabPanel.onShow( self )
		
		if self.__pyTitlesList.pySelItem is None : 
			self.firstLog = False
			return
		elif not self.__pyTitlesList.pySelItem.active :
			if not self.firstLog: return
			self.__pyTitlesList.pySelItem = None
			self.__pySelTitleInfo.onRemoveTitle()
			self.__pyTitlesList.scroll = 0
			self.firstLog = False			 
		else:
			if not self.firstLog : return	
			#将选择的称号显示在称号列表第一位
			scroll = self.__pyTitlesList.selIndex * self.__itemHeight
			self.__pyTitlesList.scroll = scroll
			self.firstLog = False

	def onEnterWorld( self ):
		player = BigWorld.player()
		titleName = player.titleName
		if titleName == "":
			titleName = labelGather.getText( "PlayerProperty:TitlePanel", "noTitle" )
		self.__pyStTitleName.text = titleName
		titles = player.titles
		for titleID in titles:
			title = g_TitleData.get( titleID, None )
			if title is None:continue
			titleName = title["name"]
			pyTitle = self.__pyTitles.get( titleID, None )
			if pyTitle is None:continue
			if titleID in [csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]: #夫妻称号
				if player.couple_lover is None:continue
				titleName = titleName%player.couple_lover.playerName
			elif titleID == csdefine.TITLE_TEACH_PRENTICE_ID:
				titleName = titleName%player.getMasterName()
			elif titleID == csdefine.TITLE_ALLY_ID:
				titleName = titleName%player.allyTitle
			pyTitle.text = titleName
			pyTitle.active = True
			if player.title == titleID:
				self.__pyUseTitleInfo.setUseTitleInfo( titleID )
				self.__setUsedTitleColor()
			self.__pyTitlesList.removeItem( pyTitle )
			self.__pyTitlesList.addItem( pyTitle, 1 )

# ----------------------------------------------------------------
from guis.controls.ListItem import SingleColListItem

class TitleItem( SingleColListItem ):
	def __init__( self, titleItem ):
		SingleColListItem.__init__( self, titleItem )
		self.pyText_.limning = Font.LIMN_NONE
		self.__title = ""
		self.titleID = -1
		self.order = -1
		self.__active = False #是否已经被激活

		self.commonBackColor = 255, 255, 255, 255
		self.highlightBackColor = 255, 255, 255, 255
		self.selectedBackColor = 255, 255, 255, 255

	def onStateChanged_( self, state ):
		SingleColListItem.onStateChanged_( self, state )
		return True

	def _getActive( self ):
		return self.__active

	def _setActive( self, active ):
		self.__active = active
		if active:
			self.commonForeColor = ( 255, 255, 255, 255 )
			self.selectedForeColor = ( 255, 235, 143, 255 )
			self.highlightForeColor = ( 255, 235, 143, 255 )
		else:
			self.commonForeColor = ( 0, 0, 0, 255 )
			self.selectedForeColor = ( 0, 0, 0, 255 )
			self.highlightForeColor = ( 0, 0, 0, 255 )

	def onMouseEnter_( self ):
		SingleColListItem.onMouseEnter_( self )
		return True

	def onMouseLeave_( self ):
		SingleColListItem.onMouseLeave_( self )
		return True


	active = property( _getActive, _setActive )

# --------------------------------------------------------------------
import skills
from ItemsFactory import SkillItem

class InfoPanel( PyGUI ):
	def __init__( self, infoPanel ):
		PyGUI.__init__( self, infoPanel )
		self.__pyRtInfo = CSRichText( infoPanel.rtInfo )
		self.__pyRtInfo.text = ""

		self.__pyRtCondit = CSRichText( infoPanel.rtCondit )
		self.__pyRtCondit.text = ""

		self.__pyRtUsage = CSRichText( infoPanel.rtUsage )
		self.__pyRtUsage.text = ""

	def setSelTitleInfo( self, pyTitle ):
		titleID = pyTitle.titleID
		active = pyTitle.active
		player = BigWorld.player()
		if titleID == 0:
			self.__pyRtInfo.text = ""
			self.__pyRtCondit.text = ""
			self.__pyRtUsage.text = ""
		else:
			if active:
				title = g_TitleData.get( titleID )
				if title is None:return
				description = title["description"]
				if titleID in [csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]:
					if player.couple_lover is None:return
					description = description%player.couple_lover.playerName
				skillID = title["skillID"]

				self.__pyRtInfo.text = PL_Font.getSource( description, fc = ( 255, 235, 143, 255 ) )

				conditText = PL_Font.getSource( labelGather.getText( "PlayerProperty:TitlePanel", "getApproach" ), fc = ( 30, 241, 234, 255 ) )
				condition = PL_Font.getSource( "%s"%title["description2"], fc = ( 255, 255, 255, 255 ) )

				self.__pyRtCondit.text = PL_Font.getSource( "%s%s"%( conditText, condition ), fc = ( 227, 207, 124, 255 ) )
				usageText = PL_Font.getSource( labelGather.getText( "PlayerProperty:TitlePanel", "useEffect" ), fc = ( 30, 241, 234, 255 ) )
				usageStr = ""
				if skillID == 0:
					usageStr = labelGather.getText( "PlayerProperty:TitlePanel", "noneTitle" )
				else:
					skill = skills.getSkill( skillID )
					buffs = skill.getBuffLink()
					for buff in buffs:
						usage = ""
						description = buff.getDescription()
						if description.find("@B"):
							usage = description.split("@B")[-1]
					usageStr += "%s%s"%( usage, PL_NewLine.getSource() )
				usageStr = PL_Font.getSource( "%s"%usageStr, fc = ( 99, 238, 85, 255 ) ) #效果说明
				self.__pyRtUsage.text = PL_Font.getSource( "%s%s"%( usageText, usageStr ), fc = ( 227, 207, 124, 255 ) )
			else:
				self.__pyRtInfo.text = labelGather.getText( "PlayerProperty:TitlePanel", "titleNotGet" )
				self.__pyRtCondit.text = ""
				self.__pyRtUsage.text = ""
		self.__pyRtCondit.top = self.__pyRtInfo.bottom
		self.__pyRtUsage.top = self.__pyRtCondit.bottom

	def setUseTitleInfo( self, titleID ):
		if titleID == 0:
			self.__pyRtInfo.text = ""
			self.__pyRtCondit.text = ""
			self.__pyRtUsage.text = ""
		else:
			player = BigWorld.player()
			title = g_TitleData.get( titleID )
			if title is None:return
			description = title["description"]
			skillID = title["skillID"]
			if titleID in [csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]:
				if player.couple_lover is None:return
				description = description%player.couple_lover.playerName
			self.__pyRtInfo.text = PL_Font.getSource( description, fc = ( 255, 235, 143, 255 ) )

			conditText = PL_Font.getSource( labelGather.getText( "PlayerProperty:TitlePanel", "getCondition" ), fc = ( 30, 241, 234, 255 ) )
			condition = PL_Font.getSource( "%s"%title["description2"], fc = ( 255, 255, 255, 255 ) )
			self.__pyRtCondit.text = PL_Font.getSource( "%s%s"%( conditText, condition ), fc = ( 99, 238, 85, 255 ) )
			usageText = PL_Font.getSource( labelGather.getText( "PlayerProperty:TitlePanel", "useEffect" ), fc = ( 30, 241, 234, 255 ) )
			usageStr = ""
			if skillID == 0:
				usageStr = labelGather.getText( "PlayerProperty:TitlePanel", "noneTitle" )
			else:
				skill = skills.getSkill( skillID )
				buffs = skill.getBuffLink()
				for buff in buffs:
					usage = ""
					description = buff.getDescription()
					if description.find("@B"):
						usage = description.split("@B")[-1]
					usageStr += "%s%s"%( usage, PL_NewLine.getSource() )
			usageStr = PL_Font.getSource( "%s"%usageStr, fc = ( 99, 238, 85, 255 ) ) #效果说明
			self.__pyRtUsage.text = PL_Font.getSource( "%s%s"%( usageText, usageStr ), fc = ( 99, 238, 85, 255 ) )
		self.__pyRtCondit.top = self.__pyRtInfo.bottom
		self.__pyRtUsage.top = self.__pyRtCondit.bottom

	def onRemoveTitle( self ):
		self.__pyRtInfo.text = ""
		self.__pyRtCondit.text = ""
		self.__pyRtUsage.text = ""
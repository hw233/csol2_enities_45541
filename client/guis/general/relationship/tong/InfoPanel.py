# -*- coding: gb18030 -*-
#
# $Id: InfoPanel.py Exp $

"""
implement InfoPanel class
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from config.tong_exp import Datas as tongExpDatas
from guis.controls.Button import Button
from ItemsFactory import SkillItem as SkillInfo
import skills as Skill
from Time import Time
import Timer
import csdefine
import csconst
import Const

SHENSHOU_NAMES = { csdefine.TONG_SHENSHOU_TYPE_1: labelGather.getText( "RelationShip:TongPanel", "shenshou_type_1" ),
		csdefine.TONG_SHENSHOU_TYPE_2: labelGather.getText( "RelationShip:TongPanel", "shenshou_type_2" ),
		csdefine.TONG_SHENSHOU_TYPE_3: labelGather.getText( "RelationShip:TongPanel", "shenshou_type_3" ),
		csdefine.TONG_SHENSHOU_TYPE_4: labelGather.getText( "RelationShip:TongPanel", "shenshou_type_4" )
		}

WEEKSTATE = {
			csdefine.NONE_STATUS : ( labelGather.getText( "RelationShip:TongPanel", "noState" ),
									labelGather.getText( "RelationShip:TongPanel", "fetePrompt" ), ),
			csdefine.STARLIGHT : ( labelGather.getText( "RelationShip:TongPanel", "starryAmrita" ),
									labelGather.getText( "RelationShip:TongPanel", "researchEnhance" ), ),
			csdefine.LUNARHALO : ( labelGather.getText( "RelationShip:TongPanel", "lunarAmrita" ),
									labelGather.getText( "RelationShip:TongPanel", "produceEnhance" ), ),
			csdefine.SUNSHINE : ( labelGather.getText( "RelationShip:TongPanel", "solarAmrita" ),
									labelGather.getText( "RelationShip:TongPanel", "actionEnhance" ), ),
		}

VALUE_COLOR = ( 255, 255, 255, 255 )

class InfoPanel( PyGUI ):

	def __init__( self, panel ):
		PyGUI.__init__(self, panel )
		self.__initpanel( panel )

	def __initpanel( self, panel ):
		self.__pyInfoItems = {}
		for name, item in panel.children:
			if not name.endswith( "_item" ):continue
			tag = name.split( "_" )[0]
			pyInfoItem = InfoItem( item ,self, tag )
			pyInfoItem.text = ""
			pyInfoItem.tag = tag
			pyInfoItem.onMouseEnter.bind( self.__onMouseEnter )
			pyInfoItem.onMouseLeave.bind( self.__onMouseLeave )
			pyInfoItem.title = labelGather.getText( "RelationShip:TongPanel", tag )
			self.__pyInfoItems[tag] = pyInfoItem
		
		self.__expBar = ExpProgressBar( panel.expBar )
		self.__expBar.name = labelGather.getText( "RelationShip:TongPanel", "rtTongExp" )
		self.__expBar.update( "--" )	

		self.__pyContributeBtn = Button( panel.showContributeBtn ) # ���Ǹ�͸����Button��������ʾ���׶���������ΪStaticText�����¼�
		self.__pyContributeBtn.onMouseEnter.bind( self.__onEnterContribute )
		self.__pyContributeBtn.onMouseLeave.bind( self.__onLeaveContribute )

		labelGather.setLabel( panel.frame_baseInfo.bgTitle.stTitle, "RelationShip:TongPanel", "tongInfo" )

	def __onEnterContribute( self ) :
		player = BigWorld.player()
		memberInfo = player.tong_memberInfos.get( player.databaseID )
		if memberInfo is None:return
		Contribute = str( memberInfo.getContribute() )
		totalContribute = str( memberInfo.getTotalContribute() )
		msg = labelGather.getText( "RelationShip:TongPanel", "contriMsg" ) % ( Contribute, totalContribute )
		toolbox.infoTip.showItemTips( self, msg )

	def __onLeaveContribute( self ) :
		toolbox.infoTip.hide()

	def __getPrice( self, money ) :
		if money <= 0:
			return "0%s0%s0%s"%( PL_Image.getSource( "guis/controls/goldicon.gui" ), PL_Image.getSource( "guis/controls/silvericon.gui" ),PL_Image.getSource( "guis/controls/coinicon.gui" ) )
		text = ""
		gold = money/10000
		silver = ( money/100 )%100
		coin = ( money%100 )%100
		if coin:
			text = str( coin ) + PL_Image.getSource( "guis/controls/coinicon.gui" )
		if silver:
			text = str( silver ) + PL_Image.getSource( "guis/controls/silvericon.gui" ) + text
		if gold:
			text = str( gold ) + PL_Image.getSource( "guis/controls/goldicon.gui" ) + text
		return text

	def __onMouseEnter( self, pyItem ):
		player = BigWorld.player()
		if pyItem.tag in ["prestige", "variable"]:
			infos = labelGather.getText( "RelationShip:TongPanel", "prestInfos" )%( player.tong_prestige, player.variable_prestige )
			toolbox.infoTip.showToolTips( self, infos )

	def __onMouseLeave( self, pyItem ):
		toolbox.infoTip.hide()

	# ---------------------------------------------------------------
	# ��Ϣ����
	# ---------------------------------------------------------------
	def setWeekState( self, state ) :
		"""
		���״̬
		"""
		stateText = WEEKSTATE.get( state, ("","") )[0]
		self.__pyInfoItems["weekState"].state = state
		self.__pyInfoItems["weekState"].text = PL_Font.getSource( stateText, fc = VALUE_COLOR )

	def setPrestige( self, presgite ):
		"""
		��������
		"""
		self.__pyInfoItems["prestige"].text = PL_Font.getSource( "%d"%presgite, fc = VALUE_COLOR )

	def memberChange( self ):
		"""
		����Ա����ʱ����
		"""
		player = BigWorld.player()
		members = player.tong_memberInfos
		tongLevel = player.tongLevel
		if tongLevel < 1:return #�����������ݻ�û�з���������ʼ�ȼ�Ϊ0����ȡ�й���Ϣ�ͻ����
		maxNumber = csconst.TONG_MEMBER_LIMIT_DICT[tongLevel]
		self.__pyInfoItems["members"].text = PL_Font.getSource( "%d/%d"%( len( members ), maxNumber ),fc = VALUE_COLOR )

	def setHoldCity( self, city ):
		"""
		���ռ�����
		"""
		cityText = csconst.g_maps_info.get( city, "" )
		if cityText == "":
			self.__pyInfoItems["holdCity"].text = PL_Font.getSource( city, fc = VALUE_COLOR )
		else:
			self.__pyInfoItems["holdCity"].text = PL_Font.getSource( cityText, fc = VALUE_COLOR )

	def setContribute( self, contribute ):
		"""
		����ڸð�ṱ�׶�
		"""
		player = BigWorld.player()
		memberInfo = player.tong_memberInfos.get( player.databaseID )
		if memberInfo is None:return
		totalContribute = memberInfo.getTotalContribute()
		self.__pyInfoItems["contribute"].text = PL_Font.getSource( "%d/%d"%( contribute, totalContribute ), fc = VALUE_COLOR )

	def setTotalContribute( self, totalContribute ):
		"""
		����ڸð����ܹ��׶�
		"""
		player = BigWorld.player()
		memberInfo = player.tong_memberInfos.get( player.databaseID )
		if memberInfo is None:return
		contribute = memberInfo.getContribute()
		self.__pyInfoItems["contribute"].text = PL_Font.getSource( "%d/%d"%( contribute, totalContribute ), fc = VALUE_COLOR )

	def setTongTotem( self, totemType ):
		"""
		�������
		"""
		pass

	def setLeague( self ):
		"""
		��ʼ�����ͬ��
		"""
		leagueInfo = ""
		tongLeagues = BigWorld.player().tong_leagues
		if len( tongLeagues ) > 0:
			for tongName in tongLeagues.itervalues():
				leagueInfo += "%s%s"%( tongName, PL_Space.getSource( 2 ) )
		else:
			leagueInfo += labelGather.getText( "RelationShip:RelationPanel", "without" )
		self.__pyInfoItems["league"].text = PL_Font.getSource( leagueInfo, fc = VALUE_COLOR )

	def addLeague( self, tongDBID ):
		"""
		��Ӱ��ͬ��
		"""
		self.setLeague()

	def delLeague( self, tongDBID ):
		"""
		ɾ��ͬ��
		"""
		tongLeagues = BigWorld.player().tong_leagues
		leagueInfo = ""
		if len( tongLeagues ) > 0:
			for tongName in tongLeagues.itervalues():
				leagueInfo += "%s%s"%( tongName, PL_Space.getSource( 2 ) )
		else:
			leagueInfo += labelGather.getText( "RelationShip:RelationPanel", "without" )
		self.__pyInfoItems["league"].text = PL_Font.getSource( leagueInfo, fc = VALUE_COLOR )

	def updateTongFund( self, fund ):
		"""
		����ʽ�
		"""
		player = BigWorld.player()
		if player.tongLevel == 0:return #�����������ݻ�û�з���������ȡ�й���Ϣ�ͻ����
		canUseFund = player.tong_getCanUseMoney()
		moneyText = self.__getPrice( canUseFund )
		self.__pyInfoItems["usableFund"].text = PL_Font.getSource( moneyText, fc = VALUE_COLOR )

	def updateActiveval( self, activeVal ):
		self.__pyInfoItems["tongActivity"].text = PL_Font.getSource( "%d"%activeVal, fc = VALUE_COLOR )
		
	def updateTongExp( self, tongExp ):
		"""
		���°�ᾭ����
		"""
		self.__expBar.update( tongExp )

	# ------------------------------------------------------
	#����
	def setTongShenShou( self, shenshouLevel, shenshouType ):
		name = ""
		if SHENSHOU_NAMES.has_key( shenshouType ):
			name += labelGather.getText( "RelationShip:TongPanel", "shensInfo" )%( SHENSHOU_NAMES[shenshouType], PL_Space.getSource( 6 ), shenshouLevel )
		else:
			name += labelGather.getText( "RelationShip:RelationPanel", "without" )
		self.__pyInfoItems["totem"].text = PL_Font.getSource( name, fc = VALUE_COLOR )

	# ------------------------------------------------------

	# --------------------------------------------------------
	def setTongInfo( self ):
		player = BigWorld.player()
		holdCity = player.tong_holdCity
		tong_leagues = player.tong_leagues
		if holdCity == "":
			self.__pyInfoItems["holdCity"].text = PL_Font.getSource( labelGather.getText( "RelationShip:RelationPanel", "without" ), fc = VALUE_COLOR )
		else:
			cityText = csconst.g_maps_info.get( holdCity, "" )
			if cityText == "":
				self.__pyInfoItems["holdCity"].text = PL_Font.getSource( holdCity, fc = VALUE_COLOR )
			else:
				self.__pyInfoItems["holdCity"].text = PL_Font.getSource( cityText, fc = VALUE_COLOR )
		name = ""
		if len( tong_leagues ) < 1:
			name += labelGather.getText( "RelationShip:RelationPanel", "without" )
		else:
			for tongName in tong_leagues.itervalues():
				name += "%s%s"%( tongName, PL_Space.getSource( 2 ) )
		self.__pyInfoItems["league"].text = PL_Font.getSource( name, fc = VALUE_COLOR )
		memberInfo = player.tong_memberInfos.get( player.databaseID )
		if memberInfo is None:return
		contribute = memberInfo.getContribute() #��ṱ�׶�
		totalContribute = memberInfo.getTotalContribute() # �����ܹ��׶�
		self.__pyInfoItems["contribute"].text = PL_Font.getSource( "%d/%d"%( contribute, totalContribute ), fc = VALUE_COLOR )
		#self.addFamily()
		canUseFund = player.tong_getCanUseMoney()
		moneyText = self.__getPrice( canUseFund )
		self.__pyInfoItems["usableFund"].text = PL_Font.getSource( moneyText, fc = VALUE_COLOR )

	def setVariablePrest( self, value ):
		"""
		��������
		"""
		self.__pyInfoItems["variable"].text = PL_Font.getSource( "%d"%value, fc = VALUE_COLOR )
		
		
	def setSignCount( self, totalSignCount ):
		"""
		�ۼ�ǩ������
		"""
		valueText = PL_Font.getSource( "%d"%totalSignCount, fc = VALUE_COLOR )
		self.__pyInfoItems["signCount"].text = labelGather.getText( "RelationShip:TongPanel", "stSignCount" ) % valueText

	def reset( self ):
		pass		
	
	def _getPyInfoItems( self ):	
		return self.__pyInfoItems
	
	pyInfoItems = property( _getPyInfoItems, )
	
# ---------------------------------------------------------------------
class InfoItem( Control ):
	def __init__( self, infoItem ,pyBinder, tag ):
		Control.__init__( self, infoItem ,pyBinder )
		self.crossFocus = True
		self.tag = tag
		self.__pyStTitle = CSRichText( infoItem.rtTitle )
		self.__pyStTitle.onMouseEnter.bind( self.__showWeek )
		self.__pyStTitle.onMouseLeave.bind( self.__hideWeek )
		self.__pyStTitle.crossFocus = tag == "weekState"
		
		self.__pyRtValue = CSRichText( infoItem.rtValue )
		self.__pyRtValue.onMouseEnter.bind( self.__showState )
		self.__pyRtValue.onMouseLeave.bind( self.__hideState )
		self.__pyRtValue.crossFocus = tag == "weekState"
		self.__pyRtValue.align = "R"
		self.__pyRtValue.text = ""

	def __showWeek( self, pyWeek ):
		if self.tag == "weekState":
			infos = labelGather.getText( "RelationShip:TongPanel", "fetePrompt" )
			toolbox.infoTip.showToolTips( pyWeek, infos )
			pass
	
	def __showState( self, pyState ):
		if self.tag == "weekState":
			infos =WEEKSTATE.get( self.pyBinder.pyInfoItems["weekState"].state, ("","") )[1]
			toolbox.infoTip.showToolTips(pyState, infos )
			pass
		
	def __hideWeek( self ):
		toolbox.infoTip.hide()
		pass
	
	def __hideState( self ):
		toolbox.infoTip.hide()
		pass
		
	def _getText( self ):
		return self.__pyRtValue.text

	def _setText( self, text ):
		self.__pyRtValue.text = text

	def _getTitle( self ):
		return self.__pyStTitle.text

	def _setTitle( self, title ):
		self.__pyStTitle.text = title

	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )
	
class ExpProgressBar( Control ):
	def __init__( self, item = None ):
		Control.__init__( self, item )
		self.__initItem( item )

	def __initItem( self, item ):
		self.__pyValueBar = ProgressBar( item.bar.bar )
		self.__pyValueBar.value = 0.0
		self.__pyValueBar.clipMode = "RIGHT"

		self.__pyStValue = StaticText( item.bar.lbValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""
		
		self.__pyStName = CSRichText( item.rtTitle )
		self.__pyStName.color = ( 236.0, 218.0, 157.0 )

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		return True

	def update( self, exp ):
		
		if exp == "--":
			self.__pyStValue.text = "-- / --"
			self.__pyValueBar.value = 0
		else:
			player = BigWorld.player()
			tongLevel = player.tongLevel
			maxExp = tongExpDatas.get( tongLevel )
			
			self.__pyValueBar.value = float( exp )/maxExp 
			self.__pyStValue.text = "%d/%d"%( exp, maxExp )

	def _getName( self ):
		return self.__pyStName.text
	
	def _setName( self, text ):
		self.__pyStName.text = text

	name = property( _getName, _setName )

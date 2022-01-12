# -*- coding: gb18030 -*-

from guis import *
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from LabelGather import labelGather
import event.EventCenter as ECenter
from Time import Time
from Function import Functor
import csdefine
import csconst

class YiJieBattleInfos( RootGUI ):

	def __init__( self ):
		panel = GUI.load( "guis/general/spacecopyabout/spaceCopyYiJieZhanChang/yiJieBattleInfos.gui" )
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.focus = False
		self.__timerControl = 0
		
		self.__pyRtRemainTime = CSRichText( panel.rtRemainTime )
		self.__pyRtRemainTime.text = ""
		
		self.__pyRtKillNum = CSRichText( panel.rtKillNum )
		self.__pyRtKillNum.text = labelGather.getText( "SpaceCopyJiJieZhanChang:yiJieInfos", "killNum" ) % "0"
		
		self.__pyRtKeepNum = CSRichText( panel.rtKeepNum )
		self.__pyRtKeepNum.text = labelGather.getText( "SpaceCopyJiJieZhanChang:yiJieInfos", "keepNum" ) % "0/0"
		
		self.__pyRtFactionInfos = CSRichText( panel.rtFaction )
		self.__pyRtFactionInfos.text = ""
		
		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_YI_JIE_BATTLE_INFOS_SHOW"] = self.__onShow				#显示界面
		self.__triggers["EVT_ON_YI_JIE_BATTLE_INFOS_HIDE"] = self.__onHide				#隐藏界面
		self.__triggers["EVT_ON_UPDATE_YIJIE_PLAYER_INFOS"] = self.__onUpdatePlayerInfos		# 更新玩家战况信息
		
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
			
	def __onUpdatePlayerInfos( self, killNum, keep, maxKeep ):
		"""
		更新玩家的连斩/最高连斩  杀人数
		"""
		keepStr = "%d/%d"%( keep, maxKeep )
		self.__pyRtKeepNum.text = labelGather.getText( "SpaceCopyJiJieZhanChang:yiJieInfos", "keepNum" ) % keepStr
		self.__pyRtKillNum.text = labelGather.getText( "SpaceCopyJiJieZhanChang:yiJieInfos", "killNum" ) % str(killNum)
			
	def __onTimeUpdate( self, startTime, persistTime ): #持续时间
		if persistTime == "-1": #为-1则没有时间限制
			self.__pyRtRemainTime.text = ""
			
		else:
			endTime = float( startTime ) + float( persistTime )
			remainTime = endTime - Time().time()
			mins = int( remainTime/60 )
			secs= int( remainTime%60 )
			if remainTime < 0:
				mins = 0
				secs = 0
			if secs < 10 :
				timeText = PL_Font.getSource( "%d:0%d"%( mins, secs ), fc = ( 230, 227, 185, 255 ) )
			else:
				timeText = PL_Font.getSource( "%d:%d"%( mins, secs ), fc = ( 230, 227, 185, 255 ) )
			timeText = labelGather.getText( "SpaceCopyJiJieZhanChang:yiJieInfos", "remianTime" ) % timeText
			self.__pyRtRemainTime.text = timeText
			
	def __updateFactionInfos( self ):
		"""
		更新各个阵营战况
		"""
		player = BigWorld.player()
		spaceID = player.spaceID
		playerFaction = player.yiJieFaction		#获取玩家自己的阵营
		angerFaction = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_ANGER_FACTION )	
		alliance = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_ALLIANCE_FACTIONS )	
		angerFaction = int( angerFaction )
		alliance = eval( alliance )
		
		angerStr = PL_Font.getSource( labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","anger" ), fc = "c3" )
		alienceStr = PL_Font.getSource( labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","alliance" ), fc = "c6" )
		
		tianScore = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_TIAN )	
		if tianScore is None:tianScore = 0
		tianPeopleNum = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_TIAN )
		if tianPeopleNum is None:tianPeopleNum = 0	
		tianStr = labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","tianzu" )
		tianStr += PL_Space.getSource( 1 )
		tianStr += labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","factionSP" ) %(str( tianScore ), str( tianPeopleNum) )
		if playerFaction == csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN:
			tianStr = PL_Font.getSource( tianStr, fc = "c4" )
		if csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN == angerFaction:
			tianStr += angerStr
		if csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN in alliance:
			tianStr += alienceStr
			
		diScore = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_DI )
		if diScore is None:diScore = 0
		diPeopleNum = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_DI )
		if diPeopleNum is None:diPeopleNum = 0	
		diStr = labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","dizu" )
		diStr += PL_Space.getSource( 1 )
		diStr += labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","factionSP" ) %(str( diScore ), str( diPeopleNum) )
		if playerFaction == csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI:
			diStr = PL_Font.getSource( diStr, fc = "c4" )
		if csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI == angerFaction:
			diStr += angerStr
		if csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI in alliance:
			diStr += alienceStr
			
		renScore = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_REN )
		if renScore is None:renScore = 0
		renPeopleNum = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_REN )
		if renPeopleNum is None:renPeopleNum = 0	
		renStr = labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","renzu" )
		renStr += PL_Space.getSource( 1 )
		renStr += labelGather.getText("SpaceCopyJiJieZhanChang:yiJieInfos","factionSP" ) %(str( renScore ), str( renPeopleNum) )
		if playerFaction == csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN:
			renStr = PL_Font.getSource( renStr, fc = "c4" )
		if csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN == angerFaction:	
			renStr += angerStr
		if csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN in alliance:
			renStr += alienceStr
		totalStr = tianStr + PL_NewLine.getSource() + diStr + PL_NewLine.getSource() + renStr
		self.__pyRtFactionInfos.text = totalStr
			
	def __updateInfos( self, startTime, persistTime ):
		"""
		更新副本时间 和阵营信息
		"""
		self.__onTimeUpdate( startTime, persistTime )			
		self.__updateFactionInfos()
		functor = Functor( self.__updateInfos, startTime, persistTime )
		self.__timerControl = BigWorld.callback( 1, functor )
			
	def __onShow( self ):
		spaceID = BigWorld.player().spaceID	
		startTime = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_START_TIME)			#开始时间
		persistTime = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_LAST_TIME)			#持续时间
		self.__updateInfos( startTime, persistTime )
		RootGUI.show( self )
		
	def __onHide( self ):
		self.hide()
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
		
	def onLeaveWorld( self ):
		self.hide()
		
	def hide( self ):
		BigWorld.cancelCallback( self.__timerControl )
		self.__timerControl = 0
		RootGUI.hide( self )

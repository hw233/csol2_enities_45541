# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.Control import Control
from guis.controls.ProgressBar import HProgressBar as ProgressBar
import csdefine

class EnergyPanel( GUIBaseObject ):
	def __init__( self, panel ):
		GUIBaseObject.__init__( self, panel )
	
		self.__pyFriHPBar = EnergyBar( panel.friEnergyBar )
		self.__pyEnmHPBar = EnergyBar( panel.enmEnergyBar )
		
		labelGather.setLabel( panel.friEnergyBar.lbLevel, "FloatName:monsterName", "friendText")
		labelGather.setLabel( panel.enmEnergyBar.lbLevel, "FloatName:monsterName", "enemyText")
		
	def updateEnergy( self, energy ):
		player = BigWorld.player()
		tongDBID = player.tong_dbID
		order = self.__getOrderByTongDBID( tongDBID )
		if order == csdefine.CITY_WAR_FINAL_FACTION_NONE:
			return
		if order == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
			self.__pyFriHPBar.update( energy.get( order ) )
			self.__pyEnmHPBar.update( ( energy.get( csdefine.CITY_WAR_FINAL_FACTION_DEFEND) ) )
		elif order == csdefine.CITY_WAR_FINAL_FACTION_DEFEND:
			self.__pyFriHPBar.update( energy.get( order ) )
			self.__pyEnmHPBar.update( ( energy.get( csdefine.CITY_WAR_FINAL_FACTION_ATTACK) ) )
		
	def __getOrderByTongDBID( self, tongDBID ):
		"""
		根据帮会ID获取判断是攻城方还是守城方
		"""
		roleOrder = 0
		player = BigWorld.player()
		tong_dbID = tongDBID
		attackTongDBID = 0
		defenceTongDBID = 0
		
		tong_quarterFinalRecord = player.tong_quarterFinalRecord
		for tongDBID, order in tong_quarterFinalRecord.iteritems():
			if order == 1:		#第一名是守城帮会
				defenceTongDBID = tongDBID
			elif order == 2:	#第二名是攻城帮会
				attackTongDBID = tongDBID
				
		attackTongInfo = player.tong_battleLeagues.get( attackTongDBID )
		defenceTongInfo = player.tong_battleLeagues.get( defenceTongDBID )
				
		if tong_dbID == defenceTongDBID or tong_dbID in defenceTongInfo["leagues"]:
			roleOrder = csdefine.CITY_WAR_FINAL_FACTION_DEFEND
		elif tong_dbID == attackTongDBID or tong_dbID in attackTongInfo["leagues"]:
			roleOrder = csdefine.CITY_WAR_FINAL_FACTION_ATTACK
			
		return roleOrder
		
class EnergyBar( Control ):
	def __init__( self, bar ):
		Control.__init__( self, bar )
		self.__pyHPBar = ProgressBar( bar.hpBg.hpBar )
		self.__pyHPBar.value = 0
		self.__value = 0
		
	def update( self, value ):
		self.__value = value
		self.__pyHPBar.value = float( value)/100
		
	def onMouseEnter_( self,):
		Control.onMouseEnter_( self )
		dsp = labelGather.getText( "FloatName:monsterName", "energy" )%( self.__value, 100 )
		toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

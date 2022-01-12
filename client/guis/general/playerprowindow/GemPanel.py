# -*- coding: gb18030 -*-
#
# $Id: GemPanel.py,v 1.1 2008-03-25 09:56:36 fangpengjun Exp $
#


import event.EventCenter as ECenter
from guis import *
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabButton
from guis.controls.StaticText import StaticText
from DrawPanel import GemDrawPanel
from ManagerPanel import GemManagePanel

class GemPanel( TabPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( panel )

	def __initialize( self, panel ) :
		self.__pyManagerPanel = GemManagePanel( panel.panel_0 )

	def __registerTriggers( self ):
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------------------------
	def initGes( self ): #初始化已领取和未领取宝石面板
		#self.__pyDrawPanel.addPetGems()
		#self.__pyDrawPanel.initCommonGems()
		pass

	def reset( self ):
		#self.__pyDrawPanel.reset()
		self.__pyManagerPanel.reset()
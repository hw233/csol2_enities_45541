# -*- coding: gb18030 -*-
# written by ganjinxing 2009-11-2

from guis import *
from guis.general.vendwindow.sellwindow.LogsPanel import VendLogsPanel as BaseLogPanel
import time


class LogsPanel( BaseLogPanel ) :

	def __init__( self, tabPanel, pyBinder = None ):
		self.__lastQueryTime = 0
		BaseLogPanel.__init__( self, tabPanel, pyBinder )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_TISHOU_ADD_SELL_RECORD"] = self.addRecord_
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def dispose( self ) :
		self.triggers_ = {}
		BaseLogPanel.dispose( self )

	def onParentShow( self ) :
		if self.visible : self.onShow()

	def onParentHide( self ) :
		self.__lastQueryTime = 0

	def onShow( self ) :
		"""
		��ʱ��ѯ
		"""
		currTime = time.time()
		if self.__lastQueryTime + 360000 > currTime : return						# ��ѯ����趨Ϊ���3��
		self.__lastQueryTime = currTime
		self.reset()
		tishouNPC = self.pyBinder.tishouNPC
		if tishouNPC is not None :
			BigWorld.callback( 0.5, tishouNPC.cell.queryTSRecord )

	def reset( self ) :
		"""
		�������ô���
		"""
		self.income_ = 0
		BaseLogPanel.reset( self )
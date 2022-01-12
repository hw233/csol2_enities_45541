# -*- coding: gb18030 -*-
#
# $Id: MapPanel.py,v 1.13 2008-08-29 02:39:21 huangyongwei Exp $

"""
implement full map class

2008.01.03 : wirten by huangyongwei
"""

import Math
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Frame import HVFrame
from guis.controls.Control import Control
from guis.controls.ScrollPanel import HVScrollPanel
from Map import Map


class MapPanel( HVFrame, Control ) :
	__DM_ORIGIN		= 1									# 原始大小模式
	__DB_ADATPED	= 2									# 适应屏幕大小模式

	def __init__( self, mapPanel ) :
		HVFrame.__init__( self, mapPanel )
		Control.__init__( self, mapPanel )
		self.__initialize( mapPanel )

		self.__dspMode = self.__DM_ORIGIN				# 地图的显示模式
		self.__scrollRate = ( 0, 0 )					# 当前滚动比例

		self.__mouseDownPos = ( 0, 0 )					# 记录鼠标按下时的位置


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, mapPanel ) :
		self.__pyCliper = HVScrollPanel( mapPanel.clipper, mapPanel.hsbar, mapPanel.vsbar )
		self.__pyCliper.h_dockStyle = "HFILL"
		self.__pyCliper.v_dockStyle = "VFILL"
		self.__pyCliper.pyHSBar.h_dockStyle = "HFILL"
		self.__pyCliper.pyHSBar.v_dockStyle = "BOTTOM"
		self.__pyCliper.pyVSBar.h_dockStyle = "RIGHT"
		self.__pyCliper.pyVSBar.v_dockStyle = "VFILL"
		self.__pyCliper.skipScroll = False
		self.__pyCliper.h_perScroll = 60.0
		self.__pyCliper.v_perScroll = 60.0
		self.__pyCliper.focus = True
		self.__pyCliper.moveFocus = True
		self.__pyCliper.onRMouseDown.bind( self.__onCliperRMouseDown )
		self.__pyCliper.onRMouseUp.bind( self.__onCliperRMouseUp )
		self.__pyCliper.onMouseMove.bind( self.__onCliperMouseMove )

		self.pyMap = Map( mapPanel.clipper.mp )

		self.__triggers = {}
		self.__registerTriggers()

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __saveScroll( self ) :
		"""
		保存当前所在的滚动位置，以便在改变分辨率后恢复到这个位置
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.__scrollRate = self.__pyCliper.scrollRate

	# -------------------------------------------------
	def __reboundMap( self ) :
		"""
		改变分别率后重新设置地图的显示模式和计算地图的单位滚动尺寸
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.orginMapSize()
		else :
			self.adaptMapSize()

	def __resetScroll( self ) :
		"""
		改变分辨率后重新设置滚动位置为滚动前的位置
		"""
		cwidth, cheight = self.__pyCliper.size
		if self.pyMap.width > cwidth :
			self.__pyCliper.h_maxScroll = self.pyMap.right - cwidth
		else :
			self.__pyCliper.h_maxScroll = 0
		if self.pyMap.height > cheight :
			self.__pyCliper.v_maxScroll = self.pyMap.bottom - cheight
		else :
			self.__pyCliper.v_maxScroll = 0
		self.__pyCliper.scrollRate = self.__scrollRate

	def __relocateMap( self ) :
		"""
		在适应屏幕大小的显示模式下，根据地图的长宽比例，设置地图为水平居中还是垂直居中
		"""
		cwidth, cheight = self.__pyCliper.size
		if self.pyMap.width < cwidth :
			self.pyMap.center = cwidth / 2
		else :
			self.pyMap.left = 0
		if self.pyMap.height < cheight :
			self.pyMap.middle = cheight / 2
		else :
			self.pyMap.top = 0
		self.__resetScroll()

	# -------------------------------------------------
	def __onResolutionChanged( self, preReso ) :
		"""
		当屏幕分辨率改变时被调用
		"""
		self.__reboundMap()


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def __onCliperRMouseDown( self, pyCover ) :
		"""
		当鼠右键在地图上按下时被调用
		"""
		uiHandlerMgr.capUI( pyCover )
		self.__mouseDownPos = pyCover.mousePos
		mc = GUI.mcursor()
		mc.shape = "movehand"								# 设置鼠标为手形，表示可以移动地图
		BigWorld.setCursor( mc )

	def __onCliperRMouseUp( self ) :
		"""
		当鼠标右键在地图上提起时被调用
		"""
		uiHandlerMgr.uncapUI( self.__pyCliper )

		mc = GUI.mcursor()
		mc.shape = "normal"
		BigWorld.setCursor( mc )

	def __onCliperMouseMove( self, dx, dy ) :
		"""
		当鼠标右在地图上移动时被调用
		"""
		if uiHandlerMgr.getCapUI() == self.__pyCliper :
			self.__pyCliper.h_scroll -= dx
			self.__pyCliper.v_scroll -= dy


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventName, *args ) :
		self.__triggers[eventName]( args )

	# -------------------------------------------------
	def setArea( self, area ) :
		"""
		设置区域区域
		"""
		self.pyMap.setArea( area )
		self.__reboundMap()

	# -------------------------------------------------
	def adaptMapSize( self ) :
		"""
		将地图大小设置为适应窗口大小
		"""
		self.__saveScroll()
		width, height = self.pyMap.viewSize
		cwidth, cheight = self.__pyCliper.size
		scaleX = cwidth / width
		scaleY = cheight / height
		if abs( scaleX ) < abs( scaleY ) :
			self.pyMap.scale = scaleX
		else :
			self.pyMap.scale = scaleY
		self.__relocateMap()
		self.__dspMode = self.__DB_ADATPED

	def orginMapSize( self ) :
		"""
		设置地图大小为原始大小
		"""
		self.__saveScroll()
		width, height = self.pyMap.viewSize
		cwidth, cheight = self.__pyCliper.size
		if width < cwidth and height < cheight :
			self.adaptMapSize()
		else :
			self.pyMap.scale = 1
			self.__relocateMap()
			self.__dspMode = self.__DM_ORIGIN

	# -------------------------------------------------
	def scrollToPoint( self, point ) :
		"""
		将地图滚动到指定点为视觉中心点
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.__pyCliper.h_scroll = point[0] - self.__pyCliper.width / 2
			self.__pyCliper.v_scroll = point[1] - self.__pyCliper.height / 2

	def resumeScroll( self ) :
		"""
		恢复滚动属性到 0,0 位置
		"""
		self.__scrollRate = 0, 0
		self.__resetScroll()

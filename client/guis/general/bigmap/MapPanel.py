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
	__DM_ORIGIN		= 1									# ԭʼ��Сģʽ
	__DB_ADATPED	= 2									# ��Ӧ��Ļ��Сģʽ

	def __init__( self, mapPanel ) :
		HVFrame.__init__( self, mapPanel )
		Control.__init__( self, mapPanel )
		self.__initialize( mapPanel )

		self.__dspMode = self.__DM_ORIGIN				# ��ͼ����ʾģʽ
		self.__scrollRate = ( 0, 0 )					# ��ǰ��������

		self.__mouseDownPos = ( 0, 0 )					# ��¼��갴��ʱ��λ��


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
		���浱ǰ���ڵĹ���λ�ã��Ա��ڸı�ֱ��ʺ�ָ������λ��
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.__scrollRate = self.__pyCliper.scrollRate

	# -------------------------------------------------
	def __reboundMap( self ) :
		"""
		�ı�ֱ��ʺ��������õ�ͼ����ʾģʽ�ͼ����ͼ�ĵ�λ�����ߴ�
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.orginMapSize()
		else :
			self.adaptMapSize()

	def __resetScroll( self ) :
		"""
		�ı�ֱ��ʺ��������ù���λ��Ϊ����ǰ��λ��
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
		����Ӧ��Ļ��С����ʾģʽ�£����ݵ�ͼ�ĳ�����������õ�ͼΪˮƽ���л��Ǵ�ֱ����
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
		����Ļ�ֱ��ʸı�ʱ������
		"""
		self.__reboundMap()


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def __onCliperRMouseDown( self, pyCover ) :
		"""
		�����Ҽ��ڵ�ͼ�ϰ���ʱ������
		"""
		uiHandlerMgr.capUI( pyCover )
		self.__mouseDownPos = pyCover.mousePos
		mc = GUI.mcursor()
		mc.shape = "movehand"								# �������Ϊ���Σ���ʾ�����ƶ���ͼ
		BigWorld.setCursor( mc )

	def __onCliperRMouseUp( self ) :
		"""
		������Ҽ��ڵ�ͼ������ʱ������
		"""
		uiHandlerMgr.uncapUI( self.__pyCliper )

		mc = GUI.mcursor()
		mc.shape = "normal"
		BigWorld.setCursor( mc )

	def __onCliperMouseMove( self, dx, dy ) :
		"""
		��������ڵ�ͼ���ƶ�ʱ������
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
		������������
		"""
		self.pyMap.setArea( area )
		self.__reboundMap()

	# -------------------------------------------------
	def adaptMapSize( self ) :
		"""
		����ͼ��С����Ϊ��Ӧ���ڴ�С
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
		���õ�ͼ��СΪԭʼ��С
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
		����ͼ������ָ����Ϊ�Ӿ����ĵ�
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.__pyCliper.h_scroll = point[0] - self.__pyCliper.width / 2
			self.__pyCliper.v_scroll = point[1] - self.__pyCliper.height / 2

	def resumeScroll( self ) :
		"""
		�ָ��������Ե� 0,0 λ��
		"""
		self.__scrollRate = 0, 0
		self.__resetScroll()

# -*- coding: gb18030 -*-

"""
implement animation icon class

2009/03/03: writen by huangyongwei
"""

import os
from guis import *
from guis.controls.Icon import Icon

class FaceIcon( Icon ) :
	def __init__( self, pyBinder = None ) :
		icon = GUI.load( "guis/tooluis/emotionbox/icon.gui" )
		Icon.__init__( self, icon )
		self.focus = False
		self.crossFocus = True

		self.__animIcon = ""								# 动画贴图路径
		self.__staticIcon = ""							# 静态贴图路径
		self.__sign = ""								# 仅仅显示转移字符
		self.__dsp = ""
		self.__isPlaying = False							# 是否处于播放动画状态

		self.icon = ""


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		Icon.onMouseEnter_( self )
		if self.icon == "":return
		self.play()
		rds.ccursor.set( "hand" )
		toolbox.infoTip.showToolTips( self, self.__sign )

	def onMouseLeave_( self ) :
		Icon.onMouseLeave_( self )
		self.stop()
		rds.ccursor.normal()
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, emote):
		"""
		更新图标等信息
		"""
		if emote is None:
			self.icon = ""
			self.__animIcon = ""
			self.__dsp = ""
			self.__sign = ""
		else:
			self.__sign = emote.sign
			self.__animIcon = emote.path
			self.__dsp = emote.dsp
			self.__staticIcon = emote.path
			self.icon = emote.path
		
	def play( self ) :
		"""
		播放动画
		"""
		self.__isPlaying = True
		Icon._setTexture( self, self.__animIcon )

	def stop( self ) :
		"""
		停止动画播放
		"""
		self.__isPlaying = False
		Icon._setTexture( self, self.__staticIcon )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSign( self ) :
		return self.__sign

	# ---------------------------------------
	def _getIcon( self ) :
		return self.__animIcon

	def _setIcon( self, icon ) :
		self.__animIcon = icon
		self.__staticIcon = icon
		if icon != "" :
			path, file = os.path.split( icon )
			name, ext = os.path.splitext( file )
			if ext == ".texanim" :
				self.__staticIcon = "%s/%s/1.dds" % ( path, name )		# 截取第一帧作为静态贴图
		if self.__isPlaying :
			Icon._setTexture( self, self.__animIcon )
		else :
			Icon._setTexture( self, self.__staticIcon )

	# -------------------------------------------------
	def _getPlaying( self ) :
		return self.__isPlaying


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	sign = property( _getSign )
	icon = property( _getIcon, _setIcon )
	playing = property( _getPlaying )

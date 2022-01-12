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

		self.__animIcon = ""								# ������ͼ·��
		self.__staticIcon = ""							# ��̬��ͼ·��
		self.__sign = ""								# ������ʾת���ַ�
		self.__dsp = ""
		self.__isPlaying = False							# �Ƿ��ڲ��Ŷ���״̬

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
		����ͼ�����Ϣ
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
		���Ŷ���
		"""
		self.__isPlaying = True
		Icon._setTexture( self, self.__animIcon )

	def stop( self ) :
		"""
		ֹͣ��������
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
				self.__staticIcon = "%s/%s/1.dds" % ( path, name )		# ��ȡ��һ֡��Ϊ��̬��ͼ
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

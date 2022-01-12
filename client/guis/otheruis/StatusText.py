# -*- coding: gb18030 -*-
#
# $Id: CenterMessage.py,v 1.4 2008-08-26 02:21:16 huangyongwei Exp $

"""
"""

import BigWorld
import GUI
import reimpl_statusText
from event import EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI


# --------------------------------------------------------------------
# --------------------------------------------------------------------
# �Զ�������ʾ��Ϣ
# --------------------------------------------------------------------
class StatusText( PyGUI ):
	"""
	�Զ�������ʾ��Ϣ
	"""
	def __init__( self, guiFilePath ):
		word = GUI.load( guiFilePath )
		GUI.addRoot( word )
		PyGUI.__init__( self, word )
		self.visible = False


# --------------------------------------------------------------------
# �Զ�������ʾ��Ϣ������
# --------------------------------------------------------------------
class StatusTextController:
	"""
	�Զ�������ʾ������,����Ķ�����ʾͬʱֻ����ʾһ������˱��뱣֤�����Ķ�����ȡ��
	"""
	def __init__( self ):
#		self.__pyAutoFightText = StatusText( self.__getStatusTextGui( "autoFight" ) )
		self.__pyAutoRunText = StatusText( self.__getStatusTextGui( "autoRun" ) )
		self.__triggers = {}
#		self.__triggers["EVT_ON_START_AUTOFIGHT"] = self.__startAutofight
#		self.__triggers["EVT_ON_STOP_AUTOFIGHT"] = self.__stopAutofight
		self.__triggers["EVT_ON_START_AUTORUN"] = self.__startAutorun
		self.__triggers["EVT_ON_STOP_AUTORUN"] = self.__stopAutorun
		for key in self.__triggers :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __startAutofight( self ) :
		self.__pyAutoFightText.visible = True

	def __stopAutofight( self ) :
		self.__pyAutoFightText.visible = False

	def __startAutorun( self, dpos ) :
		self.__pyAutoRunText.visible = True

	def __stopAutorun( self, success ) :
		self.__pyAutoRunText.visible = False
	
	@reimpl_statusText.deco_guiStatusText
	def __getStatusTextGui( self, status ):
		"""
		��ȡ�Զ�ս�������Զ�Ѱ·����
		"""
		if status == "autoFight":
			return "guis/general/autofightwindow/autoFightState.gui"
		elif status == "autoRun":
			return "guis/tooluis/navigateWord/navigateWord.gui"

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

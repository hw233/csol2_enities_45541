# -*- coding: gb18030 -*-
#
# $Id: UIScriptWrapper.py,v 1.1 2008-06-21 01:34:49 huangyongwei Exp $

"""
This module script wrapper for engine ui

2008/06/13: writen by huangyongwei
"""

import weakref
import GUI
import Debug
import util
from bwdebug import *


# --------------------------------------------------------------------
# implement wrapping function
# --------------------------------------------------------------------
def wrap( ui, pyUI ) :
	"""
	������ UI �� ptyhon UI ���������÷�װ��
	@type				ui	 : engine UI
	@param				ui	 : ���� UI
	@type				pyUI : python UI / None
	@param				pyUI : python UI( �����Ϊ None�����ʾ������� UI �� script ���� )
	@return					 : None
	"""
	GUIBaseObject = __import__( "guis/common/GUIBaseObject" ).GUIBaseObject
	if isDebuged : assert isinstance( ui, GUI.Simple ) == True, "ui must be an engine ui!"
	#assert isinstance( pyUI, GUIBaseObject ) == True, "pyUI must inherit from GUIBaseObject"
	if pyUI is None :
		ui.script = None
	else :
		ui.script = _ScriptWrapper( ui, pyUI )

def unwrap( ui ) :
	"""
	������ UI ���н������ȡ���� UI ����Ӧ�� python UI
	@type				ui : engine ui
	@param				ui : ���� UI
	@rtype				   : python UI
	@return				   : �������� UI �� script ����Ӧ�� python UI
	"""
	if ui.script is None : return None
	return getattr( ui.script, "pyUI", ui.script )			# ����а�װ������ͨ����װ�����أ�����ֱ�ӷ��� script


# --------------------------------------------------------------------
# implement inner script wrapper class
# --------------------------------------------------------------------
class _ScriptWrapper( object ) :
	__slots__ = ( "_ScriptWrapper__weakUI", "_ScriptWrapper__pyWeakUI" )
	"""
	��Ҫ���� python UI �� ���� UI �������ù�ϵ
	�����ֹ�ϵ�ֲ�������������ã���ʹ�ã���û�нű����� python UI ʱ�����ܵõ���ʱ���ͷ�
	"""
	def __init__( self, ui, pyUI ) :
		self.__weakUI = weakref.ref( ui, self.__onDie )				# �������� UI
		self.__pyWeakUI = weakref.ref( pyUI, self.__onPyDie )		# ���� python UI


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __del__( self ) :
		if Debug.output_del_ScriptWrapper :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def ui( self ) :
		"""
		��ȡ��Ӧ������ UI
		"""
		if self.__weakUI is None :
			return None
		return self.__weakUI()

	@property
	def pyUI( self ) :
		"""
		��ȡ��Ӧ�� python UI
		"""
		if self.__pyWeakUI is None :
			return None
		return self.__pyWeakUI()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onDie( self, weaker ) :
		"""
		����Ӧ������ UI ����ʱ������
		ע�⣺һ������£����÷���������ʱ����ζ�Ÿ����� UI ����Ӧ�� python ui �Ѿ����ͷŵ�
			  ���ߣ�������Ӧ�� python UI �Ѿ���Ϊ���ñ���������
			  ��Ϊ��python UI ������ UI ��ǿ���ù�ϵ�����ԣ�python û���ͷţ����� UI Ҳ�����ͷŵ�
		"""
		del self.__weakUI									# ȡ�������� UI ������
		del self.__pyWeakUI									# ȡ���� pthon UI ������
															# ע�⣺���ﲻ��ɾ�� python UI ������Ϊ���� UI �ͷŲ������� python UI �Ѿ��ͷ�
															# �п��ܻ��б�Ľű����� python UI ������

	def __onPyDie( self, weaker ) :
		"""
		����Ӧ�� python UI ����ʱ������
		ע�⣺�� python UI ɾ��ʱ��������Ӧ������ UI ҲҪ�ͷŵ�
			  ��Ҫ�ͷ����� UI������Ҫ��������п��ܶ����� UI ������
		"""
		ui = self.ui
		if ui is None : return
		ui.script = None									# ��� ui �� script ��װ��
		ui.focus = False									# �� focus �б���ɾ��
		ui.moveFocus = False								# �� moveFocus �б���ɾ��
		ui.crossFocus = False								# �� crollsFocus �б���ɾ��
		ui.dragFocus = False								# �� dragFocus �б���ɾ��
		ui.dropFocus = False								# �� dropFocus �б���ɾ��
		if ui.parent :										# ����и���
			ui.parent.delChild( ui )						# �򣬽� UI �����ĸ����г���
		elif ui in GUI.roots() :							# ��� UI ���� root �б���
			GUI.delRoot( ui )								# ����б������
		for n, ch in ui.children :							# ͬʱ
			ui.delChild( ch )								# �ͷ������е��� UI
		del self.__weakUI									# ȡ�������� UI ������
		del self.__pyWeakUI									# ȡ���� pthon UI ������


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleKeyEvent" ) :
			return pyUI.handleKeyEvent( down, key, mods )
		return False

	def handleAxisEvent( self, axis, value, dTime ):
		pyUI = self.pyUI
		if hasattr( pyUI, "handleAxisEvent" ) :
			return pyUI.handleAxisEvent( axis, value, dTime )
		return False

	def handleMouseButtonEvent( self, comp, key, down, mods, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseButtonEvent" ) :
			return pyUI.handleMouseButtonEvent( comp, key, down, mods, pos )
		return False

	def handleMouseClickEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseClickEvent" ) :
			return pyUI.handleMouseClickEvent( comp, pos )
		return False

	def handleMouseEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseEvent" ) :
			return pyUI.handleMouseEvent( comp, pos )
		return False

	def handleMouseEnterEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseEnterEvent" ) :
			return pyUI.handleMouseEnterEvent( comp, pos )
		return False

	def handleMouseLeaveEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseLeaveEvent" ) :
			return pyUI.handleMouseLeaveEvent( comp, pos )
		return False

	def handleDragStartEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragStartEvent" ) :
			return pyUI.handleDragStartEvent( comp, pos )
		return False

	def handleDragStopEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragStopEvent" ) :
			return pyUI.handleDragStopEvent( comp, pos )
		return False

	def handleDragEnterEvent( self, comp, pos, dragged ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragEnterEvent" ) :
			return pyUI.handleDragEnterEvent( comp, pos, dragged )
		return False

	def handleDragLeaveEvent( self, comp, pos, dragged ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragLeaveEvent" ) :
			return pyUI.handleDragLeaveEvent( comp, pos, dragged )
		return False

	def handleDropEvent( self, comp, pos, dropped ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDropEvent" ) :
			return pyUI.handleDropEvent( comp, pos, dropped )
		return False

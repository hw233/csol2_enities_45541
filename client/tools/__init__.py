# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.4 2008-08-30 09:12:53 huangyongwei Exp $
#
"""
implement cameras, it moved from love3.py
2008/07/29: created by huangyongwei
"""

# --------------------------------------------------------------------
# ע�⣺��ӵ��������еĹ��߱���ʵ�� ITool �ӿ�
#
# --------------------------------------------------------------------

import csol
import love3
from guis import *
from ITool import ITool
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from config.client.msgboxtexts import Datas as mbmsgs

# --------------------------------------------------------------------
# implement tool manager
# --------------------------------------------------------------------
class ToolMgr :
	__inst = None

	def __init__( self ) :
		self.__pyTools = {}						# ��������ע��Ĺ���
		self.__pyToolsMenu = None				# �г����й��ߵĲ˵�
		self.__pyCurrTool = None				# ��ǰ����ʹ�õĹ���

		self.__isShowAllHitUIs = False			# ��ʱ��������ʾ���������е� UI
		self.__pyMouseHitUI = None
		self.__mousePos = ( 0, 0 )

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = ToolMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __isMouseHit( self ) :
		"""
		����Ƿ�����κ�һ������
		"""
		for pyTool in self.__pyTools.itervalues() :
			if not pyTool.visible : continue
			if pyTool.isMouseHit() :
				return True
		return False

	def __showTool( self, pyUI ) :
		"""
		��ʾָ������
		"""
		if self.__pyCurrTool.visible : return
		if pyUI is None :
			# "�Ҳ������ʵĿؼ�"
			showAutoHideMessage( 3.0, 0x0e41, "" )
			return
		for pyTool in self.__pyTools.itervalues() :
			if pyTool.visible :
				# "�����ȹر� %s"
				showAutoHideMessage( 3.0, mbmsgs[0x0e42] % pyTool.getCHName(), "" )
				return
		self.__pyCurrTool.show( pyUI )

	# -------------------------------------------------
	def __listTools( self ) :
		"""
		�ڲ˵����г����й���
		"""
		if self.__pyToolsMenu :
			self.__pyToolsMenu.popup()
			return
		self.__pyToolsMenu = ContextMenu()
		self.__pyToolsMenu.onItemClick.bind( self.__onToolMenuItemClick )
		for name in self.__pyTools :
			pyItem = DefMenuItem( name )
			self.__pyToolsMenu.pyItems.add( pyItem )
		self.__pyToolsMenu.popup()

	def __listHitUIs( self, pyUIs ) :
		"""
		�г����������е� UI
		"""
		self.__pyUIsMenu = ContextMenu()
		self.__pyUIsMenu.onItemClick.bind( self.__onUIMenuItemClick )
		for name, pyUI in pyUIs :
			pyItem = DefMenuItem( name )
			pyItem.pyMapUI = pyUI
			self.__pyUIsMenu.pyItems.add( pyItem )
		self.__pyUIsMenu.popup()

	# -------------------------------------------------
	def __onToolMenuItemClick( self, pyItem ) :
		"""
		ѡ��ĳ������ʱ������
		"""
		self.__pyCurrTool = self.__pyTools[pyItem.text]
		if pyItem.text == "����༭��" :
			self.__pyCurrTool.show( None )
			return
		if self.__isShowAllHitUIs :								# �г������е� UI ���û�ѡ��
			pyUIs = self.__pyCurrTool.getHitUIs( self.__pyMouseHitUI, self.__mousePos )
			if len( pyUIs ) :
				self.__listHitUIs( pyUIs )
		else :													# ֱ��ѡ��ָ���� UI���ɹ����Լ��ṩ��
			pyUI = self.__pyCurrTool.getHitUI( self.__pyMouseHitUI, self.__mousePos )
			self.__showTool( pyUI )

	def __onUIMenuItemClick( self, pyItem ) :
		"""
		ѡ���г�ѡ�е�ĳ�� UI
		"""
		self.__showTool( pyItem.pyMapUI )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addTool( self, pyTool ) :
		"""
		���һ�����ߵ�������
		"""
		assert isinstance( pyTool, ITool ), "tool added to manager must be implemented ITool"
		self.__pyTools[pyTool.getCHName()] = pyTool

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if down and key in [KEY_MOUSE0, KEY_MOUSE1] and \
			mods == MODIFIER_SHIFT | MODIFIER_CTRL | MODIFIER_ALT :
				if self.__isMouseHit() : return True							# ����������һ������
				self.__pyMouseHitUI = ruisMgr.getMouseHitRoot()					# ��¼��Ҫ�����߲����Ĵ���
				self.__mousePos = csol.pcursorPosition()
				if self.__pyMouseHitUI is None : return True
				self.__listTools()
				self.__isShowAllHitUIs = ( key == KEY_MOUSE1 )
				return True
		elif down and key in [KEY_P] and \
			mods == MODIFIER_SHIFT | MODIFIER_CTRL | MODIFIER_ALT :				# ����༭����ݼ�
				self.__pyCurrTool = self.__pyTools["����༭��"]
				self.__pyCurrTool.show( None )
		elif self.__pyCurrTool and self.__pyCurrTool.rvisible :
			if self.__pyCurrTool.preKeyEvent( down, key, mods ) :
				return True
		return False


# --------------------------------------------------------------------
# global instnace
# --------------------------------------------------------------------
toolMgr = ToolMgr.instance()

# --------------------------------------------------------------------
# change global event function
# --------------------------------------------------------------------
l3_handleKeyEvent = love3.handleKeyEvent
def handleKeyEvent( down, key, mods ):
	if toolMgr.handleKeyEvent( down, key, mods ) :
		return True
	return l3_handleKeyEvent( down, key, mods )

love3.handleKeyEvent = handleKeyEvent

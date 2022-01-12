# -*- coding: gb18030 -*-
#
# $Id: ITool.py,v 1.1 2008-08-01 02:11:10 huangyongwei Exp $
#
"""
implement tool's interface
2008/07/29: created by huangyongwei
"""

from AbstractTemplates import AbstractClass

# --------------------------------------------------------------------
# 注意：添加到管理器中的工具必须实现以下的 ITool 接口
# --------------------------------------------------------------------
class ITool( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self ) :
		"""
		强制实现接口
		"""
		pass


	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def getCHName( self ) :
		"""
		获取工具的中文名称
		"""
		return ""

	# -------------------------------------------------
	def getHitUIs( self, pyRoot, mousePos ) :
		"""
		提供一组 UI 列表供用户选择，pyRoot 是鼠标击中的最上层那个 UI: ( 显示在菜单列表上的名字，UI )
		"""
		return []

	def getHitUI( self, pyRoot, mousePos ) :
		"""
		用户选取了某个 UI，pyRoot 是鼠标击中的最上层那个 UI，如果找不到则返回 None
		"""
		return None

	def show( self, pyUI ) :
		"""
		显示工具
		"""
		pass

	def hide( self ) :
		"""
		隐藏工具
		"""
		pass

	# -------------------------------------------------
	def preKeyEvent( self, down, key, mods ) :
		"""
		按键优先事件
		"""
		return False

	__abstract_methods.add( getCHName )
	__abstract_methods.add( getHitUIs )
	__abstract_methods.add( getHitUI )
	__abstract_methods.add( show )
	__abstract_methods.add( hide )

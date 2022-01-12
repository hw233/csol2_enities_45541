# -*- coding: gb18030 -*-
#
# $Id: GUIBaseObject.py,v 1.45 2008-08-27 09:03:34 huangyongwei Exp $

"""
implement base python class of gui。
2005/03/20 : writen by huangyongwei
"""
"""
composing :
	XXGUIComponent
"""

import os
import weakref
import Math
import guis.Debug as Debug
import BigWorld
from guis import *


class GUIBaseObject( object ) :
	def __init__( self, guiObject = None ) :
		object.__init__( self )
		self.__guiObject = None					# 对应的引擎 UI
		self.__initialize( guiObject )			# 初始化
		self.__disposed = False					# 是否已经析构

		self.__hDockStyle = "LEFT"				# 在水平方向上，相对其父亲的停靠方式："HFILL", "LEFT", "CENTER", "RIGHT", "S_LEFT", "S_CENTER", "S_RIGHT"
		self.__vDockStyle = "TOP"				# 在垂直方向上，相对其父亲的停靠方式："VFILL", "TOP", "MIDDLE", "BOTTOM", "S_TOP", "S_MIDDLE", "S_BOTTOM"
		self.__hDockChildren = WeakList()		# 保存水平方向上，所有相对于我而停靠的所有子 UI（这里使用弱引用链表，以免使得子 UI 无以释放）
		self.__vDockChildren = WeakList()		# 保存水平方向上，所有相对于我而停靠的所有子 UI（这里使用弱引用链表，以免使得子 UI 无以释放）

	def subclass( self, guiObject ) :
		self.__initialize( guiObject )
		return self

	def dispose( self ) :
		"""
		手工 dispose 函数。其实该函数意义不大，因为如果还有别的脚本对我保留有引用
		即便调用了该函数，也无法释放。这里只作了一些简单的属性清理工作
		"""
		if self.pyParent is not None :						# 如果 parent 的 python 存在
			self.pyParent.__delDockChild( self )			# 则将我从父亲的 dock style 列表中清除
		gui = self.__guiObject
		if gui.parent is None : GUI.delRoot( gui )			# 如果 parent 是 None，则意味着我是顶层 UI，要从 root 中清除
		else : gui.parent.delChild( gui )					# 与父亲脱离父子关系
		for n, ch in gui.children :							# 与所有的孩子
			gui.delChild( ch )								# 脱离父子关系
		gui.script = None									# 取消对引擎 UI 的引用
		self.__disposed = True								# 标记已经析构掉

	def __del__( self ) :
		if Debug.output_del_GUIBaseObject :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, guiObject ) :
		if guiObject is None : return
		if self.__guiObject is None :
			self.__guiObject = guiObject					# 引用引擎 UI（这里使用强引用的目的是，保证只要 python UI 存在，则其对应的引擎 UI 也存在）
			UIScriptWrapper.wrap( guiObject, self )			# 使引擎 UI 也对 python UI 进行绑定
															#（这里使用包装器的目的是，使引擎 UI 对 python UI 的引用为 弱引用，这些弱引用的步骤就是在
															# 包装器中完成的，这样就防止了引擎 UI 与 python UI 之间的交叉引用）
		else :
			self.resetBindingUI_( guiObject )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addDockChild( self, pyChild ) :
		"""
		添加一个孩子相对于我的停靠方式
		"""
		if pyChild.h_dockStyle != "LEFT" :					# 排除掉左停靠，因为默认是左停靠
			if pyChild not in self.__hDockChildren :
				self.__hDockChildren.append( pyChild )
		elif pyChild in self.__hDockChildren :				# 如果是从别的停靠方式改为左停靠方式，
			self.__hDockChildren.remove( pyChild )			# 则，从停靠列表中清除（不需要记录左停靠）
		if pyChild.v_dockStyle != "TOP" :					# 排除掉上停靠，因为默认是上停靠
			if pyChild not in self.__vDockChildren :
				self.__vDockChildren.append( pyChild )
		elif pyChild in self.__vDockChildren :				# 如果是从别的停靠方式改为上停靠方式，
			self.__vDockChildren.remove( pyChild )			# 则，从停靠列表中清除（不需要记录上停靠）

	def __delDockChild( self, pyChild ) :
		"""
		删除一个孩子相对于我的停靠方式
		"""
		if pyChild in self.__hDockChildren :
			self.__hDockChildren.remove( pyChild )
		if pyChild in self.__vDockChildren :
			self.__vDockChildren.remove( pyChild )


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onParentWidthChanged_( self, oldWidth, newWidth ) :
		"""
		当父亲的宽度改变时被调用
		"""
		if self.h_dockStyle == "CENTER" :						# 如果是水平中间停靠
			self.left += ( newWidth - oldWidth ) / 2.0			# 则，我中间与父亲中点的距离值是恒值
		elif self.h_dockStyle == "RIGHT" :						# 如果是右停靠
			self.left += ( newWidth - oldWidth )				# 则，我右边与父亲右边的距离值是恒等值
		elif  self.h_dockStyle == "HFILL" :						# 如果是水平扩展方式
			self.width += ( newWidth - oldWidth )				# 则，父亲的宽度增大多少，我的宽度也跟着增大多少
		elif self.h_dockStyle == "S_LEFT" :						# 如果是左伸缩停靠方式
			self.left *= ( newWidth / oldWidth )				# 则我的左距随父亲的宽度变化而按比例变化（比例值是，父亲宽度变化前后的比值）
		elif self.h_dockStyle == "S_CENTER" :					# 如果是中间伸缩停靠方式
			oldCenter = oldWidth / 2 - self.center				# 则，我中间点与父亲中间点的距离随父亲宽度的变化而按比例变化（比例值是，父亲宽度变化前后的比值）
			newCenter = oldCenter * ( newWidth / oldWidth )
			self.center = newWidth / 2 - newCenter
		elif self.h_dockStyle == "S_RIGHT" :					# 如果是右边伸缩停靠
			oldRight = oldWidth - self.right					# 则，我右边与父亲右边的距离随父亲宽度的变化而按比例变化（比例值是，父亲宽度变化前后的比值）
			newRight = oldRight * ( newWidth / oldWidth )
			self.right = newWidth - newRight

	def onParentHeightChanged_( self, oldHeight, newHeight ) :
		"""
		当父亲的高度变化时被调用
		"""
		if self.v_dockStyle == "MIDDLE" :						# 如果是垂直中间停靠
			self.top += ( newHeight - oldHeight ) / 2.0         # 则，我中间与父亲中点的距离值是恒值
		elif self.v_dockStyle == "BOTTOM" :                     # 如果是底部停靠
			self.bottom += ( newHeight - oldHeight )            # 则，我底边与父亲底边的距离值是恒等值
		elif self.v_dockStyle == "VFILL" :                      # 如果是垂直扩展方式
			self.height += ( newHeight - oldHeight )            # 则，父亲的高度增大多少，我的高度也跟着增大多少
		elif self.v_dockStyle == "S_TOP" :                      # 如果是上伸缩停靠方式
			self.top *= ( newHeight / oldHeight )               # 则我的上距随父亲的宽度变化而按比例变化（比例值是，父亲高度变化前后的比值）
		elif self.v_dockStyle == "S_MIDDLE" :                   # 如果是中间伸缩停靠方式
			oldMiddle = oldHeight / 2 - self.middle             # 则，我中间点与父亲中间点的距离随父亲宽度的变化而按比例变化（比例值是，父亲高度变化前后的比值
			newMiddle = oldMiddle * ( newHeight / oldHeight )
			self.middle = newHeight / 2 - newMiddle
		elif self.v_dockStyle == "S_BOTTOM" :                   # 如果是底边伸缩停靠
			oldBottom = oldHeight - self.bottom                 # 则，我底边与父亲右边的距离随父亲高度的变化而按比例变化（比例值是，父亲高度变化前后的比值）
			newBottom = oldBottom * ( newHeight / oldHeight )
			self.bottom = newHeight - newBottom


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def resetBindingUI_( self, gui ) :
		"""
		重新设置我所绑定的引擎 UI
		"""
		if gui == self.__guiObject : return
		oldGui = self.__guiObject								# 首先保存旧的引擎 UI
		self.__guiObject = gui									# 设置绑定的引擎 UI 为新设置的 UI
		UIScriptWrapper.wrap( gui, self )						# 包装新引擎 UI 与我的引用关系
		UIScriptWrapper.wrap( oldGui, None )					# 撤销就引擎 UI 的引用关系（如果就引擎 UI 没有别的引用，当前方法调用结束后它将会释放）
		parent = oldGui.parent									# 原来的父引擎 UI
		if parent is None :										# 如果原来没有有父 UI，则说明旧的引擎 UI 是顶层 UI
			if oldGui in GUI.roots() :							# 如果旧的引擎 UI 在 rool 中
				GUI.delRoot( oldGui )							# 则清除它
				GUI.addRoot( gui )								# 将新的引擎 UI 添加到 root 中
		else :													# 如果原来有父 UI
			for n, ch in parent.children :						# 则，遍历父 UI
				if ch != oldGui : continue						# 找到旧引擎 UI 在父 UI 中的位置
				parent.addChild( gui, n )						# 让新的 UI 替代旧的 UI
				break

		for ch in util.preFindGui( oldGui ) :					# 前序序遍找出旧 UI 的所有子孙 UI
			if ch.parent : ch.parent.delChild( ch )				# 并将它们的所有的父子关系逐个解除（只有关系解除才能实现自动释放）

	# -------------------------------------------------
	def onWidthChanged_( self, oldWidth ) :
		"""
		当我的宽度改变时被调用
		"""
		pass

	def onHeightChanged_( self, oldHeight ) :
		"""
		当我的高度改变时被调用
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getGui( self ) :
		"""
		获取对应的引擎 UI
		"""
		return self.__guiObject

	def resort( self ) :
		"""
		对 UI 按位置的 Z 值进行重新排序
		"""
		self.__guiObject.reSort()

	def hitTest( self, x, y ) :
		"""
		判断屏幕上某二维点是否落在我身上
		"""
		return self.__guiObject.hitTest( x, y )

	def isMouseHit( self ) :
		"""
		判断鼠标是否指在我身上
		"""
		return s_util.isMouseHit( self.__guiObject )

	# -------------------------------------------------
	def setToDefault( self, tiled = False ) :
		"""
		将我的各个属性设置为创世 UI 的默认属性值
		"""
		gui = self.__guiObject
		gui.verticalAnchor = "TOP"					# 设置引擎中的垂直停靠方式为默认
		gui.horizontalAnchor = "LEFT"				# 设置引擎中的水平停靠方式为默认
		gui.materialFX = "BLEND"					# 设置默认贴图的渲染方式
		gui.widthRelative = False					# 默认使用像素坐标
		gui.heightRelative = False					# 默认使用像素坐标
		gui.tiled = tiled							# 是否采用平铺模式

	# -------------------------------------------------
	def addPyChild( self, pyChild, name = "" ) :
		"""
		添加一个子 UI
		"""
		if name == "" :											# 没名字的添加方式
			self.__guiObject.addChild( pyChild.getGui() )
		else :
			self.__guiObject.addChild( pyChild.getGui(), name )	# 有名字的添加方式

		# 下面的做法很怪异，但引擎有一个 bug，只有通过以下方法，才能解决该 bug
		focus = getattr( pyChild, "focus", False )				# 获取子 UI 的 focus 属性
		if focus :												# 如果子 UI 原来的 focus 为 True
			child = pyChild.getGui()
			child.focus = False									# 则首先要将子 UI 的 focus 属性置为 false（为的是让它再次设置为 True 时有效）
			child.focus = True									# 重新设置为 True（其实引擎内部是将子 UI添加到 focus 列表）
																# 如果之前没有将它的 focus 设置为 False，这里直接设置为 True
																# 则引擎首先判断，设置前后的值是否一样，如果一样的话，将不会将 UI 添加到
																# fosus 列表（这是引擎的一个 bug，但其他的 focus（如：crossFocus 等） 没有该问题）
		self.__addDockChild( pyChild )							# 添加到停靠列表

	def delPyChild( self, pyChild ) :
		"""
		删除一个子 UI
		"""
		self.__delDockChild( pyChild )
		self.__guiObject.delChild( pyChild.getGui() )

	def clearChildren( self ) :
		"""
		清除所有子 UI
		"""
		for n, ch in self.__guiObject.children :
			self.__guiObject.delChild( ch )
		self.__hDockChildren.clear()
		self.__vDockChildren.clear()

	# -------------------------------------------------
	def getPosToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标位置（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的位置）
		"""
		pos = pyUI.posToScreen()
		selfPos = self.posToScreen()
		pos = selfPos[0] - pos[0], selfPos[1] - pos[1]
		return pos

	def getRPosToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标位置（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的位置）
		"""
		pos = pyUI.r_posToScreen()
		selfPos = self.r_posToScreen()
		pos = selfPos[0] - pos[0], selfPos[1] - pos[1]
		return pos

	# ---------------------------------------
	def getLeftToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标左距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的左距）
		"""
		return self.leftToScreen - pyUI.leftToScreen

	def getRLeftToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标左距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的左距）
		"""
		return self.r_leftToScreen - pyUI.r_leftToScreen

	def getCenterToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标中距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的中距）
		"""
		return self.centerToScreen - pyUI.leftToScreen

	def getRCenterToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标中距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的中距）
		"""
		return self.r_centerToScreen - pyUI.r_leftToScreen

	def getRightToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标右距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的右距）
		"""
		return self.rightToScreen - pyUI.leftToScreen

	def getRRightToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标右距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的右距）
		"""
		return self.r_rightToScreen - pyUI.r_leftToScreen

	# ---------------------------------------
	def getTopToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标顶距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的顶距）
		"""
		return self.topToScreen - pyUI.topToScreen

	def getRTopToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标顶距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的顶距）
		"""
		return self.r_topToScreen - pyUI.r_topToScreen

	def getMiddleToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标垂直中距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的垂直中距）
		"""
		return self.middleToScreen - pyUI.topToScreen

	def getRMiddleToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标垂直中距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的垂直中距）
		"""
		return self.r_middleToScreen - pyUI.r_topToScreen

	def getBottomToUI( self, pyUI ) :
		"""
		获取我相对与某个 UI 的像素坐标底距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的底距）
		"""
		return self.bottomToScreen - pyUI.topToScreen

	def getRBottomToParent( self, pyUI ) :
		"""
		获取我相对与某个 UI 的相对坐标底距（一般情况下用于需要获得 相对于 父亲 或 父亲的父亲 的底距）
		"""
		return self.r_bottomToScreen - pyUI.r_topToScreen


	# ----------------------------------------------------------------
	# common properties
	# ----------------------------------------------------------------
	def _getDisposed( self ) :
		return self.__disposed

	# -------------------------------------------------
	def _getName( self ) :
		return self.__guiObject.name

	def _setName( self, name ) :
		self.__guiObject.name = name

	# -------------------------------------------------
	def _getParent( self ) :
		parent = self.__guiObject.parent
		if parent is None :
			return None
		return UIScriptWrapper.unwrap( parent )

	def _getNearParent( self ) :
		parent = self.__guiObject.parent
		while parent :
			pyParent = UIScriptWrapper.unwrap( parent )
			if pyParent : return pyParent
			parent = parent.parent
		return None

	def _getTopParent( self ) :
		parent = self.__guiObject.topParent
		return UIScriptWrapper.unwrap( parent )

	# -------------------------------------------------
	def _getVisible( self ) :
		return self.getGui().visible

	def _setVisible( self, value ) :
		self.__guiObject.visible = value

	def _getRVisible( self ) :
		return self.getGui().rvisible

	# -------------------------------------------------
	def _getColor( self ) :
		return self.__guiObject.colour.tuple()

	def _setColor( self, color ) :
		if len( color ) == 3 :
			a = self.__guiObject.colour.alpha
			color = tuple( color ) + ( a, )
		self.__guiObject.colour = color

	# ---------------------------------------
	def _getAlpha( self ) :
		return self.__guiObject.colour.alpha

	def _setAlpha( self, value ) :
		self.__guiObject.colour.alpha = value

	# -------------------------------------------------
	def _getTexture( self ) :
		return self.__guiObject.textureName

	def _setTexture( self, texture ) :
		if isinstance( texture, BigWorld.PyTextureProvider ):
			self.__guiObject.texture = texture
		else:
			self.__guiObject.textureName = texture

	# ---------------------------------------
	def _getTextureFolder( self ) :
		return "/".join( self.texture.split( "/" )[:-1] )

	# -------------------------------------------------
	def _getMapping( self ) :
		return self.__guiObject.mapping

	def _setMapping( self, mapping ) :
		self.__guiObject.mapping = mapping

	# ---------------------------------------
	def _getMaterialFX( self ) :
		return self.__guiObject.materialFX

	def _setMaterialFX( self, style ) :
		self.__guiObject.materialFX = style

	# ----------------------------------------------------------------
	# pos properties
	# ----------------------------------------------------------------
	def _getHorizontalDockStyle( self ) :
		return self.__hDockStyle

	def _setHorizontalDockStyle( self, dockStyle ) :
		if isDebuged :
			assert dockStyle in ["HFILL", "LEFT", "CENTER", "RIGHT", "S_LEFT", "S_CENTER", "S_RIGHT"]
		self.__hDockStyle = dockStyle
		pyParent = self.pyParent
		if pyParent is not None :
			pyParent.__addDockChild( self )

	# ---------------------------------------
	def _getVerticalDockStyle( self ) :
		return self.__vDockStyle

	def _setVerticalDockStyle( self, dockStyle ) :
		if isDebuged :
			assert dockStyle in ["VFILL", "TOP", "MIDDLE", "BOTTOM", "S_TOP", "S_MIDDLE", "S_BOTTOM"]
		self.__vDockStyle = dockStyle
		pyParent = self.pyParent
		if pyParent is not None :
			pyParent.__addDockChild( self )

	# -------------------------------------------------
	def _getHAnchor( self ) :
		return self.__guiObject.horizontalAnchor

	def _setHAnchor( self, anchor ) :
		self.__guiObject.horizontalAnchor = anchor

	# ---------------------------------------
	def _getVAnchor( self ) :
		return self.__guiObject.verticalAnchor

	def _setVAnchor( self, anchor ) :
		self.__guiObject.verticalAnchor = anchor

	# -------------------------------------------------
	def _getLeft( self ) :
		return s_util.getGuiLeft( self.__guiObject )

	def _setLeft( self, left ) :
		s_util.setGuiLeft( self.__guiObject, left )

	# -------------------------------------------------
	def _getTop( self ) :
		return s_util.getGuiTop( self.__guiObject )

	def _setTop( self, top ) :
		s_util.setGuiTop( self.__guiObject, top )

	# -------------------------------------------------
	def _getRight( self ) :
		return s_util.getGuiRight( self.__guiObject )

	def _setRight( self, right ) :
		s_util.setGuiRight( self.__guiObject, right )

	# -------------------------------------------------
	def _getBottom( self ) :
		return s_util.getGuiBottom( self.__guiObject )

	def _setBottom( self, bottom ) :
		s_util.setGuiBottom( self.__guiObject, bottom )

	# -------------------------------------------------
	def _getCenter( self ) :
		return s_util.getGuiCenter( self.__guiObject )

	def _setCenter( self, center ) :
		s_util.setGuiCenter( self.__guiObject, center )

	# -------------------------------------------------
	def _getMiddle( self ) :
		return s_util.getGuiMiddle( self.__guiObject )

	def _setMiddle( self, middle ) :
		s_util.setGuiMiddle( self.__guiObject, middle )

	# -------------------------------------------------
	def _getPos( self ) :
		return s_util.getGuiPos( self.__guiObject )

	def _setPos( self, ( left, top ) ) :
		s_util.setGuiPos( self.__guiObject, ( left, top ) )

	# ----------------------------------------------------------------
	def _getRLeft( self ) :
		return s_util.getGuiRLeft( self.__guiObject )

	def _setRLeft( self, left ) :
		s_util.setGuiRLeft( self.__guiObject, left )

	# -------------------------------------------------
	def _getRTop( self ) :
		return s_util.getGuiRTop( self.__guiObject )

	def _setRTop( self, top ) :
		s_util.setGuiRTop( self.__guiObject, top )

	# -------------------------------------------------
	def _getRRight( self ) :
		return s_util.getGuiRRight( self.__guiObject )

	def _setRRight( self, right ) :
		s_util.setGuiRRight( self.__guiObject, right )

	# -------------------------------------------------
	def _getRBottom( self ) :
		return s_util.getGuiRBottom( self.__guiObject )

	def _setRBottom( self, bottom ) :
		s_util.setGuiRBottom( self.__guiObject, bottom )

	# -------------------------------------------------
	def _getRCenter( self ) :
		return s_util.getGuiRCenter( self.__guiObject )

	def _setRCenter( self, center ) :
		s_util.setGuiRCenter( self.__guiObject, center )

	# -------------------------------------------------
	def _getRMiddle( self ) :
		return s_util.getGuiRMiddle( self.__guiObject )

	def _setRMiddle( self, middle ) :
		s_util.setGuiRMiddle( self.__guiObject, middle )

	# -------------------------------------------------
	def _getRPos( self ) :
		return s_util.getGuiRPos( self.__guiObject )

	def _setRPos( self, ( left, top ) ) :
		s_util.setGuiRPos( self.__guiObject, ( left, top ) )

	# -------------------------------------------------
	def _getPosZ( self ) :
		return self.__guiObject.position.z

	def _setPosZ( self, z ) :
		self.__guiObject.position.z = z


	# ----------------------------------------------------------------
	# size properties
	# ----------------------------------------------------------------
	def _getWidth( self ) :
		return s_util.getGuiWidth( self.__guiObject )

	def _setWidth( self, width ) :
		oldWidth = s_util.getGuiWidth( self.__guiObject )
		s_util.setGuiWidth( self.__guiObject, width )
		for pyChild in self.__hDockChildren :
			pyChild.onParentWidthChanged_( oldWidth, width )
		if self.h_dockStyle == "CENTER" :
			self.left -= ( width - oldWidth ) / 2
		elif self.h_dockStyle == "RIGHT" :
			self.left -= width - oldWidth
		self.onWidthChanged_( oldWidth )

	# -------------------------------------------------
	def _getHeight( self ) :
		return s_util.getGuiHeight( self.__guiObject )

	def _setHeight( self, height ) :
		oldHeight = s_util.getGuiHeight( self.__guiObject )
		s_util.setGuiHeight( self.__guiObject, height )
		for pyChild in self.__vDockChildren :
			pyChild.onParentHeightChanged_( oldHeight, height )
		if self.v_dockStyle == "MIDDLE" :
			self.top -= ( height - oldHeight ) / 2
		elif self.v_dockStyle == "BOTTOM" :
			self.top -= height - oldHeight
		self.onHeightChanged_( oldHeight )

	# -------------------------------------------------
	def _getSize( self ) :
		width = self._getWidth()
		height = self._getHeight()
		return Math.Vector2( width, height )

	def _setSize( self, ( width, height ) ) :
		self._setWidth( width )
		self._setHeight( height )

	# ----------------------------------------------------------------
	def _getRWidth( self ) :
		return s_util.getGuiRWidth( self.__guiObject )

	def _setRWidth( self, width ) :
		pWidth = s_util.toPXMeasure( width )
		self._setWidth( width )

	# -------------------------------------------------
	def _getRHeight( self ) :
		return s_util.getGuiRHeight( self.__guiObject )

	def _setRHeight( self, height ) :
		pHeight = s_util.toPYMeasure( height )
		self._setHeight( height )

	# -------------------------------------------------
	def _getRSize( self ) :
		width = self._getRWidth()
		height = self._getRHeight()
		return ( width, height )

	def _setRSize( self, ( width, height ) ) :
		self._setRWidth( width )
		self._setRHeight( height )

	# -------------------------------------------------
	def _getTiled( self ) :
		return self.__guiObject.tiled

	def _setTiled( self, tiled ) :
		self.__guiObject.tiled = tiled

	def _getTileWidth( self ) :
		return self.__guiObject.tileWidth

	def _setTileWidth( self, width ) :
		self.__guiObject.tileWidth = width

	def _getTileHeight( self ) :
		return self.__guiObject.tileHeight

	def _setTileHeight( self, height ) :
		self.__guiObject.tileHeight = height


	# ----------------------------------------------------------------
	# pos to screen
	# ----------------------------------------------------------------
	def _getLeftToScreen( self ) :
		return s_util.getGuiLeftToScreen( self.__guiObject )

	def _getTopToScreen( self ) :
		return s_util.getGuiTopToScreen( self.__guiObject )

	def _getCenterToScreen( self ) :
		return s_util.getGuiCenterToScreen( self.__guiObject )

	def _getMiddleToScreen( self ) :
		return s_util.getGuiMiddleToScreen( self.__guiObject )

	def _getRightToScreen( self ) :
		return s_util.getGuiRightToScreen( self.__guiObject )

	def _getBottomToScreen( self ) :
		return s_util.getGuiBottomToScreen( self.__guiObject )

	def _getPosToScreen( self ) :
		return s_util.getGuiPosToScreen( self.__guiObject )

	# ----------------------------------------------------------------
	def _getRLeftToScreen( self ) :
		return s_util.getGuiRLeftToScreen( self.__guiObject )

	def _getRTopToScreen( self ) :
		return s_util.getGuiRTopToScreen( self.__guiObject )

	def _getRCenterToScreen( self ) :
		return s_util.getGuiRCenterToScreen( self.__guiObject )

	def _getRMiddleToScreen( self ) :
		return s_util.getGuiRMiddleToScreen( self.__guiObject )

	def _getRRightToScreen( self ) :
		return s_util.getGuiRRightToScreen( self.__guiObject )

	def _getRBottomToScreen( self ) :
		return s_util.getGuiRBottomToScreen( self.__guiObject )

	def _getRPosToScreen( self ) :
		return s_util.getGuiRPosToScreen( self.__guiObject )


	# ----------------------------------------------------------------
	# mouse pos relative from me
	# ----------------------------------------------------------------
	def _getMousePos( self ) :
		return s_util.getMouseInGuiPos( self.__guiObject )

	def _getRMousePos( self ) :
		return s_util.getMouseInGuiRPos( self.__guiObject )


	# ----------------------------------------------------------------
	# properies
	# ----------------------------------------------------------------
	disposed = property( _getDisposed )										# 指出是否已经析构掉

	# -------------------------------------------------
	# writable properties
	# -------------------------------------------------
	gui = property( lambda self : self.__guiObject )						# 获取引擎 UI
	txelems = property( lambda self : \
		getattr( self.__guiObject, "elements", {} ) )						# dict: 获取纹理对象（注：只有 GUI.TextureFrame 才有）
	visible = property( _getVisible, _setVisible )							# bool: 获取/设置可见性
	rvisible = property( _getRVisible )										# bool: 获取可见性（只要有父 UI 不可见，都为 False）
	name = property( _getName, _setName )									# str: 获取/设置名字
	color = property( _getColor, _setColor )								# tuple / Vector4: 获取/设置颜色
	alpha = property( _getAlpha, _setAlpha )								# int: 获取/设置颜色的 alpha 值
	texture = property( _getTexture, _setTexture )							# str: 获取/设置贴图
	mapping = property( _getMapping, _setMapping )							# tuple: 获取/设置 mapping 值
	materialFX = property( _getMaterialFX, _setMaterialFX ) 				# str: 贴图渲染方式：
																			# ADD, BLEND（默认）, BLEND_COLOUR, BLEND_INVERSE_COLOUR, SOLID,
																			# MODULATE2X, ALPHA_TEST, BLEND_INVERSE_ALPHA, BLEND2X, or ADD_SIGNED
																			# COLOUR_EFF（灰度）
	acceptEvent = property( lambda self : False )							# 指出 python 是否接受系统消息

	# ---------------------------------------
	h_dockStyle = property( _getHorizontalDockStyle, _setHorizontalDockStyle )	# str: 获取/设置相对父 UI 的水平停靠方式："LEFT", "CENTER", "RIGHT", "HFILL"
	v_dockStyle = property( _getVerticalDockStyle, _setVerticalDockStyle )		# str: 获取/设置相对父 UI 的垂直停靠方式："TOP", "MIDDLE", "BOTTOM", "VFILL"

	h_anchor = property( _getHAnchor, _setHAnchor )							# MACRO: 获取/设置水平方向上自身的停靠方式：UIAnchor.LEFT/UIAnchor.CENTER/UIAnchor.RIGHT
	v_anchor = property( _getVAnchor, _setVAnchor )							# MACRO: 获取/设置垂直方向上自身的停靠方式：UIAnchor.TOP/UIAnchor.MIDDLE/UIAnchor.BOTTOM

	left = property( _getLeft, _setLeft )									# float: 获取/设置左距( 像素坐标 )
	top = property( _getTop, _setTop )										# float: 获取/设置顶距( 像素坐标 )
	center = property( _getCenter, _setCenter )								# float: 获取/设置水平中距( 像素坐标 )
	middle = property( _getMiddle, _setMiddle )								# float: 获取/设置垂直中距( 像素坐标 )
	right = property( _getRight, _setRight )								# float: 获取/设置右距( 像素坐标 )
	bottom = property( _getBottom, _setBottom )								# float: 获取/设置左距( 像素坐标 )
	pos = property( _getPos, _setPos )										# float: 获取/设置左距( 像素坐标 )

	r_left = property( _getRLeft, _setRLeft )								# float: 获取/设置左距( 相对坐标 )
	r_top = property( _getRTop, _setRTop )									# float: 获取/设置顶距( 相对坐标 )
	r_center = property( _getRCenter, _setRCenter )							# float: 获取/设置水平中距( 相对坐标 )
	r_middle = property( _getRMiddle, _setRMiddle )							# float: 获取/设置垂直中距( 相对坐标 )
	r_right = property( _getRRight, _setRRight )							# float: 获取/设置右距( 相对坐标 )
	r_bottom = property( _getRBottom, _setRBottom )							# float: 获取/设置左距( 相对坐标 )
	r_pos = property( _getRPos, _setRPos )									# float: 获取/设置左距( 相对坐标 )

	posZ = property( _getPosZ, _setPosZ )									# float: 获取/设置 Z 值( 表现为层叠关系 )

	# ---------------------------------------
	width = property( _getWidth, _setWidth )								# float: 获取/设置宽度度（像素坐标）
	height = property( _getHeight, _setHeight )								# float: 获取/设置高度（像素坐标）
	size = property( _getSize, _setSize )									# tuple: 获取/设置大小（像素坐标）

	r_width = property( _getRWidth, _setRWidth )							# float: 获取/设置宽度（相对坐标）
	r_height = property( _getRHeight, _setRHeight )							# float: 获取/设置高度（相对坐标）
	r_size = property( _getRSize, _setRSize )								# tuple: 获取/设置大小（相对坐标）

	tiled = property( _getTiled, _setTiled )								# bool: 获取/设置是否采用平铺排列（不拉伸贴图）
	tileWidth = property( _getTileWidth, _setTileWidth )					# float: 获取/设置平铺大小( tiled 为 True 才有效)，采用什么坐标根据 widthRelative 而定
	tileHeight = property( _getTileWidth, _setTileWidth )					# float: 获取/设置平铺大小( tiled 为 True 才有效)，采用什么坐标根据 heightRelative 而定


	# -------------------------------------------------
	# readonly properties
	# -------------------------------------------------
	pyParent = property( _getParent )										# python ui: 获取父 pyton ui（没有则返回 None）
	pyNearParent = property( _getNearParent )								# python ui: 获取最近的一个父 python UI
	pyTopParent = property( _getTopParent )									# python ui: 获取顶层 pytyon ui（没有则返回 None）
	textureFolder = property( _getTextureFolder )							# str: 获取贴图所在的路径（不包括文件名）

	# ---------------------------------------
	leftToScreen = property( _getLeftToScreen )								# flaot: 获取相对于屏幕的左距（像素坐标）
	topToScreen = property( _getTopToScreen )								# flaot: 获取相对于屏幕的顶距（像素坐标）
	centerToScreen = property( _getCenterToScreen )							# flaot: 获取相对于屏幕的水平中距（像素坐标）
	middleToScreen = property( _getMiddleToScreen )							# flaot: 获取相对于屏幕的垂直右距（像素坐标）
	rightToScreen = property( _getRightToScreen )							# flaot: 获取相对于屏幕的右距（像素坐标）
	bottomToScreen = property( _getBottomToScreen )							# flaot: 获取相对于屏幕的底距（像素坐标）
	posToScreen = property( _getPosToScreen )								# tuple: 获取相对于屏幕的位置（像素坐标）

	r_leftToScreen = property( _getRLeftToScreen )							# flaot: 获取相对于屏幕的左距（相对坐标）
	r_topToScreen = property( _getRTopToScreen )							# flaot: 获取相对于屏幕的顶距（相对坐标）
	r_centerToScreen = property( _getRCenterToScreen )						# flaot: 获取相对于屏幕的水平中距（相对坐标）
	r_middleToScreen = property( _getRMiddleToScreen )						# flaot: 获取相对于屏幕的垂直右距（相对坐标）
	r_rightToScreen = property( _getRRightToScreen )						# flaot: 获取相对于屏幕的右距（相对坐标）
	r_bottomToScreen = property( _getRBottomToScreen )						# flaot: 获取相对于屏幕的底距（相对坐标）
	r_posToScreen = property( _getRPosToScreen )							# tuple : 获取相对于屏幕的位置（相对坐标）

	# ---------------------------------------
	mousePos = property( _getMousePos )										# tupel: 获取鼠标在我身上的坐标（像素坐标）
	r_mousePos = property( _getRMousePos )									# tupel: 获取鼠标在我身上的坐标（相对坐标）

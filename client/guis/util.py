# -*- coding: gb18030 -*-
#
# $Id: util.py,v 1.17 2008-08-27 09:03:19 huangyongwei Exp $

"""
common global functions.

2007/4/17: writen by huangyongwei
"""

import math
import sys
import inspect
import Math
import GUI
import csol
import scale_util
import UIScriptWrapper
from bwdebug import *
from guis.uidefine import *
from keys import *
from cscollections import Stack
from cscollections import Queue



# --------------------------------------------------------------------
# mapping 计算
# --------------------------------------------------------------------
def getGuiMappingBound( textureSize, mapping ) :
	"""
	根据贴图的 mapping，获取 mapping 区域的矩形（与 getGuiMapping 相对）
	@type				textureSize	: tuple
	@param				textureSize	: 贴图大小: ( width, height )
	@type				mapping		: tuple of tuples
	@param				mapping		: mapping
	@rtype							: tuple
	@return							: 矩形区域：( 左边水平坐标，右边水平坐标，上边垂直坐标，下边垂直坐标 )
	"""
	width, height = textureSize
	left = width * mapping[0][0]
	right = width * mapping[2][0]
	top = height * mapping[0][1]
	bottom = height * mapping[2][1]
	return left, right, top, bottom

def getGuiMapping( textureSize, left, right, top, bottom ) :
	"""
	获取 gui 的 mapping 值（与 getGuiMappingBound 相对）
	@type				textureSize	: tuple
	@param				textureSize	: 贴图大小: ( width, height )
	@type				left		: float
	@param				left		: mapping 的左边水平坐标
	@type				right		: float
	@param				right		: mapping 的右边边水平坐标
	@type				top			: float
	@param				top			: mapping 的顶边水垂直坐标
	@type				bottom		: float
	@param				bottom		: mapping 的底边水垂直坐标
	@rtype							: tuple of tuples
	@return							: mapping 值
	"""
	u = float( left ) / textureSize[0]
	v = float( right ) / textureSize[0]
	u1 = float( top ) / textureSize[1]
	v1 = float( bottom ) / textureSize[1]
	return ( ( u, u1 ), ( u, v1 ), ( v, v1 ), ( v, u1 ) )

def getStateMapping( size, mode = UIState.MODE_R1C1, state = UIState.ST_R1C1 ) :
	"""
	获取 ui 某种状态下的 mapping
	注意：每种状态的大小都必须一致
	@type				size  : tuple：( width, height )
	@param				size  : ui 的大小
	@type				mode  : MACRO DEINATION（tuple）
	@param				mode  : 表示状体的排列方式，多少行多少列，在 uidefine.py 中定义
	@type				state : MACRO DEFINATION（tuple）
	@param				state : 表示要获取贴图中哪行哪列，在 uidefine.py 中定义
	@rtype					  : tuple of tuples
	@return					  : 要获取的状态的 mapping
	"""
	if isDebuged :
		assert mode[0] >= state[0] and mode[1] >= state[1], \
			"The state argument is out of mode range of mode"

	sw, sh = size									# 状态大小
	rows, cols = mode								# 状态的排列方式（多少行，多少列）
	stw, sth = sw * cols, sh * rows					# 除空白部分，贴图的大小
	hexp = math.ceil( math.log( stw, 2 ) )			# 水平方向上，2 的次方数
	vexp = math.ceil( math.log( sth, 2 ) )			# 垂直方向上，2 的次方数
	tsize = 2 ** hexp, 2 ** vexp					# 整个贴图的大小
	left = sw * ( state[1] - 1 )
	right = sw * state[1]
	top = sh * ( state[0] - 1 )
	bottom = sh * state[0]
	return getGuiMapping( tsize, left, right, top, bottom )

def setGuiState( gui, mode = UIState.MODE_R1C1, state = UIState.ST_R1C1 ) :
	"""
	设置 ui 为某种状态下的 mapping
	@type				gui	  : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	  : 要设置的引擎 ui
	@type				mode  : MACRO DEFINATION
	@param				mode  : 表示状态的排列方式，多少行多少列，在 uidefine.py 中定义
	@type				state : MACRO DEFINATION
	@param				state : 表示要设置贴图中哪行哪列，在 uidefine.py 中定义
	"""
	size = scale_util.getGuiSize( gui )
	gui.mapping = getStateMapping( size, mode, state )

# -----------------------------------------------------
def getIconMapping( iconSize, layoutMode = ( 1, 1 ), row = 1, col = 1 ) :
	"""
	获取图标大贴图中，指定某行某列的某个图标的 mapping
	@type				iconSize   : tuple：( width, height )
	@param				iconSize   : 图标大小
	@type				layoutMode : tuple
	@type				layoutMode : 图标的排列方式
	@type				row		   : int
	@param				row		   : 要获取的图标在第几行
	@type				col		   : int
	@param				col		   : 要获取的图标在第几列
	@rtype						   : tuple of tuples
	@return						   : 图标的 mapping
	"""
	iw, ih = iconSize								# 图标大小
	rows, cols = layoutMode							# 图标的行数和列数
	stw, sth = iw * cols, ih * rows					# 除空白部分贴图的大小
	hexp = math.ceil( math.log( stw, 2 ) )			# 水平方向上，2 的次方数
	vexp = math.ceil( math.log( sth, 2 ) )			# 垂直方向上，2 的次方数
	tsize = 2 ** hexp, 2 ** vexp					# 贴图的大小
	left = iw * ( col - 1 )
	right = iw * col
	top = ih * ( row - 1 )
	bottom = ih * row
	return getGuiMapping( tsize, left, right, top, bottom )

def setIconMapping( icon, layoutMode = ( 1, 1 ), row = 1, col = 1 ) :
	"""
	设置图标为大贴图中的映射的哪个 mapping（图标）
	@type				icon	   : GUI.Simple / GUI.Window / GUI.Circle
	@param				icon	   : 图标的引擎 ui
	@type				layoutMode : tuple
	@type				layoutMode : 图标的排列方式
	@type				row		   : int
	@param				row		   : 要设置图标的贴图在第几行
	@type				col		   : int
	@param				col		   : 要设置图标的贴图在第几列
	@return						   : None
	"""
	iconSize = scale_util.getGuiSize( icon )
	icon.mapping = getIconMapping( iconSize, layoutMode, row, col )

# -------------------------------------------
def hflipMapping( mapping ) :
	"""
	水平翻转 mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	return mapping[3], mapping[2], mapping[1], mapping[0]

def vflipMapping( mapping ) :
	"""
	垂直翻转 mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	return mapping[1], mapping[0], mapping[3], mapping[2]

def cwRotateMapping90( mapping ) :
	"""
	顺时针旋转 90°mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	lsmap = list( mapping )
	lsmap.append( lsmap.pop( 0 ) )
	return tuple( lsmap )

def cwRotateMapping180( mapping ) :
	"""
	顺时针旋转 180°mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	lsmap = list( mapping )
	lsmap = lsmap[2:] + lsmap[:2]
	return tuple( lsmap )

def ccwRotateMapping90( mapping ) :
	"""
	逆时针旋转 90°mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	lsmap = list( mapping )
	lsmap.insert( 0, lsmap.pop() )
	return tuple( lsmap )

def ccwRotateMapping180( mapping ) :
	"""
	逆时针旋转 180°mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	lsmap = list( mapping )
	lsmap = lsmap[:2] + lsmap[2:]
	return tuple( lsmap )

def rotateMapping( mapping, rad ) :
	"""
	旋转任意角度 mapping
	@type			mapping : tuple
	@param			mapping : ( ( 左上角 ), ( 左下角 ), ( 右下角 ), ( 右上角 ) )
	@type			rad		: float
	@param,			rad		: 要旋转的角度（弧度值）
	@rtype					: tuple
	@return					: 旋转后的 mapping
	"""
	cosv = math.cos( rad )
	sinv = -math.sin( rad )
	( x0, y0 ), ( x1, y1 ), ( x2, y2 ), ( x3, y3 ) = mapping
	x10 = ( x0 - 0.5 ) * cosv - ( y0 - 0.5 ) * sinv + 0.5
	y10 = ( x0 - 0.5 ) * sinv + ( y0 - 0.5 ) * cosv + 0.5
	x11 = ( x1 - 0.5 ) * cosv - ( y1 - 0.5 ) * sinv + 0.5
	y11 = ( x1 - 0.5 ) * sinv + ( y1 - 0.5 ) * cosv + 0.5
	x12 = ( x2 - 0.5 ) * cosv - ( y2 - 0.5 ) * sinv + 0.5
	y12 = ( x2 - 0.5 ) * sinv + ( y2 - 0.5 ) * cosv + 0.5
	x13 = ( x3 - 0.5 ) * cosv - ( y3 - 0.5 ) * sinv + 0.5
	y13 = ( x3 - 0.5 ) * sinv + ( y3 - 0.5 ) * cosv + 0.5
	return ( ( x10, y10 ), ( x11, y11 ), ( x12, y12 ), ( x13, y13 ) )

# -------------------------------------------
def rotateGui( gui, rad ) :
	"""
	根据 mapping 旋转任意角度 gui
	@type			gui : GUI.Simple/GUI.Window
	@param			gui : 要旋转的引擎 UI
	@type			rad : float
	@param			rad : 要旋转的角度（弧度值），rad 大于 0 时为顺时针旋转
	"""
	mapping = ( ( 0.0, 0.0 ), ( 0.0, 1.0 ), ( 1.0, 1.0 ), ( 1.0, 0.0 ) )
	gui.mapping = rotateMapping( mapping, rad )


# --------------------------------------------------------------------
# UI 遍历
# --------------------------------------------------------------------
def preFindGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	按前序遍历引擎 ui 树的方式，搜索根据 verifier 指定的 UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : 要遍历的引擎 ui
	@type				verifier : functor
	@param				verifier : 每遍历一个子 ui，该回调都会被调用一次
								   参数：
								   ch : gui 的所有子孙引擎 UI
								   返回值：
								   ① 是否装入该子 UI 到返回链表（默认为 True，表示装入每一个子 UI）
								   ② 对搜索是否继续的态度：
								 	  如果为 1，则继续查找该子 UI 在子 UI
								 	  如果为 0，则不再查找该子 UI 的子 UI
								 	  如果为 -1，则停止整个查找进程
	@type				zOrder   : bool
	@param				zOrder   : 指出遍历时，是否按 ui 的 z 顺序，即 Z 坐标小的会在返回链表的前面
								   如果没有必要按 Z 大小排序，则将 zOrder 设置为 False，这样速度可能会快一点
	@rtype					     : list
	@return					     : 找到的所有符合条件的子 UI，其顺序是：前序（如果指定 zOrder，则 Z 坐标小的在前面）
	"""
	children = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :
		g = stack.pop()										# 最前面一个 UI 离队
		res = verifier( g )									# 调用验证回调
		if res[0] : children.append( g )					# 如果返回值的第一个元素为 True，则将 g 添加到返回列表
		if res[1] < 0 : return children						# 如果返回值的第二个元素小于 0，则结束整个搜索进程
		elif res[1] == 0 : continue							# 不再搜索 g 的子 UI
		chs = [ch for n, ch in g.children]					# 如果返回值的第二个元素大于 0，则继续搜索 g 子 UI
		if zOrder : chs.sort( key = \
			lambda ch : ch.position.z, reverse = True ) 	# 使得返回的 UI 列表中的同层 UI按 Z 从小到大来排序
		stack.pushs( chs )
	return children

def postFindGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	按后序遍历引擎 ui 树的方式，搜索根据 verifier 指定的 UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : 要遍历的引擎 ui
	@type				verifier : functor
	@param				verifier : 每遍历一个子 ui，该回调都会被调用一次
								   参数：
								   ch : gui 的所有子孙引擎 UI
								   返回值：
								   ① 是否装入该子 UI 到返回链表（默认为 True，表示装入每一个子 UI）
								   ② 对搜索是否继续的态度：
								 	  如果为 1，则继续查找该子 UI 的子 UI
								 	  如果为 0，则不再查找该子 UI 的子 UI
								 	  如果为 -1，则停止整个查找进程
	@type				zOrder   : bool
	@param				zOrder   : 指出遍历时，是否按 ui 的 z 顺序，即 Z 坐标小的会在返回链表的前面
								   如果没有必要按 Z 大小排序，则将 zOrder 设置为 False，这样速度可能会快一点
	@rtype					     : list
	@return					     : 找到的所有符合条件的子 UI，其顺序是：后序（如果指定 zOrder，则 Z 坐标小的在前面）
	"""
	children = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :										# 用后序遍历，然后再将结果翻转（正好是前序）
		g = stack.pop()											# 最前面一个 UI 离队
		res = verifier( g )										# 调用验证回调
		if res[0] : children.append( g )						# 如果返回值的第一个元素为 True，则将 g 添加到返回列表
		if res[1] < 0 : return children							# 如果返回值的第二个元素小于 0，则结束整个搜索进程
		elif res[1] == 0 : continue								# 不再搜索 g 的子 UI
		chs = [ch for n, ch in g.children]						# 如果返回值的第二个元素大于 0，则继续搜索 g 子 UI
		if zOrder : chs.sort( key = lambda ch : ch.position.z )	# 使得返回的 UI 列表中的同层 UI按 Z 从小到大来排序
		stack.pushs( chs )
	children.reverse()
	return children

# -------------------------------------------
def preFindPyGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	按前序遍历引擎 ui 树的方式，搜索根据 verifier 指定的 python UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : 要遍历的引擎 ui
	@type				verifier : functor
	@param				verifier : 每遍历一个子 python ui，该回调都会被调用一次
								   参数：
								   pyCH：gui 的所有子孙 python UI
								   返回值：
								   ① 是否装入该子 UI 到返回链表（默认为 True，表示装入每一个子 pthon UI）
								   ② 对搜索是否继续的态度：
								 	  如果为 1，则继续查找该子 UI 的子 UI
								 	  如果为 0，则不再查找该子 UI 的子 UI
								 	  如果为 -1，则停止整个查找进程
	@type				zOrder   : bool
	@param				zOrder   : 指出遍历时，是否按 ui 的 z 顺序，即 Z 坐标小的会在返回链表的前面
								   如果没有必要按 Z 大小排序，则将 zOrder 设置为 False，这样速度可能会快一点
	@rtype					     : list
	@return					     : 找到的所有符合条件的子 python UI，其顺序是：前序（如果指定 zOrder，则 Z 坐标小的在前面）
	"""
	pyChildren = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :
		g = stack.pop()										# 最前面一个 UI 离队
		pyUI = UIScriptWrapper.unwrap( g )					# 通过接引用获得 python UI
		if pyUI :											# 如果 g 有 script
			res = verifier( pyUI )							# 调用验证回调
			if res[0] : pyChildren.append( pyUI )			# 如果返回值的第一个元素为 True，则将 g 添加到返回列表
			if res[1] < 0 : return pyChildren				# 如果返回值的第二个元素小于 0，则结束整个搜索进程
			elif res[1] == 0 : continue						# 不再搜索 g 的子 UI
		chs = [ch for n, ch in g.children]					# 如果返回值的第二个元素大于 0，则继续搜索 g 子 UI
		if zOrder : chs.sort( key = \
			lambda ch : ch.position.z, reverse = True ) 	# 使得返回的 UI 列表中的同层 UI按 Z 从小到大来排序
		stack.pushs( chs )
	return pyChildren

def postFindPyGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	按后序遍历引擎 ui 树的方式，搜索根据 verifier 指定的 python UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : 要遍历的引擎 ui
	@type				verifier : functor
	@param				verifier : 每遍历一个子 python ui，该回调都会被调用一次
								   参数：
								   pyCH：gui 的所有子孙 python UI
								   返回值：
								   ① 是否装入该子 UI 到返回链表（默认为 True，表示装入每一个子 pthon UI）
								   ② 对搜索是否继续的态度：
								 	  如果为 1，则继续查找该子 UI 的子 UI
								 	  如果为 0，则不再查找该子 UI 的子 UI
								 	  如果为 -1，则停止整个查找进程
	@type				zOrder   : bool
	@param				zOrder   : 指出遍历时，是否按 ui 的 z 顺序，即 Z 坐标小的会在返回链表的前面
								   如果没有必要按 Z 大小排序，则将 zOrder 设置为 False，这样速度可能会快一点
	@rtype					     : list
	@return					     : 找到的所有符合条件的子 python UI，其顺序是：后序（如果指定 zOrder，则 Z 坐标小的在前面）
	"""
	pyChildren = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :										# 用后序遍历，然后再将结果翻转（正好是前序）
		g = stack.pop()											# 最前面一个 UI 离队
		pyUI = UIScriptWrapper.unwrap( g )						# 通过接引用获得 python UI
		if pyUI :												# 如果 g 有 script
			res = verifier( pyUI )								# 调用验证回调
			if res[0] : pyChildren.append( pyUI )				# 如果返回值的第一个元素为 True，则将 g 添加到返回列表
			if res[1] < 0 : return pyChildren					# 如果返回值的第二个元素小于 0，则结束整个搜索进程
			elif res[1] == 0 : continue							# 不再搜索 g 的子 UI
		chs = [ch for n, ch in g.children]						# 如果返回值的第二个元素大于 0，则继续搜索 g 子 UI
		if zOrder : chs.sort( key = lambda ch : ch.position.z ) # 使得返回的 UI 列表中的同层 UI按 Z 从小到大来排序
		stack.pushs( chs )
	pyChildren.reverse()
	return pyChildren


# --------------------------------------------------------------------
# 复制 UI
# --------------------------------------------------------------------
def copyGui( srcGui, handler = None ) :
	"""
	复制单个 gui（不包括所有子 UI）
	"""
	GuiType = type( srcGui )
	dstGui = GuiType( srcGui.textureName )
	dstGui.name = srcGui.name
	dstGui.visible = srcGui.visible
	dstGui.materialFX = srcGui.materialFX
	dstGui.mapping = srcGui.mapping
	dstGui.colour = srcGui.colour

	dstGui.focus = srcGui.focus
	dstGui.crossFocus = srcGui.crossFocus
	dstGui.moveFocus = srcGui.moveFocus
	dstGui.dragFocus = srcGui.dragFocus
	dstGui.dropFocus = srcGui.dropFocus

	dstGui.widthRelative = srcGui.widthRelative
	dstGui.heightRelative = srcGui.heightRelative
	dstGui.horizontalAnchor = srcGui.horizontalAnchor
	dstGui.verticalAnchor = srcGui.verticalAnchor
	dstGui.tiled = srcGui.tiled
	dstGui.tileWidth = srcGui.tileWidth
	dstGui.tileHeight = srcGui.tileHeight
	dstGui.size = srcGui.size
	dstGui.position = srcGui.position

	if GuiType is GUI.Text :								# 如果是文本 GUI
		dstGui.font = srcGui.font
		dstGui.text = srcGui.text
		if hasattr( dstGui, "fontDescription" ) :
			dstGui.fontDescription( srcGui.fontDescription() )
		if hasattr( srcGui, "stroker" ) :
			dstGui.addShader( srcGui.stroker, "stroker" )
	elif GuiType is GUI.Window :							# 如果是窗口 GUI
		dstGui.maxScroll = srcGui.maxScroll
		dstGui.scroll = srcGui.scroll
	elif GuiType is GUI.TextureFrame :						# 如果是纹理框架
		for name, elem in srcGui.elements.items() :
			newElem = GUI.Texture( elem.texture )
			dstGui.addElement( newElem, name )
			newElem.position = elem.position
			newElem.size = elem.size
			newElem.tileSize = elem.tileSize
			newElem.tiled = elem.tiled
			newElem.mapping = elem.mapping
			newElem.colour = elem.colour
		dstGui.resortElements()

	for ( name, shader ) in srcGui.shaders :				# 复制 shader
		ShaderClass = shader.__class__
		if ShaderClass == GUI.AlphaShader or \
			ShaderClass == GUI.ClipShader or \
			ShaderClass == GUI.ColourShader :
				newShader = ShaderClass()
				newShader.speed = shader.speed
				newShader.value = shader.value
		elif ShaderClass == GUI.FringeShader :
			newShader = shader
		dstGui.addShader( newShader, name )
	if handler : handler( dstGui )
	return dstGui

def copyGuiTree( gui, handler = None ) :
	"""
	复制一个与给出的引擎 ui 一致的 ui （包括所有子 UI 和 Shader）
	@type				gui		: GUI.Simple / GUI.Window / GUI.Circle
	@param				gui		: 复制的源引擎 ui
	@type				handler	: functor
	@param				handler : 创建每个 ui 的子 ui 时，该回调都会被调用一次，可以在该函数里单独重新设置某个子 ui 的部分属性
	@rtype						: GUI.Simple / GUI.Window / GUI.Circle
	@param						: 新的引擎 ui
	"""
	newGui = copyGui( gui, handler )
	queue = Queue()
	queue.enter( ( newGui, gui ) )
	while( queue.length() ) :
		g = queue.leave()
		for name, child, in g[1].children :
			new_g = copyGui( child, handler )
			g[0].addChild( new_g, name )
			queue.enter( ( new_g, child ) )
	return newGui


# --------------------------------------------------------------------
# 工具
# --------------------------------------------------------------------
def getHitUIs( className = None ) :
	"""
	获取鼠标指针处的 UI 实例
	@type			className : str
	@param			className : 要获取 UI 实例所属的类名，为 None 则获取所有实例
	@rtype					  : dict 或引擎 UI 实例，或 python UI 实例
	@return					  : 如果只有一个 UI，则返回该 UI 的实例，否则返回一系列 UI
	"""
	def isInst( pyUI ) :
		if className is None : return True
		if pyUI is None : return False
		for cls in inspect.getmro( pyUI.__class__ ) :
			if cls.__name__ == className :
				return True
		return False

	def verifier( ch ) :
		if not ch.rvisible : return False, 0
		if not scale_util.isMouseHit( ch ) : return False, 0
		pyUI = UIScriptWrapper.unwrap( ch )
		if isInst( pyUI ) :
			return True, 1
		return False, 1

	def getUIName( ui ) :
		parent = ui.parent
		if parent is None :
			return ""
		for n, ch in parent.children :
			if ch == ui :
				return n
		raise "unknow ui"

	guis = []
	roots = GUI.roots()
	roots.sort( key = lambda root : root.position.z )
	for root in roots :
		if not root.rvisible : continue
		guis += postFindGui( root, verifier )
	if len( guis ) == 1 :
		pyUI = UIScriptWrapper.unwrap( guis[0] )
		if pyUI : return pyUI
		return guis[0]
	d_guis = {}
	for idx, g in enumerate( guis ) :
		pyUI = UIScriptWrapper.unwrap( g )
		if pyUI :
			d_guis[idx] = pyUI
		else :
			name = getUIName( g )
			d_guis[idx] = ( name, g )
	return d_guis

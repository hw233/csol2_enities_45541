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
# mapping ����
# --------------------------------------------------------------------
def getGuiMappingBound( textureSize, mapping ) :
	"""
	������ͼ�� mapping����ȡ mapping ����ľ��Σ��� getGuiMapping ��ԣ�
	@type				textureSize	: tuple
	@param				textureSize	: ��ͼ��С: ( width, height )
	@type				mapping		: tuple of tuples
	@param				mapping		: mapping
	@rtype							: tuple
	@return							: ��������( ���ˮƽ���꣬�ұ�ˮƽ���꣬�ϱߴ�ֱ���꣬�±ߴ�ֱ���� )
	"""
	width, height = textureSize
	left = width * mapping[0][0]
	right = width * mapping[2][0]
	top = height * mapping[0][1]
	bottom = height * mapping[2][1]
	return left, right, top, bottom

def getGuiMapping( textureSize, left, right, top, bottom ) :
	"""
	��ȡ gui �� mapping ֵ���� getGuiMappingBound ��ԣ�
	@type				textureSize	: tuple
	@param				textureSize	: ��ͼ��С: ( width, height )
	@type				left		: float
	@param				left		: mapping �����ˮƽ����
	@type				right		: float
	@param				right		: mapping ���ұ߱�ˮƽ����
	@type				top			: float
	@param				top			: mapping �Ķ���ˮ��ֱ����
	@type				bottom		: float
	@param				bottom		: mapping �ĵױ�ˮ��ֱ����
	@rtype							: tuple of tuples
	@return							: mapping ֵ
	"""
	u = float( left ) / textureSize[0]
	v = float( right ) / textureSize[0]
	u1 = float( top ) / textureSize[1]
	v1 = float( bottom ) / textureSize[1]
	return ( ( u, u1 ), ( u, v1 ), ( v, v1 ), ( v, u1 ) )

def getStateMapping( size, mode = UIState.MODE_R1C1, state = UIState.ST_R1C1 ) :
	"""
	��ȡ ui ĳ��״̬�µ� mapping
	ע�⣺ÿ��״̬�Ĵ�С������һ��
	@type				size  : tuple��( width, height )
	@param				size  : ui �Ĵ�С
	@type				mode  : MACRO DEINATION��tuple��
	@param				mode  : ��ʾ״������з�ʽ�������ж����У��� uidefine.py �ж���
	@type				state : MACRO DEFINATION��tuple��
	@param				state : ��ʾҪ��ȡ��ͼ���������У��� uidefine.py �ж���
	@rtype					  : tuple of tuples
	@return					  : Ҫ��ȡ��״̬�� mapping
	"""
	if isDebuged :
		assert mode[0] >= state[0] and mode[1] >= state[1], \
			"The state argument is out of mode range of mode"

	sw, sh = size									# ״̬��С
	rows, cols = mode								# ״̬�����з�ʽ�������У������У�
	stw, sth = sw * cols, sh * rows					# ���հײ��֣���ͼ�Ĵ�С
	hexp = math.ceil( math.log( stw, 2 ) )			# ˮƽ�����ϣ�2 �Ĵη���
	vexp = math.ceil( math.log( sth, 2 ) )			# ��ֱ�����ϣ�2 �Ĵη���
	tsize = 2 ** hexp, 2 ** vexp					# ������ͼ�Ĵ�С
	left = sw * ( state[1] - 1 )
	right = sw * state[1]
	top = sh * ( state[0] - 1 )
	bottom = sh * state[0]
	return getGuiMapping( tsize, left, right, top, bottom )

def setGuiState( gui, mode = UIState.MODE_R1C1, state = UIState.ST_R1C1 ) :
	"""
	���� ui Ϊĳ��״̬�µ� mapping
	@type				gui	  : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	  : Ҫ���õ����� ui
	@type				mode  : MACRO DEFINATION
	@param				mode  : ��ʾ״̬�����з�ʽ�������ж����У��� uidefine.py �ж���
	@type				state : MACRO DEFINATION
	@param				state : ��ʾҪ������ͼ���������У��� uidefine.py �ж���
	"""
	size = scale_util.getGuiSize( gui )
	gui.mapping = getStateMapping( size, mode, state )

# -----------------------------------------------------
def getIconMapping( iconSize, layoutMode = ( 1, 1 ), row = 1, col = 1 ) :
	"""
	��ȡͼ�����ͼ�У�ָ��ĳ��ĳ�е�ĳ��ͼ��� mapping
	@type				iconSize   : tuple��( width, height )
	@param				iconSize   : ͼ���С
	@type				layoutMode : tuple
	@type				layoutMode : ͼ������з�ʽ
	@type				row		   : int
	@param				row		   : Ҫ��ȡ��ͼ���ڵڼ���
	@type				col		   : int
	@param				col		   : Ҫ��ȡ��ͼ���ڵڼ���
	@rtype						   : tuple of tuples
	@return						   : ͼ��� mapping
	"""
	iw, ih = iconSize								# ͼ���С
	rows, cols = layoutMode							# ͼ�������������
	stw, sth = iw * cols, ih * rows					# ���հײ�����ͼ�Ĵ�С
	hexp = math.ceil( math.log( stw, 2 ) )			# ˮƽ�����ϣ�2 �Ĵη���
	vexp = math.ceil( math.log( sth, 2 ) )			# ��ֱ�����ϣ�2 �Ĵη���
	tsize = 2 ** hexp, 2 ** vexp					# ��ͼ�Ĵ�С
	left = iw * ( col - 1 )
	right = iw * col
	top = ih * ( row - 1 )
	bottom = ih * row
	return getGuiMapping( tsize, left, right, top, bottom )

def setIconMapping( icon, layoutMode = ( 1, 1 ), row = 1, col = 1 ) :
	"""
	����ͼ��Ϊ����ͼ�е�ӳ����ĸ� mapping��ͼ�꣩
	@type				icon	   : GUI.Simple / GUI.Window / GUI.Circle
	@param				icon	   : ͼ������� ui
	@type				layoutMode : tuple
	@type				layoutMode : ͼ������з�ʽ
	@type				row		   : int
	@param				row		   : Ҫ����ͼ�����ͼ�ڵڼ���
	@type				col		   : int
	@param				col		   : Ҫ����ͼ�����ͼ�ڵڼ���
	@return						   : None
	"""
	iconSize = scale_util.getGuiSize( icon )
	icon.mapping = getIconMapping( iconSize, layoutMode, row, col )

# -------------------------------------------
def hflipMapping( mapping ) :
	"""
	ˮƽ��ת mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@rtype					: tuple
	@return					: ��ת��� mapping
	"""
	return mapping[3], mapping[2], mapping[1], mapping[0]

def vflipMapping( mapping ) :
	"""
	��ֱ��ת mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@rtype					: tuple
	@return					: ��ת��� mapping
	"""
	return mapping[1], mapping[0], mapping[3], mapping[2]

def cwRotateMapping90( mapping ) :
	"""
	˳ʱ����ת 90��mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@rtype					: tuple
	@return					: ��ת��� mapping
	"""
	lsmap = list( mapping )
	lsmap.append( lsmap.pop( 0 ) )
	return tuple( lsmap )

def cwRotateMapping180( mapping ) :
	"""
	˳ʱ����ת 180��mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@rtype					: tuple
	@return					: ��ת��� mapping
	"""
	lsmap = list( mapping )
	lsmap = lsmap[2:] + lsmap[:2]
	return tuple( lsmap )

def ccwRotateMapping90( mapping ) :
	"""
	��ʱ����ת 90��mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@rtype					: tuple
	@return					: ��ת��� mapping
	"""
	lsmap = list( mapping )
	lsmap.insert( 0, lsmap.pop() )
	return tuple( lsmap )

def ccwRotateMapping180( mapping ) :
	"""
	��ʱ����ת 180��mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@rtype					: tuple
	@return					: ��ת��� mapping
	"""
	lsmap = list( mapping )
	lsmap = lsmap[:2] + lsmap[2:]
	return tuple( lsmap )

def rotateMapping( mapping, rad ) :
	"""
	��ת����Ƕ� mapping
	@type			mapping : tuple
	@param			mapping : ( ( ���Ͻ� ), ( ���½� ), ( ���½� ), ( ���Ͻ� ) )
	@type			rad		: float
	@param,			rad		: Ҫ��ת�ĽǶȣ�����ֵ��
	@rtype					: tuple
	@return					: ��ת��� mapping
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
	���� mapping ��ת����Ƕ� gui
	@type			gui : GUI.Simple/GUI.Window
	@param			gui : Ҫ��ת������ UI
	@type			rad : float
	@param			rad : Ҫ��ת�ĽǶȣ�����ֵ����rad ���� 0 ʱΪ˳ʱ����ת
	"""
	mapping = ( ( 0.0, 0.0 ), ( 0.0, 1.0 ), ( 1.0, 1.0 ), ( 1.0, 0.0 ) )
	gui.mapping = rotateMapping( mapping, rad )


# --------------------------------------------------------------------
# UI ����
# --------------------------------------------------------------------
def preFindGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	��ǰ��������� ui ���ķ�ʽ���������� verifier ָ���� UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : Ҫ���������� ui
	@type				verifier : functor
	@param				verifier : ÿ����һ���� ui���ûص����ᱻ����һ��
								   ������
								   ch : gui �������������� UI
								   ����ֵ��
								   �� �Ƿ�װ����� UI ����������Ĭ��Ϊ True����ʾװ��ÿһ���� UI��
								   �� �������Ƿ������̬�ȣ�
								 	  ���Ϊ 1����������Ҹ��� UI ���� UI
								 	  ���Ϊ 0�����ٲ��Ҹ��� UI ���� UI
								 	  ���Ϊ -1����ֹͣ�������ҽ���
	@type				zOrder   : bool
	@param				zOrder   : ָ������ʱ���Ƿ� ui �� z ˳�򣬼� Z ����С�Ļ��ڷ��������ǰ��
								   ���û�б�Ҫ�� Z ��С������ zOrder ����Ϊ False�������ٶȿ��ܻ��һ��
	@rtype					     : list
	@return					     : �ҵ������з����������� UI����˳���ǣ�ǰ�����ָ�� zOrder���� Z ����С����ǰ�棩
	"""
	children = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :
		g = stack.pop()										# ��ǰ��һ�� UI ���
		res = verifier( g )									# ������֤�ص�
		if res[0] : children.append( g )					# �������ֵ�ĵ�һ��Ԫ��Ϊ True���� g ��ӵ������б�
		if res[1] < 0 : return children						# �������ֵ�ĵڶ���Ԫ��С�� 0�������������������
		elif res[1] == 0 : continue							# �������� g ���� UI
		chs = [ch for n, ch in g.children]					# �������ֵ�ĵڶ���Ԫ�ش��� 0����������� g �� UI
		if zOrder : chs.sort( key = \
			lambda ch : ch.position.z, reverse = True ) 	# ʹ�÷��ص� UI �б��е�ͬ�� UI�� Z ��С����������
		stack.pushs( chs )
	return children

def postFindGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	������������� ui ���ķ�ʽ���������� verifier ָ���� UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : Ҫ���������� ui
	@type				verifier : functor
	@param				verifier : ÿ����һ���� ui���ûص����ᱻ����һ��
								   ������
								   ch : gui �������������� UI
								   ����ֵ��
								   �� �Ƿ�װ����� UI ����������Ĭ��Ϊ True����ʾװ��ÿһ���� UI��
								   �� �������Ƿ������̬�ȣ�
								 	  ���Ϊ 1����������Ҹ��� UI ���� UI
								 	  ���Ϊ 0�����ٲ��Ҹ��� UI ���� UI
								 	  ���Ϊ -1����ֹͣ�������ҽ���
	@type				zOrder   : bool
	@param				zOrder   : ָ������ʱ���Ƿ� ui �� z ˳�򣬼� Z ����С�Ļ��ڷ��������ǰ��
								   ���û�б�Ҫ�� Z ��С������ zOrder ����Ϊ False�������ٶȿ��ܻ��һ��
	@rtype					     : list
	@return					     : �ҵ������з����������� UI����˳���ǣ��������ָ�� zOrder���� Z ����С����ǰ�棩
	"""
	children = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :										# �ú��������Ȼ���ٽ������ת��������ǰ��
		g = stack.pop()											# ��ǰ��һ�� UI ���
		res = verifier( g )										# ������֤�ص�
		if res[0] : children.append( g )						# �������ֵ�ĵ�һ��Ԫ��Ϊ True���� g ��ӵ������б�
		if res[1] < 0 : return children							# �������ֵ�ĵڶ���Ԫ��С�� 0�������������������
		elif res[1] == 0 : continue								# �������� g ���� UI
		chs = [ch for n, ch in g.children]						# �������ֵ�ĵڶ���Ԫ�ش��� 0����������� g �� UI
		if zOrder : chs.sort( key = lambda ch : ch.position.z )	# ʹ�÷��ص� UI �б��е�ͬ�� UI�� Z ��С����������
		stack.pushs( chs )
	children.reverse()
	return children

# -------------------------------------------
def preFindPyGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	��ǰ��������� ui ���ķ�ʽ���������� verifier ָ���� python UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : Ҫ���������� ui
	@type				verifier : functor
	@param				verifier : ÿ����һ���� python ui���ûص����ᱻ����һ��
								   ������
								   pyCH��gui ���������� python UI
								   ����ֵ��
								   �� �Ƿ�װ����� UI ����������Ĭ��Ϊ True����ʾװ��ÿһ���� pthon UI��
								   �� �������Ƿ������̬�ȣ�
								 	  ���Ϊ 1����������Ҹ��� UI ���� UI
								 	  ���Ϊ 0�����ٲ��Ҹ��� UI ���� UI
								 	  ���Ϊ -1����ֹͣ�������ҽ���
	@type				zOrder   : bool
	@param				zOrder   : ָ������ʱ���Ƿ� ui �� z ˳�򣬼� Z ����С�Ļ��ڷ��������ǰ��
								   ���û�б�Ҫ�� Z ��С������ zOrder ����Ϊ False�������ٶȿ��ܻ��һ��
	@rtype					     : list
	@return					     : �ҵ������з����������� python UI����˳���ǣ�ǰ�����ָ�� zOrder���� Z ����С����ǰ�棩
	"""
	pyChildren = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :
		g = stack.pop()										# ��ǰ��һ�� UI ���
		pyUI = UIScriptWrapper.unwrap( g )					# ͨ�������û�� python UI
		if pyUI :											# ��� g �� script
			res = verifier( pyUI )							# ������֤�ص�
			if res[0] : pyChildren.append( pyUI )			# �������ֵ�ĵ�һ��Ԫ��Ϊ True���� g ��ӵ������б�
			if res[1] < 0 : return pyChildren				# �������ֵ�ĵڶ���Ԫ��С�� 0�������������������
			elif res[1] == 0 : continue						# �������� g ���� UI
		chs = [ch for n, ch in g.children]					# �������ֵ�ĵڶ���Ԫ�ش��� 0����������� g �� UI
		if zOrder : chs.sort( key = \
			lambda ch : ch.position.z, reverse = True ) 	# ʹ�÷��ص� UI �б��е�ͬ�� UI�� Z ��С����������
		stack.pushs( chs )
	return pyChildren

def postFindPyGui( gui, verifier = lambda ui : ( True, 1 ), zOrder = False ) :
	"""
	������������� ui ���ķ�ʽ���������� verifier ָ���� python UI
	@type				gui	     : GUI.Simple / GUI.Window / GUI.Circle
	@param				gui	     : Ҫ���������� ui
	@type				verifier : functor
	@param				verifier : ÿ����һ���� python ui���ûص����ᱻ����һ��
								   ������
								   pyCH��gui ���������� python UI
								   ����ֵ��
								   �� �Ƿ�װ����� UI ����������Ĭ��Ϊ True����ʾװ��ÿһ���� pthon UI��
								   �� �������Ƿ������̬�ȣ�
								 	  ���Ϊ 1����������Ҹ��� UI ���� UI
								 	  ���Ϊ 0�����ٲ��Ҹ��� UI ���� UI
								 	  ���Ϊ -1����ֹͣ�������ҽ���
	@type				zOrder   : bool
	@param				zOrder   : ָ������ʱ���Ƿ� ui �� z ˳�򣬼� Z ����С�Ļ��ڷ��������ǰ��
								   ���û�б�Ҫ�� Z ��С������ zOrder ����Ϊ False�������ٶȿ��ܻ��һ��
	@rtype					     : list
	@return					     : �ҵ������з����������� python UI����˳���ǣ��������ָ�� zOrder���� Z ����С����ǰ�棩
	"""
	pyChildren = []
	stack = Stack()
	stack.push( gui )
	while( stack.size() ) :										# �ú��������Ȼ���ٽ������ת��������ǰ��
		g = stack.pop()											# ��ǰ��һ�� UI ���
		pyUI = UIScriptWrapper.unwrap( g )						# ͨ�������û�� python UI
		if pyUI :												# ��� g �� script
			res = verifier( pyUI )								# ������֤�ص�
			if res[0] : pyChildren.append( pyUI )				# �������ֵ�ĵ�һ��Ԫ��Ϊ True���� g ��ӵ������б�
			if res[1] < 0 : return pyChildren					# �������ֵ�ĵڶ���Ԫ��С�� 0�������������������
			elif res[1] == 0 : continue							# �������� g ���� UI
		chs = [ch for n, ch in g.children]						# �������ֵ�ĵڶ���Ԫ�ش��� 0����������� g �� UI
		if zOrder : chs.sort( key = lambda ch : ch.position.z ) # ʹ�÷��ص� UI �б��е�ͬ�� UI�� Z ��С����������
		stack.pushs( chs )
	pyChildren.reverse()
	return pyChildren


# --------------------------------------------------------------------
# ���� UI
# --------------------------------------------------------------------
def copyGui( srcGui, handler = None ) :
	"""
	���Ƶ��� gui�������������� UI��
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

	if GuiType is GUI.Text :								# ������ı� GUI
		dstGui.font = srcGui.font
		dstGui.text = srcGui.text
		if hasattr( dstGui, "fontDescription" ) :
			dstGui.fontDescription( srcGui.fontDescription() )
		if hasattr( srcGui, "stroker" ) :
			dstGui.addShader( srcGui.stroker, "stroker" )
	elif GuiType is GUI.Window :							# ����Ǵ��� GUI
		dstGui.maxScroll = srcGui.maxScroll
		dstGui.scroll = srcGui.scroll
	elif GuiType is GUI.TextureFrame :						# �����������
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

	for ( name, shader ) in srcGui.shaders :				# ���� shader
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
	����һ������������� ui һ�µ� ui ������������ UI �� Shader��
	@type				gui		: GUI.Simple / GUI.Window / GUI.Circle
	@param				gui		: ���Ƶ�Դ���� ui
	@type				handler	: functor
	@param				handler : ����ÿ�� ui ���� ui ʱ���ûص����ᱻ����һ�Σ������ڸú����ﵥ����������ĳ���� ui �Ĳ�������
	@rtype						: GUI.Simple / GUI.Window / GUI.Circle
	@param						: �µ����� ui
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
# ����
# --------------------------------------------------------------------
def getHitUIs( className = None ) :
	"""
	��ȡ���ָ�봦�� UI ʵ��
	@type			className : str
	@param			className : Ҫ��ȡ UI ʵ��������������Ϊ None ���ȡ����ʵ��
	@rtype					  : dict ������ UI ʵ������ python UI ʵ��
	@return					  : ���ֻ��һ�� UI���򷵻ظ� UI ��ʵ�������򷵻�һϵ�� UI
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

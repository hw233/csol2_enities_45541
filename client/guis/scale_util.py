# -*- coding: gb18030 -*-
#
# $Id: scale_util.py,v 1.5 2008-08-27 09:03:10 huangyongwei Exp $

"""
global methods about gui scale
"""
import math
import BigWorld
import GUI
import Language
import Math
import csol
import Font
from bwdebug import *
from cscollections import Queue

# --------------------------------------------------------------------
# methods be used in this model-self
# --------------------------------------------------------------------
def __isWindow( gui ) :
	"""
	if the gui's type is WindowGUIComponent return True
	"""
	cls = type( gui )
	return cls is GUI.Window or cls is GUI.TextureFrame

def __isText( gui ) :
	"""
	if the gui's type is TextGUIComponent return True
	"""
	return type( gui ) is GUI.Text

def __isTopGui( gui ) :
	"""
	find out if a gui is top gui
	"""
  	return gui.parent is None

def __isInWindow( gui ) :
	"""
	find out if a gui's forefather is WindowGUIComponent
	"""
	parent = gui.parent
	while( parent is not None ) :
		if __isWindow( parent ) : return True
		parent = parent.parent
	return False



# --------------------------------------------------------------------
# about gui race
# --------------------------------------------------------------------
def getWindowParent( gui ) :
	"""
	get the inner window parent
	"""
	parent = gui.parent
	while parent is not None :
		if type( parent ) is GUI.Window :
			break
		parent = parent.parent
	return parent

def getWindowParentSize( gui ) :
	wndParent = getWindowParent( gui )
	if wndParent is None :
		return BigWorld.screenSize()
	return getGuiSize( wndParent )

def getWindowParentRSize( gui ) :
	wndParent = getWindowParent( gui )
	if wndParent is None :
		return ( 2, 2 )
	return getGuiRSize( wndParent )

# --------------------------------------------------------------------
# change scale measure
# --------------------------------------------------------------------
def toRXMeasure( measure ) :
	"""
	absolute coordinate to relative coordinate on horizon
	"""
	return measure * 2 / BigWorld.screenWidth()

def toRYMeasure( measure ) :
	"""
	relative coordinate to absolute coordinate on horizon
	"""
	return measure * 2 / BigWorld.screenHeight()

def toPXMeasure( measure ) :
	"""
	absolute coordinate to relative coordinate on vertical
	"""
	return measure * BigWorld.screenWidth() * 0.5

def toPYMeasure( measure ) :
	"""
	relative coordinate to absolute coordinate on vertical
	"""
	return measure * BigWorld.screenHeight() * 0.5

# -----------------------------------------------------
def toRX( px, isScaleToWindow ) :
	"""
	absolute x-coordinate to relative x-coordinate
	"""
	rx = toRXMeasure( px )
	if isScaleToWindow : return rx			# relative to window
	return rx - 1							# relative to screen

def toRY( py, isScaleToWindow ) :
	"""
	absolute y-coordinate to relative y-coordinate
	"""
	ry = toRYMeasure( py )
	if isScaleToWindow : return -ry			# relative to window
	return 1 - ry							# relative to screen

def toPX( rx, isScaleToWindow ) :
	"""
	relative x-coordinate to absolute x-coordinate
	"""
	if isScaleToWindow :					# relative to window
		return toPXMeasure( rx )
	return toPXMeasure( rx + 1 )			# relative to screen

def toPY( ry, isScaleToWindow ) :
	"""
	relative y-coordinate to absolute y-coordinate
	"""
	if isScaleToWindow :
		return toPYMeasure( -ry )			# relative to window
	return toPYMeasure( 1 - ry )			# relative to screen

# --------------------------------------------------------------------
# get or set gui position or size
# --------------------------------------------------------------------
def getGuiLeft( gui ) :
	isScaleToWindow = __isInWindow( gui )
	left = toPX( gui.position.x, isScaleToWindow )
	if gui.horizontalAnchor == "CENTER" :
		left -= getGuiWidth( gui ) * 0.5
	elif gui.horizontalAnchor == "RIGHT" :
		left -= getGuiWidth( gui )
	return left

def setGuiLeft( gui, left ) :
	isScaleToWindow = __isInWindow( gui )
	rLeft = toRX( left, isScaleToWindow )
	if gui.horizontalAnchor == "CENTER" :
		rLeft += getGuiRWidth( gui ) * 0.5
	elif gui.horizontalAnchor == "RIGHT" :
		rLeft += getGuiRWidth( gui )
	gui.position.x = rLeft

# -------------------------------------------
def getGuiCenter( gui ) :
	width = getGuiWidth( gui )
	return getGuiLeft( gui ) + width * 0.5

def setGuiCenter( gui, center ) :
	left = center - getGuiWidth( gui ) * 0.5
	setGuiLeft( gui, left )

# -------------------------------------------
def getGuiRight( gui ) :
	width = getGuiWidth( gui )
	return getGuiLeft( gui ) + width

def setGuiRight( gui, right ) :
	left = right - getGuiWidth( gui )
	setGuiLeft( gui, left )

# -----------------------------------------------------
def getGuiTop( gui ) :
	isScaleToWindow = __isInWindow( gui )
	top = toPY( gui.position.y, isScaleToWindow )
	if gui.verticalAnchor == "CENTER" :
		top -= getGuiHeight( gui ) * 0.5
	elif gui.verticalAnchor == "BOTTOM" :
		top -= getGuiHeight( gui )
	return top

def setGuiTop( gui, top ) :
	isScaleToWindow = __isInWindow( gui )
	rTop = toRY( top, isScaleToWindow )
	if gui.verticalAnchor == "CENTER" :
		rTop -= getGuiRHeight( gui ) * 0.5
	elif gui.verticalAnchor == "BOTTOM" :
		rTop -= getGuiRHeight( gui )
	gui.position.y = rTop

# -------------------------------------------
def getGuiMiddle( gui ) :
	height = getGuiHeight( gui )
	return getGuiTop( gui ) + height * 0.5

def setGuiMiddle( gui, middle ) :
	top = middle - getGuiHeight( gui ) * 0.5
	setGuiTop( gui, top )

# -------------------------------------------
def getGuiBottom( gui ) :
	height = getGuiHeight( gui )
	return getGuiTop( gui ) + height

def setGuiBottom( gui, bottom ) :
	top = bottom - getGuiHeight( gui )
	setGuiTop( gui, top )

# -------------------------------------------
def getGuiPos( gui ) :
	left = getGuiLeft( gui )
	top = getGuiTop( gui )
	return Math.Vector2( left, top )

def setGuiPos( gui, ( left, top ) ) :
	setGuiLeft( gui, left )
	setGuiTop( gui, top )

# --------------------------------------------------------------------
def getGuiRLeft( gui ) :
	rLeft = gui.position.x
	if gui.horizontalAnchor == "CENTER" :
		rLeft -= getGuiRWidth( gui ) * 0.5
	elif gui.horizontalAnchor == "RIGHT" :
		rLeft -= getGuiRWidth( gui )
	return rLeft

def setGuiRLeft( gui, left ) :
	if gui.horizontalAnchor == "CENTER" :
		left += getGuiRWidth( gui ) * 0.5
	elif gui.horizontalAnchor == "RIGHT" :
		left += getGuiRWidth( gui )
	gui.position.x = left

# -------------------------------------------
def getGuiRCenter( gui ) :
	width = getGuiRWidth( gui )
	return getGuiRLeft( gui ) + width * 0.5

def setGuiRCenter( gui, center ) :
	left = center - getGuiRWidth( gui ) * 0.5
	setGuiRLeft( gui, left )

# -------------------------------------------
def getGuiRRight( gui ) :
	width = getGuiRWidth( gui )
	return getGuiLeft( gui ) + width

def setGuiRRight( gui, right ) :
	left = right - getGuiRWidth( gui )
	setGuiRLeft( gui, left )

# -----------------------------------------------------
def getGuiRTop( gui ) :
	rTop = gui.position.y
	if gui.verticalAnchor == "CENTER" :
		rTop += getGuiRHeight( gui ) * 0.5
	if gui.verticalAnchor == "BOTTOM" :
		rTop += getGuiRHeight( gui )
	return rTop

def setGuiRTop( gui, top ) :
	if gui.verticalAnchor == "CENTER" :
		top -= getGuiRHeight( gui ) * 0.5
	elif gui.verticalAnchor == "BOTTOM" :
		top -= getGuiRHeight( gui )
	gui.position.y = top

# -------------------------------------------
def getGuiRMiddle( gui ) :
	height = getGuiRHeight( gui )
	return getGuiRTop( gui ) - height * 0.5

def setGuiRMiddle( gui, middle ) :
	top = middle + getGuiRHeight( gui ) * 0.5
	setGuiRTop( gui, top )

# -------------------------------------------
def getGuiRBottom( gui ) :
	height = getGuiRHeight( gui )
	return getGuiRTop( gui ) - height

def setGuiRBottom( gui, bottom ) :
	top = bottom + getGuiRHeight( gui )
	setGuiRTop( gui, top )

# -------------------------------------------
def getGuiRPos( gui ) :
	left = getGuiRLeft( gui )
	top = getGuiRTop( gui )
	return Math.Vector2( left, top )

def setGuiRPos( gui, ( left, top ) ) :
	setGuiRLeft( gui, left )
	setGuiRTop( gui, top )

# --------------------------------------------------------------------
def getGuiWidth( gui ) :
	width = gui.width
	if __isText( gui ) :
		width = gui.stringWidth( gui.text )
	elif gui.widthRelative :
		width = toPXMeasure( width )
	return width

def setGuiWidth( gui, width ) :
	if __isText( gui ) : return
	if gui.widthRelative :
		width = toRXMeasure( width )
	gui.width = width

# -------------------------------------------
def getGuiHeight( gui ) :
	height = gui.height
	if __isText( gui ) :
		if gui.font.endswith( ".font" ) :
			height = Font.getFontHeight( gui.font )
		else :
			height = gui.fontDescription()["size"]
	elif gui.heightRelative :
		height = toPYMeasure( height )
	return height

def setGuiHeight( gui, height ) :
	if __isText( gui ) : return
	if gui.heightRelative :
		height = toRYMeasure( height )
	gui.height = height

# -------------------------------------------
def getGuiSize( gui ) :
	width = getGuiWidth( gui )
	height = getGuiHeight( gui )
	return Math.Vector2( width, height )

def setGuiSizes( gui, ( width, height ) ) :
	setGuiWidth( gui, width )
	setGuiHeight( gui, height )

# ----------------------------------------------------
def getGuiRWidth( gui ) :
	width = gui.width
	if __isText( gui ) :
		width = gui.stringWidth( gui.text )
		width = toRXMeasure( width )
	elif not gui.widthRelative :
		width = toRXMeasure( width )
	return width

def setGuiRWidth( gui, width ) :
	if __isText( gui ) : return
	if not gui.widthRelative :
		width = toPXMeasure( width )
	gui.width = width

# -------------------------------------------
def getGuiRHeight( gui ) :
	height = gui.height
	if __isText( gui ) :
		if gui.font.endswith( ".font" ) :
			height = Font.getFontHeight( gui.font )
		else :
			height = gui.fontDescription()["size"]
		height = toRYMeasure( height )
	elif not gui.heightRelative :
		height = toRYMeasure( height )
	return height

def setGuiRHeight( gui, height ) :
	if __isText( gui ) : return
	if not gui.heightRelative :
		height = toPYMeasure( height )
	gui.height = height

# -------------------------------------------
def getGuiRSize( gui ) :
	width = getGuiRWidth( gui )
	height = getGuiRHeight( gui )
	return ( width, height )

def setGuiRSize( gui, ( width, height ) ) :
	setGuiRWidth( width )
	setGuiRHeight( height )

# --------------------------------------------------------------------
# gui relative to screen
# --------------------------------------------------------------------
def getGuiLeftToScreen( gui ) :
	"""
	get gui's left on screen coordinate
	"""
	n_pos = gui.screenToClient( 0, 0 )
	return -n_pos[0]

def getGuiCenterToScreen( gui ) :
	"""
	get gui's center on screen coordinate
	"""
	width = getGuiWidth( gui )
	return  getGuiLeftToScreen( gui ) + width * 0.5

def getGuiRightToScreen( gui ) :
	"""
	get gui's right on screen coordinate
	"""
	width = getGuiWidth( gui )
	return  getGuiLeftToScreen( gui ) + width

# -------------------------------------------
def getGuiTopToScreen( gui ) :
	"""
	get gui's top on screen coordinate
	"""
	n_pos = gui.screenToClient( 0, 0 )
	return -n_pos[1]

def getGuiMiddleToScreen( gui ) :
	"""
	get gui's middle on screen coordinate
	"""
	height = getGuiHeight( gui )
	return getGuiTopToScreen( gui ) + height * 0.5

def getGuiBottomToScreen( gui ) :
	"""
	get gui's bottom on screen coordinate
	"""
	height = getGuiHeight( gui )
	return getGuiTopToScreen( gui ) + height

# -------------------------------------------
def getGuiPosToScreen( gui ) :
	"""
	get gui's location on screen coordinate
	"""
	left = getGuiLeftToScreen( gui )
	top = getGuiTopToScreen( gui )
	return Math.Vector2( left, top )

# -----------------------------------------------------
def getGuiRLeftToScreen( gui ) :
	"""
	get gui's relative left on screen coordinate
	"""
	n_pos = gui.screenToClient( -1.0, 1.0 )
	return -n_pos[0] - 1.0

def getGuiRCenterToScreen( gui ) :
	"""
	get gui's relative center on screen coordinate
	"""
	width = getGuiRWidth( gui )
	return  getGuiRLeftToScreen( gui ) + width * 0.5

def getGuiRRightToScreen( gui ) :
	"""
	get gui's relative right on screen coordinate
	"""
	width = getGuiRWidth( gui )
	return  getGuiRLeftToScreen( gui ) + width

# -------------------------------------------
def getGuiRTopToScreen( gui ) :
	"""
	get gui's relative top on screen coordinate
	"""
	n_pos = gui.screenToClient( -1.0, 1.0 )
	return n_pos[1] + 1

def getGuiRMiddleToScreen( gui ) :
	"""
	get gui's relative middle on screen coordinate
	"""
	height = getGuiRHeight( gui )
	return getGuiRTopToScreen( gui ) - height * 0.5

def getGuiRBottomToScreen( gui ) :
	"""
	get gui's relative bottom on screen coordinate
	"""
	height = getGuiRHeight( gui )
	return getGuiRTopToScreen( gui ) - height

def getGuiRPosToScreen( gui ) :
	"""
	get gui's relative position on screen coordinate
	"""
	left = getGuiRLeftToScreen( gui )
	top = getGuiRTopToScreen( gui )
	return Math.Vector2( left, top )


# --------------------------------------------------------------------
# about gui and mouse
# --------------------------------------------------------------------
def isMouseHit( gui ) :
	"""
	get a value indicates if the mouse is locatting in the gui
	"""
	if not gui.rvisible : return False
	px, py = csol.pcursorPosition()
	return gui.hitTest( px, py )

# -----------------------------------------------------
def getMouseInGuiPos( gui ) :
	"""
	get mouse's position relative to gui
	"""
	( cx, cy ) = csol.pcursorPosition()
	( gx, gy ) = getGuiPosToScreen( gui )
	return Math.Vector2( cx - gx, cy - gy )

def getMouseInGuiRPos( gui ) :
	"""
	get mouse's relative position relative gui
	"""
	pPos = getMouseInGuiPos( gui )
	left = toRXMeasure( pPos[0] )
	top = -toRYMeasure( pPos[1] )
	return Math.Vector2( left, top )


# --------------------------------------------------------------------
# about gui texture frame element
# 注意，如果采用相对坐标，则 GUI.Texture 的相对坐标是相对其所属的 GUI.TextureFrame 的坐标
# --------------------------------------------------------------------
def toFElemRXMeasure( pmeasure, owner ) :
	pwidth = owner.width
	if pwidth == 0.0 : return 0.0
	if owner.widthRelative :
		pwidth = pwidth * BigWorld.screenWidth() * 0.5
	return 2.0 * pmeasure / pwidth

def toFElemRYMeasure( pmeasure, owner ) :
	pheight = owner.height
	if pheight == 0.0 : return 0.0
	if owner.heightRelative :
		pheight = pheight * BigWorld.screenHeight() * 0.5
	return 2.0 * pmeasure / pheight

def toFElemPXMeasure( rmeasure, owner ) :
	pwidth = rwidth = owner.width
	if pwidth == 0.0 : return 0.0
	if owner.widthRelative :
		pwidth = rwidth * BigWorld.screenWidth() * 0.5
	return pwidth * rmeasure * 0.5

def toFElemPYMeasure( rmeasure, owner ) :
	pheight = rheight = owner.height
	if pheight == 0.0 : return 0.0
	if owner.heightRelative :
		pheight = rheight * BigWorld.screenHeight() * 0.5
	return pheight * rmeasure * 0.5

# -----------------------------------------------------
def getFElemLeft( felem ) :
	owner = felem.owner
	if owner and owner.widthRelative :
		return toFElemPXMeasure( felem.position.x, owner )
	return felem.position.x

def setFElemLeft( felem, left ) :
	owner = felem.owner
	if owner and owner.widthRelative :
		felem.position.x = toFElemRXMeasure( left, owner )
	else :
		felem.position.x = left

# -------------------------------------------
def getFElemCenter( felem ) :
	width = getFElemWidth( felem )
	left = getFElemLeft( felem )
	return left + width * 0.5

def setFElemCenter( felem, center ) :
	width = getFElemWidth( felem )
	setFElemLeft( felem, center - width * 0.5 )

# -------------------------------------------
def getFElemRight( felem ) :
	width = getFElemWidth( felem )
	left = getFElemLeft( felem )
	return left + width

def setFElemRight( felem, right ) :
	width = getFElemWidth( felem )
	setFElemLeft( felem, right - width )

# -------------------------------------------
def getFElemTop( felem ) :
	owner = felem.owner
	if owner and owner.heightRelative :
		return -toFElemPYMeasure( felem.position.y, owner )
	return felem.position.y

def setFElemTop( felem, top ) :
	owner = felem.owner
	if owner and owner.heightRelative :
		felem.position.y = -toFElemRYMeasure( top, owner )
	else :
		felem.position.y = top

# -------------------------------------------
def getFElemMiddle( felem ) :
	top = getFElemTop( felem )
	height = getFElemHeight( felem )
	return top + height * 0.5

def setFElemMiddle( felem, middle ) :
	height = getFElemHeight( felem )
	setFElemTop( felem, middle - height * 0.5 )

# -------------------------------------------
def getFElemBottom( felem ) :
	top = getFElemTop( felem )
	height = getFElemHeight( felem )
	return top + height

def setFElemBottom( felem, bottom ) :
	height = getFElemHeight( felem )
	setFElemTop( felem, bottom - height )

# -------------------------------------------
def getFElemPos( felem ) :
	owner = felem.owner
	x, y, z = felem.position
	if owner :
		if owner.widthRelative :
			x = toFElemPXMeasure( x, owner )
		if owner.heightRelative :
			y = -toFElemPYMeasure( y, owner )
	return Math.Vector2( x, y )

def setFElemPos( felem, pos ) :
	owner = felem.owner
	x, y = pos
	if owner :
		if owner.widthRelative :
			x = toFElemRXMeasure( x, owner )
		if owner.heightRelative :
			y = -toFElemRYMeasure( y, owner )
	felem.position.x = x
	felem.position.y = y

# -----------------------------------------------------
def getFElemRLeft( felem ) :
	owner = felem.owner
	if not owner or owner.widthRelative :
		return felem.position.x
	return toFElemRXMeasure( felem.position.x, owner )

def setFElemRLeft( felem, left ) :
	owner = felem.owner
	if not owner or owner.widthRelative :
		felem.position.x = left
	else :
		felem.position.x = toFElemPXMeasure( left, owner )

# -------------------------------------------
def getFElemRCenter( felem ) :
	width = getFElemRWidth( felem )
	left = getFElemRLeft( felem )
	return left + width * 0.5

def setFElemRCenter( felem, center ) :
	width = getFElemRWidth( felem )
	setFElemRLeft( felem, center - width * 0.5 )

# -------------------------------------------
def getFElemRRight( felem ) :
	left = getFElemRLeft( felem )
	return left + getFElemRWidth( felem )

def setFElemRRight( felem, right ) :
	left = right - getFElemRWidth( felem )
	setFElemRLeft( felem, left )

# -------------------------------------------
def getFElemRTop( felem ) :
	owner = felem.owner
	if not owner or owner.heightRelative :
		return felem.position.y
	return -toFElemRYMeasure( felem.position.y, owner )

def setFElemRTop( felem, top ) :
	owner = felem.owner
	if not owner or owner.heightRelative :
		felem.position.y = top
	else :
		felem.position.y = -toFElemPYMeasure( top, owner )

# -------------------------------------------
def getFElemRMiddle( felem ) :
	height = getFElemRHeight( felem )
	top = getFElemRTop( felem )
	return top - height * 0.5

def setFElemRMiddle( felem, middle ) :
	height = getFElemRHeight( felem )
	setFElemRTop( felem, middle + height * 0.5 )

# -------------------------------------------
def getFElemRBottom( felem ) :
	top = getFElemRTop( felem )
	return top - getFElemRHeight( felem )

def setFElemRBottom( felem, bottom ) :
	height = getFElemRHeight( felem )
	setFElemRTop( felem, bottom + height )

# -------------------------------------------
def getFElemRPos( felem ) :
	owner = felem.owner
	x, y, z = felem.position
	if owner :
		if not owner.widthRelative :
			x = toFElemRXMeasure( x, owner )
		if not owner.heightRelative :
			y = -toFElemRYMeasure( y, owner )
	return Math.Vector2( x, y )

def setFElemRPos( felem, pos ) :
	owner = felem.owner
	x, y = pos
	if owner :
		if not owner.widthRelative :
			x = toFElemPXMeasure( x, owner )
		if not owner.heightRelative :
			y = -toFElemPYMeasure( y, owner )
	felem.position.x = x
	felem.position.y = y

# -----------------------------------------------------
def getFElemWidth( felem ) :
	owner = felem.owner
	if owner and owner.widthRelative :
		return toFElemPXMeasure( felem.size.x, owner )
	return felem.size.x

def setFElemWidth( felem, width ) :
	owner = felem.owner
	if owner and owner.widthRelative :
		felem.size.x = toFElemRXMeasure( width, owner )
	else :
		felem.size.x = width

# -------------------------------------------
def getFElemHeight( felem ) :
	owner = felem.owner
	if owner and owner.heightRelative :
		return toFElemPYMeasure( felem.size.y, owner )
	return felem.size.y

def setFElemHeight( felem, height ) :
	owner = felem.owner
	if owner and owner.heightRelative :
		felem.size.y = toFElemRYMeasure( height, owner )
	else :
		felem.size.y = height

# -------------------------------------------
def getFElemSize( felem ) :
	owner = felem.owner
	w, h = felem.size
	if owner :
		if owner.widthRelative :
			w = toFElemPXMeasure( w, owner )
		if owner.heightRelative :
			h = toFElemPYMeasure( h, owner )
	return Math.Vector2( w, h )

def setFElemSize( felem, size ) :
	owner = felem.owner
	w, h = size
	if owner :
		if owner.widthRelative :
			w = toFElemRXMeasure( w, owner )
		if owner.heightRelative :
			h = toFElemRYMeasure( h, owner )
	felem.size = w, h

# -----------------------------------------------------
def getFElemRWidth( felem ) :
	owner = felem.owner
	if not owner or owner.widthRelative :
		return felem.size.x
	return toFElemRXMeasure( felem.size.x, owner )

def setFElemRWidth( felem, width ) :
	owner = felem.owner
	if not owner or owner.widthRelative :
		felem.size.x = width
	else :
		felem.size.x = toFElemPXMeasure( width, owner )

# -------------------------------------------
def getFElemRHeight( felem ) :
	owner = felem.owner
	if not owner or owner.heightRelative :
		return felem.size.y
	return toFElemRYMeasure( felem.size.y, owner )

def setFElemRHeight( felem, height ) :
	owner = felem.owner
	if owner or owner.heightRelative :
		felem.size.y = height
	else :
		felem.size.y = toFElemPYMeasure( height, owner )

# -------------------------------------------
def getFElemRSize( felem ) :
	owner = felem.owner
	w, h = felem.size
	if owner :
		if not owner.widthRelative :
			w = toFElemRXMeasure( felem.size.x, owner )
		if not owner.heightRelative :
			h = toFElemRYMeasure( felem.size.y, owner )
	return Math.Vector2( w, h )

def setFElemRSize( felem, size ) :
	owner = felem.owner
	w, h = size
	if owner :
		if not owner.widthRelative :
			w = toFElemPXMeasure( w, owner )
		if not owner.heightRelative :
			h = toFElemPYMeasure( h, owner )
	felem.size = w, h

# -----------------------------------------------------
def getFElemTWidth( felem ) :
	owner = felem.owner
	if owner and owner.widthRelative :
		return toFElemPXMeasure( felem.tileSize.x, owner )
	return felem.tileSize.x

def setFElemTWidth( felem, width ) :
	owner = felem.owner
	if owner and owner.widthRelative :
		felem.tileSize.x = toFElemRXMeasure( width, owner )
	else :
		felem.tileSize.x = width

def getFElemTHeight( felem ) :
	owner = felem.owner
	if owner and owner.heightRelative :
		return toFElemPYMeasure( felem.tileSize.y, owner )
	return felem.tileSize.y

def setFElemTHeight( felem, height ) :
	owner = felem.owner
	if owner and owner.heightRelative :
		felem.tileSize.y = toFElemRYMeasure( height, owner )
	else :
		felem.tileSize.y = height

def getFElemTSize( felem ) :
	owner = felem.owner
	w, h = felem.tileSize
	if owner :
		if owner.widthRelative :
			w = toFElemPXMeasure( w, owner )
		if owner.heightRelative :
			h = toFElemPYMeasure( h, owner )
	return Math.Vector2( w, h )

def setFElemTSize( felem, size ) :
	owner = felem.owner
	w, h = size
	if owner :
		if owner.widthRelative :
			w = toFElemRXMeasure( w, owner )
		if owner.heightRelative :
			h = toFElemRYMeasure( h, owner )
	felem.tileSize = w, h

# -----------------------------------------------------
def getFElemTRWidth( felem ) :
	owner = felem.owner
	if not owner or owner.widthRelative :
		return felem.tileSize.x
	return toFElemRXMeasure( felem.x, owner )

def setFElemTRWidth( felem, width ) :
	owner = felem.owner
	if not owner or owner.widthRelative :
		felem.tileSize.x = width
	else :
		felem.tileSize.x = toFElemPXMeasure( width, owner )

def getFElemTRHeight( felem ) :
	owner = felem.owner
	if not owner or owner.heightRelative :
		return felem.tileSize.y
	return toFElemRYMeasure( felem.tileSize.y, owner )

def setFElemTRHeight( felem, height ) :
	owner = felem.owner
	if owner or owner.heightRelative :
		felem.tileSize.y = height
	else :
		felem.tileSize.y = toFElemPYMeasure( height, owner )

def getFElemTRSize( felem ) :
	owner = felem.owner
	w, h = felem.tileSize
	if owner :
		if not owner.widthRelative :
			w = toFElemRXMeasure( felem.tileSize.x, owner )
		if not owner.heightRelative :
			h = toFElemRYMeasure( felem.tileSize.y , owner)
	return Math.Vector2( w, h )

def setFElemTRSize( felem, size ) :
	owner = felem.owner
	w, h = size
	if owner :
		if not owner.widthRelative :
			w = toFElemPXMeasure( w, owner )
		if not owner.heightRelative :
			h = toFElemPYMeasure( h, owner )
	felem.tileSize = w, h

# -*- coding: gb18030 -*-
#
# $Id: Font.py,v 1.4 2008-03-19 10:31:21 huangyongwei Exp $

"""
implement text operator class.

2008.01.26: writen by huangyongwei
"""

import GUI
import csol
import ResMgr


# --------------------------------------------------------------------
# 全局定义
# --------------------------------------------------------------------
# 字体效果
LIMN_NONE		= 0				# 没描画效果
LIMN_OUT		= 1				# 描边
LIMN_SHD		= 2				# 描阴影


_sect = ResMgr.openSection( "fonts/config.xml" )
_defSect = _sect["default"]
_floatSect = _sect["floatName"]
defFont = _defSect.readString( "defFont" )				# 默认字体
defFontSize = _defSect.readInt( "defSize" )				# 默认字体大小
defCharSpace = _defSect.readInt( "charSpace" )			# 默认字间距
defLimning = _defSect.readInt( "limning" )				# 默认字体效果
defLimnColor = _defSect.readVector4( "limnColor" )		# 字体效果默认颜色
defSpacing = _defSect.readFloat( "lineSpacing" )		# 默认行间距
floatFont = _floatSect.readString( "defFont" )
floatFontSize = _floatSect.readInt( "defSize" )
floatCharSpace = _floatSect.readInt( "charSpace" )
floatLimning = _floatSect.readInt( "limning" )
floatLimnColor = _floatSect.readVector4( "limnColor" )
floatSpacing = _floatSect.readFloat( "lineSpacing" )

ResMgr.purge( "fonts/config.xml" )
del _sect
del _defSect
del _floatSect

# --------------------------------------------------------------------
# 模块定义
# --------------------------------------------------------------------
_g_limners = {}					# 描边/阴影 shader（同 shader 颜色的文本标签共享一个 shader）

# --------------------------------------------------------------------
# 全局函数
# --------------------------------------------------------------------
def createLimnShader( style, color ) :
	"""
	创建一个描边/阴影 shader
	特别说明：shader 一旦创建，就会永远保存，也就是说，理论上会造成泄漏，但实际上整个游戏中只会用很少 shader（最多两三种）
	"""
	global _g_limners
	color = tuple( color )
	if len( color ) == 3 : color += ( 255, )
	limners = _g_limners.get( style, {} )
	shader = limners.get( color, None )
	if shader : return shader
	shader = GUI.FringeShader()
	shader.gray = False
	shader.colour = color
	shader.shadow = ( style == LIMN_SHD )
	limners[color] = shader
	_g_limners[style] = limners
	return shader


# -----------------------------------------------------
def getFontWidth( font ) :
	"""
	get font height
	@type			font : str
	@param			font : the font you want to get its width
	@rtype				 : int
	@return				 : width of the given font
	"""
	t = GUI.Text( "" )
	t.font = font
	return t.stringWidth( "A" )

def getFontHeight( font ) :
	"""
	get font height
	@type			font : str
	@param			font : the font you want to get its height
	@rtype				 : int
	@return				 : height of the given font
	"""
	return csol.getFontHeight( font )

def isWideFont( font ) :
	"""
	indicate wether the font you given is chinese font
	@type			font : str
	@param			font : the font you want to get its height
	@rtype				 : bool
	@return				 : if it is chinese return true
	"""
	return csol.isChineseFont(font)

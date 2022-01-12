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
# ȫ�ֶ���
# --------------------------------------------------------------------
# ����Ч��
LIMN_NONE		= 0				# û�軭Ч��
LIMN_OUT		= 1				# ���
LIMN_SHD		= 2				# ����Ӱ


_sect = ResMgr.openSection( "fonts/config.xml" )
_defSect = _sect["default"]
_floatSect = _sect["floatName"]
defFont = _defSect.readString( "defFont" )				# Ĭ������
defFontSize = _defSect.readInt( "defSize" )				# Ĭ�������С
defCharSpace = _defSect.readInt( "charSpace" )			# Ĭ���ּ��
defLimning = _defSect.readInt( "limning" )				# Ĭ������Ч��
defLimnColor = _defSect.readVector4( "limnColor" )		# ����Ч��Ĭ����ɫ
defSpacing = _defSect.readFloat( "lineSpacing" )		# Ĭ���м��
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
# ģ�鶨��
# --------------------------------------------------------------------
_g_limners = {}					# ���/��Ӱ shader��ͬ shader ��ɫ���ı���ǩ����һ�� shader��

# --------------------------------------------------------------------
# ȫ�ֺ���
# --------------------------------------------------------------------
def createLimnShader( style, color ) :
	"""
	����һ�����/��Ӱ shader
	�ر�˵����shader һ���������ͻ���Զ���棬Ҳ����˵�������ϻ����й©����ʵ����������Ϸ��ֻ���ú��� shader����������֣�
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

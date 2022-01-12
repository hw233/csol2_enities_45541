#
# -*- coding: gb18030 -*-
# $Id: PL_Font.py,v 1.2 2008-05-19 04:52:17 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from bwdebug import *
from guis.controls.RichText import BasePlugin
from share import defParser

class PL_Font( BasePlugin ) :
	"""
	字体属性插件，插件格式为：
	@F{ n = 字体名称; fc = 前景色; bc = 背景色; fa = 前景色 alpha 值; ba = 背景色 alpha 值;
	    fs = 字体大小; cs = 字间距; bl = 1 或 0（表示字体是否为粗体）; il = 1 或 0（表示字体是否为斜体）; ul = 1 或 0（表示是否有下划线）; so = 0 或 1（是否有删除线）}
	其中每个属性都是可选的。例如 @F{ n = 字体名称 } 或 @F{ fc = 前景色 } 都是合法的，它们分别表示只设置字体和只设置前景色
	注：一旦格式化后，跟在该格式化后面的所有文本都追随该格式化表现，要恢复原来的表现，要重新格式化回来
	"""
	esc_ = "@F"

	def __init__( self, owner ) :
		BasePlugin.__init__( self, owner )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		"""
		截取本插件的格式化文本
		"""
		formatText, leaveText = defParser.getFormatScope( text )
		if formatText == "" : return None, leaveText							# 格式化失败
		strAttrs = defParser.getAttrInfos( formatText )
		attrInfos = {}
		tmpOuter = pyRichText.tmpOuter__
		attrInfos["font"] = strAttrs.get( 'n', tmpOuter.font )
		fcolor = strAttrs.get( 'fc', "" )
		bcolor = strAttrs.get( 'bc', "" )
		falpha = strAttrs.get( 'fa', "" )
		balpha = strAttrs.get( 'ba', "" )
		attrInfos["fcolor"] = defParser.tranColor( fcolor, tmpOuter.fcolor )
		attrInfos["bcolor"] = defParser.tranColor( fcolor, tmpOuter.bcolor )
		attrInfos["falpha"] = defParser.tranInt( falpha, tmpOuter.fcolor[3] )
		attrInfos["balpha"] = defParser.tranInt( balpha, tmpOuter.bcolor[3] )

		size = strAttrs.get( "fs", None )
		chSpace = strAttrs.get( "cs", None )
		bold = strAttrs.get( "bl", None )
		italic = strAttrs.get( "il", None )
		underline = strAttrs.get( "ul", None )
		strikeOut = strAttrs.get( "so", None )
		if size : attrInfos["fs"] = defParser.tranInt( size, tmpOuter.fontSize )
		if chSpace : attrInfos["cs"] = defParser.tranFloat( chSpace, tmpOuter.charSpace )
		if bold : attrInfos["bl"] = defParser.tranInt( bold, tmpOuter.bold )
		if italic : attrInfos["il"] = defParser.tranInt( italic, tmpOuter.italic )
		if underline : attrInfos["ul"] = defParser.tranInt( underline, tmpOuter.underline )
		if strikeOut : attrInfos["so"] = defParser.tranInt( strikeOut, tmpOuter.strikeOut )

		return attrInfos, leaveText

	def transform( self, pyRichText, attrInfos ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		fr, fg, fb = attrInfos['fcolor'][:3]
		br, bg, bb = attrInfos['bcolor'][:3]
		fa = attrInfos["falpha"]
		ba = attrInfos["balpha"]
		tmpOuter = pyRichText.tmpOuter__
		tmpOuter.font = attrInfos["font"]
		tmpOuter.fcolor = fr, fg, fb, fa
		tmpOuter.bcolor = br, bg, bb, ba

		size = attrInfos.get( "fs", None )
		chSpace = attrInfos.get( "cs", None )
		bold = attrInfos.get( "bl", None )
		italic = attrInfos.get( "il", None )
		underline = attrInfos.get( "ul", None )
		strikeOut = attrInfos.get( "so", None )
		tmpOuter.font = attrInfos['font']
		if size is not None : tmpOuter.fontSize = size
		if chSpace is not None : tmpOuter.charSpace = chSpace
		if bold is not None : tmpOuter.bold = bold
		if italic is not None : tmpOuter.italic = italic
		if underline is not None : tmpOuter.underline = underline
		if strikeOut is not None : tmpOuter.strikeOut = strikeOut

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, text = "", **attrInfos ) :
		"""
		通过提供的属性信息，获取格式化文本
		@type			text	  : str
		@param			text	  : 要格式化的文本，如果该值不为空，则在格式化完该字符串后，自动将字体和颜色恢复为 RichText 默认的颜色，
									否则格式化将一直延伸到下一个 @F 为止
		@type			attrInfos : dict
		@param			attrInfos : 字体格式化属性:
									{ n = 字体名称( 可以不带 .font 扩展名); fc = 前景色; bc = 背景色; fa = 前景色 alpha 值; ba = 背景色 alpha 值;
									  fs = 字体大小; cs = 字间距; bl = 1 或 0（是否为粗体）; il = 1 或 0（是否为斜体）; ul = 1 或 0（是否有下划线）; so = 1 或 0（是否有删除线）}
		@rtype					  : str
		@return					  : RichText 可识别的格式化文本
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		strAttrs = []
		for key, value in attrInfos.iteritems() :
			if isDebuged :
				assert key in ( "n", "fc", "bc", "fa", "ba", \
					"fs", "bl", "il", "ul", "so" ), \
					"%s is not the keyword of the PL_Font plugin for RichText!" % key
			strAttrs.append( "%s=%s" % ( key, str( value ) ) )
		if len( strAttrs ) == 0 : return text
		return struct % ( ";".join( strAttrs ) ) + text + "@D"

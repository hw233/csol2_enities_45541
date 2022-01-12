#
# -*- coding: gb18030 -*-
# $Id: PL_Align.py,v 1.4 2008-08-20 07:39:54 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from bwdebug import *
from guis.controls.RichText import BasePlugin
from share import defParser

class PL_Align( BasePlugin ) :
	"""
	设置文本对齐方式的插件，插件格式为: @A{文本水平对齐方式}
	其中文本对齐方式有：“L”( 表示左对齐 )，“C”( 表示居中 )，“R” ( 表示右对齐 )
	"""
	esc_ = "@A"

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
		if formatText == "" : return None, text							# 格式化失败
		tmpAligns = formatText.strip().split( ';' )						# 拆分停靠方式
		aligns = []
		for align in tmpAligns :
			align = align.strip()
			if len( align ) != 1 : continue
			if align in "LCRTMB" :
				aligns.append( align )
		if len( aligns ) :
			return aligns, leaveText
		return None, leaveText											# 返回去掉格式化文本（转义字符和大括括起来的文本）后的文本

	def transform( self, pyRichText, attrInfo ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		for align in attrInfo :
			if align in "LCR" :
				pyRichText.setTmpAlign__( align )					# 设置文本水平对齐方式
			elif align in "TMB" :
				pyRichText.setTmpLineFlat__( align )				# 设置文本高低对齐方式

	# ----------------------------------------------------------------
	@classmethod
	def getStartAlign( SELF, text ) :
		"""
		获取某段文本，的起始对齐方式
		"""
		if not text.startswith( SELF.esc_ ) : return ( None, None )
		text = text[len( SELF.esc_ ):]
		formatText, leaveText = defParser.getFormatScope( text )
		if formatText == "" : return ( "L", "T" )					# 默认为靠左上角
		aligns = [None, None]
		tmpAligns = formatText.strip().split( ';' )					# 拆分停靠方式
		for align in tmpAligns :
			align = align.strip()
			if len( align ) != 1 : continue
			if align in "LCR" :
				aligns[0] = align
			elif align in "TMB" :
				aligns[1] = align
		return tuple( aligns )

	@classmethod
	def getSource( SELF, align = None, lineFlat = None ) :
		"""
		通过提供的属性信息，获取格式化文本
		@type			align	 : chr
		@param			align	 : 文本水平对齐方式: 靠左对齐：“L”，居中：“C”，靠右对齐“R”
		@type			lineFlat : chr
		@param			lineFlat : 前后两段高矮不一的文本的高低对齐方式：顶部对齐：“T”，中间对齐：“M”，底部对齐：“B”
		@rtype					 : str
		@return					 : RichText 可识别的格式化文本
		"""
		if isDebuged :
			if align : assert len( align ) == 1 and align in "LCR", "align mode must be: 'L', 'C', 'R'"
			if lineFlat : assert len( lineFlat ) == 1 and lineFlat in "TMB", "lineflat mode must be: 'T', 'M', 'B'"
		if align and lineFlat :
			return "%s{%s;%s}" % ( SELF.esc_, align, lineFlat )
		elif align :
			return "%s{%s}" % ( SELF.esc_, align )
		elif lineFlat :
			return "%s{%s}" % ( SELF.esc_, lineFlat )
		return ""

#
# -*- coding: gb18030 -*-
# $Id: PL_Space.py,v 1.3 2008-05-20 08:32:24 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from guis.controls.RichText import BasePlugin
from share import defParser
import reimpl_PL_Space

class PL_Space( BasePlugin ) :
	"""
	插入空格插件，格式为：@S 或者 @S{插入空行数量}
	倘若为 @S 则默认插入一个空格
	"""
	esc_ = "@S"

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
		if formatText == "" :											# 没有指定添加的空格数，则默认一个
			return None, " " + leaveText
		count = defParser.tranInt( formatText, 1 )
		count = max( 1, count )
		return None, " " * count + leaveText

	def transform( self, pyRichText, attrInfo ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		pass

	# ----------------------------------------------------------------
	@classmethod
	@reimpl_PL_Space.deco_PL_Space_getSource
	def getSource( SELF, n ) :
		"""
		获取插入空格格式化文本
		@type					n : int
		@param					n : 空格数
		@rtype					  : str
		@return					  : RichText 可识别的格式化文本
		"""
		assert n > 0, "n moust great than 0."
		if n == 1 : return SELF.esc_
		return "%s{%d}" % ( SELF.esc_, n )

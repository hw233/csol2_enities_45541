#
# -*- coding: gb18030 -*-
# $Id: PL_NewLine.py,v 1.3 2008-05-20 08:32:24 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from guis.controls.RichText import BasePlugin
from share import defParser

class PL_NewLine( BasePlugin ) :
	"""
	插入空行插件，格式为：@B 或者 @B{插入空行数量}
	倘若为 @B 则默认插入一个空行
	"""
	esc_ = "@B"

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
		if formatText == "" :											# 没有指定添加的空行数，则默认一个
			return 1, leaveText
		count = defParser.tranInt( formatText, 1 )
		count = max( 1, count )
		return count, leaveText

	def transform( self, pyRichText, count ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		pyRichText.newLine__( count )

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, n = 1 ) :
		"""
		获取换行的格式化文本
		@type					n : int
		@param					n : 空行数
		@rtype					  : str
		@return					  : RichText 可识别的格式化文本
		"""
		assert n > 0, "n moust great than 0."
		if n == 1 : return SELF.esc_
		return "%s{%d}" % ( SELF.esc_, n )

# --------------------------------------------------------------------
# 为了省时，将标记作为全局变量
# --------------------------------------------------------------------
g_newLine = PL_NewLine.getSource( )
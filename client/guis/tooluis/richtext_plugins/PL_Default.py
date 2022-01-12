#
# -*- coding: gb18030 -*-
# $Id: PL_Default.py,v 1.2 2008-05-19 04:52:17 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""


from guis.controls.RichText import TmpOuter, BasePlugin
from share import defParser

class PL_Default( BasePlugin ) :
	"""
	设置接着的文本字体、前景色颜色、背景色为默认值
	"""
	esc_ = "@D"

	def __init__( self, owner ) :
		BasePlugin.__init__( self, owner )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		"""
		截取本插件的格式化文本
		"""
		return self.esc, text

	def transform( self, pyRichText, attrInfo ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		pyRichText.tmpOuter__ = TmpOuter( pyRichText )

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF ) :
		"""
		通过提供的属性信息，获取格式化文本
		@return				  : RichText 可识别的格式化文本
		"""
		return SELF.esc_

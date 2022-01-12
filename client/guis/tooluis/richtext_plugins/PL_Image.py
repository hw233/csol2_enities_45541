#
# -*- coding: gb18030 -*-
# $Id: PL_Image.py,v 1.3 2008-08-19 09:33:02 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

import os
import GUI
from guis.UIFixer import hfUILoader
from guis.controls.RichText import BasePlugin
from share import defParser
from LinkImage import LinkImage

class PL_Image( BasePlugin ) :
	"""
	插入图像格式化插件，格式为：@I{ p = 图像配置路径; t = 图像路径; m = 超链接标记; s = 图像大小( w, h ) }
	其中 p 选项是必须的，其他两个选项可选
	倘若设置了 m 选项，并且其值不为空字符串，则该图像可以产生超链接功能（即点击该图像时，RichText 的 onComponentLClick 等事件将会被触发）
	注：p 的值是指图像配置路径，而不是图像途径。即，它的扩展名应该是：*.gui
	"""
	esc_ = "@I"

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
		if formatText == "" : return None, leaveText						# 格式化失败
		strAttrs = defParser.getAttrInfos( formatText )
		attrs = {}
		path = strAttrs.get( "p", "" )
		texture = strAttrs.get( "t", "" )
		text = strAttrs.get( "text", "" )
		if path.endswith( ".gui" ) :
			try :
				image = GUI.load( path )
			except :
				image = hfUILoader.load( "guis/controls/richtext/deficon.gui" )
		else :
			image = hfUILoader.load( "guis/controls/richtext/deficon.gui" )
		if texture != "" :													# 使用指定贴图
			image.textureName = texture
		attrs["image"] = image
		attrs["mark"] = strAttrs.get( "m", "" )
		strSize = strAttrs.get( "s", "" )
		attrs["size"] = defParser.tranTuple( strSize, 2 * [int], image.size )
		attrs["text"] = text
		color = defParser.tranColor( strAttrs.get( "c", "" ), None )
		if color : image.colour = color
		return attrs, leaveText

	def transform( self, pyRichText, imageInfo ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		image = imageInfo['image']
		mark = imageInfo['mark']
		pyImage = LinkImage( image, mark )
		pyImage.text = imageInfo['text']
		pyImage.size = imageInfo['size']									# 设置大小
		if not pyRichText.autoNewline :										# 如果不自动换行
			pyRichText.addElement__( pyImage )								# 则将图像放到当前行中
			return

		space = pyRichText.getCurrLineSpace__()								# 当前行剩余宽度
		if pyImage.width <= space :											# 如果当前剩余宽度，可以放下一个图像
			pyRichText.addElement__( pyImage )								# 则将图像放到当前行中
		elif pyImage.width > space and not pyRichText.isNewLine__() :		# 如果当前行剩余宽度不可以放下一个图像
			pyRichText.paintCurrLine__()									# 粘贴当前行
			self.transform( pyRichText, imageInfo )							# 并将图像放到下一行中处理
		elif pyImage.width > space :										# 如果 RichText 的最大宽度都不能容纳这个图像
			pyRichText.addElement__( pyImage )								# 则将图像放到当前行中
			pyRichText.paintCurrLine__()									# 粘贴当前行

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, path = "", texture = "", lmark = "", size = None, color = None, text = "" ) :
		"""
		通过提供的属性信息，获取插入图像格式化文本
		@type				path  : str
		@param				path  : 图像配置路径
		@type				lmark : str
		@param				lmark : 超链接标记
		@type				size  : tuple
		@param				size  : 图像大小( 宽，高 )
		@type				text  : str
		@param				text  : 该图片的文本表示(由使用者自己定义)，
									将作为RichText的viewText部分，以方便聊天记录的保存
		@return					  : RichText 可识别的格式化文本
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		strAttrs = []
		assert path != "" or texture != "", \
			"at least one of argument 'path' and 'texture' must't be empty string!"
		if path != "" : strAttrs.append( "p=%s" % path )
		if texture != "" : strAttrs.append( "t=%s" % texture )
		if lmark != "" : strAttrs.append( "m=%s" % lmark )
		if text != "" : strAttrs.append( "text=%s" % text )
		if size is not None : strAttrs.append( "s=%f,%f" % size )
		if color :
			if type( color ) is tuple and len( color ) == 3 :
				color += ( 255, )
			strAttrs.append( "c=%s" % str( color ) )
		return struct % ( ";".join( strAttrs ) )

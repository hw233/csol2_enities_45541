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
from guis.controls.RichText import BasePlugin
from share import defParser
from guis.controls.Icon import Icon

class PL_Image_Gui( BasePlugin ) :
	"""
	该插件是用于贴上某个GUI，并且该GUI中有一图像是动态可变的，避免重复拼接多个GUI
	插入图像格式化插件，格式为: @II{ p = 图像配置路径;mp =图像的路径; m = 超链接标记; s = 图像大小( w, h ) }
	p为gui的配置路径，该gui必须有一个子gui名字叫"Image" mp为可变的图像的路径
	注：p 的值是指图像配置路径，而不是图像途径。即，它的扩展名应该是：*.gui
	"""
	esc_ = "@M"

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
		if formatText == "" : None, leaveText								# 格式化失败
		strAttrs = defParser.getAttrInfos( formatText )
		attrs = {}
		path = strAttrs.get( "p", "" )
		ext = os.path.splitext( path )[1]
		if ext == ".gui" :													# 扩展名为 gui
			try :
				image = GUI.load( path )
			except ValueError :
				image = GUI.load( "guis/controls/richtext/deficon.gui" )
		else :																# 不是配置文件
			image = GUI.load( "guis/controls/richtext/deficon.gui" )
			if ext != "" : image.textureName = path							# 扩展名为贴图
		attrs["image"] = image
		attrs["mpath"] = strAttrs.get( "mp", "" )
		strSize = strAttrs.get( "s", "" )
		color = defParser.tranColor( strAttrs.get( "c", "" ), None )
		if color : image.colour = color
		return attrs, leaveText

	def transform( self, pyRichText, imageInfo ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		image = imageInfo['image']
		mpath = imageInfo['mpath']
		image.image.textureName = mpath										# 设置图像
		pyIcon = Icon( image )
		if not pyRichText.autoNewline :										# 如果不自动换行
			pyRichText.addElement__( pyIcon )								# 则将图像放到当前行中
			return

		space = pyRichText.getCurrLineSpace__()								# 当前行剩余宽度
		if pyIcon.width <= space :											# 如果当前剩余宽度，可以放下一个图像
			pyRichText.addElement__( pyIcon )								# 则将图像放到当前行中
		elif pyIcon.width > space and not pyRichText.isNewLine__() :		# 如果当前行剩余宽度不可以放下一个图像
			pyRichText.paintCurrLine__()									# 粘贴当前行
			self.transform( pyRichText, imageInfo )							# 并将图像放到下一行中处理
		elif pyIcon.width > space :										# 如果 RichText 的最大宽度都不能容纳这个图像
			pyRichText.addElement__( pyIcon )								# 则将图像放到当前行中
			pyRichText.paintCurrLine__()									# 粘贴当前行

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, path, mpath = "" ) :
		"""
		通过提供的属性信息，获取插入图像格式化文本
		@type				path  : str
		@param				path  : 图像配置路径
		@type				size  : tuple
		@param				size  : 图像大小( 宽，高 )
		@return					  : RichText 可识别的格式化文本
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		strAttrs = []
		strAttrs.append( "p=%s" % path )
		if mpath != "" : strAttrs.append( "mp=%s" % mpath)
		return struct % ( ";".join( strAttrs ) )

#
# -*- coding: gb18030 -*-
# $Id: PL_Link.py,v 1.3 2008-08-19 09:33:02 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

import csstring
from guis import *
from guis.controls.RichText import BasePlugin
from share import defParser
from LinkLabel import LinkLabel
from csstring import g_interpunctions

class PL_Link( BasePlugin ) :
	"""
	插入超链接插件，格式为：@L{ t = '超链接文本'; m = 超链接标记;
		cfc = 普通状态下前景色; cbc = 普通状态下背景色; hfc = 鼠标进入状态下前景色; hbc = 鼠标进入状态下背景色; ul = 0 或 1 表示是否有下划线; }
	其中 t 和 m 选项是必选的，其他可选
	"""
	esc_ = "@L"

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
		if formatText == "" : return None, leaveText								# 格式化失败
		attrs = {}
		tmpOuter = pyRichText.tmpOuter__
		strAttrs = defParser.getAttrInfos( formatText )
		attrs["text"] = strAttrs.get( "t", "" )
		attrs["mark"] = strAttrs.get( "m", "" )
		if attrs["text"] == "" : attrs["text"] = "<error link label: no link text>"
		elif attrs["mark"] == "" : attrs["text"] += "<error link label: no link mark>"

		cfc = strAttrs.get( "cfc", "" )
		cbc = strAttrs.get( "cbc", "" )
		hfc = strAttrs.get( "hfc", cfc )											# 如果没有设置高亮的前景色，则使用正常状态下的前景色
		hbc = strAttrs.get( "hbc", cbc )											# 如果没有设置高亮的背景色，则使用正常状态下的背景色
		attrs["cfc"] = defParser.tranColor( cfc, tmpOuter.fcolor )
		attrs["cbc"] = defParser.tranColor( cbc, tmpOuter.bcolor )
		attrs["hfc"] = defParser.tranColor( hfc, tmpOuter.fcolor )
		attrs["hbc"] = defParser.tranColor( hbc, tmpOuter.bcolor )

		attrs["ul"] = strAttrs.get( "ul", "0" )										# 下划线

		return attrs, leaveText

	def transform( self, pyRichText, linkInfo, pyForeLabel = None ) :
		"""
		通过格式化信息，利用 RichText 提供的 API，向 RichText 中粘贴自定义元素
		"""
		pyLabel = LinkLabel( linkInfo['mark'] )							# 创建一个链接标签
		pyLabel.pyForeLabel = pyForeLabel								# 设置它的前置标签
		if pyForeLabel : pyForeLabel.pyNextLabel = pyLabel				# 设置它后置标签的前置标签
		pyLabel.commonForeColor = cfcolor = linkInfo["cfc"]				# 链接标签普通状态下的前景色
		pyLabel.commonBackColor = linkInfo["cbc"]						# 链接标签普通状态下的背景色
		pyLabel.highlightForeColor = linkInfo["hfc"]					# 链接标签高亮状态下的前景色
		pyLabel.highlightBackColor = linkInfo["hbc"]					# 链接标签高亮状态下的背景色

		tmpOuter = pyRichText.tmpOuter__
		pyLabel.charSpace = tmpOuter.charSpace							# 字间距
		pyLabel.setFontInfo( {
			"font" : tmpOuter.font,										# 字体
			"size" : tmpOuter.fontSize,									# 字体大小
			"bold" : tmpOuter.bold,										# 是否使用粗体
			"italic" : tmpOuter.italic,									# 是否使用斜体
			"underline" : linkInfo["ul"] != "0",						# 是否有下划线
			} )

		text = linkInfo["text"]											# 链接文本
		ltext, rtext = text, ""											# 默认不作自动换行
		if pyRichText.autoNewline :										# 如果自动换行
			space = pyRichText.getCurrLineSpace__()						# 获取当前行剩余宽度
			ltext, rtext, lwtext, rwtext = pyLabel.splitText( space, "CUT", text )	# 在剩余宽度范围内拆分字符串
			if len( rwtext ) :
				fchr = csstring.toString( rwtext[0] )
				if fchr in g_interpunctions :							# 不折断标点符号
					ltext += fchr
					rtext = csstring.toString( rwtext[1:] )
		if rtext == "" :												# 如果没有折断文本，则说明剩余宽度可以放下整个字符串
			pyLabel.text = ltext
			pyRichText.addElement__( pyLabel )							# 放到当前行中
		elif ltext == "" and not pyRichText.isNewLine__() :				# 如果剩余的宽度不足以放下一个文字
			pyRichText.paintCurrLine__()								# 粘贴当前行
			self.transform( pyRichText, linkInfo )						# 转到下一行中粘贴
		elif ltext == "" :												# 如果最大宽度太小，连一个字也放不下
			wtext = csstring.toWideString( text )
			pyLabel.text = csstring.toString( wtext[0] )				# 则只放一个字
			pyRichText.addElement__( pyLabel )							# 添加到当前行
			pyRichText.paintCurrLine__()								# 粘贴当前行
			linkInfo['text'] = csstring.toString( wtext[1:] )			# 获取剩余文本
			self.transform( pyRichText, linkInfo, pyLabel )				# 转到下一行中粘贴剩余文本
		else :															# 如果文本被折断成两半
			pyLabel.text = ltext
			pyRichText.addElement__( pyLabel )							# 将折断的左边文本放到当前行
			pyRichText.paintCurrLine__()								# 粘贴当前行
			linkInfo['text'] = rtext									# 获取剩余文本
			self.transform( pyRichText, linkInfo, pyLabel )				# 转到下一行中粘贴剩余文本

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, text, mark, **dspMode ) :
		"""
		通过提供的超链接信息提获取格式化文本
		@type				text	: str
		@param				text	: 超链接文本
		@type				mark	: str
		@param				mark	: 超链接标记
		@type				dspMode : dict
		@param				dspMode : 超链接表现形式：
									  { cfc = 普通前景色; cbc = 普通背景色; hfc = 高丽前景色; hbc = 高亮背景色;
										bl = 1 或 0（表示是否是粗体）; il = 1 或 0（表示是否是斜体）; ul = 1 或 0（表示是否有下划线）}
		@rtype						: str
		@return						: RichText 可识别的格式化文本
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		attrStrs = []
		attrStrs.append( "t=%s" % text )
		attrStrs.append( "m=%s" % mark )
		for key, value in dspMode.iteritems() :
			if isDebuged :
				assert key in ( "cfc", "cbc", "hfc", "hbc", "ul" ), \
					"%s is not the keyword of the link plugin for RichText!" % key
			attrStrs.append( "%s=%s" % ( key, value ) )
		return struct % ( ";".join( attrStrs ) )

# -*- coding: gb18030 -*-
#

"""
UI 文本标签管理器
2010.03.08: writen by huangyongwei
"""

import GUI
import bwdebug
import Language
import csstring
import Font
import Color
from AbstractTemplates import Singleton
from SmartImport import smartImport


"""
配置可包含的关键字有：
text		: 文本（必填）
font		: 字体
fontSize	: 字体大小
charSpace	: 字间距
color		: 字体颜色
limning		: 描边模式：0 为没描边（不设置该关键字），1 描边，2 阴影，默认为 Font.defLimning
limnColor	: 描边颜色，默认为 Font.defLimnColor
"""

# --------------------------------------------------------------------
# 标签对象
# --------------------------------------------------------------------
class Label( object ) :
	__sltos__ = ( "text", "font", "fontSize", "charSpace", "color", "limning", "limnColor" )
	def __init__( self, text, font, fontSize, charSpace, color, limning, limnColor ) :
		self.text = text
		self.wtext = csstring.toWideString( text )
		self.font = font
		self.fontSize = fontSize
		self.charSpace = charSpace
		self.color = color
		self.limning = limning
		self.limnColor = limnColor


# --------------------------------------------------------------------
# 标签管理器
# --------------------------------------------------------------------
class LabelGather( Singleton ) :
	def __init__( self ) :
		self.__labels = {}


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getLabelCfg( self, key ) :
		"""
		加载文本标签配置
		"""
		d = self.__labels.get( key, None )
		if d is None :
			d = smartImport( "config.client.labels.%s" % key )
		self.__labels[key] = d
		return d

	# -------------------------------------------------
	def __getColor( self, color, defColor = ( 255, 255, 255, 255 ) ) :
		"""
		获取颜色
		"""
		if type( color ) is tuple :				# RGB 颜色
			if len( color ) == 3 :
				color += ( 255, )
			defColor = color
		else :									# 整数值颜色
			color = Color.intColor2RGBColor( color )
			defColor = color + ( 255, )
		return defColor


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getText( self, key, lbName, *args ) :
		"""
		获取标签信息
		@type			key	   : str
		@param			key	   : 标签在配置中的前缀
		@type			lbName : str
		@param			lbName : 标签名称
		@type			args   : 任何基本类型
		@param			args   : 格式化参数
		@rtype				   : str
		@return				   : 标签文本
		"""
		if bwdebug.isDebuged :
			assert ":" in key, "error label key '%s'" % key
		text = self.__getLabelCfg( key )[lbName]["text"]
		if len( args ) == 0 : return text
		return text % args

	def getLabel( self, key, lbName, *args ) :
		"""
		获取标签信息
		@type			key	   : str
		@param			key	   : 标签在配置中的前缀
		@type			lbName : str
		@param			lbName : 标签名称
		@type			args   : 任何基本类型
		@param			args   : 格式化参数
		@rtype				   : Label
		@return				   : 存在的话，返回标签信息实例
		"""
		if bwdebug.isDebuged :
			assert ":" in key, "error label key '%s'" % key

		lbInfo = self.__getLabelCfg( key )[lbName]
		font = lbInfo.get( "font", Font.defFont )
		fontSize = lbInfo.get( "fontSize", Font.defFontSize )
		charSpace = lbInfo.get( "fontSize", Font.defCharSpace )
		color = ( 255, 255, 255, 255 )
		limning = lbInfo.get( "limning", Font.defLimning )
		limnColor = lbInfo.get( "limnColor", Font.defLimnColor )
		if lbInfo.has_key( "color" ) :
			color = self.__getColor( lbInfo["color"] )
		text = lbInfo["text"]
		if len( args ) > 0 : text = text % args
		return Label( text, font, fontSize, charSpace, color, limning, limnColor )

	def setLabel( self, uilabel, key, lbName, *args ) :
		"""
		设置引擎标签的文本
		@type			uilabel : GUI.Text
		@param			uilabel : 引擎文本标签
		@type			key		: str
		@param			key		: 标签在配置中的前缀
		@type			lbName	: str
		@param			lbName	: 标签名称
		@type			args	: 任何基本类型
		@param			args	: 格式化参数
		"""
		if bwdebug.isDebuged :
			assert ":" in key, "error label key '%s'" % key
			assert type( uilabel ) is GUI.Text, "uilabel must be a GUI.Text!"

		lbInfo = self.__getLabelCfg( key )[lbName]
		font = lbInfo.get( "font", Font.defFont )
		fontSize = lbInfo.get( "fontSize", Font.defFontSize )
		charSpace = lbInfo.get( "charSpace", Font.defCharSpace )
		limning = lbInfo.get( "limning", Font.defLimning )
		limnColor = lbInfo.get( "limnColor", Font.defLimnColor )
		uilabel.fontDescription( {
			"font" : font,
			"size" : fontSize,
			"charOffset" : ( charSpace, 0 )
			} )

		if "color" in lbInfo :
			uilabel.colour = self.__getColor( lbInfo["color"] )
		text = lbInfo["text"]
		if len( args ) > 0 : text = text % args
		uilabel.text = csstring.toWideString( text )
		if limning != Font.LIMN_NONE :
			shader = Font.createLimnShader( limning, limnColor )
			uilabel.addShader( shader, "limner" )

	def setPyLabel( self, pyLabel, key, lbName, *args ) :
		"""
		设置 python 标签的文本( pyLabel 要有 "font", "color", "text" 这三个属性 )
		@type			pyLabel : control.StaticLabel / Control.Label
		@param			pyLabel : 引擎文本标签
		@type			key		: str
		@param			key		: 标签在配置中的前缀
		@type			lbName	: str
		@param			lbName	: 标签名称
		@type			args	: 任何基本类型
		@param			args	: 格式化参数
		"""
		if bwdebug.isDebuged :
			assert ":" in key, "error label key '%s'" % key
			assert hasattr( pyLabel, "font" ) and \
				hasattr( pyLabel, "color" ), "Error python label!"

		lbInfo = self.__getLabelCfg( key )[lbName]
		pyLabel.font = lbInfo.get( "font", Font.defFont )
		pyLabel.fontSize = lbInfo.get( "fontSize", Font.defFontSize )
		pyLabel.charSpace = lbInfo.get( "charSpace", Font.defCharSpace )
		pyLabel.limnColor = lbInfo.get( "limnColor", Font.defLimnColor )
		pyLabel.limning = lbInfo.get( "limning", Font.defLimning )
		if "color" in lbInfo :
			pyLabel.color = self.__getColor( lbInfo["color"] )
		text = lbInfo["text"]
		if len( args ) > 0 : text = text % args
		pyLabel.text = csstring.toWideString( text )

	def setPyBgLabel( self, pyBg, key, lbName, *args ) :
		"""
		设置 python 按钮的文本( pyLabel 要有 "font", "foreColor", "text" 这三个属性 )
		@type			pyBtn  : control.StaticLabel / Control.Label
		@param			pyBtn  : 引擎文本标签
		@type			key	   : str
		@param			key	   : 标签在配置中的前缀
		@type			lbName : str
		@param			lbName : 标签名称
		@type			args   : 任何基本类型
		@param			args   : 格式化参数
		"""
		if bwdebug.isDebuged :
			assert ":" in key, "error label key '%s'" % key
			assert hasattr( pyBg, "text" ) and \
				hasattr( pyBg, "font" ) and \
				hasattr( pyBg, "foreColor" ), "Error bg label!"

		lbInfo = self.__getLabelCfg( key )[lbName]
		pyBg.font = lbInfo.get( "font", Font.defFont )
		pyBg.fontSize = lbInfo.get( "fontSize", Font.defFontSize )
		pyBg.charSpace = lbInfo.get( "charSpace", Font.defCharSpace )
		pyBg.limnColor = lbInfo.get( "limnColor", Font.defLimnColor )
		pyBg.limning = lbInfo.get( "limning", Font.defLimning )
		if "color" in lbInfo :
			pyBg.foreColor = self.__getColor( lbInfo["color"] )
		text = lbInfo["text"]
		if len( args ) > 0 : text = text % args
		pyBg.text = csstring.toWideString( text )


# --------------------------------------------------------------------
# 全局实例
# --------------------------------------------------------------------
labelGather = LabelGather()

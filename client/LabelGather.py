# -*- coding: gb18030 -*-
#

"""
UI �ı���ǩ������
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
���ÿɰ����Ĺؼ����У�
text		: �ı������
font		: ����
fontSize	: �����С
charSpace	: �ּ��
color		: ������ɫ
limning		: ���ģʽ��0 Ϊû��ߣ������øùؼ��֣���1 ��ߣ�2 ��Ӱ��Ĭ��Ϊ Font.defLimning
limnColor	: �����ɫ��Ĭ��Ϊ Font.defLimnColor
"""

# --------------------------------------------------------------------
# ��ǩ����
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
# ��ǩ������
# --------------------------------------------------------------------
class LabelGather( Singleton ) :
	def __init__( self ) :
		self.__labels = {}


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getLabelCfg( self, key ) :
		"""
		�����ı���ǩ����
		"""
		d = self.__labels.get( key, None )
		if d is None :
			d = smartImport( "config.client.labels.%s" % key )
		self.__labels[key] = d
		return d

	# -------------------------------------------------
	def __getColor( self, color, defColor = ( 255, 255, 255, 255 ) ) :
		"""
		��ȡ��ɫ
		"""
		if type( color ) is tuple :				# RGB ��ɫ
			if len( color ) == 3 :
				color += ( 255, )
			defColor = color
		else :									# ����ֵ��ɫ
			color = Color.intColor2RGBColor( color )
			defColor = color + ( 255, )
		return defColor


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getText( self, key, lbName, *args ) :
		"""
		��ȡ��ǩ��Ϣ
		@type			key	   : str
		@param			key	   : ��ǩ�������е�ǰ׺
		@type			lbName : str
		@param			lbName : ��ǩ����
		@type			args   : �κλ�������
		@param			args   : ��ʽ������
		@rtype				   : str
		@return				   : ��ǩ�ı�
		"""
		if bwdebug.isDebuged :
			assert ":" in key, "error label key '%s'" % key
		text = self.__getLabelCfg( key )[lbName]["text"]
		if len( args ) == 0 : return text
		return text % args

	def getLabel( self, key, lbName, *args ) :
		"""
		��ȡ��ǩ��Ϣ
		@type			key	   : str
		@param			key	   : ��ǩ�������е�ǰ׺
		@type			lbName : str
		@param			lbName : ��ǩ����
		@type			args   : �κλ�������
		@param			args   : ��ʽ������
		@rtype				   : Label
		@return				   : ���ڵĻ������ر�ǩ��Ϣʵ��
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
		���������ǩ���ı�
		@type			uilabel : GUI.Text
		@param			uilabel : �����ı���ǩ
		@type			key		: str
		@param			key		: ��ǩ�������е�ǰ׺
		@type			lbName	: str
		@param			lbName	: ��ǩ����
		@type			args	: �κλ�������
		@param			args	: ��ʽ������
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
		���� python ��ǩ���ı�( pyLabel Ҫ�� "font", "color", "text" ���������� )
		@type			pyLabel : control.StaticLabel / Control.Label
		@param			pyLabel : �����ı���ǩ
		@type			key		: str
		@param			key		: ��ǩ�������е�ǰ׺
		@type			lbName	: str
		@param			lbName	: ��ǩ����
		@type			args	: �κλ�������
		@param			args	: ��ʽ������
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
		���� python ��ť���ı�( pyLabel Ҫ�� "font", "foreColor", "text" ���������� )
		@type			pyBtn  : control.StaticLabel / Control.Label
		@param			pyBtn  : �����ı���ǩ
		@type			key	   : str
		@param			key	   : ��ǩ�������е�ǰ׺
		@type			lbName : str
		@param			lbName : ��ǩ����
		@type			args   : �κλ�������
		@param			args   : ��ʽ������
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
# ȫ��ʵ��
# --------------------------------------------------------------------
labelGather = LabelGather()

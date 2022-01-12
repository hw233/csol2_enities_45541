# -*- coding: gb18030 -*-
#
# $Id: PropertyItem.py,v 1.10 2008-08-21 08:26:09 fangpengjun Exp $

import BigWorld
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from config.client.PlayerPropertyDescription import playerPropertyDescription as property_dsp
from LivingConfigMgr import LivingConfigMgr
from CombatSystemExp import CombatExp
livingInstance = LivingConfigMgr.instance()

class PropertyItem( Control ):

	def __init__( self, tag, richItem, isPlayer = True ):
		Control.__init__( self, richItem, pyBinder = None )
		self.__tag = tag
		self.crossFocus = True
		self.maxVal = 0.0
		self.minVal = 0.0
		self.isPlayer = isPlayer						#是否为自己的角色属性面板的
		self.__initialize( richItem )
		self.damage = None

	def __initialize( self, richItem ):
		self.__pyStTitle = StaticText( richItem.lbTitle )
		if self.__tag == "PK":
			self.__pyStTitle.fontSize = 14
		self.__pyStTitle.text = ""
		self.__pyLbValue = StaticText( richItem.lbValue )
		self.__pyLbValue.text = ""
		self.__pyLbValue.realText = ""

	def __getDescription( self, tag ):
		dsp = ""
		race = BigWorld.player().getClass()
		if property_dsp.has_key( race ) :
			tag = self.tag
			if property_dsp[race].has_key( tag ) :
				dsp = property_dsp[race][tag]
		return dsp

	# --------------------------------------------------------------------------
	def onMouseEnter_( self,):
		Control.onMouseEnter_( self )
		tag = self.tag
		dsp = ""
		player = BigWorld.player()
		exp = CombatExp( player, player )
		if not self.isPlayer:return
		if tag == "Amor":
			text = self.__pyLbValue.text
			if text == "":return
			amor = int( text )
			amorRate = max( 0.0, exp.getPhysicsDamageReductionRate() )
			if amorRate > 0.95:
				amorRate = 0.95
			dsp = labelGather.getText( "PlayerProperty:EquipPanel", "amorRate" )%( amorRate*100)
		elif tag == "MagAmor":
			text = self.__pyLbValue.text
			if text == "":return
			magAmor = int( text )
			magAmorRate = max( 0.0, exp.getMagicDamageReductionRate() )
			if magAmorRate > 0.95:
				magAmorRate = 0.95
			dsp = labelGather.getText( "PlayerProperty:EquipPanel", "magAmorRate" )%( magAmorRate*100)	
		elif tag == "Vim":
			dsp = 	dsp = self.__getDescription( tag )	
			if BigWorld.player().level < 50:
				dsp += labelGather.getText( "PlayerProperty:EquipPanel", "livingSkillOpenTips" )
		else:
			dsp = self.__getDescription( tag )
		if self.__pyLbValue.realText != "":
			titleText = self.__pyStTitle.text
			valueText = self.__pyLbValue.realText
			valueTip = labelGather.getText( "PlayerProperty:EquipPanel", "valueTip" )%( titleText, valueText )
			dsp += valueTip
		toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

	def updateValue( self, tag, value ):# 更新各属性值
		player = BigWorld.player()
		if tag in ["Force","Brains","Agility","Habitus","Potential","Ditheism", "PK","Amor","MagAmor","MagDam","Credit","Honor"]:
			textInfo = str( int( value ))
		elif tag == "Vim":
			if player.level < 50:
				textInfo = "0/0"
			else:
				maxVim = livingInstance.getMaxVimByLevel( BigWorld.player().getLevel() )
				textInfo = "%d/%d"%( value, maxVim )
		else:				
			rate = float( value )
			textInfo = "%0.2f%%" % ( rate*100.0 )
		if len( textInfo ) > 7:
			self.__pyLbValue.text = "..."
			self.__pyLbValue.realText = textInfo
		else:
			self.__pyLbValue.text = textInfo
			self.__pyLbValue.realText = ""
	
	def onLevelChange( self, oldLevel, level ):
		"""
		角色等级改变,活力值上限也相应改变
		"""
		maxVim = livingInstance.getMaxVimByLevel( level )
		textInfo = "%d/%d"%( BigWorld.player().vim, maxVim )
		if len( textInfo ) > 7:
			self.__pyLbValue.text = "..."
			self.__pyLbValue.realText = textInfo
		else:
			self.__pyLbValue.text = textInfo
			self.__pyLbValue.realText = ""

	# -------------------------------------------------------------------
	def updateMax( self, maxVal ):
		self.maxVal = maxVal
		textInfo = str( int( maxVal+ self.minVal )/2 )
		if len( textInfo ) > 7:
			self.__pyLbValue.text = "..."
			self.__pyLbValue.realText = textInfo
		else:
			self.__pyLbValue.text = textInfo
			self.__pyLbValue.realText = ""

	def updateMin( self, minVal ):
		self.minVal = minVal
		textInfo = str( int( minVal+ self.maxVal )/2 )
		if len( textInfo ) > 7:
			self.__pyLbValue.text = "..."
			self.__pyLbValue.realText = textInfo
		else:
			self.__pyLbValue.text = textInfo
			self.__pyLbValue.realText = ""

	# -------------------------------------------------------------------
	def _getTag( self ):

		return self.__tag

	def _setTag( self, tag ):

		self.__tag = tag

	def _getTitle( self ):

		return self.__pyStTitle.text

	def _setTitle( self, title ):

		self.__pyStTitle.text = title

	tag = property( _getTag, _setTag )
	title = property( _getTitle, _setTitle )

	

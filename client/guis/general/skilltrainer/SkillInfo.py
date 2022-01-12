# -*- coding: gb18030 -*-
#
# $Id: SkillInfo.py,v 1.7 2008-07-05 04:19:33 fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.SkillItem import SkillItem as SkillObject
from ItemsFactory import SkillItem
import skills as Skill
import csdefine

class SkillInfo( PyGUI ):
	__cg_panel = None

	def __init__( self ):
		if SkillInfo.__cg_panel is None :
			SkillInfo.__cg_panel = GUI.load( "guis/general/skilltrainer/skillinfo.gui" )
		panel = util.copyGuiTree( SkillInfo.__cg_panel )
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )

		self.__pyLbLevel = StaticText( panel.lbLevel )
		self.__pyLbLevel.text = ""

		self.__pyLbName = StaticText( panel.lbName )
		self.__pyLbName.text = ""

		self.__pyLbPassive = StaticText( panel.lbPassive )
		self.__pyLbPassive.visible = False

		self.__pyLbIntonate = StaticText( panel.lbIntonate )
		self.__pyLbIntonate.text = ""

		self.__pyLbCoolDown = StaticText( panel.lbCoolDown )
		self.__pyLbCoolDown.text = ""

		self.__pySkillItem = SkillObject( panel.skillItem )
		self.__pySkillItem.dragFocus = False

	def updateInfo( self, skill ):
		if skill == None:
			self.__pyLbLevel.text = ""
			self.__pyLbName.text = ""
			self.__pyLbPassive.visible = False
			self.__pySkillItem.update( None )
			self.__pyLbIntonate.text = ""
			self.__pyLbCoolDown.text = ""
			return
		self.__pyLbLevel.text = "LV%i"%skill.getLevel()
		self.__pyLbName.text = skill.getName()
		self.__pyLbPassive.visible = skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE
		leranSkill = Skill.getSkill( skill.getLearnID() )
		skillInfo = SkillItem( leranSkill )
		self.__pySkillItem.update( skillInfo )

		time = skill.getIntonateTime()
		text = labelGather.getText( "SkillTrainer:main", "singing" )%time
		if time - int( time ) == 0 :
			text = labelGather.getText( "SkillTrainer:main", "singing" )%time
		self.__pyLbIntonate.text = text

		time = skill.getMaxCDTime()
		text = labelGather.getText( "SkillTrainer:main", "coolDown" )%time
		if time - int( time ) == 0 :
			text = labelGather.getText( "SkillTrainer:main", "coolDown" )%time
		self.__pyLbCoolDown.text = text
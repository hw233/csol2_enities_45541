# -*- coding: gb18030 -*-
#
# $Id: Spell_LivingSkill.py,v 1.1 10:13 2009-12-12 jiangyi Exp $

"""
������ࣨ����������������
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from LivingConfigMgr import LivingConfigMgr
from config.client.labels.skills import lbs_Spell_LivingSkill

lvc = LivingConfigMgr.instance()

class Spell_LivingSkill( Spell ):
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )


	def getDescription( self ):
		"""
		�������Ҫ����������,�������ӵ�ǰ������¼��������Ϣ
		"""
		player = BigWorld.player()
		skillID = int( self._datas['ID'] )
		if not player.livingskill.has_key( skillID ):
			return lbs_Spell_LivingSkill[1]
		lvSkill = player.livingskill[skillID]
		des = lvc.getDesByLevel( skillID, lvSkill[0] )
		if des is None or des == "":
			return ""
		dess = des.split("|")
		des = dess[len(dess)-1]
		return des						# self._datas[ "Description" ]

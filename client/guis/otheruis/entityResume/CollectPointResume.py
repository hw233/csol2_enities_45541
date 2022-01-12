# -*- coding: gb18030 -*-
#
# $Id: CollectPointResume.py,v 1.1 11:12 2010-4-7 jiangyi Exp $


import BigWorld
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from LabelGather import labelGather

SKILLID_NAME = {
				790001001:labelGather.getText( "EntityResume:collectPoint", "skill_mining" ),
				790002001:labelGather.getText( "EntityResume:collectPoint", "skill_gatherSilk" ),
				790003001:labelGather.getText( "EntityResume:collectPoint", "skill_decorticate" ),
				790004001:labelGather.getText( "EntityResume:collectPoint", "skill_pickJade" ),
				790005001:labelGather.getText( "EntityResume:collectPoint", "skill_lumbering" ),
				0:labelGather.getText( "EntityResume:collectPoint", "skill_none" ),
			}

class CollectPointResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		player = BigWorld.player()
		text = entity.uname
		text += PL_NewLine.getSource()
		lvs = player.livingskill
		skillID = entity.reqSkillID
		selum = entity.sleUpMax
		sle = entity.reqSle
		if skillID not in lvs:
			addMsg = labelGather.getText( "EntityResume:collectPoint", "needSkill", SKILLID_NAME[skillID] )
			infoText = PL_Font.getSource( addMsg, fc = ( 255, 0, 0 ) )
			text += "%s%s"%( PL_NewLine.getSource(), infoText )
			
		else:
			reqSkill = labelGather.getText( "EntityResume:collectPoint", "needSkill", SKILLID_NAME[skillID] )
			reqSkillText = PL_Font.getSource( reqSkill, fc = ( 0, 255, 0 ) )
			text += reqSkillText
			text += PL_NewLine.getSource()
			
			playrSle = lvs[skillID][0]	
			reqPoint = labelGather.getText( "EntityResume:collectPoint", "needPoint", sle )	
			canGainSleText = ""
			reqPointText = ""	
			if playrSle < sle:			
				reqPointText = PL_Font.getSource( reqPoint, fc = ( 255, 0, 0 ) )	#熟练度不足			
			else:
				reqPointText = PL_Font.getSource( reqPoint, fc = ( 0, 255, 0 ) )	#熟练度足够			
				if playrSle < selum:	#可以正常获得熟练度
					canGainSle = labelGather.getText( "EntityResume:collectPoint", "canGainSle" )
					canGainSleText = PL_Font.getSource( canGainSle, fc = ( 0, 255, 0 ) )
				else:		# 无法正常获得熟练度
					canGainSle = labelGather.getText( "EntityResume:collectPoint", "cantGainSle" )
					canGainSleText = PL_Font.getSource( canGainSle, fc = ( 232, 100, 27 ) )
			text += reqPointText
			text += PL_NewLine.getSource()
			text += canGainSleText
			
		return text


instance = CollectPointResume()
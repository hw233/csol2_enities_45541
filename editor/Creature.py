# -*- coding: utf_8 -*-

# $Id: Creature.py,v 1.1 2008-04-30 04:13:06 phw Exp $


"""
"""
import NPCModelLoader

g_models = NPCModelLoader.instance

class Creature:
	def modelName( self, props ) :
		modelNumber = props["modelNumber"]
		if len( modelNumber ):
			models = g_models.getModelSources( modelNumber )
			if len( models ) == 1:
				return models[0]
			else:
				return "helpers/props/standin.model"
		else:
			return "helpers/props/standin.model"

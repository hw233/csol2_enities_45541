# -*- coding: utf-8 -*-


def getRanleMonster( self, entity, type, className ):
		monsters = entity.entitiesInRange( type )
		for m in monsters:
			if m.className  == className:
				return m
		
		return None


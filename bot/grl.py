# -*- coding: utf-8 -*-

import BigWorld
import Kuma

bot = Kuma.bots

def addMonster():		#Ìí¼ÓBOSS
	bot.getRoleList()
	bot.gmCmd("/clone 20714003")

def gossipW():			#¿ª¹Ö
	if bot.lstRoleList != []:
		entities = []
		b = bot.lstRoleList[0]
		for i in BigWorld.bots[b.id].entities.values():
			if i.__class__.__name__ == "Monster":
				entities.append(i)
		count = len(bot.lstRoleList)
		for i in xrange(count):
			bot.lstRoleList[i].cell.gossipWith(entities[i].id, "NPCStart.s1")
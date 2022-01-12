# -*- coding: gb18030 -*-

# �����˲����ô���

import BigWorld
import items
g_items = items.instance()

def createPetBattle():
	"""
	��Ҵ�����ս����
	"""
	lstIDs = [60201068, 60201069, 60201070, 60201071]
	lenIDs = len(lstIDs)
	no = 0
	for player in BigWorld.entities.values():
		if player.__class__.__name__ == "Role":
			# ���û�г�ս����
			if player.pcg_hasActPet() != True:
				player.setLevel(80)
				# ���û�г���
				if player.pcg_petDict.count() < 1:
					itemID = lstIDs[no % lenIDs]
					item = g_items.createDynamicItem(itemID, 1)
					player.addItem(item, 0)
					player.useItem(player.id, item.uid, player.id)
					no = no + 1
					def callBack():
						dbid = player.pcg_petDict.getDict().keys()[0]
						player.pcg_conjurePet(player.id, dbid)
				else:
					# �����ս
					dbid = player.pcg_petDict.getDict().keys()[0]
					player.pcg_conjurePet(player.id, dbid)

def setGrade(nGrade = 110):
	"""
	�������Ȩ��
	"""
	for player in BigWorld.entities.values():
		if player.__class__.__name__ == "Role":
			player.grade = nGrade
	
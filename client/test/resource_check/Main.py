# -*- coding: gb18030 -*-


from checkResource import *
from ResourcesConfig import MonsterConfig
from ResourcesConfig import MapConfig
from ResourcesConfig import GuiConfig
from ResourcesConfig import ParticleConfig
from ResourcesConfig import ItemConfig

configDict={
	"MonsterConfig":["entities/locale_default/config/server/gameObject/NPCMonster.xml","entities/locale_default/config/server/gameObject/NPCObject.xml"],  #"����NPC����" \
	"MapConfig":["entities/locale_default/config/server/gameObject/space",],   #"�ռ�����"      \
	"GuiConfig":["guis_v2","guis"],  #"GUI����"     \
	"ParticleConfig":["entities/locale_default/config/client/SkillEffect/ParticleConfig.py",],  #"��Ч����"      \
	#"������Ч����" : (BranchParticleConfig, "entities/locale_default/config/client/SkillEffect/BranchParticleConfig.py")\
	"ItemConfig":["entities/locale_default/config/item/ItemData",],  #"��Ʒ����"      \
}




def getAllConfigItem():
	"""
	"""
	resourceItems = {
						"model" : [],
						"map" : [],
						"gui" : [],
						"particle": [],
						"dds" : [],
						}
	MonsterIns = MonsterConfig(configDict["MonsterConfig"])
	MapIns = MapConfig(configDict["MapConfig"])
	GuiIns = GuiConfig(configDict["GuiConfig"])
	ParticleIns = ParticleConfig(configDict["ParticleConfig"])
	ItemIns = ItemConfig(configDict["ItemConfig"])
	inslist = [MonsterIns,MapIns,GuiIns,ItemIns,ParticleIns]
	for i in inslist:
		resourceItems["model"] = add(resourceItems["model"], i.getModel())
		resourceItems["map"] = add(resourceItems["map"], i.getMap())
		resourceItems["gui"] = add(resourceItems["gui"], i.getGui())
		resourceItems["particle"] = add(resourceItems["particle"], i.getParticle())
		resourceItems["dds"] = add(resourceItems["dds"], i.getDds())
	return resourceItems


		
def add(list1, list2):
	for item in list2:
		if item not in list1:
			list1.append(item)
	return list1

def copyDirs(sourceDir, targetDir):
    #sourceDir = "D:/AB/csgame/datas"
    #targetDir = "D:/new"  #windowsƽ̨����\\
    #����Ŀ¼�ṹ
    if "datas/" in sourceDir:
        relativepath = sourceDir.split("datas/")[1]
    elif sourceDir.endswith("datas"):
        relativepath = "../datas"
    for f in os.listdir(relativepath):
        sourceF = sourceDir + "/" + f
        targetF = targetDir + "/" + f
        #print sourceDir, targetDir, sourceF, targetF
        if os.path.isdir(PATH + "/" + sourceF):
            if not os.path.isdir(targetDir):
                os.makedirs(targetDir)
            if not os.path.isdir(targetF):
                os.makedirs(targetF)
            copyDirs(sourceF, targetF)

#def doCopy( resourcesItem = getAllConfigItem(), targetPath = None ):
	"""
	"""
	#for i in resourcesItem:
	#	i.copyTo( targetPath )
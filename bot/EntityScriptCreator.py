
g_filtter_out_entities = [ "Role", "Account" ]	# ��Ҫ���˵���entityType

import ResMgr

def create( path = r"entities/entities.xml" ):
	section = ResMgr.openSection( path )
	for entityType in section.keys():
		if entityType in g_filtter_out_entities:
			continue
		entityPath = "entities/bot/%s.py" % entityType
		fp = open(entityPath,"w")
	ResMgr.purge( path )
	
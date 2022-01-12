# -*- coding: gb18030 -*-

import Language
import csdefine

g_section = Language.openConfigSection( "config/hairs.xml" )

g_map_class2hairs = {
					csdefine.CLASS_FIGHTER	: 3,	#սʿ
					csdefine.CLASS_WARLOCK	: 4,	#��ʦ
					csdefine.CLASS_SWORDMAN	: 1,	#����
					csdefine.CLASS_ARCHER		: 2,	#����
					csdefine.CLASS_MAGE		: 5,	#��ʦ
					csdefine.CLASS_PRIEST		: 6,	#��ʦ
					}


def init( hairFile ):
	"""
	load hair form .xml
	"""
	global g_section
	if g_section is None:
		g_section = Language.openConfigSection( hairFile )

def getModelPath( hairID ):
	"""
	return hair model path, if not found, return the first model match with hair type
	"""
	isfemale = lambda val: bool(val >= 5)	# true if is female

	strhid = str(hairID)
	if g_section.has_key( strhid ):
		return g_section[strhid].asString

	# no that hair id, return first match type
	classID = strhid[0]
	gender = isfemale( int(strhid[1]) )
	for key in g_section.keys():
		if key[0] == classID and gender == isfemale( int(key[1]) ):
			return g_section[key].asString

def getStyles( classID, gender ):
	"""
	������ĳ��ְҵ���Ա���ص�����ͷ�������б�
	classID, gender must int
	"""
	#print "before:", classID, gender
	isfemale = lambda val: bool(val >= 5)	# true if is female
	gender = bool(gender)
	classID = g_map_class2hairs[classID & csdefine.RCMASK_CLASS]
	styles = []
	#print "after:", classID, gender
	for key in g_section.keys():
		#print classID, gender, key, int(key[0]), isfemale( int(key[1]) )
		#print type(classID), type(gender), type(key), int(key[0]), isfemale( int(key[1]) )
		if int(key[0]) == classID and gender == isfemale( int(key[1]) ):
			styles.append( key )
	#print styles
	return styles



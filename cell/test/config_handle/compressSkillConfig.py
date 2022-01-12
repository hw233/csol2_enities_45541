import binascii
import cPickle

HEAD_STRING = "Datas_"
ROOT_SKIL_ID_LEN = 6
ROOT_SKIL_ID_LEN01 = 7
SUB_SKILL_ID_LEN = 3



def compress( config, skillID ):
	"""
	"""
	if len(skillID ) != len(HEAD_STRING) + ROOT_SKIL_ID_LEN + SUB_SKILL_ID_LEN  and len(skillID ) !=  len(HEAD_STRING) + ROOT_SKIL_ID_LEN01 + SUB_SKILL_ID_LEN :
		return getattr( config, skillID )
	
	rootID = skillID[0: -3] + "001"
	
	if skillID == rootID:
		return getattr( config, skillID )
	
	skConfig = cPickle.loads( binascii.a2b_hex( getattr( config, skillID ) ))
	
	rootSkString = getattr( config, rootID, "" )
	if rootSkString != "":
		rootSkConfig = cPickle.loads( binascii.a2b_hex( rootSkString  ))
		for key in skConfig.keys():
			if skConfig[key] == rootSkConfig[key]:
				del skConfig[key]
	
	return binascii.b2a_hex( cPickle.dumps( skConfig , 2 ) ) 



def start( config, outFile ):
	f = open( outFile, "w" )
	for i in dir( config ):
		if HEAD_STRING in i:
			f.write( i +" = "+'"'+compress( config, i )+'"'+"\n" )
	f.close()



def makeUpSkillConfigDict( rarConfig, skillID ):
	
	skConfig = cPickle.loads( binascii.a2b_hex( getattr( rarConfig, skillID )))
	
	if len(skillID ) != len(HEAD_STRING) + ROOT_SKIL_ID_LEN + SUB_SKILL_ID_LEN  and len(skillID ) !=  len(HEAD_STRING) + ROOT_SKIL_ID_LEN01 + SUB_SKILL_ID_LEN :
		return skConfig
	
	
	
	rootID = skillID[0: -3] + "001"
	rootSkString = getattr( rarConfig, rootID, "" )
	if rootSkString == "":
		return skConfig
	rootSkConfig = cPickle.loads( binascii.a2b_hex( rootSkString  ))
	
	for key in rootSkConfig:
		if key in skConfig:
			continue
		skConfig[key] = rootSkConfig[key]
	return skConfig


def compare( config, rarConfig ):
	"""
	"""
	for i in dir(rarConfig):
		if HEAD_STRING in i:
			skillDict = makeUpSkillConfigDict( config, i )
			mskillDict = makeUpSkillConfigDict( rarConfig, i )
			assert  mskillDict == skillDict

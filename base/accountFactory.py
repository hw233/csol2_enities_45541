# -*- coding: gb18030 -*-


"""
������ʱ�ʺ���

սʿ	��
��ʦ	Ů
��ʿ	��
����	Ů
��ʦ	��
��ʦ	Ů

fengming_city
yanhuang_city
jiuli_city
"""

from bwdebug import *
import csdefine

m_accountParam = [
		[csdefine.JIULI 	| csdefine.CLASS_FIGHTER	| csdefine.GENDER_MALE, "jiuli", 		( 352.33, -32.91, -211.25 )],	# ���� ��ս
		[csdefine.JIULI		| csdefine.CLASS_WARLOCK	| csdefine.GENDER_FEMALE, "jiuli", 		( 352.33, -32.91, -211.25 )],	# ���� Ů��
		[csdefine.YANHUANG	| csdefine.CLASS_SWORDMAN	| csdefine.GENDER_MALE, "yanhuang", 	( 0, 0, 0 ) ],					# �׻� �н�
		[csdefine.YANHUANG	| csdefine.CLASS_ARCHER	| csdefine.GENDER_FEMALE, "yanhuang", 	( 0, 0, 0 ) ],					# �׻� Ů��
		[csdefine.FENGMING	| csdefine.CLASS_MAGE		| csdefine.GENDER_MALE, "fengming", 	( 723.14, 20.14, 441.00 )],		# ���� �з�
		[csdefine.FENGMING	| csdefine.CLASS_PRIEST	| csdefine.GENDER_FEMALE, "fengming", 	( 723.14, 20.14, 441.00 )],		# ���� Ů��
		]

def createAccount( accNamePrefix ):
        i = 1
	for e in m_accountParam:
		acc = accNamePrefix + "_%i" % (i)
		i = i + 1
		createAccountToDB( acc, *e )
		lmCommand = "INSERT INTO bigworldLogOnMapping values (\"%s\", \"\", 1, \"%s\")" % (acc, acc)
		BigWorld.executeRawDatabaseCommand( lmCommand )

def createAccountToDB( accName, raceclass, spaceName, position ):
	propDict = {}
	propDict["playerName"] = accName
	propDict["raceclass"] = raceclass
	propDict["spaceType"] = spaceName
	propDict["position"] = position
	INFO_MSG( "Create new account %s" % ( accName ) )
	entity = BigWorld.createBaseLocally( "Role", propDict )
	entity.writeToDB( writeToDBCallback )

def writeToDBCallback( isSuccess, entity ):
	INFO_MSG( "create account %s %s." % (str(isSuccess), entity.cellData["playerName"]) )
	if isSuccess:
		entity.destroy()	# close entity


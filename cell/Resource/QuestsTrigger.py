import csstatus


g_QuestsLevelUpTrigger = [ ( 11, 12345678 )
								]

MsgDict = {
			12345678: csstatus.ROLE_QUEST_108START_DIRECT
			}

def SendQuestMsg( player, questID ):
	"""
	"""
	player.statusMessage( MsgDict[questID] )
# -*- coding: utf-8 -*-
import csdefine
import HanleFunc as Func

from Monster import Monster

AT_DICT = {}

def MAP_PRESS( id, obj ):
	AT_DICT[ id ] = obj

def getHandle( task ):
	if AT_DICT.has_key( task.getType() ):
		return AT_DICT[ task.getType() ]()
		
class ATaskInterface( object ):
	ttype =  csdefine.QUEST_OBJECTIVE_NONE
	def __init__( self  ):
		AT_DICT( ttype, self )
	
	def do( self, etntity, task ):
		pass
	
	def stop( self, entity, task ):
		pass
	
	def getTarget( self ):
		return None
	
	def setComplete( self ):
		# 直接把目标完成
		pass

class ATaskTime( ATaskInterface ):
	type =  csdefine.QUEST_OBJECTIVE_TIME
	def __init__( self  ):
		ATaskInterface.__init__( self )
		
class ATaskKill( ATaskInterface ):
	ttype =  csdefine.QUEST_OBJECTIVE_KILL
	def __init__( self  ):
		ATaskInterface.__init__( self )
	
	def do( self, etntity, task ):
		# 开始任务战斗
		etntity.autoQuestFight()
	
	def stop( self, etntity, task ):
		# 停止任务战斗
		etntity.stopQuestFight()
	
	def getTarget( self, entity ):
		return Func.getRanleMonster( entity, Monster, self.str1 )

class ATaskKills( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_KILLS
	def __init__( self ):
		ATaskInterface.__init__( self )
		
	def do( self, etntity, task ):
		# 开始任务战斗
		etntity.autoQuestFight()
	
	def stop( self, etntity, task ):
		# 停止任务战斗
		etntity.stopQuestFight()

class ATaskKillRoleTypeMonster( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_KILL_ROLE_TYPE_MONSTER
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskKillDart( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_DART_KILL
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskDeliver( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_DELIVER
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskDeliverQuality( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskEventItemUsed( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskSkillLearned( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SKILL_LEARNED
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskLivingSkillLearned( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED
	def __init__( self ):
		ATaskInterface.__init__( self )
				
class ATaskEventTrigger( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER	
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskOwnPet( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_OWN_PET
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskTeam( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_TEAM
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskLevel( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_LEVEL
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskQuestNormal( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_QUEST_NORMAL
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskQuest( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_QUEST
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskDeliverPet( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_DELIVER_PET
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit_Quality( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit_Effect( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit_Level( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit_Binded( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit_Yinpiao( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskPetEvent( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_PET_EVENT
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskPetAct( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_PET_ACT
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskEvolution( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_EVOLUTION
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskImperialExamination( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskShowKaoGuan( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskKillWithPet( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_KILL_WITH_PET
	def __init__( self ):
		ATaskInterface.__init__( self )
		
class ATaskQuestion( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_QUESTION
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskTalk( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_TALK
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskHasBuff( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_HASBUFF
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskPotentialFinish( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskSubmit_LQEquip( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskEventSkillUsed( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskEventUpdateSetRevivePos( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS
	def __init__( self ):
		ATaskInterface.__init__( self )

class ATaskEnterSpace( ATaskInterface ):
	ttype = csdefine.QUEST_OBJECTIVE_ENTER_SPCACE
	def __init__( self ):
		ATaskInterface.__init__( self )



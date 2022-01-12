# -*- coding: gb18030 -*-

#CPU消耗统计

import csdefine
import time
from bwdebug import *
import Resource.AIData
g_npcaiActDatas = Resource.AIData.aiAction_instance()
g_npcaiCndDatas = Resource.AIData.aiConditon_instance()

CPU_CAL_START = True
CAL_SKILL_START = True
CAL_AI_START = True
CAL_AI_SC_START = True

SKILL_WARNING_COUNT 		= 10000
SKILL_WARNING_PER_CALL_COST = 350
SKILL_WARNING_PER_CALL_TIME_FOR_TEST = 1000


AI_WARNING_COUNT 		= 10000
AI_WARNING_COST_COUNT	= 1000
AI_WARNING_PER_CALL_COST = 1000
AI_WARNING_PER_CALL_TIME_FOR_TEST = 1000

AI_SCRIPT_WARNING_COUNT 		= 100000
AI_SCRIPT_WARNING_PER_CALL_COST = 300
AI_SCRIPT_WARNING_PER_CALL_TIME_FOR_TEST = 1000

def CPU_CostCal( cType, csubType,  param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
	"""
	搜集CPU消耗数据
	"""
	if not CPU_CAL_START:
		return

	g_calSubject[cType].do( csubType, param1, param2, param3, param4, param5 )


def printSkillCost( count = 0, singleCost = 0 ):
	"""
	"""
	for i in g_calSubject[csdefine.CPU_COST_SKILL].skillsCost:
		info = g_calSubject[csdefine.CPU_COST_SKILL].skillsCost[i]
		for j in info:			
			if info[j][0] > count and info[j][2] > singleCost:
				print i, j, info[j]

def printSepSkillCost( count = 0, singleCost = 0 ):
	"""
	"""
	sepSkillCost = g_calSubject[csdefine.CPU_COST_SKILL].sepSkillCost
	for skillID in sepSkillCost:
		for className in sepSkillCost[ skillID ]:
			info = sepSkillCost[ skillID ][ className ]
			for subType in info:
				if info[ subType ][ 0 ] > count and info[ subType ][ 2 ] > singleCost:
					print "%10s" % skillID, " %8s " % className, subType, info[ subType ]

def printAICost( count = 0, singleCost = 0 ):
	"""
	"""
	for i in g_calSubject[csdefine.CPU_COST_AI].aisCost:
		info = g_calSubject[csdefine.CPU_COST_AI].aisCost[i]
		for j in info:			
			if info[j][0] > count and info[j][2] > singleCost:
				print i, j, info[j]

def printAIScCost( type = 0, script = '', count = 0, singleCost = 0 ):
	"""
	type: 1 action, 2 condition
	action: scriptName, eg:AIAction10, AICnd82
	cout: call times
	"""
	format = '%-7s%-15s%-23s'
	print format % ( 'Type', 'Script', 'Times')
	print 45 * '-'
	for i in g_calSubject[csdefine.CPU_COST_AI_SC].aiScCost:
		if type and i != type:
			continue
		info = g_calSubject[csdefine.CPU_COST_AI_SC].aiScCost[i]
		for j in info:
			if j ==0:
				ERROR_MSG( " Type:%i, ai id is 0" % ( i )  )
				continue
			if info[j][0] > count and info[j][2] > singleCost:
				scriptName = getAIScriptName( i, j )
				if script and scriptName != script:
					continue
				print format % ( i, scriptName, info[j] )

def getAIScriptName(  type, id ):
	"""
	根绝AI类型和ID获得脚本名称
	"""
	scriptName = ""
	if type == csdefine.AI_ACTION:
		scriptName =  g_npcaiActDatas.__getitem__( id ).__name__
	if type == csdefine.AI_CONDITION:
		scriptName =  g_npcaiCndDatas.__getitem__( id ).__name__
	return scriptName

class costCal:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass
	
	def do( self, csubType, param1, param2, param3, param4, param5 ):
		"""
		"""
		pass



class skillCostCal:
	def __init__( self ):
		"""
		"""
		self.skillsCost = {}			# such as:{ skillID: ( totalCost, useCount, perCost ) }
		self.calType = csdefine.CPU_COST_SKILL
		self.saveInfo    = {}
		self.sepSkillCost = {}
		self.sepSkillInfo = {}

	def do(  self, csubType, skillID, className, param3, param4, param5 ):
		"""
		csubType: 消耗子类(检测技能、使用技能、技能到达)，eg: csdefine.CPU_COST_SKILL_USE
		如果传过来的className为空，则默认用8个0代替
		"""
		if not CAL_SKILL_START:
			return
		if className == "":
			className = '0' * 8
		curTime = time.time()
		self.doSkillCostStat( curTime, csubType, skillID, className, param3, param4, param5  )
		self.doSepSkillCostStat( curTime, csubType, skillID, className, param3, param4, param5 )

	def doSkillCostStat( self, curTime, csubType, skillID, param2, param3, param4, param5 ):
		"""
		技能消耗统计
		"""
		if csubType in self.saveInfo:
			if skillID == self.saveInfo[csubType][0]:
				self.saveInfo[csubType] = ( self.saveInfo[csubType][0], curTime - self.saveInfo[csubType][1] )
				self.recordSkillCost( csubType, self.saveInfo[csubType][0], self.saveInfo[csubType][1]  )
			del self.saveInfo[csubType]
		else:
			self.saveInfo[csubType] = ( skillID, curTime )

	def doSepSkillCostStat( self, curTime, csubType, skillID, className, param3, param4, param5 ):
		"""
		某个怪物使用某个技能的消耗 separate skill cost
		self.sepSkillInfo = {}
		"""
		if csubType in self.sepSkillInfo:
			if skillID in self.sepSkillInfo[csubType]:
				for item in self.sepSkillInfo[ csubType ][ skillID ]:
					if className == item[ 0 ]:
						subTime =  curTime - item[ 1 ]
						self.recordSepSkillCost( csubType, skillID, subTime, className  )
						self.sepSkillInfo[csubType][ skillID ].remove( item )
						return
				
				self.sepSkillInfo[csubType][ skillID ].append( (className, curTime ) )
			else:
				self.sepSkillInfo[csubType][ skillID ] = []
				self.sepSkillInfo[csubType][ skillID ].append( ( className, curTime ) )
		else:
			if csubType not in self.sepSkillInfo:
				self.sepSkillInfo[ csubType ] = {}
			if skillID not in self.sepSkillInfo[ csubType ]:
				self.sepSkillInfo[ csubType ][ skillID ] = []
			self.sepSkillInfo[csubType][ skillID ].append( ( className, curTime ) )

	def recordSkillCost( self, csubType, skillID, subTime ):
		"""
		记录总体技能消耗
		"""
		if subTime > 0.01:
			return
		if skillID not in self.skillsCost:
			self.skillsCost[skillID] = {}
		if csubType not in self.skillsCost[skillID]:
			self.skillsCost[skillID][csubType] = ( 0, 0, 0 )
		x,y,z = self.skillsCost[skillID][csubType]
		x += 1
		y = y + int( subTime * 1000000 )
		z = int( y/x  )
		self.skillsCost[skillID][csubType] = ( x, y, z )
		if x > SKILL_WARNING_COUNT and x%SKILL_WARNING_COUNT == 0:
			WARNING_MSG("skill(%i) subType(%i) be called more times(%i)!! perTime(%i)."%( skillID, csubType, x, z ) )
		if z > SKILL_WARNING_PER_CALL_COST and x > SKILL_WARNING_PER_CALL_TIME_FOR_TEST and x%SKILL_WARNING_COUNT == 0:
			WARNING_MSG("skill(%i) subType(%i) cost heavily(%i)!!"%( skillID, csubType, z ) )

	def recordSepSkillCost( self, csubType, skillID, subTime, className ):
		"""
		记录某个怪物的技能消耗
		如果怪物的className为空，则传过来的className为怪物ID，如果是系统技能，则传过来的className为8个0
		"""
		if subTime > 0.01:
			return
		
		if skillID not in self.sepSkillCost:
			self.sepSkillCost[skillID] = {}
		if className not in self.sepSkillCost[ skillID ]:
			self.sepSkillCost[ skillID ][ className ] = {}
		if csubType not in self.sepSkillCost[skillID][ className ]:
			self.sepSkillCost[skillID][className][csubType] = ( 0, 0, 0 )
		x,y,z = self.sepSkillCost[skillID][className][csubType]
		x += 1
		y = y + int( subTime * 1000000 )
		z = int( y/x  ) 
		self.sepSkillCost[skillID][className][csubType] = ( x, y, z )
		if x > SKILL_WARNING_COUNT and x%SKILL_WARNING_COUNT == 0:
			WARNING_MSG("ClassName or ID( %s ),skill(%i) subType(%i) be called more times(%i)!! perTime(%i)."%( className, skillID, csubType, x, z ) )
		if z > SKILL_WARNING_PER_CALL_COST and x > SKILL_WARNING_PER_CALL_TIME_FOR_TEST and x%SKILL_WARNING_COUNT == 0:
			WARNING_MSG("ClassName or ID( %s ), skill(%i) subType(%i) cost heavily(%i)!!"%( className, skillID, csubType, z ) )


class aiCostCal:
	def __init__( self ):
		"""
		"""
		self.aisCost = {}			# such as:{ skillID: ( totalCost, useCount, perCost ) }
		self.calType = csdefine.CPU_COST_AI
		self.saveInfo    = {}

	def record( self, csubType, className, subTime ):
		"""
		"""
		if subTime > 0.01:
			return
		if className not in self.aisCost:
			self.aisCost[className] = {}
		if csubType not in self.aisCost[className]:
			self.aisCost[className][csubType] = ( 0, 0, 0 )
		x,y,z = self.aisCost[className][csubType]
		x += 1
		y = y + int( subTime * 1000000 )
		z = int( y/x  )
		self.aisCost[className][csubType] = ( x, y, z )
		if x > AI_WARNING_COUNT and x%AI_WARNING_COUNT == 0:
			WARNING_MSG("Monster(%s)'s ai subType(%i) be called more times(%i)!! perTime(%i)"%( className, csubType, x, z ) )
		if z > AI_WARNING_PER_CALL_COST and x > AI_WARNING_PER_CALL_TIME_FOR_TEST and x%AI_WARNING_COST_COUNT == 0:
			WARNING_MSG("Monster(%s) ai subType(%i) cost heavily(%i)!!"%( className, csubType, z ) )

	def do(  self, csubType, param1, param2, param3, param4, param5 ):
		"""
		param1 : className
		"""
		if not CAL_AI_START:
			return
		curTime = time.time()
		if csubType in self.saveInfo:
			if param1 == self.saveInfo[csubType][0]:
				self.saveInfo[csubType] = ( self.saveInfo[csubType][0], curTime - self.saveInfo[csubType][1] )
				self.record( csubType, self.saveInfo[csubType][0], self.saveInfo[csubType][1]  )
			del self.saveInfo[csubType]
		else:
			self.saveInfo[csubType] = ( param1, curTime )

class aiScCostCal:
	"""
	AI使用频率统计
	"""
	def __init__( self ):
		"""
		"""
		self.aiScCost = {}		# such as:{ aiID: ( aiDataID, className ) }
		self.calType = csdefine.CPU_COST_AI_SC
		self.saveInfo = {}		# { type: useTimes }

	def record(  self, subType, aiID, subTime ):
		"""
		记录AI使用频率
		"""
		if subTime > 0.01:
			return
		if subType not in self.aiScCost:
			self.aiScCost[ subType ] = {}
		if aiID not in self.aiScCost[ subType ]:
			self.aiScCost[ subType ][ aiID ] = ( 0, 0, 0 )

		x,y,z = self.aiScCost[subType][aiID]
		x += 1
		y = y + int( subTime * 1000000 )
		z = int( y/x  )
		self.aiScCost[ subType ][ aiID ] = ( x, y , z )
		if x > AI_SCRIPT_WARNING_COUNT and x % AI_SCRIPT_WARNING_COUNT == 0:
			WARNING_MSG("AI(%s) has  ben called more times(%i)!! perTime(%i)"%( getAIScriptName( subType, aiID ), x, z ) )
		if z > AI_SCRIPT_WARNING_PER_CALL_COST and x > AI_SCRIPT_WARNING_PER_CALL_TIME_FOR_TEST and x % AI_SCRIPT_WARNING_PER_CALL_TIME_FOR_TEST == 0:
			WARNING_MSG("AI(%s) cost heavily(%i)!!"%(  getAIScriptName( subType, aiID ), z ) )

	def do(  self, subType, param1, param2, param3, param4, param5 ):
		"""
		subType: 1 AI动作；2 AI条件
		param1: aiID
		"""
		if not CAL_AI_SC_START:
			return
		curTime = time.time()
		if param1 in self.saveInfo:
			self.saveInfo[ param1 ] = curTime - self.saveInfo[ param1 ]
			self.record( subType, param1, self.saveInfo[param1] )
			del self.saveInfo[ param1 ]
		else:
			self.saveInfo[param1] = curTime

g_calSubject = {	csdefine.CPU_COST_SKILL: skillCostCal(),
					csdefine.CPU_COST_AI: aiCostCal(),
					csdefine.CPU_COST_AI_SC: aiScCostCal(),
					}
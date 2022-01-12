# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.6 2008-04-23 04:01:12 kebiao Exp $

"""
怪物NPC的类
"""

from NPCObject import NPCObject
from bwdebug import *
from NPCBaseAttrLoader import NPCBaseAttrLoader					# 怪物四项基础属性加载器
from MonsterIntensifyPropertyData import MonsterIntensifyPropertyData
from NPCExpLoader import NPCExpLoader								# 怪物经验加载器
import ItemTypeEnum
import csdefine
import csconst
import random
g_npcBaseAttr = NPCBaseAttrLoader.instance()
g_npcExp = NPCExpLoader.instance()
g_monsterIntensifyAttr = MonsterIntensifyPropertyData.instance()

class Monster(NPCObject):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )
		self.equips = {}						# 怪物的装备列表；key == order, value == itemID
		self.aiData	= {}						# 怪物的AI数据表
		self._expRate = 0.0						# 怪物经验比率的计算
		self.callList = []						# 呼叫同伴表 [npcid,...]
		self.attrAIDefLevel = 0					# 怪物的默认AI等级
		self.prestige = []						# 被杀死后主角可获得的声望值；[ (id, value), ...]; id == 势力索引，value == 增加的数量

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		NPCObject.onLoadEntityProperties_( self, section )

		# 性别、职业、种族、势力
		raceclass = 0
		#raceclass += section.readInt( "gender" )			# 暂时忽略此功能，全部默认为男，因为策划这部份暂时没用上
		raceclass |= section.readInt( "class" ) << 4
		raceclass |= section.readInt( "race" ) << 8
		raceclass |= section.readInt( "faction" ) << 12
		self.setEntityProperty( "raceclass", raceclass )
		self.setEntityProperty( "level", section.readInt( "level" ) )
		self._expRate = section.readFloat( "expRate" )
		self.setEntityProperty( "baseAtt", section.readFloat( "baseAtt" ) )

		# AI
		self.setEntityProperty( "petModelScale",			section.readFloat( "petModelScale" ) )			# 被捕捉为宠物后的模型缩放比例 2008-12-5 add by gjx
		#self.setEntityProperty( "attackSkill",				section.readInt("attackSkill") )				# 攻击技能，无此技能时为物理攻击
		if section.has_key( "walkPath" ):
			self.setEntityProperty( "walkPath",				eval(section.readString("walkPath")) )			# 巡逻路径
		if section.has_key( "initiativeRange" ):
			self.setEntityProperty( "initiativeRange",		section["initiativeRange"].asFloat )			# 主动攻击范围
		self.setEntityProperty( "range_base",				int( section["range_base"].asFloat * csconst.FLOAT_ZIP_PERCENT ) )					# 攻击距离基础值
		self.setEntityProperty( "viewRange",				section["viewRange"].asFloat )					# 视野范围（主动攻击范围）
		self.setEntityProperty( "territory",				section["territory"].asFloat )					# 领域范围（追击范围）
		if section.has_key( "petName" ):
			self.setEntityProperty( "petName",				section["petName"].asString )					# 宠物名字
		if section.has_key( "callRange" ):
			self.setEntityProperty( "callRange",			section["callRange"].asFloat )					# 呼叫同伴范围
		self.attrAIDefLevel = section.readInt("aiLevel")

		# 武器模型显示相关
		"""
		modelNumber = section.readString( "lefthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "lefthandNumber", modelNumber )

		modelNumber = section.readString( "righthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "righthandNumber", modelNumber )
		"""
		self._lefthandNumbers = []
		self._righthandNumbers = []
		if section.has_key( "lefthandNumber" ):
			self._lefthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["lefthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "righthandNumber" ):
			self._righthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["righthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "callList" ):
			for item in section[ "callList" ].values():
				self.callList.append( item.asString )

		# 记录最小、最大等级，创建时根据最小、最大等级随机产生
		self.minLv = section.readInt("minLv")
		self.maxLv = section.readInt("maxLv")
		
		self.petInbornSkills = []
		petInbornSkills = section.readString( "petInbornSkills" )
		if petInbornSkills != "":
			self.petInbornSkills = [int( skillID ) for skillID in petInbornSkills.split( ";" )]
			
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		NPCObject.load( self, section )
		self.mapPetID = section.readString( "petID" )
		self.takeLevel = section.readInt( "takeLevel" )
		# 加载声望配置
		if section["prestige"] is not None:
			for e in section["prestige"].readVector2s( "item" ):
				self.prestige.append( ( int( e[0] ), int( e[1] ) ) )		# 必须转成整数

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		pass

	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		创建一个NPC实体在地图上
		@param   spaceID: 地图ID号
		@type    spaceID: INT32
		@param  position: entity的出生位置
		@type   position: VECTOR3
		@param direction: entity的出生方向
		@type  direction: VECTOR3
		@param      param: 该参数默认值为None，传给实体的数据
		@type    	param: dict
		@return:          一个新的NPC Entity
		@rtype:           Entity
		"""
		if param is None:
			param = {}

		if param.has_key( 'level' ):
			param["level"] = min( param["level"], self.maxLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		# 注：所需要的g_npcExp属性当前还没移到common，详见cell/ObjectScripts/Monster.py，以后需要移到common中
		param["exp"] = g_npcExp.get( param["level"] ) * self._expRate
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		# 以职业和等级为参数，更新全局属性
		# 注：所需要的g_npcBaseAttr属性当前还没移到common，详见cell/ObjectScripts/Monster.py，以后需要移到common中
		param.update( g_npcBaseAttr.get( self.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS, param["level"] ) )
		return NPCObject.createEntity( self, spaceID, position, direction, param )

	def createBaseAnywhere( self, param = None, callback = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		@rtype						   : Entity
		@return						   : return a new entity
		"""
		if param is None:
			param = {}

		if param.has_key( 'level' ):
			param["level"] = min( param["level"], self.maxLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		# 注：所需要的g_npcExp属性当前还没移到common，详见cell/ObjectScripts/Monster.py，以后需要移到common中
		param["exp"] = g_npcExp.get( param["level"] ) * self._expRate
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		# 以职业和等级为参数，更新全局属性
		# 注：所需要的g_npcBaseAttr属性当前还没移到common，详见cell/ObjectScripts/Monster.py，以后需要移到common中
		param.update( g_npcBaseAttr.get( self.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS, param["level"] ) )
		NPCObject.createBaseAnywhere( self, param, callback )

	def createLocalBase( self, param = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		"""
		if param is None:
			param = {}

		if param.has_key( 'level' ):
			param["level"] = min( param["level"], self.maxLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		# 注：所需要的g_npcExp属性当前还没移到common，详见cell/ObjectScripts/Monster.py，以后需要移到common中
		param["exp"] = g_npcExp.get( param["level"] ) * self._expRate
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		# 以职业和等级为参数，更新全局属性
		# 注：所需要的g_npcBaseAttr属性当前还没移到common，详见cell/ObjectScripts/Monster.py，以后需要移到common中
		param.update( g_npcBaseAttr.get( self.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS, param["level"] ) )
		attrs = g_monsterIntensifyAttr.getAttrs( self.className, param["level"] )
		if attrs:
			param.update( attrs )
		return NPCObject.createLocalBase( self, param )

	def getInbornSkills( self ):
		"""
		获得此类monster所生成宠物的的天赋技能
		"""
		return self.petInbornSkills
		
# Monster.py

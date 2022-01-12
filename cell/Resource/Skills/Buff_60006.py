# -*- coding:gb18030 -*-

from SpellBase import *
from bwdebug import *
from Buff_Normal import Buff_Normal
import csdefine
from Function import newUID

class Buff_60006( Buff_Normal ):
	"""
	引爆，身体变大，身体变色（BUFF），该BUFF结束后，施放AOE爆炸技能
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# 变大的倍率
		self._p3 = 0		# AOE技能的伤害比例
		self._p4 = 0		# AOE技能的伤害范围
		self._p5 = 0		# AOE技能对自身造成的损伤比例
		self.NPCOldModelScale = 1.0	# 记录modelScale改变前的默认scale以便恢复
		
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] )		# 变大的倍率
		tempList2 = dict[ "Param2" ].split( ";" )
		self._p3 = float( tempList2[0] ) / 100		# AOE技能的伤害比例
		self._p4 = int( tempList2[1] )				# AOE技能的伤害范围
		self._p5 = float( int( tempList2[2] ) ) / 100	# AOE技能对自身造成的损伤比例
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		self.NPCOldModelScale = receiver.modelScale
		receiver.modelScale = self._p1
		receiver.addFlag( csdefine.ENTITY_FLAG_CHANG_COLOR_RED )
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		receiver.removeFlag( csdefine.ENTITY_FLAG_CHANG_COLOR_RED )
		receiver.modelScale = self.NPCOldModelScale
		entityList = receiver.entitiesInRangeExt( self._p4, None, receiver.position )
		entityCount = 10
		for entity in entityList:
			if receiver.queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
				damage = self.calcDotDamage( receiver, entity, csdefine.DAMAGE_TYPE_MAGIC, self._p3*entity.HP_Max )
				entity.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				entity.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
				entityCount -= 1
				if entityCount == 0:
					break
					
		# 对自身造成的伤害
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_MAGIC, self._p5*receiver.HP_Max )
		receiver.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
		receiver.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
		Buff_Normal.doEnd( self, receiver, buffData )
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self.NPCOldModelScale }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_60006()
		obj.__dict__.update( self.__dict__ )

		obj.NPCOldModelScale = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

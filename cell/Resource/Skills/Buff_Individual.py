# -*- coding: gb18030 -*-
"""
目前，我们的buff载入机制中存在如下问题： 

如果在Buff_1234脚本中存在如下代码： 
def doBegin( self, receiver, buffData ): 
   self.playerID = receiver.id 
那么，假如 
1）技能5687带有buff 1234 
1）向player1（id = 1）施法5678加载了buff 1234 
2）随后，又向player2（id = 2）也施法5678，因此也加载了buff 1234 

那么cell上player1.attrBuffs[buff 1234 idx]["skill"].playerID == player2.id

换言之，对于buff 1234而言，self.playerID是一种个性化数据（即它是和不同玩家相关的），而同一技能的buff 1234的实例全局只有一个，因此产生了数据覆盖的问题。

由于上述情况存在已久，大量代码采取了大体一致的处理措施，即在： 
doBegin( self, receiver, buffData )中人为复制自身。（参见buff:15003） 

所以处于稳定性考虑，针对问题描述中的情况，不对底层机制做任何修改。

但是，在doBegin()中复制自身的解决办法仍然有一个问题——大量代码中拥有大体雷同的addToDict/createFromDict，制作这个基类，就是为了解决
上述问题，并且简化包含有“玩家个性化数据”buff的实现。如果某个buff需要保存玩家个性化数据，请继承这个类。

使用概要：
1) 继承这个类
2) 根据需要在如下四个事件中初始化个性化数据：_onDoBegin， _onDoEnd, _onDoReload, _onDoLoop，初始化完毕之后，使用_packIndividualData（）将数据打包。
然后，一切个性化数据的迁移问题交给此类处理即可，子类中不需要做任何的额外处理。（一个使用此机制的例子是：Buff_Vehicle）

注意事项：
1）一旦继承了这个类，就不需要也不应该重载createFromDict/addToDict
2）只能在这四个方法：_onDoBegin， _onDoEnd, _onDoReload, _onDoLoop中使用_packIndividualData（）来打包数据，否则将引发断言错。
3）强烈建议只通过_packIndividualData（）来打包数据，否则将绕过安全检查。
4）_packIndividualData（）打包数据时需要一个键——值对，键的名字必须是此类实例中的属性名，否则引发断言错(这么做的原因请参考相应代码中的注释)。
5）个性化数据的值，由_packIndividualData（）打包时确定，换言之，一旦修改了任何个性化数据，就应该调用_packIndividualData（）对此数据进行打包，否则就会出现数据迁移后不一致的情况。
6）由于这是一整套机制，如果在cell上继承了这个类，那么，大多需要将数据传播到客户端的数情况下，也应该在client上继承相应的同名类。
7）不能在子类中不调用基类的receive，否则此机制失效。

2011-1-14 16:38
by mushuang
"""



import BigWorld
from bwdebug import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_Individual ( Buff_Normal ):
	"""
	玩家个体相关的buff，如果某个buff中需要保存一些针对每个玩家的个性化数据，那么请继承此buff
	不继承此buff且也不采取其他措施就直接处理玩家个性化数据会产生“单实例”问题，详见：CSOL-10239
	by mushuang
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._packedIndividualData = {}
		self.__canPackData = False # 此标志用来验证打包“不同玩家独立”数据的时机是否正确，在不正确的时机打包自己的数据同样无法避免“单实例”问题
		
	def _packIndividualData( self, key, val ):
		"""
		@addIndividualData:将每个玩家相关的数据打包
		@key: 此数据的在类实现中的实例名
		@val: 此数据的值
		"""
		# 确定是否应该在此时打包“不同玩家独立”数据，在不正确的时机打包自己的数据同样无法避免“单实例”问题
		assert self.__canPackData, "You can't pack individual data now!"
		
		# 不支持私有属性（__开头的属性），这种东西用会造成一些纠结的代码，但是保护属性（_开头的属性）是可以使用的
		assert not key.startswith( "__" ), "Private attribute is not supported!"
		
		# 此类的实例中必须包含以“key”为名的属性，否则就认为出错，这样的限制也许过于严厉，但是，严格限定有助于减少
		# bug，对于这一条如果不限定，容易造成代码数据名不一致，而额外增加代码的复杂度（比如一个属性在cell上叫_hp，在
		# client上却叫_healthPercent），所以考虑再三，我还是决定保留这条限定。
		assert hasattr( self, key ), "Attribute: %s must exist in this object"%key
		
		self._packedIndividualData[ key ] = val
		

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		# 因为先调用基类，所以receiver是ghost的情况，在基类中已经处理
		Buff_Normal.receive( self, caster, receiver )
		
		# 替换已经加载的buff数据的中的buff实例，这样来实现:每个玩家身上加载的是不同的buff实例
		buffData = receiver.findBuffByID( self.getID() )
		assert buffData, "Can't find buffData!"
		
		# 生成自身副本，从而保证加载在每个玩家身上的buff都是独立的
		buffData["skill"] = self.__clone()
		
	def _onDoBegin( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doBegin调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。
		"""
		pass
		
	def _onDoEnd( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doEnd调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。
		"""
		pass
	
	def _onDoLoop( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doLoop调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。
		"""
	
	def _onDoReload( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doReload调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。
		"""

	
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		# 由于在receive中克隆了自己，所以这个调用实际上发生在每个玩家各自的buff实例上
		
		Buff_Normal.doBegin( self, receiver, buffData )
		
		self.__canPackData = True
		self._onDoBegin( receiver, buffData )
		self.__canPackData = False
		
	
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		
		self.__canPackData = True
		self._onDoLoop( receiver, buffData )
		self.__canPackData = False
		
		return Buff_Normal.doLoop( self, receive, buffData )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		
		# doReload无需什么特殊处理，在buffReload时，从数据库中反序列化出来的对象已经是每个玩家不同的了
		# 参考：SkillTypeImpl.py
		
		self.__canPackData = True
		self._onDoReload( receiver, buffData )
		self.__canPackData = False
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		
		# 流程中在这里调用的已经是每个玩家身上不同的buff实例，所以不做任何特殊处理
		
		self.__canPackData = True
		self._onDoEnd( receiver, buffData )
		self.__canPackData = False
		
	def __clone( self ):
		"""
		克隆自身
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		return obj
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		
		
		注意:如果你继承了“Buff_Individual”类，一定不要覆盖这个方法。
		
		"""
		DEBUG_MSG( "Adding individual data to dict:%s"%str( { "param" : self._packedIndividualData } ) )
		return { "param" : self._packedIndividualData }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		注意:如果你继承了“Buff_Individual”类，一定不要覆盖这个方法。
		
		@type data: dict
		"""
		obj = self.__clone()
		
		obj._packedIndividualData = data[ "param" ]
		
		# 由于这个数据是下线保存的，所以当第一次应用此模块中的代码恢复时，必然是None，
		# （因为之前是通过Skill.addToDict中的默认机制保存的）， 不做处理就会在
		# _packIndividualData() 时出现异常。2011-1-25 10:01 by mushuang
		if obj._packedIndividualData is None:
			WARNING_MSG( "Deprecated data of \"param\" found, resetting _packedIndividualData to {}" )
			obj._packedIndividualData = {}
			
		DEBUG_MSG( "Restore individual Data to _packedIndividualData: %s"%data[ "param" ] )
		
		# 将打包运输的“不同玩家相关数据”正确设置到各个字段中去
		for key,val in self._packedIndividualData.iteritems():
			assert hasattr( obj, key ),"Can't find attribute: %s in this object!"%key
			setattr( obj, key, val )
		
		# _uid目前并没有使用，但是安全起见并且为了保证机制的完整性，还是按部就班地处理它。
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
	

	
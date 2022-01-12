# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.10 2008-07-23 03:14:04 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csdefine
import csconst
from bwdebug import *
from GameObject import GameObject
from Resource.PatrolMgr import PatrolMgr
g_patrolMgr = PatrolMgr.instance()

class Space( GameObject ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		GameObject.__init__( self )
		self._spaceConfigInfo = {}
		self._spaceType = csdefine.SPACE_TYPE_NORMAL

		# 是否由副本去计算pk值， 默认情况下由role->die接口计算。
		# 由于副本有很多不同的需求， 部分副本中pk不计算pk值， 有些副本只在特定的对手计算pk值， 因此
		# 有类似需求副本可以讲该标记设置为true或者在配置中配置一个标签"CalcPkValue"， 然后重载onRoleDie
		# 实现不同的需求.
		self.isSpaceCalcPkValue = False
		self.isDiffCampTeam = False							# 是否允许不同阵营的玩家组队
		self.canPk = False									# 是否允许pk
		self.canQieCuo = False								# 是否允许切磋
		self.isSpaceDesideDrop = False
		self.canArrest = False								# 此地图是否可以逮捕罪犯
		self.canFly = False									# 此地图是否可以飞行
		self.canVehicle = True								# 此地图是否可以召唤骑宠
		self.canConjureEidolon = True						# 此地图是否可以召唤小精灵
		self.deathDepth = 0									# 在此地图超出这个深度时将会死掉
		self.canGetAccum = 0								# 此地图杀怪是否可以获得气运值
		self.canConjurePet = True							# 此地图是否可以召唤宠物
		self.playerAoI = None								# 玩家视野范围(AoI)半径，如果是None，则不对AoI进行设置
		self.campHonourReward = False

		# 此地图的空间外接盒配置
		self.minBBox = ( 0, 0, 0 )
		self.maxBBox = ( 0, 0, 0 )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		GameObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "dirmapping", section["dirMapping"].asString )	# chunk 路径
		g_patrolMgr.loadUserString( section["dirMapping"].asString )
		self.setEntityProperty( "timeon", section["TimeOn"].asInt )
		if section.has_key( "SpaceType" ):
			self._spaceType = eval( "csdefine." + section["SpaceType"].asString )
		if section.has_key( "TimeOfDay" ):
			self._timeOfDay = section["TimeOfDay"].asInt
		if section.has_key( "DiffCampTeam" ):
			self.isDiffCampTeam = True
		if section.has_key( "CalcPkValue" ):
			self.isSpaceCalcPkValue = True
		if section.has_key( "CanPk" ):
			self.canPk = section["CanPk"].asInt
		if section.has_key( "SpaceDesideDrop" ):
			self.isSpaceDesideDrop = True
		if section.has_key( "canArrest" ):
			self.canArrest = True
		if section.has_key( "canFly" ):
			self.canFly = bool( section["canFly"].asInt )
		if section.has_key( "CanQieCuo" ):
			self.canQieCuo = section["CanQieCuo"].asInt
		if section.has_key( "canVehicle" ):
			self.canVehicle = bool( section["canVehicle"].asInt )
		if section.has_key( "canConjureEidolon" ):
			self.canConjureEidolon = section["canConjureEidolon"].asInt
		if section.has_key( "canGetAccum" ):
			self.canGetAccum = section["canGetAccum"].asInt
		if section.has_key( "canConjurePet" ):
			self.canConjurePet = section["canConjurePet"].asInt
		if section.has_key( "playerAoI" ) :
			self.playerAoI = section["playerAoI"].asFloat
		if section.has_key( "campHonourReward" ):
			self.campHonourReward = True

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		GameObject.load( self, section )

		spaceSec = section["Space"]

		# 获取Transport信息
		if spaceSec.has_key("Transport"):
			self._spaceConfigInfo[ "Transport" ] = {}
			dict = self._spaceConfigInfo[ "Transport" ]
			for objName, sect in spaceSec._Transport.items():
				dict = {"name" : sect.readString("Name")}
				dict["position"] = sect.readVector3("Pos")
				dict["radius"] = sect.readFloat("radius")
				dict["transportSign"] = sect.readInt64("Sign")
				dict["uid"] = 0

		#获取Door
		doormap = {}
		keys = spaceSec.keys()
		self._spaceConfigInfo[ "Doormap" ] = doormap

		try:
			KeySect = spaceSec.child(keys.index("Door"))
			for name, sect in KeySect.items():
				doordict = {"name" : sect.readString("Name")}
				doordict["position"] = sect.readVector3("Pos")
				doordict["radius"] = sect.readFloat("radius")
				doordict["destSpace"] = sect.readString("DestSpace")
				doordict["destPosition"] = sect.readVector3("DestPos")
				doordict["destDirection"] = sect.readVector3("DestDirection")
				doordict["modelNumber"] = sect.readString("modelNumber")
				doordict["modelScale"] = sect.readFloat("modelScale")
				doormap[name] = doordict
		except:
			pass

		# 如果空间中有外接盒配置，则初始化 by mushuang
		if spaceSec.has_key( "spaceBBoxMin" ) and spaceSec.has_key( "spaceBBoxMax" ):
			bboxMinStr = spaceSec[ "spaceBBoxMin" ].asString
			bboxMaxStr = spaceSec[ "spaceBBoxMax" ].asString

			minCoordAry = bboxMinStr.split( "," )
			maxCoordAry = bboxMaxStr.split( "," )
			assert len( minCoordAry ) == 3, "spaceBBoxMin is not in correct format( x,y,z required )"
			assert len( maxCoordAry ) == 3, "spaceBBoxMax is not in correct format( x,y,z required )"

			try:
				minBBox = ( float( minCoordAry[0] ), float( minCoordAry[1] ), float( minCoordAry[2] ) )
				maxBBox = ( float( maxCoordAry[0] ), float( maxCoordAry[1] ), float( maxCoordAry[2] ) )
			except:
				assert False, " Incorrect format of spaceBBoxMin/spaceBBoxMax, number needed! "

			assert minBBox[ 0 ] < maxBBox[ 0 ] and minBBox[ 1 ] <= maxBBox[ 1 ] and minBBox[ 2 ] < maxBBox[ 2 ], "Coordinate of spaceBBoxMin should be smaller than spaceBBoxMax's"

			self.minBBox = minBBox
			self.maxBBox = maxBBox

		# 读取死亡深度配置
		self.deathDepth = spaceSec.readFloat( "deathDepth", -100.0 )

	def getSpaceType( self ):
		return self._spaceType

	def getSpaceConfig( self ):
		"""
		"""
		return self._spaceConfigInfo

	def getTimeOfDay( self ):
		return self._timeOfDay

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		self._createDoor( selfEntity )
		self._createTransport( selfEntity )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		if self.campHonourReward and killer:
			role.camp_beKilled( killer )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		pass

	def onSpaceDestroy( self, selfEntity ):
		"""
		当space entity的onDestroy()方法被调用时触发此接口；
		在此我们可以处理一些事情，如把记录下来的玩家全部传送到指定位置等；
		"""
		pass

	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		"""
		#如果条件  packedDomainDataInTo 在写脚本时就应该对应上相关条件
		级别大月10，
		params = self.packedDataInTo( player )
		if params[ "level" ] < 10:
			return csstatus.SPACE_MISS_LEVELLACK
		在某队伍
		if not entity.getTeamMailbox():
			return csstatus.SPACE_MISS_NOTTEAM
		军团判断
		if not entity.corpsID:
			return csstatus.SPACE_MISS_NOTCORPS
		物品判断
		for name, bag in entity.kitbags.items():
			if bag.find2All( self.__itemName ):
				if self.val == self.__itemName:
					return csstatus.SPACE_OK
		return csstatus.SPACE_MISS_NOTITEM
		"""
		return csstatus.SPACE_OK

	def checkDomainLeaveEnable( self, entity ):
		"""
		在cell上检查该空间离开的条件
		例子：某场景在玩家没达到某目的时， 永远不允许离开， 比如监狱.
		"""
		return csstatus.SPACE_OK

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		gotoPlane = entity.queryTemp( "gotoPlane", False )
		if gotoPlane:
			return { "gotoPlane":gotoPlane }
		return {}

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		pickDict = {}
		pickDict[ "databaseID" ] = entity.databaseID
		pickDict[ "playerName" ] = entity.playerName
		return pickDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		pickDict = {}
		pickDict[ "databaseID" ] = entity.databaseID
		pickDict[ "playerName" ] = entity.playerName
		return pickDict

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		if self.playerAoI is not None:
			INFO_MSG("Set entity(ID:%i) AoI to %.1f on enter space %s." % ( baseMailbox.id, self.playerAoI, self.className ))
			BigWorld.entities[baseMailbox.id].setAoIRadius( self.playerAoI )			# 进入空间设置玩家的AoI

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		if self.playerAoI is not None:
			INFO_MSG("Recover entity(ID:%i) AoI to %.1f on leave space %s." % ( baseMailbox.id, csconst.ROLE_AOI_RADIUS, self.className ))
			player = BigWorld.entities.get( baseMailbox.id )
			if hasattr(player, "setAoIRadius"):							# 测试表明，如果客户端使用BigWorld.disconnect方法断开连接，到这里时player将没有setAoIRadius方法
				player.setAoIRadius( csconst.ROLE_AOI_RADIUS )			# 离开空间则恢复默认的AoI

	def _createTransport( self, selfEntity ):
		"""
		创建Transport
		"""
		print "Create createTransport..."
		configInfo = self.getSpaceConfig()
		if configInfo.has_key("Transport"):
			for projDict in configInfo[ "Transport" ]:
				BigWorld.createEntity("SpaceTransport", selfEntity.spaceID, projDict["position"], (0, 0, 0), projDict )

	def _createDoor( self, selfEntity ):
		"""
		创建Door
		"""
		print "Create createDoor..."
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "Doormap" ].iteritems():
			print "create Door ", name
			BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 0), otherDict )


	def onLeaveTeam( self, playerEntity ):
		"""
		队员离开队伍通知所在space的script
		"""
		pass

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		pass

	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		传送完毕，玩家已经进入空间
		"""

		if self.canFly:
			# 如果空间可以飞行，就开启和飞行相关的各种检测，否则关闭相关检测
			baseMailbox.client.enableFlyingRelatedDetection( self.minBBox, self.maxBBox )
		else:
			baseMailbox.client.disableFlyingRelatedDetection()


	def canUseSkill( self, playerEntity, skillID ):
		"""
		是否能够使用空间专属技能
		"""
		return False

	def requestInitSpaceSkill( self, playerEntity ):
		# 请求初始化副本技能
		pass

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		pass

	def copyTemplate_onMonsterDie( self, spaceBase, monsterID, monsterClassName, killerID ):
		"""
		新副本模板的怪物死亡通知
		"""
		pass

	def onEntitySpaceGone( self, entity ):
		"""
		called when the space this entity is in wants to shut down. 
		"""
		pass

# $Log: not supported by cvs2svn $
# Revision 1.9  2008/03/07 06:39:14  kebiao
# 添加巡逻相关功能
#
# Revision 1.8  2008/02/04 07:44:39  phw
# 修改了属性名称
#
# Revision 1.7  2007/12/15 11:27:37  huangyongwei
# onLoadEntityProperty 改为 onLoadEntityProperties
#
# Revision 1.6  2007/10/03 07:40:42  phw
# 代码整理
# method added:
#     _createTransport(), 来自SpaceNormal.py
#     _createDoor(), 来自SpaceNormal.py
#
# Revision 1.5  2007/09/29 06:55:37  phw
# method modified: onLoadEntityProperties_(), 修正"TimeOn"参数读取不正确的bug
#
# Revision 1.4  2007/09/29 06:52:01  phw
# method modified: onLoadEntityProperties_(), dirMapping -> dirmapping, TimeOn -> timeon，以修正space找不到地图数据的问题
#
# Revision 1.3  2007/09/29 05:59:34  phw
# 修改了“dirMapping”、“TimeOn”的读取位置，从原来的Load()转移到onLoadEntityProperties_()
# 增加了onSpaceDestroy()回调；
# 修改onEnter(), onLeave()的参数cellMailbox为baseMailbox
#
# Revision 1.2  2007/09/24 08:30:17  kebiao
# add:onTimer
#
# Revision 1.1  2007/09/22 09:09:19  kebiao
# space脚本基础类
#
#
#

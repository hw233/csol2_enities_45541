# -*- coding: gb18030 -*-

# For updating skill items when the target moves far away or close
# by ganjinxing 2010-11-09

import BigWorld
import event.EventCenter as ECenter
from Function import Functor
from AbstractTemplates import Singleton


class SKItemDetector( Singleton ) :

	def __init__( self ) :
		self.__currTarget = -1											# 当前目标的ID
		self.__triggers = {}

		self.__itemToDist = {}											# 格子到距离的映射
		self.__distToItem = {}											# 距离到格子的映射
		self.__distToTrap = {}											# 距离到陷阱的映射

		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		注册事件
		"""
		self.__triggers["EVT_ON_TARGET_BINDED"]			= self.__onTargetBinded		# 当改变选择目标时被触发
		self.__triggers["EVT_ON_TARGET_UNBINDED"]		= self.__onTargetUnbinded	# 当改变选择目标时被触发
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __onTargetBinded( self, target ) :
		"""
		事件触发选择目标
		"""
		self.updateTarget()
		for pyItem in self.__itemToDist.keys() :						# 因为外部可能会改变字典长度，所以不要用iterkeys
			pyItem.onDetectorTrigger()

	def __onTargetUnbinded( self, target ) :
		"""
		事件触发移除目标
		"""
		self.unbindTarget()
		for pyItem in self.__itemToDist.keys() :						# 因为外部可能会改变字典长度，所以不要用iterkeys
			pyItem.onDetectorTrigger()

	# -------------------------------------------------
	def __onTrapThrough( self, distInfo, trapEnts ) :
		"""
		某个陷阱触发
		"""
		trapData = self.__distToTrap.get( distInfo )
		if trapData is None : return									# 很诡异的情况，删了陷阱后依然有回调
		isEnter = BigWorld.player() in trapEnts
		if trapData[2] == isEnter : return								# 这里判断玩家是否穿越了陷阱
		trapData[2] = isEnter
		pyItems = self.__distToItem.get( distInfo, [] )
		for pyItem in list( pyItems ) :
			pyItem.onDetectorTrigger()									# 约定的更新方法

	def __createTrap( self, distInfo ) :
		"""
		创建某个距离段的陷阱
		"""
		player = BigWorld.player()
		if player is None or not player.isPlayer() : return None
		target = player.targetEntity
		if target is None or target is player : return None				# 如果当前没有目标或者目标是自己，则不创建
		trapData = self.__distToTrap.get( distInfo )
		if trapData : return trapData									# 如果距离段对应的陷阱已存在，则不再创建
		trapFunc = Functor( self.__onTrapThrough, distInfo )			# 回调函数，将距离加入以作识别
		skType, dist = distInfo											# 获取距离的长度和计算方式
		absoDist = DistCalcMap[ skType ]( player, target, dist )
		trapID = target.addTrapExt( absoDist, trapFunc )					# 创建陷阱
		trapData = [ trapID, trapFunc, None ]							# 保存距离和陷阱的映射（最后一个None是预留位）
		self.__distToTrap[ distInfo ] = trapData
		return trapData

	def __delTrap( self, trapID ) :
		"""
		删除ID为trapID的陷阱
		"""
		target = BigWorld.entities.get( self.__currTarget )				# 获取当前的目标
		if target is None : return
		target.delTrap( trapID )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		"""
		触发事件时调用
		"""
		self.__triggers[ evtMacro ]( *args )

	def unbindTarget( self ) :
		"""
		移除当前目标
		"""
		target = BigWorld.entities.get( self.__currTarget )				# 获取之前的目标
		if target :														# 如果之前的目标还在
			for trapData in self.__distToTrap.itervalues() :			# 则将之前加到其身上的陷阱移除
				target.delTrap( trapData[0] )
		self.__distToTrap = {}											# 清空距离到陷阱的映射
		self.__currTarget = -1

	def updateTarget( self ) :
		"""
		更新目标
		"""
		target = None
		player = BigWorld.player()
		if player and player.isPlayer() :
			target = player.targetEntity
		if target is None or target is player :							# 当前没有目标
			self.unbindTarget()
		elif target.id != self.__currTarget :							# 目标发生改变
			self.unbindTarget()
			self.__currTarget = target.id
			for distInfo in self.__distToItem.iterkeys() :				# 重新绑定一个目标后
				self.__createTrap( distInfo )							# 则在目标身上创建对应距离段的陷阱

	# -------------------------------------------------
	def bindPyItem( self, pyItem, distInfo ) :
		"""
		将一个技能格子绑定到侦测器
		@param		pyItem 		: 界面技能脚本实例
		@param		distInfo	: 更新距离: ( "COM", 5 ) 普通技能，攻击距离是5米；
											( "PET", 10 ) 宠物技能，攻击距离10米
		@type		distInfo	: tuple : ( dist, label )
		"""
		self.__createTrap( distInfo )									# 创建某个距离段的陷阱
		pyItems = self.__distToItem.get( distInfo )						# 查找该距离段的数据
		if pyItems is None :											# 如果还没有创建
			pyItems = set()												# 则创建一个新的
			self.__distToItem[ distInfo ] = pyItems
		pyItems.add( pyItem )											# 保存下新添加的格子

		distData = self.__itemToDist.get( pyItem )						# 搜索该格子对应的距离信息
		if distData is None :											# 如果还没有信息
			distData = set()											# 则新建一个
			self.__itemToDist[ pyItem ] = distData
		distData.add( distInfo )										# 将新的距离信息保存
		#print "-------->>> bind item count:", len( self.__itemToDist )

	def unbindPyItem( self, pyItem ) :
		"""
		将一个技能格子从侦测器移除
		@param		pyItem 		: 界面技能脚本实例
		"""
		distData = self.__itemToDist.get( pyItem )
		if distData is None : return									# 如果没有该格子对应的数据，则直接退出
		for distInfo in distData :
			pyItems = self.__distToItem.get( distInfo )					# 查找格子数据
			pyItems.remove( pyItem )									# 将该格子移除
			if len( pyItems ) : continue								# 如果该距离段还有其他格子，则继续
			trapData = self.__distToTrap.get( distInfo )				# 否则如果该距离段已没有格子，
			if trapData :
				self.__delTrap( trapData[0] )							# 则将陷阱移除
				del self.__distToTrap[ distInfo ]						# 将陷阱对应的距离段移除
			del self.__distToItem[ distInfo ]							# 将格子对应的距离信息移除
		del self.__itemToDist[ pyItem ]									# 将距离对应的格子数据移除
		#print "-------->>> leave item count:", len( self.__itemToDist )

	# -------------------------------------------------
	def clearDetector( self ) :
		"""
		清空探测器
		"""
		self.unbindTarget()
		self.__itemToDist = {}											# 格子到距离的映射
		self.__distToItem = {}											# 距离到格子的映射


SKIDetector = SKItemDetector()


#---------------------------------------------------------------------
# 技能攻击距离的计算方法
#---------------------------------------------------------------------
def calcDistInCommon( caster, target, dist ) :
	"""
	普通技能的攻击距离计算方法
	"""
	tDistBB = target.getBoundingBox().z / 2
	cDistBB = caster.getBoundingBox().z / 2
	return dist + tDistBB + cDistBB										# 攻击距离要算上模型偏差

def calcDistInPet( caster, target, dist ) :
	"""
	宠物技能的攻击距离计算方法
	"""
	return dist

# -----------------------------------------------------
DistCalcMap = {
	"COM" : calcDistInCommon,
	"PET" : calcDistInPet,
	}

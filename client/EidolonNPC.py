# -*- coding: gb18030 -*-

import BigWorld
import random
import csdefine
import csconst
import Define
import keys
import event.EventCenter as ECenter
from bwdebug import *
import weakref
from NPC import NPC
from Function import Functor
import skills
import GUIFacade
import InvoicesPackType
import Timer
from NavigateProxy import NavigateProxy
from PetNavigate import PetChaser

FOLLOW_BEHIND_DISTANCE			= 3	# 米，跟随在主人身边的距离
FOLLOW_DETECT_INTERVAL			= 0.5	# 秒，跟随侦测时间间隔

TIME_TO_GET_INVOICE = 1.0

def calFollowPosition( srcPosition, dstPosition, distance = FOLLOW_BEHIND_DISTANCE ):
	"""
	计算源位置与目标位置连线上离目标位置distance远的那个点

	@param dstPosition : 目标当前位置，Vector3
	rType : 与dstPosition路程为FOLLOW_BEHIND_DISTANCE米的position，Vector3
	计算出srcPosition到dstPosition的单位向量的反向量，然后乘模
	"""
	ppDistance = srcPosition.flatDistTo( dstPosition )
	if ppDistance < distance:
		return srcPosition
	return ( ( dstPosition - srcPosition ) / ppDistance ) * ( ppDistance - distance ) + srcPosition

def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	策划规则是：如果价钱小于1，就算1
	如果大于1，则取整
	"""
	if price < 1:
		return 1
	return int( price )


class EidolonChaser(PetChaser):

	def _getFollowPosition( self ):
		"""<Overriding method>
		获取追踪位置，小精灵是跟在玩家身后
		"""
		target = self._followTarget()
		if target:
			return self._formatPosition(target.position, target.yaw, -self._stayRange())
		else:
			return self._consigner.position

	def _addTimer( self ):
		"""<Overriding method>
		开始追踪后启动timer不停追踪目标
		"""
		self._cancelTimer()
		self._timer = Timer.addTimer( 0.5, 0.5, self._onTimer )

	def _onTimer( self ):
		"""<Overriding method>
		跟随timer回调
		"""
		# 由于客户端不保存小精灵的id，所以玩家速度改变时
		# 无法通过id查找小精灵并通知其速度改变，所以在每
		# 一个跟随timer回调时主动侦测速度改变
		self.updateSpeed(self._consigner.getSpeed())
		PetChaser._onTimer(self)


class EidolonNPC( NPC ) :
	"""
	小精灵NPC
	"""
	def __init__( self ) :
		"""
		"""
		NPC.__init__( self )
		self.navigator = None

		self.attrTrainInfo = {}
		self.currLearning = set()		# 记录当前正在学习的skillID

		self.invoiceIndexList = []
		self.__invoiceCount = 0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enterWorld( self ):
		"""
		"""
		NPC.enterWorld( self )
		if self.isOwnerClient():
			self.cell.clientReady()
			self.navigator = EidolonChaser(self, NavigateProxy(self))

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		"""
		player = BigWorld.player()
		if not self.isOwnerClient() and player.getLevel() <= csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL: # 其他客户端隐藏模型
			return
		NPC.createModel( self, event )

	def leaveWorld( self ) :
		"""
		离开世界时做点事
		"""
		NPC.leaveWorld( self )
		self.__invoiceCount = 0
		if self.isOwnerClient():	# 如果是主人的client，执行清理行为
			self.cancelFollow()
			BigWorld.player().onEidolonLeaveWorld()

	def onControlled( self, isControlled ):
		""""""
		INFO_MSG("Eidolon(%i) is controlled by client: %s"%(self.id, isControlled))
		if isControlled:
			self.initPhysics()
			self.initFollow()
		else:
			self.cancelFollow()

	def filterCreator( self ):
		"""
		template method.
		创建小精灵的filter模块
		"""
		return BigWorld.AvatarFilter()

	def initFollow( self ):
		"""
		初始化小精灵的跟随ai
		"""
		self.navigator.followEntity( BigWorld.player(), FOLLOW_BEHIND_DISTANCE, self.getSpeed() )

	def initPhysics( self ):
		# 只有controlledBy对象才能初始化physics，此时有可能客户端的controlledBy设置还未初始化完毕，就算此时初始化不成功，启动followCheck后检测没有physics会再次初始化
		try:
			self.physics = keys.SIMPLE_PHYSICS
			self.physics.fall = True
			self.physics.collide = False
		except AttributeError:
			TRACE_MSG( "Only controlled entities have a 'physics' attribute,maybe controlledBy hasnot init" )

	def cancelFollow( self ):
		"""
		"""
		self.stopMove()

	def standActionOff( self ):
		self.am.matchCaps = [8]

	def standActionOn( self ):
		self.am.matchCaps = [0]

	def isOwnerClient( self ):
		"""
		是否在主人的客户端
		"""
		return BigWorld.player().id == self.ownerID

	def stopMove( self ) :
		"""
		停止移动
		"""
		self.navigator.stop()

	def getSpeed( self ):
		return BigWorld.player().move_speed * ( 1.2 )	# 比玩家速度快一点，避免掉队

	def updateVelocity( self ) :
		"""
		更新跟随速度
		"""
		self.navigator.updateSpeed(self.getSpeed())

	def vipShareSwitch( self ):
		"""
		设置vip共享
		"""
		if self.isOwnerClient():
			self.cell.vipShareSwitch()

	def set_bornTime( self, oldValue ):
		"""
		获得小精灵出生时间后可算出小精灵离销毁还剩多少时间
		"""
		pass

	# --------------------------------------------------------------------------
	# 技能学习功能
	# --------------------------------------------------------------------------
	def receiveTrainInfos( self, skillIDs ):
		"""
		@param skillIDs: array of int64
		"""
		#self.attrTrainIDs = set( skillIDs )
		if len(self.attrTrainInfo) != 0:  #判断技能有没有加载过
			self.attrTrainInfo = {}
			self.getSkillAndShowWindow(skillIDs)
		else:
			self.loadSkillAndShowWindow(skillIDs)

	def getSkillAndShowWindow(self, skillIDs):
		for id  in skillIDs:
			spell = skills.getSkill( id )
			name = spell.getName()
			type = 0	# 暂时全为0
			level = spell.getReqLevel()
			cost = spell.getCost()
			self.attrTrainInfo[id] = [name, type, level, cost]

		self.filterIdle()
		GUIFacade.showLearnSkillWindow( self )

	def loadSkillAndShowWindow(self, skillIDs):
		onceLoadNum = 10 			#一次性加载技能数
		callTimer = 0.2 			#再次执行时间

		def onSectionGetSkill():
			getIDs = []
			if len(skillIDs) > onceLoadNum:
				getIDs = skillIDs[0:onceLoadNum]
			else:
				getIDs = skillIDs

			for id  in getIDs:
				skillIDs.pop(0)
				spell = skills.getSkill( id )
				name = spell.getName()
				type = 0	# 暂时全为0
				level = spell.getReqLevel()
				cost = spell.getCost()
				self.attrTrainInfo[id] = [name, type, level, cost]

			if len(skillIDs) > 0:
				BigWorld.callback( callTimer, onSectionGetSkill )
			else:
				self.filterIdle()
				GUIFacade.showLearnSkillWindow( self )

		onSectionGetSkill()

	def train( self, player, skillID ):
		"""
		@type skillID: INT16
		"""
		if skillID not in self.attrTrainInfo:
			#ERROR_MSG( "%i not exist." % skillID )
			player.statusMessage( csstatus.SKILL_NOT_HAVE, skillID )
			return
		self.currLearning.add( skillID )

		self.cell.trainPlayer( skillID )

	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		法术中断

		@type reason: INT
		"""
		NPC.NPC.spellInterrupted( self, skillID, reason )
		if skillID in self.currLearning:
			self.currLearning.discard( skillID )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		正式施放法术——该起施法动作了

		@type skillID: INT
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		try:
			NPC.NPC.castSpell( self, skillID, targetObject )
		except Exception, err:
			ERROR_MSG( err )
		if skillID in self.currLearning:
			self.currLearning.discard( skillID )
			GUIFacade.onSkillLearnt( skillID )

	def filterIdle( self ):
		"""
		过滤没有用的 （满级或者其他）
		"""
		skillIDs = []
		for s in self.attrTrainInfo:
			if skills.getSkill( s ).islearnMax( self ):
				skillIDs.append( s )
		for s in skillIDs:
			self.attrTrainInfo.pop( s )

	def getLearnSkillIDs( self ) :
		"""
		获取所有学习技能
		"""
		self.filterIdle()
		skillIDs = self.attrTrainInfo.keys()
		count = len( skillIDs )
		for i in xrange( 1, count ):
			for ii in xrange( i ):
				iskill = skills.getSkill( skillIDs[i] )
				iiskill = skills.getSkill( skillIDs[ii] )
				if iskill.getFirstReqLevel() < iiskill.getFirstReqLevel():
					tmp = skillIDs[i]
					skillIDs[i] = skillIDs[ii]
					skillIDs[ii] = tmp
		return skillIDs

	# --------------------------------------------------------------------------
	# 商人功能
	# --------------------------------------------------------------------------

	def addInvoiceCB( self, argUid, argInvoice ):
		"""
		增加一个商品

		@param  argUid: 该商品的唯一标识符
		@type   argUid: UINT16
		@param argInvoice: InvoiceDataType类型的商品实例
		@type  argInvoice: class instance
		"""
		item = argInvoice.getSrcItem()
		item.set( "price", priceCarry( item.getPrice() * self.invSellPercent ) )		# 计算新价格
		item.set( "invoiceType", argInvoice.getItemType() )								# 商品按使用对象分的类别（hyw--08.08.11）
		item.setAmount( argInvoice.getAmount() )
		argInvoice.uid = argUid														# 记录唯一标识
		#self.attrInvoices[argUid] = argInvoice
		GUIFacade.onInvoiceAdded( self.id, argInvoice )

		if argUid == self.__invoiceCount :											# 表示申请完毕（hyw--2008.06.16）
			self.__invoiceCount = 0

	def resetInvoices( self, space ):
		"""
		清除商品列表

		@param space: 商人的商品数量
		@type  space: INT8
		"""
		#self.attrInvoices.clear()
		GUIFacade.onResetInvoices( space )

	def onBuyArrayFromCB( self, state ):
		"""
		批量物品回收回调

		@param state: 回收状态，1 = 成功， 0 = 失败
		@type  state: UINT8
		@return: 无
		"""
		#INFO_MSG( "state = %i" % state )
		GUIFacade.onSellToNPCReply( state )

	def onInvoiceLengthReceive( self, length ):
		"""
		define method
		获得商品列表长度
		"""
		GUIFacade.setInvoiceAmount( length )
		self.invoiceIndexList = range( 1, length + 1, 1 )
		self.__invoiceCount = length						# 记下商品总数量（hyw -- 2008.09.16）
		if length == 0:
			return
		self.requestInvoice()

	def requestInvoice( self ):
		"""
		获得一批商品列表
		"""
		length = len( self.invoiceIndexList )
		if length > 0:
			self.cell.requestInvoice( self.invoiceIndexList[0] ) #请求一批商品列表， 暂时是 14个
		if length > 14:
			self.invoiceIndexList = self.invoiceIndexList[14:]
			BigWorld.callback( TIME_TO_GET_INVOICE, self.requestInvoice )
		else:
			self.invoiceIndexList = []

	def isRequesting( self ) :
		"""
		是否正在申请商品列表
		hyw -- 2008.09.16
		"""
		return self.__invoiceCount > 0
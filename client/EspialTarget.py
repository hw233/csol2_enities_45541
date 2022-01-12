# -*- coding: gb18030 -*-
#
# $Id: EspialTarget.py,v 1.00 2008/09/6 11:19:09 huangdong Exp $

import GUIFacade
import csdefine
import event.EventCenter as ECenter
import BigWorld
from ItemsFactory import ObjectItem as ItemInfo
import csstatus


class EspialTarget:
	"""
	观察对方的模块，主要完成请求数据和接受处理数据的任务
	"""
	_instance = None
	def __init__ ( self ):
		self.__assignmentData = [] #记录需要去cell取数据的任务
		self.target = None			#要观察的对象
		self.callback = 0			#记录请求数据的回调函数
		self.NowAssignment = 0		#当前在完成的任务
		self.getNumber = 0			#记录一次取的数量
		self.haveGetNumber = 0		#记录现在应该从哪取
		self.endEspial = False		#记录是否结束观察

	def onEspialTarget(self ,target ):
		"""
		观察对方
		@param   target: 对方玩家
		@type    target: ROLE
		from EspialTarget import espial
		espial.onEspialTarget(BigWorld.player())
		"""
		if target.__class__.__name__ != "Role":		# 在某些情况下 这里会进来其他类型的对象
			return
		BigWorld.cancelCallback( self.callback )
		self.target = target
		self.endEspial = False
		lenth = BigWorld.player().position.flatDistTo(target.position) #计算玩家与目标的距离
		if lenth > 10.0: #如果距离超过10米 提示距离过远 不能查看
			BigWorld.player().statusMessage( csstatus.ESPIAL_TARGET_TOOFAR )
			return
		BigWorld.player().targetItems = [] #清空要观察的对象的装备列表 以便从服务器重新获取
		BigWorld.player().espial_id = target.id	#记录观察的对方的ID
		self.SetAssignment(0, 4)	#开始设定要去服务器取的任务,1次取4个
		self.NowAssignment = 0		#当前在完成的任务索引
		self.__assignmentData = [  #记录需要取的数据
					 "property",
					 "equip",	#获取装备 一次4个
					]
		ECenter.fireEvent( "EVT_ON_SHOW_TARGET", target )		#发送消息 让界面去显示UI(此时UI没有数据 只有空的界面)
		self.showTargetModel(target)	#显示对方人物的模型(由于人物模型不用通过服务器获取，所以直接显示)
		self.getInfos()					#向服务器请求需要的对方玩家的信息

	def SetAssignment( self ,beginPos, OnceNumber ):
		"""
		初试化取任务的相关数据，记录取的开始位置和数量，以便分多次去获取数据，避免一次请求过多数据 造成网络阻塞
		@param   beginPos: 开始取的位置(比如取人物的装备，从装备的LIST中多少索引开始取)
		@type    beginPos: INT
		@param   OnceNumber: 取的数量(比如取人物的装备，从装备的LIST中取多少个)
		@type    OnceNumber: INT
		"""
		self.BeginPos = beginPos
		self.getNumber = OnceNumber

	def SetNextAssignment(self ,beginPos, OnceNumber ):
		"""
		开始下次任务时,设定取的开始位置和数量
		@param   beginPos: 开始取的位置(比如取人物的装备，从装备的LIST中多少索引开始取)
		@type    beginPos: INT
		@param   OnceNumber: 取的数量(比如取人物的装备，从装备的LIST中取多少个)
		@type    OnceNumber: INT
		"""
		self.SetAssignment( beginPos, OnceNumber )	#重新设置取的位置和数量
		self.NowAssignment += 1						#任务记数加1 表示开始__assignmentData列表中的下个任务

	def getInfos(self ):
		"""
		获取数据的回调函数，每0.2秒获取一部分对方玩家的信息 避免网络堵塞
		如果需要加入新的任务 还得修改此函数 加入新的任务分支
		"""
		try:
			assignment = self.__assignmentData[self.NowAssignment]		#获取当前的任务
		except IndexError:	#如果已经超出了任务列表表示已经无任务 那么 不再回调
			return
		if self.endEspial:	#如果强制结束,那么停止获取。
			return
		if assignment == "property":	#这里分别判断任务而调用不同的请求函数 这里是获取对方属性
			BigWorld.player().cell.getTargetAttribute(self.target.id) #获取对方的属性信息
			self.SetNextAssignment(0, 4 )#开始获取下一次任务 因为属性是一次获取
		elif assignment == "equip":		 #获取对方装备
			if	self.BeginPos > 15:		 #如果已经试图获取的装备数量 超过15个 那么停止获取 防止后面没有接收到发送完毕的消息 而进入死循环
				return
			BigWorld.player().cell.getTargetEquip(self.target.id,self.BeginPos,self.getNumber)	#获取对方的装备信息
			self.SetAssignment(self.getNumber + self.BeginPos, 4)								#开始获取下一次
		else:
			return
		self.callback = BigWorld.callback( 0.2, self.getInfos ) 	#继续获取

	def showTargetEquip(self , items, ifEnd):
		"""
		显示玩家的装备
		@param   items: 对方装备的列表（一次获取的装备，这里一次是4个）
		@type    items: List
		@param   ifEnd: 记录是否已经取完
		@type    ifEnd: BOOL
		"""
		if  ifEnd:	#如果取完了，那么 开始下个任务
			self.SetNextAssignment(0, 0)
		itemInfos = []
		for item in items:	#分多次向UI发送装备数据
			BigWorld.player().targetItems.append( item )
			itemsInfo = ItemInfo( item ) #包装一次装备
			itemInfos.append(itemsInfo)	 #加入数据列表
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_EQUIP", ( itemInfos ) ) #通知界面 只通知一次比分多次通知跟节约性能

	def showTargetOtherInfo(self ,otherInfo):
		"""
		显示玩家的帮会 职位 等级 性别......
		@param   otherInfo: 对方的玩家的帮会 职位 等级 性别......数据
		@type    otherInfo: dictionary
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_TFINFO", (otherInfo) )	#显示玩家其他属性

	def showTargetModel(self, target):
		"""
		显示对方玩家的模型
		@param   target: 对方玩家的实体
		@type    target: PLAYERROLE
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_SHWO_TARGET_MODEL", target )	#显示玩家的模型

	def stopEspial( self ):
		"""
		停止观察对方，通常是在玩家跑出自己的AOI返回后触发。
		观察界面关闭时也会触发。
		"""
		BigWorld.cancelCallback( self.callback )
		BigWorld.player().espial_id = 0
		self.endEspial = True		# 设置强制结束获取数据的标志
		ECenter.fireEvent( "EVT_ON_END_SHOW_TARGET" )

	@staticmethod
	def instance():
		"""
		获取模块的实例
		"""
		if EspialTarget._instance is None:
			EspialTarget._instance = EspialTarget()
		return EspialTarget._instance

def instance():
	return EspialTarget.instance()

espial = EspialTarget.instance()
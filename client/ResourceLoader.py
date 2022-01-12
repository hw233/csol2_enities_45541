# -*- coding: gb18030 -*-
#
# $Id: ResourceLoader.py,v 1.30 2008-09-03 01:40:09 huangyongwei Exp $

"""
implement resource loading class

2008/01/15: writen by huangyongwei
2008/07.24: refactored( 重构 ) by huangyongwei
"""

# --------------------------------------------------------------------
# 实现思想：
# 资源的加载宏观上分为三大模块：
# ① 启动游戏需要加载的资源
#    这部分暂时是“单程”的，也就是一次性加载，因此加载进度并不会表现在进度条中
# ② 登录时需要加载的资源
#    这部分实际上并没有显式地加载资源，仅仅是对角色选择的场景的加载进行进度侦测
# ③ 进入游戏时需要加载的资源
#    这个部分比较广，目前大体加载进度分为：
#		 角色相关的一些配置的加载			↓
#		 界面加载							↓
#		 角色登录							↓
#		 角色属性申请（向服务器申请）		↓
#		 一些状态的初始化
# ④ 角色跳转加载
#    这部分其实紧紧是对跳转后的场景加载进度进行侦测
#
# -------------------------------------------
# 以上的分步加载分别摊分到四个函数对象中，实现各自管理虽然有些加载比较简单，
# 如启动游戏的资源加载，和跳转加载，但为了更加模块化，以便日后更加容易修改
# 和管理，因此还是将其实现细节与 ResourceLoader 分离。
# 况且在资源加载并非在整个游戏过程中时刻运行，所以其对性能并非极其苛刻。
#
# --------------------------------------------------------------------

import time
import BigWorld
import csol
import csdefine
import Define
import event.EventCenter as ECenter
from bwdebug import *
from AbstractTemplates import Singleton
from AbstractTemplates import AbstractClass
from Function import Functor
from gbref import rds
from navigate import NavDataMgr

# ---------------------------------
# 需要初始化的模块
# ---------------------------------
from PetFormulas import formulas as petFormulas
from guis.UIFactory import uiFactory
from guis.UISounder import uiSounder


_g_out_loadingInfo = False								# 是否输出加载进度相信信息

_g_loadSceneLimitSec	= 1.0							# 同一场景跳转时的最短时间限制，延时用，解决只有几个chunk的insideChunk小地图
														# 刷的一声就进入了游戏，加载线程处理的碰撞信息没有加载导致怪物掉下去的问题。

# --------------------------------------------------------------------
# implement resource wrapper for game start
# --------------------------------------------------------------------
class _Wrapper :
	def __init__( self, inst, methodName, *param ) :
		self.__inst = inst
		self.__methodName = methodName
		self.__param = param

	def __call__( self ) :
		method = getattr( self.__inst, self.__methodName )
		if _g_out_loadingInfo :
			INFO_MSG( "calling function/method: %s..." % str( method ) )
		method( *self.__param  )


# --------------------------------------------------------------------
# implement loader's base class
# --------------------------------------------------------------------
class _BaseLoader( AbstractClass ) :
	__abstract_methods = set()

	def run( self ) :
		csol.swapWorkingSet()					# 加载资源前前调用一次 csol.swapWorkingSet，释放一些物理内存。

	def cancel( self ) :
		pass

	__abstract_methods.add( run )
	__abstract_methods.add( cancel )


# --------------------------------------------------------------------
# implement game start resource loader
# --------------------------------------------------------------------
class _StartLoader( _BaseLoader ) :
	"""
	并没有放到初始化进度条中，因此加载下面的资源时（游戏刚刚启动时），进度条会卡一下
	"""
	def run( self ) :
		rds.wordsProfanity.initialize()						# 加载词汇过滤表，配置文件路径放在模块中
		uiSounder.initialize()								# 初始化 UI 声音

		roots = uiFactory.getCommonRoots()					# 常规 UI
		roots += uiFactory.getLoginRoots()					# 登录用的 UI
		for root in roots :
			uiFactory.createRoot( *root )					# 创建常规 UI 和登录 UI
		uiFactory.createTempRoots()							# 创建临时的工具 UI

	def cancel( self ) :
		"""
		没有用 callback 加载，因此 cancel 没意义
		"""
		pass


# --------------------------------------------------------------------
# implement login loader
# --------------------------------------------------------------------
class _LoginLoader( _BaseLoader ) :
	def __init__( self ) :
		self.__callback = None
		self.__cbid = 0
		self.__detectors = []
		self.__totalProgress = 0.0
		self.__currDetector = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __startDetect( self, callback ) :
		"""
		侦测旧的场景是否已经清掉（加载进度小于 0.2 时才真正开始新的场景加载）
		"""
		progress = BigWorld.spaceLoadStatus()
		if progress < 0.2 :
			callback( 1.0 )
			return
		loginMgr = __import__( "LoginMgr" )
		if loginMgr.loginSpaceMgr.getSpaceByType( ) != 0:
			callback( 1.0 )
			return
		callback( 0.0 )
		func = Functor( self.__startDetect, callback )
		self.__cbid = BigWorld.callback( 0.01, func )

	def __sceneDetect( self, callback ) :
		"""
		角色场景加载侦测
		"""
		progress = BigWorld.spaceLoadStatus()
		if progress >= 1.0 :
			callback( 1.0 )
		else :															# 如果场景还没加载完毕
			callback( progress )										# 则，直接通知进度
			func = Functor( self.__sceneDetect, callback )
			self.__cbid = BigWorld.callback( 0.01, func )				# 并且进入下一个 tick

	# ---------------------------------------
	def __callInitializer( self, initializers, totalCount, callback, progress ) :
		"""
		分别调用各个角色加载器
		"""
		oneProgress = float( progress ) / totalCount						# 当前初始化返回的进度
		leaveCount = len( initializers )									# 剩余的初始化器个数
		passCount = totalCount - leaveCount									# 已经调用完的初始化器个数
		passProgress = float( passCount - 1 ) / totalCount + oneProgress	# 已经加载完的进度
		callback( passProgress )
		if progress >= 1 and leaveCount :
			initer = initializers.pop( 0 )
			func = Functor( self.__callInitializer, initializers, totalCount, callback )
			self.__cbid = BigWorld.callback( 0.01, Functor( initer, func ) )

	def __callInitializers( self, initializers, callback ) :
		"""
		按顺序调用角色创建/角色选择的加载器
		"""
		count = len( initializers )
		func = Functor( self.__callInitializer, initializers, count, callback )
		initializers.pop( 0 )( func )

	def __initRoleSelector( self, callback ) :
		"""
		初始化角色选择
		"""
		self.__callInitializers( rds.roleSelector.getInitializers(), callback )

	# -------------------------------------------------
	def __detecte( self ) :
		"""
		判断是否真正进入场景加载（因为有可能前一次场景还没销毁）
		"""
		def callback( progress ) :
			pieceProgress = progress * self.__currDetector[0]
			totalProgress = self.__totalProgress + pieceProgress
			self.__callback( totalProgress )
			if progress >= 1.0 :
				self.__totalProgress += self.__currDetector[0]
				if len( self.__detectors ) :
					self.__detecte()

		if len( self.__detectors ) :
			self.__currDetector = self.__detectors.pop( 0 )
			self.__currDetector[1]( callback )
		else :
			self.__callback( 1.0 )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def run( self, callback ) :
		_BaseLoader.run( self )
		self.__detectors = [
			( 0.1, self.__startDetect ),						# 侦测什么时候开始场景加载
			( 0.1, self.__sceneDetect ),						# 侦测什么时候场景加载完毕
			( 0.8, self.__initRoleSelector ),					# 初始化角色选择
			]													# 第一维是各自占用的百分比，加总必需为 1.0
		self.__callback = callback
		self.__totalProgress = 0.0
		self.__detecte()

	def cancel( self ) :
		"""
		取消当前加载侦测
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None

# --------------------------------------------------------------------
# implement creator loader
# --------------------------------------------------------------------
class _CreatorLoader( _BaseLoader ) :
	def __init__( self ) :
		self.__callback = None
		self.__cbid = 0
		self.__detectors = []
		self.__totalProgress = 0.0
		self.__currDetector = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __sceneDetect( self, callback ) :
		"""
		角色场景加载侦测
		"""
		progress = BigWorld.spaceLoadStatus()
		if progress >= 1.0 :
			callback( 1.0 )
		else :															# 如果场景还没加载完毕
			callback( progress )										# 则，直接通知进度
			func = Functor( self.__sceneDetect, callback )
			self.__cbid = BigWorld.callback( 0.01, func )				# 并且进入下一个 tick

	# ---------------------------------------
	def __callInitializer( self, initializers, totalCount, callback, progress ) :
		"""
		分别调用各个角色加载器
		"""
		oneProgress = float( progress ) / totalCount						# 当前初始化返回的进度
		leaveCount = len( initializers )									# 剩余的初始化器个数
		passCount = totalCount - leaveCount									# 已经调用完的初始化器个数
		passProgress = float( passCount - 1 ) / totalCount + oneProgress	# 已经加载完的进度
		callback( passProgress )
		if progress >= 1 and leaveCount :
			initer = initializers.pop( 0 )
			func = Functor( self.__callInitializer, initializers, totalCount, callback )
			self.__cbid = BigWorld.callback( 0.01, Functor( initer, func ) )

	def __callInitializers( self, initializers, callback ) :
		"""
		按顺序调用角色创建/角色选择的加载器
		"""
		count = len( initializers )
		func = Functor( self.__callInitializer, initializers, count, callback )
		initializers.pop( 0 )( func )


	def __initRoleCreator( self, callback ) :
		"""
		初始化角色创建地图摄像机
		"""
		self.__callInitializers( [ rds.roleCreator.preLoadSomething ], callback )

	def __initRoleEntity( self, callback ) :
		"""
		初始化地图8个角色实体
		"""
		self.__callInitializers( [ rds.roleCreator.initRoleEntity ], callback )
		
	
	def __checkRoleCreate( self, callback ):
		self.__callInitializers( [ rds.roleCreator.checkRoleCreate ], callback )

	# -------------------------------------------------
	def __detecte( self ) :
		"""
		判断是否真正进入场景加载（因为有可能前一次场景还没销毁）
		"""
		def callback( progress ) :
			pieceProgress = progress * self.__currDetector[0]
			totalProgress = self.__totalProgress + pieceProgress
			self.__callback( totalProgress )
			if progress >= 1.0 :
				self.__totalProgress += self.__currDetector[0]
				if len( self.__detectors ) :
					self.__detecte()

		if len( self.__detectors ) :
			self.__currDetector = self.__detectors.pop( 0 )
			self.__currDetector[1]( callback )
		else :
			self.__callback( 1.0 )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def run( self, callback ) :
		_BaseLoader.run( self )
		self.__detectors = [
			( 0.1, self.__sceneDetect ),	# 侦测什么时候场景加载完毕
			( 0.3, self.__initRoleCreator ),# 初始化角色创建地图摄像机
			( 0.4, self.__initRoleEntity ),# 初始化地图8个角色实体
			( 0.2, self.__checkRoleCreate ) #检测8个角色是否加载完毕
			]													# 第一维是各自占用的百分比，加总必需为 1.0
		self.__callback = callback
		self.__totalProgress = 0.0
		self.__detecte()

	def cancel( self ) :
		"""
		取消当前加载侦测
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None

# --------------------------------------------------------------------
# implement world resource loader
# --------------------------------------------------------------------
class _WorldLoader( _BaseLoader ) :
	# ----------------------------------------------------------------
	# 加载函数封装器
	# ----------------------------------------------------------------
	class _LWrapper :
		def __init__( self, loader, percent ) :
			self.__loader = loader							# 加载函数

			self.finished = False							# 是否已经丢弃（下次加载时不再需要加载）
			self.percent = percent							# 占用的加载进度

		def __call__( self ) :
			self.__loader( self, self.percent )

	# ----------------------------------------------------------------
	# _WorldLoader
	# ----------------------------------------------------------------
	def __init__( self ) :
		self.__resWrapps = []											# 资源加载包装器
		self.__uis = uiFactory.getWorldRoots()							# enterword 时要加载的 ui
		self.__playerInitTypes = []										# 角色要初始化的属性类型
		self.__startLoadSceneTime = 0

		# -----------------------------------
		# 加载函数（下面存在交叉引用，但因为 Loader 需要常驻内存，因此不重要）
		self.__loaders = [
			_WorldLoader._LWrapper( self.__loadResources, 0.01 ),		# 加载配置资源
			_WorldLoader._LWrapper( self.__loadUIs, 0.29 ),				# 加载 UI
			_WorldLoader._LWrapper( self.__loadPixieDatas, 0.1 ),		# 加载随身精灵对话数据
			_WorldLoader._LWrapper( self.__requestEnterWorld, 0.1 ),	# 登录
			_WorldLoader._LWrapper( self.__loadScene, 0.50 ),			# 场景侦测和角色属性资源请求
			]
		assert sum( [r.percent for r in self.__loaders] ) == 1.0, \
			"total progress must be 100%"								# 总进度值必须为 100％

		# -----------------------------------
		self.__callback = None											# 实时进度回调函数
		self.__cbid = 0													# callback ID
		self.__uiControlId = 0

		self.__isInWorld = False										# 角色是否已经进入世界
		self.__currProgress = 0											# 当前加载进度
		self.__abandonProgress = 0										# 加载完毕的进度分配值


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __abandonFinishedLoaders( self ) :
		"""
		丢弃只需加载一次，并且已经加载完毕的加载函数
		"""
		count = len( self.__loaders )
		for idx in xrange( count - 1, -1, -1 ) :						# 循环所有加载函数
			wrapper = self.__loaders[idx]
			if wrapper.finished :										# 如果加载函数加载完毕
				self.__loaders.remove( wrapper )						# 则从列表中清除之
				self.__abandonProgress += wrapper.percent				# 并增加丢弃的进度值

	def __nextLoading( self ) :
		"""
		进入下一个加载
		"""
		if len( self.__tmpLoaders ) == 0 :								# 如果没有加载函数
			if self.__currProgress < 1.0 :								# 如果加载完毕但进度不足 100％
				self.__callback( 1.0 )									# 则强制为 100％
			self.__abandonFinishedLoaders()								# 丢弃只需加载一次，并且已经加载完毕的加载函数
			self.__callback = None										# 则清除对 callback 的引用
			del self.__tmpLoaders
		else :															# 否则
			self.__tmpLoaders.pop( 0 )()								# 弹出一个加载函数

	def __notify( self, progress ) :
		"""
		回调加载进度
		"""
		progress /= ( 1.0 - self.__abandonProgress )					# 因为不存在全部进度被丢弃，因此不作除零检查
		self.__callback( progress )


	# -------------------------------------------------
	# 加载配置资源
	# -------------------------------------------------
	def __cycleLoadResources( self ) :
		"""
		循环加载资源
		"""
		count = len( self.__resWrapps )											# 剩余的资源数量
		if count == 0 : return													# 如果所有资源都加载完毕
		self.__resWrapps.pop( 0 )()												# 弹出下一个资源
		passCount = self.__tmpMaxCount - count + 1								# 已经加载过的数量
		self.__tmpCallback( float( passCount ) / self.__tmpMaxCount )			# 以当前加载完毕的百分比回调加载函数
		self.__cbid = BigWorld.callback( 0.01, self.__cycleLoadResources )		# 进入下一个 tick

	def __loadResources( self, wrapper, percent ) :
		"""
		加载资源
		"""
		def detect( progress ) :												# 加载侦测回调
			currProgress = self.__currProgress + progress * percent				# 累计当前总进度
			self.__notify( currProgress )										# 以当前总进度回调
			if progress == 1.0 :												# 如果加载完毕
				del self.__tmpMaxCount											# 则删除临时数量
				del self.__tmpCallback											# 删除临时 callback
				self.__currProgress += percent									# 设置总进度值
				wrapper.finished = True											# 标记为只加载一次（并且已经全部加载完毕）
				self.__nextLoading()											# 进入下一个加载函数

		self.__tmpMaxCount = len( self.__resWrapps )							# 设置最大资源加载数量
		self.__tmpCallback = detect												# 设置 callback
		if len( self.__resWrapps  ) :
			self.__cycleLoadResources()											# 用 callback 循环加载
		else :
			detect( 1.0 )

	# -------------------------------------------------
	# 加载 UI
	# -------------------------------------------------
	def __cycleLoadUIs( self ) :
		"""
		循环加载 UI
		"""
		count = len( self.__uis )												# 剩余的资源数量
		if count == 0 :
			uiFactory.relateRoots()												# 初始化窗口关系
			return																# 如果所有资源都加载完毕
		uiInfo = self.__uis.pop( 0 )											# 弹出下一个资源
		if _g_out_loadingInfo :
			start = time.time()
			memUsage = csol.memoryUsage()
			INFO_MSG( "initializing UI %s..." % str( uiInfo[1] ) )
		uiFactory.createRoot( *uiInfo )											# 创建 UI
		if _g_out_loadingInfo :
			INFO_MSG( "used time: %f used mem: %f" % ( time.time() - start, csol.memoryUsage() - memUsage ) )
		passCount = self.__tmpMaxCount - count + 1								# 已经加载过的数量
		self.__tmpCallback( float( passCount ) / self.__tmpMaxCount )			# 以当前加载完毕的百分比回调加载函数
		self.__cbid = BigWorld.callback( 0.01, self.__cycleLoadUIs )			# 进入下一个 tick

	def __loadUIs( self, wrapper, percent ) :
		"""
		加载 UI
		"""
		def detect( progress ) :												# 加载侦测回调
			currProgress = self.__currProgress + progress * percent				# 累计当前总进度
			self.__notify( currProgress )										# 以当前总进度回调
			if progress == 1.0 :												# 如果加载完毕
				del self.__tmpMaxCount											# 则删除临时数量
				del self.__tmpCallback											# 删除临时 callback
				self.__currProgress += percent									# 设置总进度值
				wrapper.finished = True											# 标记为只加载一次（并且已经全部加载完毕）
				self.__nextLoading()											# 进入下一个加载函数
				csol.swapWorkingSet()

		self.__tmpMaxCount = len( self.__uis )									# 设置最大资源加载数量
		self.__tmpCallback = detect												# 设置 callback
		self.__tmpCallback = detect												# 设置 callback
		if len( self.__uis ) :
			self.__cycleLoadUIs()												# 用 callback 循环加载
		else :
			detect( 1.0 )

	# -------------------------------------------------
	# 加载随身精灵操作提示
	# -------------------------------------------------
	def __loadPixieDatas( self, wrapper, percent ) :
		"""
		加载操作提示
		"""
		rds.helper.uiopHelper.initialize()
		rds.helper.pixieHelper.initialize()
		self.__currProgress += percent
		self.__notify( self.__currProgress )
		self.__nextLoading()

	# -------------------------------------------------
	# 向服务器请求进入世界
	# -------------------------------------------------
	def __enterWorldDetect( self ) :
		"""
		侦测是否登录完毕
		"""
		if self.__isInWorld :													# 当 onEnterWorld 调用，该值会被置为 True
			self.__tmpCallback( 1.0 )											# 设置进度为 1.0，表示登录完毕
		else :
			if self.__tmpProgress < 1.0 :										# 模拟的临时进度
				self.__tmpCallback( self.__tmpProgress )						# 回调当前进度
				self.__tmpProgress += 0.01										# 递增当前进度值
			self.__cbid = BigWorld.callback( 0.01, self.__enterWorldDetect )	# 继续下一个侦测

	def __requestEnterWorld( self, wrapper, percent ) :
		"""
		请求 enterworld
		"""
		def detect( progress ) :											# 进入游戏进度回调
			currProgress = self.__currProgress + progress * percent
			self.__notify( currProgress )									# 回调总进度
			if progress == 1.0 :											# 完毕
				del self.__tmpProgress										# 删除临时变量
				del self.__tmpCallback
				self.__currProgress += percent								# 增加总进度
				self.__nextLoading()										# 进入下一个侦测

		rds.gameMgr.requestEnterWorld()										# 进入游戏
		self.__tmpProgress = 0												# 在登录没响应前模拟登录进度值
		self.__tmpCallback = detect											# 设置临时进度回调
		self.__enterWorldDetect()											# 调用进入世界侦测

	# -------------------------------------------------
	# 申请角色属性资源和场景侦测同时进行
	# -------------------------------------------------
	def __requestPlayerProperties( self ) :
		"""
		向服务器请求玩家资源
		"""
		count = len( self.__playerInitTypes )								# 剩余的申请数量
		if count == 0 : return 1.0											# 如果申请完毕
		if not self.__tmpRequesting :
			start = time.time()
			itype, name = self.__playerInitTypes.pop( 0 )					# 弹出一个申请类型

			def endRequested() :
				self.__tmpRequesting = False								# 申请结束，则设置正在申请标记为 False
				if _g_out_loadingInfo :
					INFO_MSG( "request %s end! used time: %f" % ( name, time.time() - start ) )

			def vehicleDataRequested():
				endRequested()
				ECenter.fireEvent( "EVT_ON_VEHICLE_DATA_LOADED" ) # 骑宠数据加载完毕的通知

			self.__tmpRequesting = True
			if _g_out_loadingInfo :
				INFO_MSG( "requesting: %s..." % name )
			# 骑宠状态由buff代表之后，其加载就具有特殊性，界面有时候需要骑宠数据的时候其并未加载，所以单独设置一个加载完成事件，
			# 以帮助界面正确完成其工作。 by mushuang
			if itype == csdefine.ROLE_INIT_VEHICLES:
				BigWorld.player().requestInitialize( itype, vehicleDataRequested )		# 调用申请函数
			else:
				BigWorld.player().requestInitialize( itype, endRequested )		# 调用申请函数

		return float( self.__tmpInitCount - count ) / self.__tmpInitCount	# 返回已经申请完毕的进度值

	def __resetSpaceLoadRate( self ):
		"""
		重置加上时间限制的加载进度
		"""
		self.__startLoadSceneTime = time.time()

	def __getSpaceLoadRate( self ):
		"""
		加上时间限制的加载进度
		"""
		timeEfflux = time.time() - self.__startLoadSceneTime
		timeLimitRate = timeEfflux / _g_loadSceneLimitSec
		if timeLimitRate > 1.0:
			timeLimitRate = 1.0
		totalRate = ( BigWorld.spaceLoadStatus() + timeLimitRate ) / 2.0
		return totalRate

	def __cycleSceneDetect( self ) :
		"""
		循环侦测进度
		"""
		sceneProgress = self.__getSpaceLoadRate()							# 获取场景加载进度
		if not self.__tmpSceneLoading :										# 如果还没进入场景加载
			if sceneProgress < 0.2 : 										# 如果进度小于一个值（暂定为 0.2）（以防前面场景还没消失）
				self.__tmpSceneLoading = True								# 则，认为新场景已经开始加载
		reqProgress = self.__requestPlayerProperties()						# 获取角色属性请求的进度
		progress = ( sceneProgress + reqProgress ) / 2.0					# 取较小的进度值作为当前进度
		self.__tmpCallback( progress )										# 回调进度值
		if progress >= 1.0 : return
		self.__cbid = BigWorld.callback( 0.01, self.__cycleSceneDetect )

	def __loadScene( self, wrapper, percent ) :
		"""
		加载场景和初始角色数据
		"""
		def detect( progress ) :											# 进度侦测
			currProgress = self.__currProgress + progress * percent			# 增加当前进度
			self.__notify( currProgress )									# 回调总进度值
			if progress == 1.0 :											# 如果全部加载完毕
				del self.__tmpSceneLoading									# 则删除临时属性
				del self.__tmpInitCount
				del self.__tmpRequesting
				del self.__tmpCallback
				self.__currProgress += percent								# 增加总进度值
				self.__nextLoading()										# 跳到下一个侦测函数

		self.__tmpSceneLoading = False										# 标记是否已经进入场景加载
		self.__tmpInitCount = len( self.__playerInitTypes )					# 角色属性申请的总数量
		self.__tmpRequesting = False										# 标记是否处于请求属性资源中
		self.__tmpCallback = detect											# 临时回调
		rds.worldCamHandler.use()											# 重新设置相机
		rds.worldCamHandler.reset()
		self.__resetSpaceLoadRate()
		self.__cycleSceneDetect()											# 场景加载侦测


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onGameStart( self ) :
		"""
		当游戏准备就绪时被调用
		"""
		# 必须在这个地方包装资源加载对象，因为有些对象是 GameInit 后才创建的
		self.__resWrapps = [
			_Wrapper( rds.helper.systemHelper, "initialize" ),
			_Wrapper( rds.helper.courseHelper, "initialize" ),
			_Wrapper( rds.gameSettingMgr, "initSettings" ),
			]

	def onEnterWorld( self ) :
		"""
		当角色进入世界时被调用
		"""
		self.__isInWorld = True

		# 角色上所有的初始化方法
		self.__playerInitTypes = [ \
			( csdefine.ROLE_INIT_OPRECORDS, "operation records" ),			# 操作记录列表
			( csdefine.ROLE_INIT_KITBAGS, "kitbag" ),						# 背包
			( csdefine.ROLE_INIT_ITEMS, "items" ),							# 物品
			( csdefine.ROLE_INIT_COMPLETE_QUESTS, "complete quests" ),		# 完成的任务列表
			( csdefine.ROLE_INIT_QUEST_LOGS, "quest logs" ),				# 任务日志
			( csdefine.ROLE_INIT_SKILLS, "skills" ),						# 技能列表
			( csdefine.ROLE_INIT_BUFFS, "buffs" ),							# buff 列表
			( csdefine.ROLE_INIT_COLLDOWN, "cooldowns" ),					# cooldown
			( csdefine.ROLE_INIT_PETS, "pets" ),							# 宠物
			( csdefine.ROLE_INIT_PRESTIGE, "prestige" ),					# 声望
			( csdefine.ROLE_INIT_VEHICLES, "vehicles" ),					# 骑宠
			( csdefine.ROLE_INIT_QUICK_BAR, "quickbar items" ),				# 快捷栏
			( csdefine.ROLE_INIT_DAOFA, "daofas" ),							# 道法
			( csdefine.ROLE_INIT_REWARD_QUESTS, "reward quests" ),			# 悬赏任务
			#( csdefine.ROLE_INIT_OFLMSGS, "offline messages"),				# 离线消息
			]

	def onLeaveWorld( self ) :
		"""
		当角色离开世界时被调用
		"""
		self.__isInWorld = False

	# -------------------------------------------------
	def run( self, callback ) :
		_BaseLoader.run( self )
		self.__callback = callback
		self.__currProgress = 0
		self.__tmpLoaders = self.__loaders[:]
		self.__nextLoading()

	def cancel( self ) :
		"""
		取消当前加载进度
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None
		for name in self.__dict__.keys() :								# 删除所有临时变量
			if name.startswith( "_WorldLoader__tmp" ) :
				self.__dict__.pop( name )


# --------------------------------------------------------------------
# teleport loader
# --------------------------------------------------------------------
class _TeleportLoader( _BaseLoader ) :
	TLP_SPACE		= 0					# 场景跳转侦测
	TLP_AREA		= 1					# 区域跳转侦测

	def __init__( self ) :
		self.__callback = None
		self.__cbid = 0
		self.__startLoadSceneTime = 0
		self.__lastRate = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetSpaceLoadRate( self ):
		"""
		重置加上时间限制的加载进度
		"""
		self.__lastRate = 0
		self.__startLoadSceneTime = time.time()

	def __getSpaceLoadRate( self ):
		"""
		加上时间限制的加载进度
		"""
		timeEfflux = time.time() - self.__startLoadSceneTime
		timeLimitRate = timeEfflux / _g_loadSceneLimitSec
		if timeLimitRate > 1.0:
			timeLimitRate = 1.0
		currRate = ( BigWorld.spaceLoadStatus() + timeLimitRate ) / 2.0
		currRate = max( self.__lastRate, currRate )
		return currRate

	def __spaceSceneDetect( self ) :
		"""
		场景侦测
		"""
		progress = self.__getSpaceLoadRate()								# 获取场景加载进度
		self.__callback( progress )											# 实时回调当前场景加载进度
		if progress == 1.0 : return											# 场景加载完毕
		self.__lastRate = progress
		self.__cbid = BigWorld.callback( 0.5, self.__spaceSceneDetect )		# 还没加载完毕，继续下一个侦测 tick


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def run( self, tlpType, callback ) :
		_BaseLoader.run( self )
		self.__callback = callback
		self.__resetSpaceLoadRate()
		self.__cbid = BigWorld.callback( 0.5, self.__spaceSceneDetect )

	def cancel( self ) :
		"""
		取消当前侦测
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None

# --------------------------------------------------------------------
# implement resource loader
# --------------------------------------------------------------------
class ResourceLoader( Singleton ) :
	def __init__( self ) :
		self.__startLoader = _StartLoader()									# 游戏刚刚启动时的资源加载器
		self.__loginLoader = _LoginLoader()									# 登录资源加载器
		self.__creatorLoader = _CreatorLoader()	
		self.__worldLoader = _WorldLoader()									# 世界资源加载器
		self.__teleportLoader = _TeleportLoader()							# 跳转侦测

		self.__notifier = lambda progress : progress						# 进度通知回调（进度条会设置该回调）

		self.__currLoader = None											# 当前活动的加载器
		self.__curSpaceFolder = ""											# 当前所在空间的文件夹名字
		self.__isUsedCameraInWorld = False									# 是否已在新场景中设定好摄像机


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __notify( self, progress ) :
		"""
		通知进度条
		"""
		self.__notifier( progress )

	def __changeSpaceDetect( self ):
		"""
		侦测游戏场景的切换
		"""
		player = BigWorld.player()
		if player and player.isPlayer():
			if not self.__isUsedCameraInWorld :
				self.__isUsedCameraInWorld = True
				from LoadingAnimation import loadingAnimation
				if not loadingAnimation.isPlay:
					rds.worldCamHandler.use()
			spaceFolder = BigWorld.player().getSpaceFolder()
			if spaceFolder != self.__curSpaceFolder:
				self.__curSpaceFolder = spaceFolder
				self.onEnterNewSpace( spaceFolder )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnterNewSpace( self, spaceFolder ):
		"""
		当游戏场景刚切换时的回调函数
		@type		spaceFolder: string
		@param		spaceFolder: 将要进入新场景所在的文件夹名字
		"""
		NavDataMgr.instance().loadNavData( spaceFolder, 1.0 )

	def onGameStart( self ) :
		"""
		当游戏准备就绪时被调用
		"""
		self.__worldLoader.onGameStart()

	def onRoleEnterWorld( self ) :
		"""
		当角色进入世界时被调用
		"""
		self.__worldLoader.onEnterWorld()

	def onRoleLeaveWorld( self ) :
		"""
		当角色离开世界时被调用
		"""
		self.__worldLoader.onLeaveWorld()

	def onOffline( self ) :
		"""
		当客户端离线时被调用
		"""
		if self.__currLoader :
			self.__loginLoader.cancel()
			self.__worldLoader.cancel()
			self.__teleportLoader.cancel()
			self.__curSpaceFolder = ""
			self.__isUsedCameraInWorld = False
			self.__currLoader = None
			ECenter.fireEvent( "EVT_ON_BREAK_LOADING" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setNotifier( self, notifier ) :
		"""
		设置进度通知回调
		"""
		assert notifier is None or callable( notifier ), \
			"notifier must be None or a callable instance!"
		if notifier is None :
			self.__notifier = lambda progress : progress
		else :
			self.__notifier = notifier

	# -------------------------------------------------
	def loadStartResource( self ) :
		"""
		当游戏启动时被调用
		"""
		self.__startLoader.run()											# 直接加载，没有进度回调

	def loadLoginSpace( self, enter, callback ) :
		"""
		进入角色选择时，加载场景
		@type				callback : functor
		@param				callback : 当场景加载完毕将会被调用
		"""
		def detect( progress ) :
			if progress >= 1 :
				self.__currLoader = None
			if progress < 0 :												# 初始化 patrial path 或选择角色模型失败
				ECenter.fireEvent( "EVT_ON_BREAK_LOADING" )
			else :
				self.__notify( progress )									# 通知进度条

		if enter :
			ECenter.fireEvent( "EVT_ON_BEGIN_ENTER_RS_LOADING", \
				self, callback )											# 进入角色选择
		else :
			ECenter.fireEvent( "EVT_ON_BEGIN_BACK_RS_LOADING", \
				self, callback )											# 返回角色选择
		self.__currLoader = self.__loginLoader								# 当前加载器
		self.__loginLoader.run( detect )

	def loadCreatorSpace( self, callback ) :
		"""
		加载创建角色资源，加载完毕时被调用
		"""
		def detect( progress ) :
			if progress >= 1 :
				self.__currLoader = None
				#callback()
			self.__notify( progress )
		self.__currLoader = self.__creatorLoader
		ECenter.fireEvent( "EVT_ON_BEGIN_WORLD_LOADING", self, callback )
		self.__isUsedCameraInWorld = False
		self.__creatorLoader.run( detect )

	# -------------------------------------------------
	def loadEnterWorldResource( self, callback ) :
		"""
		加载世界资源，加载完毕时被调用
		"""
		def detect( progress ) :
			if progress >= 1 :
				self.__currLoader = None
			self.__notify( progress )
			self.__changeSpaceDetect()

		ECenter.fireEvent( "EVT_ON_BEGIN_WORLD_LOADING", self, callback )
		self.__currLoader = self.__worldLoader
		self.__isUsedCameraInWorld = False
		self.__worldLoader.run( detect )

	def teleportSpace( self, callback ) :
		"""
		加载场景侦测
		@type				callback : functor
		@param				callback : 当场景加载完毕将会被调用
		"""
		def detect( progress ) :
			if progress >= 1 :
				player = BigWorld.player()
				if player and hasattr( player, "onTeleportReady" ):
					player.onTeleportReady()
				self.__currLoader = None
			self.__notify( progress )
			self.__changeSpaceDetect()

		ECenter.fireEvent( "EVT_ON_BEGIN_WORLD_LOADING", self, callback )
		self.__currLoader = self.__teleportLoader
		self.__isUsedCameraInWorld = False
		self.__teleportLoader.run( _TeleportLoader.TLP_SPACE, detect )

	def teleportArea( self, callback ) :
		"""
		加载区域侦测
		@type				callback : functor
		@param				callback : 当场景加载完毕将会被调用
		"""
		def detect( progress ) :
			if progress >= 1 :
				self.__currLoader = None
			self.__notify( progress )
			self.__changeSpaceDetect()

		ECenter.fireEvent( "EVT_ON_BEGIN_WORLD_LOADING", self, callback )
		self.__currLoader = self.__teleportLoader
		self.__isUsedCameraInWorld = False
		self.__teleportLoader.run( _TeleportLoader.TLP_AREA, detect )

	# -------------------------------------------------
	def cancelCurrLoading( self ) :
		"""
		取消当前加载
		"""
		self.__curSpaceFolder = ""
		self.__isUsedCameraInWorld = False
		if self.__currLoader :
			self.__currLoader.cancel()
		else :
			ERROR_MSG( "no loading running currently!" )

	def isCreatorLoader( self ):
		"""
		是否在加载创建角色资源
		"""
		return self.__currLoader == self.__creatorLoader

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
resLoader = ResourceLoader()

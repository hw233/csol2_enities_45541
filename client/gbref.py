# -*- coding: gb18030 -*-
#
# $Id: gbref.py,v 1.31 2008-08-30 10:06:30 wangshufeng Exp $

"""
implement global reference methods

2007/04/28 : writen by huangyongwei
"""

import math
import csol
import BigWorld
import Math
from bwdebug import *
from AbstractTemplates import Singleton

# --------------------------------------------------------------------
# global variables' local class
# --------------------------------------------------------------------
class RDShare :
	__inst = None
	def __init__( self ) :
		assert RDShare.__inst is None

		# -----------------------------------
		# global singleton ( 单件 )
		# -----------------------------------
		self.gameMgr = None								# game manager
		self.statusMgr = None							# game status
		self.soundMgr = None							# sound model( initialize in game init )
		self.shortcutMgr = None							# shortcut manager
		self.targetMgr = None							# target manager
		self.loginMgr = None							# login space manager
		self.mapMgr = None								# map area manager( initialize in game init )
		self.npcDatasMgr = None							# 客户端 NPC 数据管理器
		self.entityDecoratorMgr = None					# 附加附加表现管理器
		self.hyperlinkMgr = None						# 超链接管理器
		self.titleMgr = None							# 称号管理器
		self.viewInfoMgr = None							# 自由可视信息设置管理器
		self.ruisMgr = None								# ui manager
		self.uiHandlerMgr = None						# ui handler manager
		self.tactFactory = None
		self.uiFactory = None							# ui factory
		self.ccursor = None								# 鼠标管理器
		self.resLoader = None							# resource loading manager
		self.helper = None								# helper
		self.castIndicator = None						# 施放指示器
		self.questRelatedNPCVisible = None				# 任务相关NPC可见性
		self.globalSkillMgr = None						# 全局特殊技能管理器
		self.itemModel = None
		self.npcModel = None
		self.npcVoice = None
		self.mutexShowMgr = None						# 互斥窗口管理器

		self.textFormatMgr = None						# textFormat manager

		self.worldCamHandler = None						# 用于在 InWorld 状态中处理根据鼠标决定相机方向的模块

		self.loginer = None								# login
		self.roleSelector = None						# role select
		self.roleCreator = None							# role clreate

		self.wordsProfanity = None						# vocabulary filter for chat( initialize in game init )
		self.acursor = None								# cursor animator( initialize in game init )
		self.damageStatistic = None						# 玩家伤害输入统计

		self.equipEfects = None							# effect of equip( initialize in game init )
		self.omm = None									# items manager( initialize in game init )
		self.itemsDict = None							# ( initialize in game init )
		self.randomEffect = None						# effect random manager
		self.spellEffect = None

		self.roleMaker = None							# 角色模型管理器
		self.effectMgr = None							# 效果管理器
		self.equipParticle = None						# 装备强化、镶嵌信息
		self.skillEffect = None							# 技能效果
		self.modelFetchMgr = None						# 模型后线程加载管理模块
		self.areaEffectMgr = None						# 区域效果管理
		self.enEffectMgr = None							# 环境效果管理
		self.cameraFlyMgr = None						# 摄像头飞行管理
		self.actionMgr = None							# 动作管理模块
		self.cameraEventMgr = None						# 摄像头事件管理
		self.spaceEffectMgr = None						# 场景光效管理

		self.opIndicator = None							# 玩家操作指示器
		self.spaceCopyFormulas = None					# 可排队副本信息管理器

		# -----------------------------------
		# config data sections
		# -----------------------------------
		self.loadingScreenGUI = None					# 启动界面
		self.scriptsConfig = None						# ( initialized in function "init" )
		self.engineConfig = None						# ( initialized in function "init" )
		self.userPreferences = None						# ( initialized in function "init" )


rds = RDShare()



# --------------------------------------------------------------------
# other global functions
# --------------------------------------------------------------------
def cursorToDropPoint() :
	"""
	get three dimensionality mouse position
	@rtype				: Vector3
	@return				: position in world
	"""
	if not csol.cursorInWindow():	# 鼠标在游戏窗口外
		return None
	pj = BigWorld.projection()
	ly = pj.nearPlane * math.tan( pj.fov * 0.5 )
	lx = ly * BigWorld.screenWidth() / BigWorld.screenHeight()

	( cx, cy ) = csol.rcursorPosition()
	vNearPlane = Math.Vector3( lx * cx, ly * cy, pj.nearPlane )
	vNearPlane.normalise()
	vFarPlane = Math.Vector3( vNearPlane )
	vFarPlane.x *= pj.farPlane
	vFarPlane.y *= pj.farPlane
	vFarPlane.z *= pj.farPlane

	spaceID = BigWorld.player().spaceID
	camera = BigWorld.camera()
	mInvert = Math.Matrix( camera.invViewMatrix )
	vSrc = mInvert.applyToOrigin()
	vDst = mInvert.applyPoint( vFarPlane )
	vDir = Math.Vector3( vSrc - vDst )
	vDir.normalise()
	vSrc = vSrc - vDir * pj.nearPlane
	collideResult = BigWorld.collide( spaceID, vSrc, vDst )

	while collideResult is not None :
		if collideResult[2] == 13 :
			vSrc = collideResult[0] - vDir * 0.05
			collideResult = BigWorld.collide( spaceID, vSrc, vDst )
		else :
			break
	if collideResult is None:
		return None
	vcollide = collideResult[0]
	vcollide.y += 0.2
	dp = BigWorld.findDropPoint( spaceID, vcollide, 13 )
	if dp is None :
		return None
	return dp[0]


def cursorFirstDropPoint():
	"""
	get three dimensionality mouse position
	不过滤遮挡
	@rtype				: Vector3
	@return				: position in world
	"""
	pj = BigWorld.projection()
	ly = pj.nearPlane * math.tan( pj.fov * 0.5 )
	lx = ly * BigWorld.screenWidth() / BigWorld.screenHeight()

	( cx, cy ) = csol.rcursorPosition()
	vNearPlane = Math.Vector3( lx * cx, ly * cy, pj.nearPlane )
	vNearPlane.normalise()
	vFarPlane = Math.Vector3( vNearPlane )
	vFarPlane.x *= pj.farPlane
	vFarPlane.y *= pj.farPlane
	vFarPlane.z *= pj.farPlane

	spaceID = BigWorld.player().spaceID
	camera = BigWorld.camera()
	mInvert = Math.Matrix( camera.invViewMatrix )
	vSrc = mInvert.applyToOrigin()
	vDst = mInvert.applyPoint( vFarPlane )
	vDir = Math.Vector3( vSrc - vDst )
	vDir.normalise()
	vSrc = vSrc - vDir * pj.nearPlane
	collideResult = BigWorld.collide( spaceID, vSrc, vDst )
	if collideResult is None:
		return None

	vcollide = collideResult[0]
	vcollide.y += 0.2
	dp = BigWorld.findDropPoint( spaceID, vcollide )
	if dp is None :
		return None
	return dp[0]


# --------------------------------------------------------------------
# python config writer
# --------------------------------------------------------------------
def delSubSection( sect, subSect ) :
	"""
	删除一个子 section
	"""
	pass

class PyConfiger( Singleton ) :
	"""
	实现写 py 配置
	"""
	def __init__( self ) :
		self.__builders = {}							# 复合类型字符串转换操作
		self.__builders[tuple]	= self.__buildTuple		# 元组
		self.__builders[list]	= self.__buildList		# 链表
		self.__builders[dict]	= self.__buildDict		# 字典


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __buildList( self, l, tabs ) :
		"""
		构建链表串
		"""
		s = "["
		for e in l :
			s += "\n"
			s += tabs + self.__toString( e, tabs )
			s += ","
		return s + "\n%s]" % tabs

	def __buildTuple( self, t, tabs ) :
		"""
		构建元组串
		"""
		s = "("
		for e in t :
			s += "%s," % self.__toString( e, tabs )
		return s + ")"

	def __buildDict( self, d, tabs ) :
		"""
		构建字典串
		"""
		s = "{"
		for k, v in d.iteritems() :
			s += "\n"
			sk = tabs + self.__toString( k, tabs )
			sv = self.__toString( v, tabs + "\t" )
			s += "%s:%s," % ( sk, sv )
		return s + "\n%s}" % tabs

	def __buildUndef( self, e, tabs ) :
		"""
		构建非特化类型
		"""
		if isinstance( e, basestring ) :
			return "'%s'" % e
		return str( e )

	# ---------------------------------------
	def __toString( self, ele, tabs ) :
		"""
		分派
		"""
		builder = self.__builders.get( type( ele ), self.__buildUndef )
		return builder( ele, tabs )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def read( self, path, default = None, isReload = False ) :
		"""
		读取一个 py 配置
		@type				path	 : str
		@param				path	 : 配置路径，格式为：XX/XXX/XXXX.py
		@type				default  : alltypes
		@param				default  : 加载失败时的默认值
		@type				isReload : bool
		@param				isReload : 是否重新加载
		@rtype						 : dict/list/tuple
		@return						 : 从配置中读出的字典( 注意：即便调用多次，返回的仍然是同一份数据 )
		"""
		if path.endswith( ".py" ) :
			path = path[:-3]
		try :
			module = __import__( path )
			if isReload : reload( module )
			return module.Datas
		except :
			ERROR_MSG( "config '%s' is not exist!" % path )
		return default

	def write( self, d, path ) :
		"""
		将字典写到 python 配置
		@type				d	 : dict/list/tuple
		@param				d	 : 要写到配置的字典
		@type				path : str
		@param				path : 保存路径
		@rtype					 : bool
		@return					 : 写成功返回 True，否则返回 False
		"""
		path = "entities/%s" % path
		f = None
		try :
			f = open( path, 'w' )
		except IOError, err :
			ERROR_MSG( err )
		else :
			text = "# -*- coding: gb18030 -*-\n"				# py 头
			text += "Datas = " + self.__toString( d, "\t" )	# 将字典合并为字符串
			f.write( text )
			f.close()
			return True
		return False

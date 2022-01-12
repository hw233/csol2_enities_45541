# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Pixie
import Define
import Math
from Function import Functor
import Const
MAX_COUNT = 5
# ------------------------------------------------------------------------------
# Class EffectMgr:
# 效果管理器
# 用于实现各种特殊效果，包括各种光效效果，模型效果等
# ------------------------------------------------------------------------------
class EffectMgr:
	__instance = None

	def __init__( self ):
		assert EffectMgr.__instance is None

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = EffectMgr()
		return SELF.__instance

	def accessNode( self, model, hardPoint ):
		"""
		访问指定模型的指定绑定点
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@return					: pyNode
		"""
		if model is None: return None
		try:
			return model.node( hardPoint )
		except:
			ERROR_MSG( "Can't find node(%s) in (%s)" % ( hardPoint, model.sources ) )
			return model.root

	def createModel( self, subModels, subDyes = [], params = {} ):
		"""
		在主线程创建一个模型，实时返回一个PyModel实例
		但是：如果一个entity在其prerequisites方法有返回相关模型路径
		那么创建该模型时是不会影响主线程的，此举能避免卡机现象
		entity在enterWorld时应该以此方法创建模型，这样能实时获得模型。
		This function will block the main thread to load models in
		the event that they were not specified as prerequisites
		@param subModels		:	要创建的模型路径列表
		@type subModels			:	List of String
		@param subDyes			:	子模型的Dye字典
		@type subDyes			:	dict
		@param params			:	模型的效果参数列表
		@type params			:	dict
		@return					:	PyModel or None
		"""
		model = None
		if len( subModels ) == 0: return model
		try :
			model = BigWorld.Model( *subModels )
		except Exception, errStr :
			msg = "\nCan't build models below:\n"
			for models in subModels :
				msg += 5 * "\t" + models + "\n"
			DEBUG_MSG( msg )

		self.createModelDye( model, subDyes, params )
		return model

	def createModelBG( self, subModels, onLoadCompleted, subDyes = [], params = {} ):
		"""
		在后线程创建一个模型，创建好模型后回调
		一些实时要求不严格的模型应该以此方法创建，才不会影响主线程
		如一些技能光效表现等
		@param subModels		:	要创建的模型路径列表
		@type subModels			:	List of String
		@param onLoadCompleted	:	创建好模型后的回调函数
		@type onLoadCompleted	:	Function
		@param subDyes			:	子模型的Dye字典
		@type subDyes			:	dict
		@param params			:	模型的效果参数列表
		@type params			:	dict
		@return					:	None
		"""
		if len( subModels ) == 0:
			if callable( onLoadCompleted ):
				onLoadCompleted( None )
			return

		callback = ModelLoaderCallback( self, list( subModels ), onLoadCompleted, subDyes, params )
		subModels = list( subModels )
		subModels.append( callback )
		BigWorld.fetchModel( *subModels )

	def createParticle( self, model, hardPoint, path, detachTime = 0.0, type = Define.TYPE_PARTICLE_SCENE, scale = 1.0 ) :
		"""
		在主线程给指定模型的指定绑定点绑上指定的光效
		实在想不到什么地方应该用这个
		有什么比主线程流畅更重要？
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@type		path		: String
		@param		path		: 光效路径
		@rtype					: particleInstance
		"""
		if path == "": return
		try:
			p = Pixie.create( path )
		except:
			ERROR_MSG( "Can't find resources(%s)" % ( path ) )
			return None

		p.type = type
		p.scale = scale
		self.attachObject( model, hardPoint, p )
		p.force()

		if detachTime > 0.0:
			functor = Functor( self.detachObject, model, hardPoint, p )
			BigWorld.callback( detachTime, functor )
		return p

	def createParticleBG( self, model, hardPoint, path, onLoadCompleted = None, detachTime = 0.0, type = Define.TYPE_PARTICLE_SCENE, scale = 1.0 ) :
		"""
		在后线程给指定模型的指定绑定点绑上指定的光效
		这个显然很受欢迎
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@type		path		: String
		@param		path		: 光效路径
		@rtype					: None
		@type       detachTime  : Float
		@param      detachTime  : 删除光效延时
		"""
		if path == "": return

		def loadCompleted( p ):
			self.attachObject( model, hardPoint, p )
			p.force()
			if callable( onLoadCompleted ):
				onLoadCompleted( p )
			if detachTime > 0.0:
				functor = Functor( self.detachObject, model, hardPoint, p )
				BigWorld.callback( detachTime, functor )

		self.pixieCreateBG( path, loadCompleted, type, scale )

	def pixieCreateBG( self, path, callback = None, type = Define.TYPE_PARTICLE_SCENE, scale = 1.0 ):
		"""
		后线程创建一个粒子
		"""
		def loadCompleted( p ):
			p.type = type
			p.scale = scale
			if callable( callback ):
				callback( p )

		Pixie.createBG( path, loadCompleted )

	def createModelDye( self, model, subDyes = [], params = {} ):
		"""
		在指定的模型设置一个Dye效果
		@param model			:	要设置的模型
		@type model				:	PyModel
		@param subDyes			:	子模型的Dye字典
		@type subDyes			:	dict
		@param params			:	模型的效果参数列表
		@type params			:	dict
		@return					:	PyModel or None
		"""
		if model is None: return
		for value in subDyes:
			if len( value ) != 2: continue
			dyeName, dyeValue = value
			if hasattr( model, dyeName ):
				setattr( model, dyeName, dyeValue )
			else:
				ERROR_MSG( "(%s) has no attribute name(%s)" % ( model.sources, dyeName ) )
				continue
		for dyeName, dyeParams in params.iteritems():
			if hasattr( model, dyeName ):
				attr = getattr( model, dyeName )
				for key, value in dyeParams.iteritems():
					if hasattr( attr, key ):
						setattr( attr, key, value )
					else:
						ERROR_MSG( "(%s) has no attribute name(%s.%s)" % ( model.sources, attr, key ) )
						continue
			else:
				ERROR_MSG( "(%s) has no attribute name(%s)" % ( model.sources, dyeName ) )
				continue

	def linkObject( self, model, hardPoint, object ):
		"""
		给指定模型的指定绑定点添加指定的object
		和 attachObject 方法不同
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@type		object		: PyMetaParticleSystem/PyModel
		@param		object		: 光效实例/模型实例
		"""
		if model is None: return
		node = self.accessNode( model, hardPoint )
		if node is None: return
		if "HP_" not in hardPoint: return
		key = hardPoint.replace( "HP_", "" )
		setattr( model, key, object )

	def getLinkObject( self, model, hardPoint ):
		"""
		返回指定模型的指定绑定点的Link object
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		"""
		if model is None: return
		node = self.accessNode( model, hardPoint )
		if node is None: return
		if "HP_" not in hardPoint: return
		key = hardPoint.replace( "HP_", "" )
		return getattr( model, key, None )

	def attachObject( self, model, hardPoint, object ):
		"""
		给指定模型的指定绑定点添加指定的object
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@type		object		: PyMetaParticleSystem/PyModel
		@param		object		: 光效实例/模型实例
		"""
		if model is None: return
		if object is None: return
		if object.attached: return
		node = self.accessNode( model, hardPoint )
		if node is None: return
		node.attach( object )

	def detachObject( self, model, hardPoint, object ) :
		"""
		给指定模型的指定绑定点移除指定的object
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@type		object		: PyMetaParticleSystem/PyModel
		@param		object		: 光效实例/模型实例
		"""
		if object is None: return
		if not object.inWorld: return
		if not object.attached: return
		if model is None: return None
		node = self.accessNode( model, hardPoint )
		if node is None: return
		if object in node.attachments:
			node.detach( object )

	def nodeModelCheck( self, node, model ):
		"""
		检查某绑定点上是否存在指定模型/光效实例 by姜毅
		"""
		natts = node.attachments
		if len( natts ) == 0: return True
		for natt in natts:
			if type( natt ) is not BigWorld.Model: continue
			if natt.sources == model.sources: return False
		return True

	def fadeOutParticle( self, particle ):
		"""
		渐隐一个粒子光效
		@type		particle	: PyMetaParticleSystem
		@param		particle	: 光效实例
		"""
		if particle is None: return
		if not particle.inWorld: return
		if not particle.attached: return

		for i in xrange( particle.nSystems() ):
			particle_actions = [action for action in particle.system( i ).actions if action.typeID == Define.PSA_SOURCE_TYPE_ID]
			for ac in particle_actions:
				ac.timeTriggered = False

	def fastOutParticle( self, particle ):
		"""
		迅速隐藏一个粒子光效
		这个接口和detachObject所产生的效果是一样的，但是这个接口不会把粒子移除world
		类似于一个model.visible产生的效果
		"""
		if particle is None: return
		if not particle.attached: return
		self.fadeOutParticle( particle )
		particle.clear()

	def fadeInParticle( self, particle ):
		"""
		渐入一个粒子光效
		@type		particle	: PyMetaParticleSystem
		@param		particle	: 光效实例
		"""
		if particle is None: return
		if not particle.inWorld: return
		if not particle.attached: return

		for i in xrange( particle.nSystems() ):
			particle_actions = [action for action in particle.system( i ).actions if action.typeID == Define.PSA_SOURCE_TYPE_ID]
			sink_actions = [action for action in particle.system( i ).actions if action.typeID == Define.PSA_SINK_TYPE_ID]
			if len(sink_actions) and sink_actions[0].maximumAge < 0 :
				continue
			for ac in particle_actions:
				ac.timeTriggered = True

	def fadeOutModelAttachments( self, pyModel ):
		"""
		渐隐一个模型的所有负载物
		@type		pyModel	: PyModel
		@param		pyModel	: 模型
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		for node in pyModel.nodes():
			for object in node.attachments:
				if isinstance( object, Pixie.MetaParticleSystem ):
					self.fadeOutParticle( object )

	def fadeInModelAttachments( self, pyModel ):
		"""
		渐入一个模型的所有负载物
		@type		pyModel	: PyModel
		@param		pyModel	: 模型
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		for node in pyModel.nodes():
			for object in node.attachments:
				if isinstance( object, Pixie.MetaParticleSystem ):
					self.fadeInParticle( object )

	def addModelBGInPos( self, pyModel, hardPoint, subModels, onLoadCompleted = None, lastTime = 0.0 ):
		"""
		在指定的模型绑定点的位置添加一个模型
		@type		pyModel			: pyModel
		@param		pyModel			: 模型
		@type		hardPoint		: String
		@param		hardPoint		: 绑定点
		@type		subModels		: list of string
		@param		subModels		: 模型资源
		@type		onLoadCompleted	: Function
		@param		onLoadCompleted	: 加载完模型回调
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return

		def loadCompleted( model ):
			if model is None: return
			if not pyModel.inWorld: return
			pos = self.accessNodePos( pyModel, hardPoint  )
			if pos.length < 0.1:
				pos = pyModel.position
			self.addModelWithPos( pos, model, onLoadCompleted, lastTime )
			model.yaw = pyModel.yaw

		self.createModelBG( subModels, loadCompleted )

	def addModelBGWithPos( self, pos, subModels, onLoadCompleted = None, lastTime = 0.0 ):
		"""
		在指定的模型绑定点的位置添加一个模型
		@type		pos				: vector3
		@param		pos				: 位置坐标
		@type		subModels		: list of string
		@param		subModels		: 模型资源
		@type		onLoadCompleted	: Function
		@param		onLoadCompleted	: 加载完模型回调
		"""
		def loadCompleted( model ):
			self.addModelWithPos( pos, model, onLoadCompleted, lastTime )

		self.createModelBG( subModels, loadCompleted )

	def addModelWithPos( self, pos, model, onLoadCompleted = None, lastTime = 0.0 ):
		"""
		在某位置加上某模型
		@type		pos				: vector3
		@param		pos				: 位置坐标
		@type		model			: PyModel
		@param		model			: 模型
		@type		onLoadCompleted	: Function
		@param		onLoadCompleted	: 回调
		"""
		if model is None: return
		player = BigWorld.player()
		if player is None: return
		if not player.inWorld: return
		player.addModel( model )
		model.position = pos
		if callable( onLoadCompleted ):
			onLoadCompleted( model )
		if lastTime > 0.0:
			functor = Functor( player.delModel, model )
			BigWorld.callback( lastTime, functor )

	def modelShine( self, model, type, texture, colour, scale, offset ):
		"""
		给指定的模型自发光
		@type		model		: pyModel
		@param		model		: 模型
		@type		type		: Int
		@param		type		: 自发光类型
		@type		texture		: String
		@param		texture		: 发光贴图路径
		@type		colour		: Vector4
		@param		colour		: 发光颜色
		@type		scale		: Vector4
		@param		scale		: 发光缩放
		@type		offset		: Vector3
		@param		offset		: 发光片偏移量
		"""
		if model is None: return
		model.isNeedGlow = True
		model.setModelRenderID( 0 )
		model.glowType = type
		model.setSubModelGlowMap( 0, texture )
		model.setSubModelScale( 0, scale )
		model.setSubModelColour( 0, colour )
		model.setSubModelOffset( 0, offset )

	def accessNodePos( self, model, hardPoint ):
		"""
		访问指定模型的指定绑定点坐标
		@type		model		: pyModel
		@param		model		: 模型
		@type		hardPoint	: String
		@param		hardPoint	: 绑定点
		@return					: pyNode
		"""
		if model is None: return Math.Vector3()
		node = self.accessNode( model, hardPoint )
		if node is None: return Math.Vector3()

		m = Math.Matrix( node )
		return m.applyToOrigin()

	def multipleScaleModel( self, pyModel, multiple, lastTime = 1.0, callback = None ):
		"""
		缩放模型，模型缩放multiple倍，这个值以1为标准，
		如0.5则表示缩小为原来的1半。2则为放大到原来的一倍。
		缩放速度默认为每秒/25帧的速度
		@type		pyModel		: PyModel
		@param		pyModel		: 缩放的模型
		@type		multiple	: Float
		@param		multiple	: 缩放的倍数
		@type		lastTime	: Float
		@param		lastTime	: 缩放的持续时间
		@return					: None
		"""
		# 模型不在世界不能缩放
		if not pyModel.inWorld: return
		# 缩放倍数为负数或者为0、1, 不需要缩放
		if multiple <=0 or multiple == 1: return
		# 模型的原始Scale
		srcScale = pyModel.scale
		# 模型的最终Scale
		decScale = srcScale.scale( multiple )
		self.scaleModel( pyModel, decScale, lastTime, callback )

	def scaleModel( self, pyModel, decScale, lastTime = 1.0, callback = None ):
		"""
		缩放模型，模型缩放至值decScale
		缩放速度默认为每秒/25帧的速度
		@type		pyModel		: PyModel
		@param		pyModel		: 缩放的模型
		@type		decScale	: Vector3
		@param		decScale	: 最终缩放至的值
		@type		lastTime	: Float
		@param		lastTime	: 缩放的持续时间
		@return
		"""
		# 模型不在世界不能缩放
		if not pyModel.inWorld: return
		# 不缩放
		srcScale = pyModel.scale
		if decScale == srcScale: return
		# 如果缩放持续时间为0,则为瞬间缩放
		if lastTime == 0:
			pyModel.scale = decScale
			if callable( callback ):
				callback()
			return
		# 根据持续时间算出模型变换次数
		count = int( lastTime/0.04  )
		# 每次模型缩放的变换量
		perScale = ( decScale - srcScale )/count
		# 生成模型缩放值列表
		scaleValues = []
		for k in xrange( 1, count ):
			scaleValues.append( srcScale + perScale.scale( k ) )
		# 计算误差，最后一帧的缩放值
		scaleValues[-1] = decScale

		self.setModelScales( pyModel, scaleValues, callback )

	def setModelScales( self, pyModel, scaleValues, callback = None ):
		"""
		根据缩放值列表按顺序缩放模型
		@type		pyModel		: PyModel
		@param		pyModel		: 缩放的模型
		@type		scaleValues	: List
		@param		scaleValues	: List of Vector3
		@return					: None
		"""
		def set():
			if not pyModel.inWorld: return
			if len( scaleValues ) == 0:
				if callable( callback ):
					callback()
				return
			scale = scaleValues.pop()
			pyModel.scale = scale
			BigWorld.callback( 0.04, set )

		scaleValues.reverse()
		set()

	def cameraShake( self, lastTime, shakeRange, shakeCenter ):
		"""
		摄像机晃动
		@type		lastTime		: Float
		@param		lastTime		: 晃动持续的时间
		@type		shakeRange		: Vector3
		@param		shakeRange		: XYZ轴晃动的幅度
		@type		shakeCenter		: Vector3
		@param		shakeCenter		: 中心点的晃动幅度
		@return						: None
		"""
		camera = BigWorld.camera()
		if camera is None: return

		if not hasattr( camera, "shake" ): return
		camera.shake( lastTime, shakeRange, shakeCenter )

	def fadeOutModel( self, pyModel, lastTime = 1.0 ):
		"""
		渐隐模型
		@type		pyModel		: PyModel
		@param		pyModel		: 渐变的模型
		@type		lastTime	: Float
		@param		lastTime	: 渐隐的持续时间
		@return
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return

		self.setModelAlpha( pyModel, 0.0, lastTime )

	def fadeInModel( self, pyModel, lastTime = 0.01 ):
		"""
		渐入模型
		@type		pyModel		: PyModel
		@param		pyModel		: 渐变的模型
		@type		lastTime	: Float
		@param		lastTime	: 渐隐的持续时间
		@return
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return

		self.setModelAlpha( pyModel, 1.0, lastTime )

	def setModelAlpha( self, pyModel, alpha, lastTime = 0.0 ):
		"""
		设置模型的alpha
		@type		pyModel		: PyModel
		@param		pyModel		: 模型
		@type		alpha		: Float
		@param		alpha		: alpha Value
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		
		pyModel.setAlpha( alpha, lastTime )

	def setModelColor( self, pyModel, srcColor, dstColor = (1,1,1,1), lastTime = 0.0 ):
		"""
		模型指定时间由srcColor变为dstColor
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		pyModel.originColorBlend = srcColor
		pyModel.targetColorBlend = dstColor
		pyModel.colorBlendTimeLen = lastTime
		pyModel.enableColorBlend = True

class ModelLoaderCallback:
	def __init__( self, parent, subModles, callback, subDyes, params ):
		self.parent = parent
		self.subModles = subModles
		self.callback = callback
		self.subDyes = subDyes
		self.params = params

	def __call__( self, model ):
		if model is None:
			msg = "\nCan't build models below:\n"
			for models in self.subModles:
				msg += 5 * "\t" + models + "\n"
			DEBUG_MSG( msg )
		self.parent.createModelDye( model, self.subDyes, self.params )
		if callable( self.callback ):
			self.callback( model )

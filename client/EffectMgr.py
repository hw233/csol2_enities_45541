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
# Ч��������
# ����ʵ�ָ�������Ч�����������ֹ�ЧЧ����ģ��Ч����
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
		����ָ��ģ�͵�ָ���󶨵�
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
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
		�����̴߳���һ��ģ�ͣ�ʵʱ����һ��PyModelʵ��
		���ǣ����һ��entity����prerequisites�����з������ģ��·��
		��ô������ģ��ʱ�ǲ���Ӱ�����̵߳ģ��˾��ܱ��⿨������
		entity��enterWorldʱӦ���Դ˷�������ģ�ͣ�������ʵʱ���ģ�͡�
		This function will block the main thread to load models in
		the event that they were not specified as prerequisites
		@param subModels		:	Ҫ������ģ��·���б�
		@type subModels			:	List of String
		@param subDyes			:	��ģ�͵�Dye�ֵ�
		@type subDyes			:	dict
		@param params			:	ģ�͵�Ч�������б�
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
		�ں��̴߳���һ��ģ�ͣ�������ģ�ͺ�ص�
		һЩʵʱҪ���ϸ��ģ��Ӧ���Դ˷����������Ų���Ӱ�����߳�
		��һЩ���ܹ�Ч���ֵ�
		@param subModels		:	Ҫ������ģ��·���б�
		@type subModels			:	List of String
		@param onLoadCompleted	:	������ģ�ͺ�Ļص�����
		@type onLoadCompleted	:	Function
		@param subDyes			:	��ģ�͵�Dye�ֵ�
		@type subDyes			:	dict
		@param params			:	ģ�͵�Ч�������б�
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
		�����̸߳�ָ��ģ�͵�ָ���󶨵����ָ���Ĺ�Ч
		ʵ���벻��ʲô�ط�Ӧ�������
		��ʲô�����߳���������Ҫ��
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		@type		path		: String
		@param		path		: ��Ч·��
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
		�ں��̸߳�ָ��ģ�͵�ָ���󶨵����ָ���Ĺ�Ч
		�����Ȼ���ܻ�ӭ
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		@type		path		: String
		@param		path		: ��Ч·��
		@rtype					: None
		@type       detachTime  : Float
		@param      detachTime  : ɾ����Ч��ʱ
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
		���̴߳���һ������
		"""
		def loadCompleted( p ):
			p.type = type
			p.scale = scale
			if callable( callback ):
				callback( p )

		Pixie.createBG( path, loadCompleted )

	def createModelDye( self, model, subDyes = [], params = {} ):
		"""
		��ָ����ģ������һ��DyeЧ��
		@param model			:	Ҫ���õ�ģ��
		@type model				:	PyModel
		@param subDyes			:	��ģ�͵�Dye�ֵ�
		@type subDyes			:	dict
		@param params			:	ģ�͵�Ч�������б�
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
		��ָ��ģ�͵�ָ���󶨵����ָ����object
		�� attachObject ������ͬ
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		@type		object		: PyMetaParticleSystem/PyModel
		@param		object		: ��Чʵ��/ģ��ʵ��
		"""
		if model is None: return
		node = self.accessNode( model, hardPoint )
		if node is None: return
		if "HP_" not in hardPoint: return
		key = hardPoint.replace( "HP_", "" )
		setattr( model, key, object )

	def getLinkObject( self, model, hardPoint ):
		"""
		����ָ��ģ�͵�ָ���󶨵��Link object
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		"""
		if model is None: return
		node = self.accessNode( model, hardPoint )
		if node is None: return
		if "HP_" not in hardPoint: return
		key = hardPoint.replace( "HP_", "" )
		return getattr( model, key, None )

	def attachObject( self, model, hardPoint, object ):
		"""
		��ָ��ģ�͵�ָ���󶨵����ָ����object
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		@type		object		: PyMetaParticleSystem/PyModel
		@param		object		: ��Чʵ��/ģ��ʵ��
		"""
		if model is None: return
		if object is None: return
		if object.attached: return
		node = self.accessNode( model, hardPoint )
		if node is None: return
		node.attach( object )

	def detachObject( self, model, hardPoint, object ) :
		"""
		��ָ��ģ�͵�ָ���󶨵��Ƴ�ָ����object
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		@type		object		: PyMetaParticleSystem/PyModel
		@param		object		: ��Чʵ��/ģ��ʵ��
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
		���ĳ�󶨵����Ƿ����ָ��ģ��/��Чʵ�� by����
		"""
		natts = node.attachments
		if len( natts ) == 0: return True
		for natt in natts:
			if type( natt ) is not BigWorld.Model: continue
			if natt.sources == model.sources: return False
		return True

	def fadeOutParticle( self, particle ):
		"""
		����һ�����ӹ�Ч
		@type		particle	: PyMetaParticleSystem
		@param		particle	: ��Чʵ��
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
		Ѹ������һ�����ӹ�Ч
		����ӿں�detachObject��������Ч����һ���ģ���������ӿڲ���������Ƴ�world
		������һ��model.visible������Ч��
		"""
		if particle is None: return
		if not particle.attached: return
		self.fadeOutParticle( particle )
		particle.clear()

	def fadeInParticle( self, particle ):
		"""
		����һ�����ӹ�Ч
		@type		particle	: PyMetaParticleSystem
		@param		particle	: ��Чʵ��
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
		����һ��ģ�͵����и�����
		@type		pyModel	: PyModel
		@param		pyModel	: ģ��
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		for node in pyModel.nodes():
			for object in node.attachments:
				if isinstance( object, Pixie.MetaParticleSystem ):
					self.fadeOutParticle( object )

	def fadeInModelAttachments( self, pyModel ):
		"""
		����һ��ģ�͵����и�����
		@type		pyModel	: PyModel
		@param		pyModel	: ģ��
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		for node in pyModel.nodes():
			for object in node.attachments:
				if isinstance( object, Pixie.MetaParticleSystem ):
					self.fadeInParticle( object )

	def addModelBGInPos( self, pyModel, hardPoint, subModels, onLoadCompleted = None, lastTime = 0.0 ):
		"""
		��ָ����ģ�Ͱ󶨵��λ�����һ��ģ��
		@type		pyModel			: pyModel
		@param		pyModel			: ģ��
		@type		hardPoint		: String
		@param		hardPoint		: �󶨵�
		@type		subModels		: list of string
		@param		subModels		: ģ����Դ
		@type		onLoadCompleted	: Function
		@param		onLoadCompleted	: ������ģ�ͻص�
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
		��ָ����ģ�Ͱ󶨵��λ�����һ��ģ��
		@type		pos				: vector3
		@param		pos				: λ������
		@type		subModels		: list of string
		@param		subModels		: ģ����Դ
		@type		onLoadCompleted	: Function
		@param		onLoadCompleted	: ������ģ�ͻص�
		"""
		def loadCompleted( model ):
			self.addModelWithPos( pos, model, onLoadCompleted, lastTime )

		self.createModelBG( subModels, loadCompleted )

	def addModelWithPos( self, pos, model, onLoadCompleted = None, lastTime = 0.0 ):
		"""
		��ĳλ�ü���ĳģ��
		@type		pos				: vector3
		@param		pos				: λ������
		@type		model			: PyModel
		@param		model			: ģ��
		@type		onLoadCompleted	: Function
		@param		onLoadCompleted	: �ص�
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
		��ָ����ģ���Է���
		@type		model		: pyModel
		@param		model		: ģ��
		@type		type		: Int
		@param		type		: �Է�������
		@type		texture		: String
		@param		texture		: ������ͼ·��
		@type		colour		: Vector4
		@param		colour		: ������ɫ
		@type		scale		: Vector4
		@param		scale		: ��������
		@type		offset		: Vector3
		@param		offset		: ����Ƭƫ����
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
		����ָ��ģ�͵�ָ���󶨵�����
		@type		model		: pyModel
		@param		model		: ģ��
		@type		hardPoint	: String
		@param		hardPoint	: �󶨵�
		@return					: pyNode
		"""
		if model is None: return Math.Vector3()
		node = self.accessNode( model, hardPoint )
		if node is None: return Math.Vector3()

		m = Math.Matrix( node )
		return m.applyToOrigin()

	def multipleScaleModel( self, pyModel, multiple, lastTime = 1.0, callback = None ):
		"""
		����ģ�ͣ�ģ������multiple�������ֵ��1Ϊ��׼��
		��0.5���ʾ��СΪԭ����1�롣2��Ϊ�Ŵ�ԭ����һ����
		�����ٶ�Ĭ��Ϊÿ��/25֡���ٶ�
		@type		pyModel		: PyModel
		@param		pyModel		: ���ŵ�ģ��
		@type		multiple	: Float
		@param		multiple	: ���ŵı���
		@type		lastTime	: Float
		@param		lastTime	: ���ŵĳ���ʱ��
		@return					: None
		"""
		# ģ�Ͳ������粻������
		if not pyModel.inWorld: return
		# ���ű���Ϊ��������Ϊ0��1, ����Ҫ����
		if multiple <=0 or multiple == 1: return
		# ģ�͵�ԭʼScale
		srcScale = pyModel.scale
		# ģ�͵�����Scale
		decScale = srcScale.scale( multiple )
		self.scaleModel( pyModel, decScale, lastTime, callback )

	def scaleModel( self, pyModel, decScale, lastTime = 1.0, callback = None ):
		"""
		����ģ�ͣ�ģ��������ֵdecScale
		�����ٶ�Ĭ��Ϊÿ��/25֡���ٶ�
		@type		pyModel		: PyModel
		@param		pyModel		: ���ŵ�ģ��
		@type		decScale	: Vector3
		@param		decScale	: ������������ֵ
		@type		lastTime	: Float
		@param		lastTime	: ���ŵĳ���ʱ��
		@return
		"""
		# ģ�Ͳ������粻������
		if not pyModel.inWorld: return
		# ������
		srcScale = pyModel.scale
		if decScale == srcScale: return
		# ������ų���ʱ��Ϊ0,��Ϊ˲������
		if lastTime == 0:
			pyModel.scale = decScale
			if callable( callback ):
				callback()
			return
		# ���ݳ���ʱ�����ģ�ͱ任����
		count = int( lastTime/0.04  )
		# ÿ��ģ�����ŵı任��
		perScale = ( decScale - srcScale )/count
		# ����ģ������ֵ�б�
		scaleValues = []
		for k in xrange( 1, count ):
			scaleValues.append( srcScale + perScale.scale( k ) )
		# ���������һ֡������ֵ
		scaleValues[-1] = decScale

		self.setModelScales( pyModel, scaleValues, callback )

	def setModelScales( self, pyModel, scaleValues, callback = None ):
		"""
		��������ֵ�б�˳������ģ��
		@type		pyModel		: PyModel
		@param		pyModel		: ���ŵ�ģ��
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
		������ζ�
		@type		lastTime		: Float
		@param		lastTime		: �ζ�������ʱ��
		@type		shakeRange		: Vector3
		@param		shakeRange		: XYZ��ζ��ķ���
		@type		shakeCenter		: Vector3
		@param		shakeCenter		: ���ĵ�Ļζ�����
		@return						: None
		"""
		camera = BigWorld.camera()
		if camera is None: return

		if not hasattr( camera, "shake" ): return
		camera.shake( lastTime, shakeRange, shakeCenter )

	def fadeOutModel( self, pyModel, lastTime = 1.0 ):
		"""
		����ģ��
		@type		pyModel		: PyModel
		@param		pyModel		: �����ģ��
		@type		lastTime	: Float
		@param		lastTime	: �����ĳ���ʱ��
		@return
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return

		self.setModelAlpha( pyModel, 0.0, lastTime )

	def fadeInModel( self, pyModel, lastTime = 0.01 ):
		"""
		����ģ��
		@type		pyModel		: PyModel
		@param		pyModel		: �����ģ��
		@type		lastTime	: Float
		@param		lastTime	: �����ĳ���ʱ��
		@return
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return

		self.setModelAlpha( pyModel, 1.0, lastTime )

	def setModelAlpha( self, pyModel, alpha, lastTime = 0.0 ):
		"""
		����ģ�͵�alpha
		@type		pyModel		: PyModel
		@param		pyModel		: ģ��
		@type		alpha		: Float
		@param		alpha		: alpha Value
		"""
		if pyModel is None: return
		if not pyModel.inWorld: return
		
		pyModel.setAlpha( alpha, lastTime )

	def setModelColor( self, pyModel, srcColor, dstColor = (1,1,1,1), lastTime = 0.0 ):
		"""
		ģ��ָ��ʱ����srcColor��ΪdstColor
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

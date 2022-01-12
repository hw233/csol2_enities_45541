# -*- coding: gb18030 -*-
#
# $Id: ResourceLoader.py,v 1.30 2008-09-03 01:40:09 huangyongwei Exp $

"""
implement resource loading class

2008/01/15: writen by huangyongwei
2008/07.24: refactored( �ع� ) by huangyongwei
"""

# --------------------------------------------------------------------
# ʵ��˼�룺
# ��Դ�ļ��غ���Ϸ�Ϊ����ģ�飺
# �� ������Ϸ��Ҫ���ص���Դ
#    �ⲿ����ʱ�ǡ����̡��ģ�Ҳ����һ���Լ��أ���˼��ؽ��Ȳ���������ڽ�������
# �� ��¼ʱ��Ҫ���ص���Դ
#    �ⲿ��ʵ���ϲ�û����ʽ�ؼ�����Դ�������ǶԽ�ɫѡ��ĳ����ļ��ؽ��н������
# �� ������Ϸʱ��Ҫ���ص���Դ
#    ������ֱȽϹ㣬Ŀǰ������ؽ��ȷ�Ϊ��
#		 ��ɫ��ص�һЩ���õļ���			��
#		 �������							��
#		 ��ɫ��¼							��
#		 ��ɫ�������루����������룩		��
#		 һЩ״̬�ĳ�ʼ��
# �� ��ɫ��ת����
#    �ⲿ����ʵ�����Ƕ���ת��ĳ������ؽ��Ƚ������
#
# -------------------------------------------
# ���ϵķֲ����طֱ�̯�ֵ��ĸ����������У�ʵ�ָ��Թ�����Ȼ��Щ���رȽϼ򵥣�
# ��������Ϸ����Դ���أ�����ת���أ���Ϊ�˸���ģ�黯���Ա��պ���������޸�
# �͹�����˻��ǽ���ʵ��ϸ���� ResourceLoader ���롣
# ��������Դ���ز�����������Ϸ������ʱ�����У�����������ܲ��Ǽ�����̡�
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
# ��Ҫ��ʼ����ģ��
# ---------------------------------
from PetFormulas import formulas as petFormulas
from guis.UIFactory import uiFactory
from guis.UISounder import uiSounder


_g_out_loadingInfo = False								# �Ƿ�������ؽ���������Ϣ

_g_loadSceneLimitSec	= 1.0							# ͬһ������תʱ�����ʱ�����ƣ���ʱ�ã����ֻ�м���chunk��insideChunkС��ͼ
														# ˢ��һ���ͽ�������Ϸ�������̴߳������ײ��Ϣû�м��ص��¹������ȥ�����⡣

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
		csol.swapWorkingSet()					# ������Դǰǰ����һ�� csol.swapWorkingSet���ͷ�һЩ�����ڴ档

	def cancel( self ) :
		pass

	__abstract_methods.add( run )
	__abstract_methods.add( cancel )


# --------------------------------------------------------------------
# implement game start resource loader
# --------------------------------------------------------------------
class _StartLoader( _BaseLoader ) :
	"""
	��û�зŵ���ʼ���������У���˼����������Դʱ����Ϸ�ո�����ʱ�����������Ῠһ��
	"""
	def run( self ) :
		rds.wordsProfanity.initialize()						# ���شʻ���˱������ļ�·������ģ����
		uiSounder.initialize()								# ��ʼ�� UI ����

		roots = uiFactory.getCommonRoots()					# ���� UI
		roots += uiFactory.getLoginRoots()					# ��¼�õ� UI
		for root in roots :
			uiFactory.createRoot( *root )					# �������� UI �͵�¼ UI
		uiFactory.createTempRoots()							# ������ʱ�Ĺ��� UI

	def cancel( self ) :
		"""
		û���� callback ���أ���� cancel û����
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
		���ɵĳ����Ƿ��Ѿ���������ؽ���С�� 0.2 ʱ��������ʼ�µĳ������أ�
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
		��ɫ�����������
		"""
		progress = BigWorld.spaceLoadStatus()
		if progress >= 1.0 :
			callback( 1.0 )
		else :															# ���������û�������
			callback( progress )										# ��ֱ��֪ͨ����
			func = Functor( self.__sceneDetect, callback )
			self.__cbid = BigWorld.callback( 0.01, func )				# ���ҽ�����һ�� tick

	# ---------------------------------------
	def __callInitializer( self, initializers, totalCount, callback, progress ) :
		"""
		�ֱ���ø�����ɫ������
		"""
		oneProgress = float( progress ) / totalCount						# ��ǰ��ʼ�����صĽ���
		leaveCount = len( initializers )									# ʣ��ĳ�ʼ��������
		passCount = totalCount - leaveCount									# �Ѿ�������ĳ�ʼ��������
		passProgress = float( passCount - 1 ) / totalCount + oneProgress	# �Ѿ�������Ľ���
		callback( passProgress )
		if progress >= 1 and leaveCount :
			initer = initializers.pop( 0 )
			func = Functor( self.__callInitializer, initializers, totalCount, callback )
			self.__cbid = BigWorld.callback( 0.01, Functor( initer, func ) )

	def __callInitializers( self, initializers, callback ) :
		"""
		��˳����ý�ɫ����/��ɫѡ��ļ�����
		"""
		count = len( initializers )
		func = Functor( self.__callInitializer, initializers, count, callback )
		initializers.pop( 0 )( func )

	def __initRoleSelector( self, callback ) :
		"""
		��ʼ����ɫѡ��
		"""
		self.__callInitializers( rds.roleSelector.getInitializers(), callback )

	# -------------------------------------------------
	def __detecte( self ) :
		"""
		�ж��Ƿ��������볡�����أ���Ϊ�п���ǰһ�γ�����û���٣�
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
			( 0.1, self.__startDetect ),						# ���ʲôʱ��ʼ��������
			( 0.1, self.__sceneDetect ),						# ���ʲôʱ�򳡾��������
			( 0.8, self.__initRoleSelector ),					# ��ʼ����ɫѡ��
			]													# ��һά�Ǹ���ռ�õİٷֱȣ����ܱ���Ϊ 1.0
		self.__callback = callback
		self.__totalProgress = 0.0
		self.__detecte()

	def cancel( self ) :
		"""
		ȡ����ǰ�������
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
		��ɫ�����������
		"""
		progress = BigWorld.spaceLoadStatus()
		if progress >= 1.0 :
			callback( 1.0 )
		else :															# ���������û�������
			callback( progress )										# ��ֱ��֪ͨ����
			func = Functor( self.__sceneDetect, callback )
			self.__cbid = BigWorld.callback( 0.01, func )				# ���ҽ�����һ�� tick

	# ---------------------------------------
	def __callInitializer( self, initializers, totalCount, callback, progress ) :
		"""
		�ֱ���ø�����ɫ������
		"""
		oneProgress = float( progress ) / totalCount						# ��ǰ��ʼ�����صĽ���
		leaveCount = len( initializers )									# ʣ��ĳ�ʼ��������
		passCount = totalCount - leaveCount									# �Ѿ�������ĳ�ʼ��������
		passProgress = float( passCount - 1 ) / totalCount + oneProgress	# �Ѿ�������Ľ���
		callback( passProgress )
		if progress >= 1 and leaveCount :
			initer = initializers.pop( 0 )
			func = Functor( self.__callInitializer, initializers, totalCount, callback )
			self.__cbid = BigWorld.callback( 0.01, Functor( initer, func ) )

	def __callInitializers( self, initializers, callback ) :
		"""
		��˳����ý�ɫ����/��ɫѡ��ļ�����
		"""
		count = len( initializers )
		func = Functor( self.__callInitializer, initializers, count, callback )
		initializers.pop( 0 )( func )


	def __initRoleCreator( self, callback ) :
		"""
		��ʼ����ɫ������ͼ�����
		"""
		self.__callInitializers( [ rds.roleCreator.preLoadSomething ], callback )

	def __initRoleEntity( self, callback ) :
		"""
		��ʼ����ͼ8����ɫʵ��
		"""
		self.__callInitializers( [ rds.roleCreator.initRoleEntity ], callback )
		
	
	def __checkRoleCreate( self, callback ):
		self.__callInitializers( [ rds.roleCreator.checkRoleCreate ], callback )

	# -------------------------------------------------
	def __detecte( self ) :
		"""
		�ж��Ƿ��������볡�����أ���Ϊ�п���ǰһ�γ�����û���٣�
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
			( 0.1, self.__sceneDetect ),	# ���ʲôʱ�򳡾��������
			( 0.3, self.__initRoleCreator ),# ��ʼ����ɫ������ͼ�����
			( 0.4, self.__initRoleEntity ),# ��ʼ����ͼ8����ɫʵ��
			( 0.2, self.__checkRoleCreate ) #���8����ɫ�Ƿ�������
			]													# ��һά�Ǹ���ռ�õİٷֱȣ����ܱ���Ϊ 1.0
		self.__callback = callback
		self.__totalProgress = 0.0
		self.__detecte()

	def cancel( self ) :
		"""
		ȡ����ǰ�������
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None

# --------------------------------------------------------------------
# implement world resource loader
# --------------------------------------------------------------------
class _WorldLoader( _BaseLoader ) :
	# ----------------------------------------------------------------
	# ���غ�����װ��
	# ----------------------------------------------------------------
	class _LWrapper :
		def __init__( self, loader, percent ) :
			self.__loader = loader							# ���غ���

			self.finished = False							# �Ƿ��Ѿ��������´μ���ʱ������Ҫ���أ�
			self.percent = percent							# ռ�õļ��ؽ���

		def __call__( self ) :
			self.__loader( self, self.percent )

	# ----------------------------------------------------------------
	# _WorldLoader
	# ----------------------------------------------------------------
	def __init__( self ) :
		self.__resWrapps = []											# ��Դ���ذ�װ��
		self.__uis = uiFactory.getWorldRoots()							# enterword ʱҪ���ص� ui
		self.__playerInitTypes = []										# ��ɫҪ��ʼ������������
		self.__startLoadSceneTime = 0

		# -----------------------------------
		# ���غ�����������ڽ������ã�����Ϊ Loader ��Ҫ��פ�ڴ棬��˲���Ҫ��
		self.__loaders = [
			_WorldLoader._LWrapper( self.__loadResources, 0.01 ),		# ����������Դ
			_WorldLoader._LWrapper( self.__loadUIs, 0.29 ),				# ���� UI
			_WorldLoader._LWrapper( self.__loadPixieDatas, 0.1 ),		# ����������Ի�����
			_WorldLoader._LWrapper( self.__requestEnterWorld, 0.1 ),	# ��¼
			_WorldLoader._LWrapper( self.__loadScene, 0.50 ),			# �������ͽ�ɫ������Դ����
			]
		assert sum( [r.percent for r in self.__loaders] ) == 1.0, \
			"total progress must be 100%"								# �ܽ���ֵ����Ϊ 100��

		# -----------------------------------
		self.__callback = None											# ʵʱ���Ȼص�����
		self.__cbid = 0													# callback ID
		self.__uiControlId = 0

		self.__isInWorld = False										# ��ɫ�Ƿ��Ѿ���������
		self.__currProgress = 0											# ��ǰ���ؽ���
		self.__abandonProgress = 0										# ������ϵĽ��ȷ���ֵ


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __abandonFinishedLoaders( self ) :
		"""
		����ֻ�����һ�Σ������Ѿ�������ϵļ��غ���
		"""
		count = len( self.__loaders )
		for idx in xrange( count - 1, -1, -1 ) :						# ѭ�����м��غ���
			wrapper = self.__loaders[idx]
			if wrapper.finished :										# ������غ����������
				self.__loaders.remove( wrapper )						# ����б������֮
				self.__abandonProgress += wrapper.percent				# �����Ӷ����Ľ���ֵ

	def __nextLoading( self ) :
		"""
		������һ������
		"""
		if len( self.__tmpLoaders ) == 0 :								# ���û�м��غ���
			if self.__currProgress < 1.0 :								# ���������ϵ����Ȳ��� 100��
				self.__callback( 1.0 )									# ��ǿ��Ϊ 100��
			self.__abandonFinishedLoaders()								# ����ֻ�����һ�Σ������Ѿ�������ϵļ��غ���
			self.__callback = None										# ������� callback ������
			del self.__tmpLoaders
		else :															# ����
			self.__tmpLoaders.pop( 0 )()								# ����һ�����غ���

	def __notify( self, progress ) :
		"""
		�ص����ؽ���
		"""
		progress /= ( 1.0 - self.__abandonProgress )					# ��Ϊ������ȫ�����ȱ���������˲���������
		self.__callback( progress )


	# -------------------------------------------------
	# ����������Դ
	# -------------------------------------------------
	def __cycleLoadResources( self ) :
		"""
		ѭ��������Դ
		"""
		count = len( self.__resWrapps )											# ʣ�����Դ����
		if count == 0 : return													# ���������Դ���������
		self.__resWrapps.pop( 0 )()												# ������һ����Դ
		passCount = self.__tmpMaxCount - count + 1								# �Ѿ����ع�������
		self.__tmpCallback( float( passCount ) / self.__tmpMaxCount )			# �Ե�ǰ������ϵİٷֱȻص����غ���
		self.__cbid = BigWorld.callback( 0.01, self.__cycleLoadResources )		# ������һ�� tick

	def __loadResources( self, wrapper, percent ) :
		"""
		������Դ
		"""
		def detect( progress ) :												# �������ص�
			currProgress = self.__currProgress + progress * percent				# �ۼƵ�ǰ�ܽ���
			self.__notify( currProgress )										# �Ե�ǰ�ܽ��Ȼص�
			if progress == 1.0 :												# ����������
				del self.__tmpMaxCount											# ��ɾ����ʱ����
				del self.__tmpCallback											# ɾ����ʱ callback
				self.__currProgress += percent									# �����ܽ���ֵ
				wrapper.finished = True											# ���Ϊֻ����һ�Σ������Ѿ�ȫ��������ϣ�
				self.__nextLoading()											# ������һ�����غ���

		self.__tmpMaxCount = len( self.__resWrapps )							# ���������Դ��������
		self.__tmpCallback = detect												# ���� callback
		if len( self.__resWrapps  ) :
			self.__cycleLoadResources()											# �� callback ѭ������
		else :
			detect( 1.0 )

	# -------------------------------------------------
	# ���� UI
	# -------------------------------------------------
	def __cycleLoadUIs( self ) :
		"""
		ѭ������ UI
		"""
		count = len( self.__uis )												# ʣ�����Դ����
		if count == 0 :
			uiFactory.relateRoots()												# ��ʼ�����ڹ�ϵ
			return																# ���������Դ���������
		uiInfo = self.__uis.pop( 0 )											# ������һ����Դ
		if _g_out_loadingInfo :
			start = time.time()
			memUsage = csol.memoryUsage()
			INFO_MSG( "initializing UI %s..." % str( uiInfo[1] ) )
		uiFactory.createRoot( *uiInfo )											# ���� UI
		if _g_out_loadingInfo :
			INFO_MSG( "used time: %f used mem: %f" % ( time.time() - start, csol.memoryUsage() - memUsage ) )
		passCount = self.__tmpMaxCount - count + 1								# �Ѿ����ع�������
		self.__tmpCallback( float( passCount ) / self.__tmpMaxCount )			# �Ե�ǰ������ϵİٷֱȻص����غ���
		self.__cbid = BigWorld.callback( 0.01, self.__cycleLoadUIs )			# ������һ�� tick

	def __loadUIs( self, wrapper, percent ) :
		"""
		���� UI
		"""
		def detect( progress ) :												# �������ص�
			currProgress = self.__currProgress + progress * percent				# �ۼƵ�ǰ�ܽ���
			self.__notify( currProgress )										# �Ե�ǰ�ܽ��Ȼص�
			if progress == 1.0 :												# ����������
				del self.__tmpMaxCount											# ��ɾ����ʱ����
				del self.__tmpCallback											# ɾ����ʱ callback
				self.__currProgress += percent									# �����ܽ���ֵ
				wrapper.finished = True											# ���Ϊֻ����һ�Σ������Ѿ�ȫ��������ϣ�
				self.__nextLoading()											# ������һ�����غ���
				csol.swapWorkingSet()

		self.__tmpMaxCount = len( self.__uis )									# ���������Դ��������
		self.__tmpCallback = detect												# ���� callback
		self.__tmpCallback = detect												# ���� callback
		if len( self.__uis ) :
			self.__cycleLoadUIs()												# �� callback ѭ������
		else :
			detect( 1.0 )

	# -------------------------------------------------
	# ���������������ʾ
	# -------------------------------------------------
	def __loadPixieDatas( self, wrapper, percent ) :
		"""
		���ز�����ʾ
		"""
		rds.helper.uiopHelper.initialize()
		rds.helper.pixieHelper.initialize()
		self.__currProgress += percent
		self.__notify( self.__currProgress )
		self.__nextLoading()

	# -------------------------------------------------
	# ������������������
	# -------------------------------------------------
	def __enterWorldDetect( self ) :
		"""
		����Ƿ��¼���
		"""
		if self.__isInWorld :													# �� onEnterWorld ���ã���ֵ�ᱻ��Ϊ True
			self.__tmpCallback( 1.0 )											# ���ý���Ϊ 1.0����ʾ��¼���
		else :
			if self.__tmpProgress < 1.0 :										# ģ�����ʱ����
				self.__tmpCallback( self.__tmpProgress )						# �ص���ǰ����
				self.__tmpProgress += 0.01										# ������ǰ����ֵ
			self.__cbid = BigWorld.callback( 0.01, self.__enterWorldDetect )	# ������һ�����

	def __requestEnterWorld( self, wrapper, percent ) :
		"""
		���� enterworld
		"""
		def detect( progress ) :											# ������Ϸ���Ȼص�
			currProgress = self.__currProgress + progress * percent
			self.__notify( currProgress )									# �ص��ܽ���
			if progress == 1.0 :											# ���
				del self.__tmpProgress										# ɾ����ʱ����
				del self.__tmpCallback
				self.__currProgress += percent								# �����ܽ���
				self.__nextLoading()										# ������һ�����

		rds.gameMgr.requestEnterWorld()										# ������Ϸ
		self.__tmpProgress = 0												# �ڵ�¼û��Ӧǰģ���¼����ֵ
		self.__tmpCallback = detect											# ������ʱ���Ȼص�
		self.__enterWorldDetect()											# ���ý����������

	# -------------------------------------------------
	# �����ɫ������Դ�ͳ������ͬʱ����
	# -------------------------------------------------
	def __requestPlayerProperties( self ) :
		"""
		����������������Դ
		"""
		count = len( self.__playerInitTypes )								# ʣ�����������
		if count == 0 : return 1.0											# ����������
		if not self.__tmpRequesting :
			start = time.time()
			itype, name = self.__playerInitTypes.pop( 0 )					# ����һ����������

			def endRequested() :
				self.__tmpRequesting = False								# �������������������������Ϊ False
				if _g_out_loadingInfo :
					INFO_MSG( "request %s end! used time: %f" % ( name, time.time() - start ) )

			def vehicleDataRequested():
				endRequested()
				ECenter.fireEvent( "EVT_ON_VEHICLE_DATA_LOADED" ) # ������ݼ�����ϵ�֪ͨ

			self.__tmpRequesting = True
			if _g_out_loadingInfo :
				INFO_MSG( "requesting: %s..." % name )
			# ���״̬��buff����֮������ؾ;��������ԣ�������ʱ����Ҫ������ݵ�ʱ���䲢δ���أ����Ե�������һ����������¼���
			# �԰���������ȷ����乤���� by mushuang
			if itype == csdefine.ROLE_INIT_VEHICLES:
				BigWorld.player().requestInitialize( itype, vehicleDataRequested )		# �������뺯��
			else:
				BigWorld.player().requestInitialize( itype, endRequested )		# �������뺯��

		return float( self.__tmpInitCount - count ) / self.__tmpInitCount	# �����Ѿ�������ϵĽ���ֵ

	def __resetSpaceLoadRate( self ):
		"""
		���ü���ʱ�����Ƶļ��ؽ���
		"""
		self.__startLoadSceneTime = time.time()

	def __getSpaceLoadRate( self ):
		"""
		����ʱ�����Ƶļ��ؽ���
		"""
		timeEfflux = time.time() - self.__startLoadSceneTime
		timeLimitRate = timeEfflux / _g_loadSceneLimitSec
		if timeLimitRate > 1.0:
			timeLimitRate = 1.0
		totalRate = ( BigWorld.spaceLoadStatus() + timeLimitRate ) / 2.0
		return totalRate

	def __cycleSceneDetect( self ) :
		"""
		ѭ��������
		"""
		sceneProgress = self.__getSpaceLoadRate()							# ��ȡ�������ؽ���
		if not self.__tmpSceneLoading :										# �����û���볡������
			if sceneProgress < 0.2 : 										# �������С��һ��ֵ���ݶ�Ϊ 0.2�����Է�ǰ�泡����û��ʧ��
				self.__tmpSceneLoading = True								# ����Ϊ�³����Ѿ���ʼ����
		reqProgress = self.__requestPlayerProperties()						# ��ȡ��ɫ��������Ľ���
		progress = ( sceneProgress + reqProgress ) / 2.0					# ȡ��С�Ľ���ֵ��Ϊ��ǰ����
		self.__tmpCallback( progress )										# �ص�����ֵ
		if progress >= 1.0 : return
		self.__cbid = BigWorld.callback( 0.01, self.__cycleSceneDetect )

	def __loadScene( self, wrapper, percent ) :
		"""
		���س����ͳ�ʼ��ɫ����
		"""
		def detect( progress ) :											# �������
			currProgress = self.__currProgress + progress * percent			# ���ӵ�ǰ����
			self.__notify( currProgress )									# �ص��ܽ���ֵ
			if progress == 1.0 :											# ���ȫ���������
				del self.__tmpSceneLoading									# ��ɾ����ʱ����
				del self.__tmpInitCount
				del self.__tmpRequesting
				del self.__tmpCallback
				self.__currProgress += percent								# �����ܽ���ֵ
				self.__nextLoading()										# ������һ����⺯��

		self.__tmpSceneLoading = False										# ����Ƿ��Ѿ����볡������
		self.__tmpInitCount = len( self.__playerInitTypes )					# ��ɫ���������������
		self.__tmpRequesting = False										# ����Ƿ�������������Դ��
		self.__tmpCallback = detect											# ��ʱ�ص�
		rds.worldCamHandler.use()											# �����������
		rds.worldCamHandler.reset()
		self.__resetSpaceLoadRate()
		self.__cycleSceneDetect()											# �����������


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onGameStart( self ) :
		"""
		����Ϸ׼������ʱ������
		"""
		# ����������ط���װ��Դ���ض�����Ϊ��Щ������ GameInit ��Ŵ�����
		self.__resWrapps = [
			_Wrapper( rds.helper.systemHelper, "initialize" ),
			_Wrapper( rds.helper.courseHelper, "initialize" ),
			_Wrapper( rds.gameSettingMgr, "initSettings" ),
			]

	def onEnterWorld( self ) :
		"""
		����ɫ��������ʱ������
		"""
		self.__isInWorld = True

		# ��ɫ�����еĳ�ʼ������
		self.__playerInitTypes = [ \
			( csdefine.ROLE_INIT_OPRECORDS, "operation records" ),			# ������¼�б�
			( csdefine.ROLE_INIT_KITBAGS, "kitbag" ),						# ����
			( csdefine.ROLE_INIT_ITEMS, "items" ),							# ��Ʒ
			( csdefine.ROLE_INIT_COMPLETE_QUESTS, "complete quests" ),		# ��ɵ������б�
			( csdefine.ROLE_INIT_QUEST_LOGS, "quest logs" ),				# ������־
			( csdefine.ROLE_INIT_SKILLS, "skills" ),						# �����б�
			( csdefine.ROLE_INIT_BUFFS, "buffs" ),							# buff �б�
			( csdefine.ROLE_INIT_COLLDOWN, "cooldowns" ),					# cooldown
			( csdefine.ROLE_INIT_PETS, "pets" ),							# ����
			( csdefine.ROLE_INIT_PRESTIGE, "prestige" ),					# ����
			( csdefine.ROLE_INIT_VEHICLES, "vehicles" ),					# ���
			( csdefine.ROLE_INIT_QUICK_BAR, "quickbar items" ),				# �����
			( csdefine.ROLE_INIT_DAOFA, "daofas" ),							# ����
			( csdefine.ROLE_INIT_REWARD_QUESTS, "reward quests" ),			# ��������
			#( csdefine.ROLE_INIT_OFLMSGS, "offline messages"),				# ������Ϣ
			]

	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
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
		ȡ����ǰ���ؽ���
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None
		for name in self.__dict__.keys() :								# ɾ��������ʱ����
			if name.startswith( "_WorldLoader__tmp" ) :
				self.__dict__.pop( name )


# --------------------------------------------------------------------
# teleport loader
# --------------------------------------------------------------------
class _TeleportLoader( _BaseLoader ) :
	TLP_SPACE		= 0					# ������ת���
	TLP_AREA		= 1					# ������ת���

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
		���ü���ʱ�����Ƶļ��ؽ���
		"""
		self.__lastRate = 0
		self.__startLoadSceneTime = time.time()

	def __getSpaceLoadRate( self ):
		"""
		����ʱ�����Ƶļ��ؽ���
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
		�������
		"""
		progress = self.__getSpaceLoadRate()								# ��ȡ�������ؽ���
		self.__callback( progress )											# ʵʱ�ص���ǰ�������ؽ���
		if progress == 1.0 : return											# �����������
		self.__lastRate = progress
		self.__cbid = BigWorld.callback( 0.5, self.__spaceSceneDetect )		# ��û������ϣ�������һ����� tick


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
		ȡ����ǰ���
		"""
		BigWorld.cancelCallback( self.__cbid )
		self.__callback = None

# --------------------------------------------------------------------
# implement resource loader
# --------------------------------------------------------------------
class ResourceLoader( Singleton ) :
	def __init__( self ) :
		self.__startLoader = _StartLoader()									# ��Ϸ�ո�����ʱ����Դ������
		self.__loginLoader = _LoginLoader()									# ��¼��Դ������
		self.__creatorLoader = _CreatorLoader()	
		self.__worldLoader = _WorldLoader()									# ������Դ������
		self.__teleportLoader = _TeleportLoader()							# ��ת���

		self.__notifier = lambda progress : progress						# ����֪ͨ�ص��������������øûص���

		self.__currLoader = None											# ��ǰ��ļ�����
		self.__curSpaceFolder = ""											# ��ǰ���ڿռ���ļ�������
		self.__isUsedCameraInWorld = False									# �Ƿ������³������趨�������


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __notify( self, progress ) :
		"""
		֪ͨ������
		"""
		self.__notifier( progress )

	def __changeSpaceDetect( self ):
		"""
		�����Ϸ�������л�
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
		����Ϸ�������л�ʱ�Ļص�����
		@type		spaceFolder: string
		@param		spaceFolder: ��Ҫ�����³������ڵ��ļ�������
		"""
		NavDataMgr.instance().loadNavData( spaceFolder, 1.0 )

	def onGameStart( self ) :
		"""
		����Ϸ׼������ʱ������
		"""
		self.__worldLoader.onGameStart()

	def onRoleEnterWorld( self ) :
		"""
		����ɫ��������ʱ������
		"""
		self.__worldLoader.onEnterWorld()

	def onRoleLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		self.__worldLoader.onLeaveWorld()

	def onOffline( self ) :
		"""
		���ͻ�������ʱ������
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
		���ý���֪ͨ�ص�
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
		����Ϸ����ʱ������
		"""
		self.__startLoader.run()											# ֱ�Ӽ��أ�û�н��Ȼص�

	def loadLoginSpace( self, enter, callback ) :
		"""
		�����ɫѡ��ʱ�����س���
		@type				callback : functor
		@param				callback : ������������Ͻ��ᱻ����
		"""
		def detect( progress ) :
			if progress >= 1 :
				self.__currLoader = None
			if progress < 0 :												# ��ʼ�� patrial path ��ѡ���ɫģ��ʧ��
				ECenter.fireEvent( "EVT_ON_BREAK_LOADING" )
			else :
				self.__notify( progress )									# ֪ͨ������

		if enter :
			ECenter.fireEvent( "EVT_ON_BEGIN_ENTER_RS_LOADING", \
				self, callback )											# �����ɫѡ��
		else :
			ECenter.fireEvent( "EVT_ON_BEGIN_BACK_RS_LOADING", \
				self, callback )											# ���ؽ�ɫѡ��
		self.__currLoader = self.__loginLoader								# ��ǰ������
		self.__loginLoader.run( detect )

	def loadCreatorSpace( self, callback ) :
		"""
		���ش�����ɫ��Դ���������ʱ������
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
		����������Դ���������ʱ������
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
		���س������
		@type				callback : functor
		@param				callback : ������������Ͻ��ᱻ����
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
		�����������
		@type				callback : functor
		@param				callback : ������������Ͻ��ᱻ����
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
		ȡ����ǰ����
		"""
		self.__curSpaceFolder = ""
		self.__isUsedCameraInWorld = False
		if self.__currLoader :
			self.__currLoader.cancel()
		else :
			ERROR_MSG( "no loading running currently!" )

	def isCreatorLoader( self ):
		"""
		�Ƿ��ڼ��ش�����ɫ��Դ
		"""
		return self.__currLoader == self.__creatorLoader

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
resLoader = ResourceLoader()

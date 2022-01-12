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
		# global singleton ( ���� )
		# -----------------------------------
		self.gameMgr = None								# game manager
		self.statusMgr = None							# game status
		self.soundMgr = None							# sound model( initialize in game init )
		self.shortcutMgr = None							# shortcut manager
		self.targetMgr = None							# target manager
		self.loginMgr = None							# login space manager
		self.mapMgr = None								# map area manager( initialize in game init )
		self.npcDatasMgr = None							# �ͻ��� NPC ���ݹ�����
		self.entityDecoratorMgr = None					# ���Ӹ��ӱ��ֹ�����
		self.hyperlinkMgr = None						# �����ӹ�����
		self.titleMgr = None							# �ƺŹ�����
		self.viewInfoMgr = None							# ���ɿ�����Ϣ���ù�����
		self.ruisMgr = None								# ui manager
		self.uiHandlerMgr = None						# ui handler manager
		self.tactFactory = None
		self.uiFactory = None							# ui factory
		self.ccursor = None								# ��������
		self.resLoader = None							# resource loading manager
		self.helper = None								# helper
		self.castIndicator = None						# ʩ��ָʾ��
		self.questRelatedNPCVisible = None				# �������NPC�ɼ���
		self.globalSkillMgr = None						# ȫ�����⼼�ܹ�����
		self.itemModel = None
		self.npcModel = None
		self.npcVoice = None
		self.mutexShowMgr = None						# ���ⴰ�ڹ�����

		self.textFormatMgr = None						# textFormat manager

		self.worldCamHandler = None						# ������ InWorld ״̬�д��������������������ģ��

		self.loginer = None								# login
		self.roleSelector = None						# role select
		self.roleCreator = None							# role clreate

		self.wordsProfanity = None						# vocabulary filter for chat( initialize in game init )
		self.acursor = None								# cursor animator( initialize in game init )
		self.damageStatistic = None						# ����˺�����ͳ��

		self.equipEfects = None							# effect of equip( initialize in game init )
		self.omm = None									# items manager( initialize in game init )
		self.itemsDict = None							# ( initialize in game init )
		self.randomEffect = None						# effect random manager
		self.spellEffect = None

		self.roleMaker = None							# ��ɫģ�͹�����
		self.effectMgr = None							# Ч��������
		self.equipParticle = None						# װ��ǿ������Ƕ��Ϣ
		self.skillEffect = None							# ����Ч��
		self.modelFetchMgr = None						# ģ�ͺ��̼߳��ع���ģ��
		self.areaEffectMgr = None						# ����Ч������
		self.enEffectMgr = None							# ����Ч������
		self.cameraFlyMgr = None						# ����ͷ���й���
		self.actionMgr = None							# ��������ģ��
		self.cameraEventMgr = None						# ����ͷ�¼�����
		self.spaceEffectMgr = None						# ������Ч����

		self.opIndicator = None							# ��Ҳ���ָʾ��
		self.spaceCopyFormulas = None					# ���ŶӸ�����Ϣ������

		# -----------------------------------
		# config data sections
		# -----------------------------------
		self.loadingScreenGUI = None					# ��������
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
	if not csol.cursorInWindow():	# �������Ϸ������
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
	�������ڵ�
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
	ɾ��һ���� section
	"""
	pass

class PyConfiger( Singleton ) :
	"""
	ʵ��д py ����
	"""
	def __init__( self ) :
		self.__builders = {}							# ���������ַ���ת������
		self.__builders[tuple]	= self.__buildTuple		# Ԫ��
		self.__builders[list]	= self.__buildList		# ����
		self.__builders[dict]	= self.__buildDict		# �ֵ�


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __buildList( self, l, tabs ) :
		"""
		��������
		"""
		s = "["
		for e in l :
			s += "\n"
			s += tabs + self.__toString( e, tabs )
			s += ","
		return s + "\n%s]" % tabs

	def __buildTuple( self, t, tabs ) :
		"""
		����Ԫ�鴮
		"""
		s = "("
		for e in t :
			s += "%s," % self.__toString( e, tabs )
		return s + ")"

	def __buildDict( self, d, tabs ) :
		"""
		�����ֵ䴮
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
		�������ػ�����
		"""
		if isinstance( e, basestring ) :
			return "'%s'" % e
		return str( e )

	# ---------------------------------------
	def __toString( self, ele, tabs ) :
		"""
		����
		"""
		builder = self.__builders.get( type( ele ), self.__buildUndef )
		return builder( ele, tabs )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def read( self, path, default = None, isReload = False ) :
		"""
		��ȡһ�� py ����
		@type				path	 : str
		@param				path	 : ����·������ʽΪ��XX/XXX/XXXX.py
		@type				default  : alltypes
		@param				default  : ����ʧ��ʱ��Ĭ��ֵ
		@type				isReload : bool
		@param				isReload : �Ƿ����¼���
		@rtype						 : dict/list/tuple
		@return						 : �������ж������ֵ�( ע�⣺������ö�Σ����ص���Ȼ��ͬһ������ )
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
		���ֵ�д�� python ����
		@type				d	 : dict/list/tuple
		@param				d	 : Ҫд�����õ��ֵ�
		@type				path : str
		@param				path : ����·��
		@rtype					 : bool
		@return					 : д�ɹ����� True�����򷵻� False
		"""
		path = "entities/%s" % path
		f = None
		try :
			f = open( path, 'w' )
		except IOError, err :
			ERROR_MSG( err )
		else :
			text = "# -*- coding: gb18030 -*-\n"				# py ͷ
			text += "Datas = " + self.__toString( d, "\t" )	# ���ֵ�ϲ�Ϊ�ַ���
			f.write( text )
			f.close()
			return True
		return False

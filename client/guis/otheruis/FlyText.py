# -*- coding: gb18030 -*-
#
# $Id : FlyText.py,v 1.1 2006/09/20 09 :02 :40 panguankong Exp $

"""
implement damage text class
-- 2007/jan/08 : created by huangyw
"""


import time
import BigWorld
import GUI
import Pixie
from bwdebug import *
from Function import Functor
from guis import *
from guis.common.RootGUI import RootGUI
from AbstractTemplates import Singleton
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from config.skill.Skill import SkillDataMgr as skMgr
import utils
import csdefine
import ResMgr
import Font
import csstring

output_del_info = False

# 数学模型：v在时间t内从va线性变化到vb，求：
# 经过了tx时间后，vx的值是多少
def vx( va, vb, t, tx ):
	if tx <= t:
		return va + tx * (vb - va) / t
	else:
		return vb

def linearZoomOut( base, tx, t, maxScale ):
	"""
	线性缩小
	"""
	return vx(base * maxScale, base, t, tx)

def linearZoomIn( base, tx, t, maxScale ):
	"""
	线性放大
	"""
	return vx(base, base * maxScale, t, tx)

def linearScale( base, tx, zoomIn_t=0.12, zoomOut_t=0.15, maxScale=2.65 ):
	"""
	线性缩放，先放大然后恢复
	"""
	if tx <= zoomIn_t:
		return linearZoomIn(base, tx, zoomIn_t, maxScale)
	else:
		return linearZoomOut(base, tx-zoomIn_t, zoomOut_t, maxScale)


# --------------------------------------------------------------------
# implement FlyTextBaseGUI
# This GUI implements the FlyText daping from the top of the player
# --------------------------------------------------------------------
class FlyTextBaseGUI( PyGUI ):
	"""
	"""
	__cc_fly_texts = []

	def __init__( self, bg ) :
		PyGUI.__init__( self, bg )
		self.posZ = 1.0
		self.startTime_ = time.time()
		self.lastTime_ = 0
		FlyTextBaseGUI.__cc_fly_texts.append( self )

	def __del__( self ) :
		PyGUI.__del__( self )
		if Debug.output_del_FlyText :
			INFO_MSG( str( self ) )

	# ---------------------------------------------------------------
	# protected:
	# these methods should be inherited and implemented by it's sub-class
	# ---------------------------------------------------------------
	def updatePosition_( self, passTime ) :
		pass

	def updateColor_( self, passTime ) :
		pass

	def updateSize_( self, passTime ) :
		pass

	# ---------------------------------------------------------------
	# protected:
	# ---------------------------------------------------------------
	def onUpdate_( self ) :
		passTime = time.time() - self.startTime_
		if passTime >= self.lastTime_ :
			if self.pyParent:
				self.pyParent.delPyChild( self )
			self.dispose()
		else :
			self.updatePosition_( passTime )
			self.updateColor_( passTime )
			self.updateSize_( passTime )
			BigWorld.callback( 0.06, self.onUpdate_ )

	# ---------------------------------------------------------------
	# public:
	# ---------------------------------------------------------------
	def dispose( self ) :
		PyGUI.dispose( self )
		if self in FlyTextBaseGUI.__cc_fly_texts :
			FlyTextBaseGUI.__cc_fly_texts.remove( self )
		self.visible = False
		recycleInst( self.__class__, self )

	def startFly( self, entityID, lastTime = 1.5 ) :
		entity = BigWorld.entities.get( entityID, None )
		if not entity :
			self.dispose()
		else :
			self.startTime_ = time.time()
			self.lastTime_ = lastTime
			self.onUpdate_()
			self.visible = True


class FlyFadeText( FlyTextBaseGUI ):

	def __init__( self, label ) :
		FlyTextBaseGUI.__init__( self, label )

		self.fader_ = GUI.AlphaShader()
		self.fader_.speed = 0.3
		label.addShader( self.fader_ )
		self.primalSize_ = (0, 0)

	def init( self, text, font ) :
		"""
		"""
		label = self.getGui()
		label.explicitSize = False
		label.text = csstring.toWideString(text)
		label.font = font
		self.fader_.value = 1.0
		self.primalSize_ = (label.width, label.height)

	def updateColor_( self, passTime ) :
		"""
		"""
		if passTime > self.lastTime_ * 0.4 :
			self.fader_.value *= 0.65


# --------------------------------------------------------------------
# implement DmgText
# --------------------------------------------------------------------
class DmgText( FlyFadeText ) :
	"""
	"""
	def __init__( self ) :
		label = GUI.Text("")
		FlyFadeText.__init__( self, label )

	def initPosition( self ):
		"""
		初始化位置
		"""
		self.bottom -= 32

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def updatePosition_( self, passTime ) :
		"""
		"""
		self.bottom += 8

	def updateColor_( self, passTime ) :
		"""
		"""
		if passTime > self.lastTime_ / 2.5 :
			self.fader_.value *= 0.65

	def updateSize_( self, passTime ) :
		"""
		"""
		pass

	def startFly( self, entityID, lastTime = 1.5, sizeScale = 1 ) :
		"""
		"""
		w, h = self.primalSize_
		self.primalSize_ = (w*sizeScale, h*sizeScale)
		self.gui.explicitSize = True
		self.initPosition()
		FlyTextBaseGUI.startFly( self, entityID, lastTime )


# --------------------------------------------------------------------
# implement HealthText class
# --------------------------------------------------------------------
class HealthText( DmgText ):
	"""
	"""
	def __init__( self ) :
		DmgText.__init__( self )
		self.gui.font = "healthtext.font"
		self.__delta = 0

	def init( self, text ) :
		label = self.getGui()
		label.explicitSize = False
		label.text = text
		self.fader_.value = 1.0
		self.primalSize_ = (label.width, label.height)
		self.__delta = 0

# --------------------------------------------------------------------
# implement TargetDmgText class
# --------------------------------------------------------------------
class TargetDmgText( DmgText ):
	"""
	"""
	def __init__( self ):
		DmgText.__init__( self )

	def initPosition( self ):
		pass

	# ----------------------------------------------------------------
	# protected:
	# ----------------------------------------------------------------
	def updatePosition_( self, passTime ):
		"""
		"""
		self.bottom -= 5

	def updateSize_( self, passTime ):
		# 0.2秒内放大到8.0倍
		label = self.getGui()
		label.width = linearZoomIn( self.primalSize_[0], passTime, 0.2, 8.0 )
		label.height = linearZoomIn( self.primalSize_[1], passTime, 0.2, 8.0 )

# --------------------------------------------------------------------
# implement MagicText class
# --------------------------------------------------------------------
class MagicText( DmgText ):
	"""
	"""
	def __init__( self ):
		DmgText.__init__( self )
		self.gui.font = "magictext.font"
		self.__delta = 0

	def init( self, text ):
		label = self.getGui()
		label.explicitSize = False
		label.text = text
		self.fader_.value = 1.0
		self.primalSize_ = (label.width, label.height)
		self.__delta = 0

	def initPosition( self ):
		"""
		初始化位置
		"""
		self.bottom -= 10

# --------------------------------------------------------------------
# implement ExpText class
# --------------------------------------------------------------------
class ExpText( DmgText ):
	"""
	"""
	def __init__( self ) :
		DmgText.__init__( self )
		self.gui.font = "exptext.font"
		self.bottom -= 35

	def init( self, text ) :
		label = self.getGui()
		label.explicitSize = False
		label.text = ";<=>?" + text
		self.fader_.value = 1.0
		self.primalSize_ = (label.width, label.height)

	def initPosition( self ):
		pass

	# ----------------------------------------------------------------
	# protected:
	# ----------------------------------------------------------------
	def updatePosition_( self, passTime ) :
		pass

	def updateSize_( self, passTime ) :
		pass

	# ----------------------------------------------------------------
	# public:
	# ----------------------------------------------------------------
	def startFly( self, entityID, lastTime = 1.8 ) :
		"""
		"""
		DmgText.startFly( self, entityID, lastTime )

# --------------------------------------------------------------------
# implement AccumText class
# --------------------------------------------------------------------
class AccumText( DmgText ):
	"""
	"""
	def __init__( self ) :
		DmgText.__init__( self )
		self.gui.font = "exptext.font"
		self.__delta = 0

	def init( self, text ) :
		label = self.getGui()
		label.explicitSize = False
		label.text = text
		label.colour = ( 238, 199, 16, 255 )
		self.fader_.value = 1.0
		self.primalSize_ = (label.width, label.height)
		self.__delta = 0

	def initPosition( self ):
		pass

	# ----------------------------------------------------------------
	# protected:
	# ----------------------------------------------------------------
	def updatePosition_( self, passTime ) :
		"""
		"""
		if passTime < 0.4 :										# 缩放时缓慢上升
			self.bottom -= 5
			self.left += 8
		else :													# 回复后快速上升
			self.bottom -= 20 * 0.55 ** self.__delta
			self.left += 25 * 0.55 ** self.__delta
			self.__delta += 1

	def updateSize_( self, passTime ) :
		pass

# --------------------------------------------------------------------
# implement FlySkillName class
# --------------------------------------------------------------------
class FlySkillName( FlyTextBaseGUI ) :
	"""
	"""
	__cg_bg = None

	def __init__( self ) :
		if FlySkillName.__cg_bg is None :
			FlySkillName.__cg_bg = GUI.load( "guis/general/skillnames/skillname.gui" )

		bg = util.copyGuiTree( FlySkillName.__cg_bg )
		uiFixer.firstLoadFix( bg )
		bg.horizontalAnchor = "CENTER"
		bg.verticalAnchor = "CENTER"
		FlyTextBaseGUI.__init__( self, bg )
		self.__fader = bg.fader

		self.__delta = 0
		self.__primalSize = self.size

	def init( self, skillID ) :
		self.__delta = 0
		self.__fader.value = 1.0
		self.__loadSkillName( skillID )


	# ---------------------------------------------------------------
	# protected:
	# ---------------------------------------------------------------
	def updatePosition_( self, passTime ) :
		"""
		"""
		if passTime < 0.4 :										# 缩放时缓慢上升
			self.bottom -= 10
		else :													# 回复后快速上升
			self.bottom -= 35 * 0.45 ** self.__delta
			self.__delta += 1

	def updateColor_( self, passTime ) :
		"""
		"""
		if passTime > self.lastTime_ / 2 :
			self.__fader.value *= 0.55

	def updateSize_( self, passTime ) :
		"""
		"""
		# 先放大后缩小，在前面0.1秒放到最大，在随后的0.15秒内恢复回原始大小
		self.width = linearScale( self.__primalSize[0], passTime )
		self.height = linearScale( self.__primalSize[1], passTime )


	# ----------------------------------------------------------------
	# private:
	# ----------------------------------------------------------------
	def __loadSkillName( self, skillID ) :
		"""
		"""
		#preSkillID = str( skillID )[:-3]	# 已经修改了技能图片的加载方式
		self.texture = "maps/skillnames/%s.tga" % skillID


class FlyRestText( FlyTextBaseGUI ):

	__cg_bg = None

	def __init__( self ) :
		if FlyRestText.__cg_bg is None :
			FlyRestText.__cg_bg = GUI.load( "guis/general/skillnames/resttext.gui" )

		bg = util.copyGuiTree( FlyRestText.__cg_bg )
		uiFixer.firstLoadFix( bg )
		FlyTextBaseGUI.__init__( self, bg )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.__fader = bg.fader
		self.__delta = 0
		self.__primalSize = self.size
		self.__startTime = time.time()
		self.__lastTime = 0
		self.__flashCBID = 0

	def init( self ) :
		self.__delta = 0
		self.__fader.value = 1.0
		self.texture = "guis/general/skillnames/rest.dds"

	# ---------------------------------------------------------------
	# protected:
	# ---------------------------------------------------------------
	def updatePosition_( self, passTime ) :
		"""
		"""
		if passTime < 0.4 :										# 缩放时缓慢上升
			self.bottom -= 10
		else :													# 回复后快速上升
			self.bottom -= 35 * 0.45 ** self.__delta
			self.__delta += 1

	def __updateColor( self, passTime ) :
		"""
		"""
		if passTime > self.__lastTime / 2 :
			self.__fader.value *= 0.55

	def __updateSize( self, passTime ) :
		"""
		"""
		# 先放大后缩小，在前面0.1秒放到最大，在随后的0.15秒内恢复回原始大小
		self.width = linearScale( self.__primalSize[0], passTime )
		self.height = linearScale( self.__primalSize[1], passTime )

	def __onUpdate( self ) :
		passTime = time.time() - self.__startTime
		if passTime >= self.__lastTime :
			self.visible = False
			BigWorld.cancelCallback( self.__flashCBID )
			self.__flashCBID = 0
			if self.pyParent:
				self.pyParent.delPyChild( self )
			self.dispose()
		else :
			self.__updateColor( passTime )
			self.__updateSize( passTime )
			self.__flashCBID = BigWorld.callback( 0.06, self.__onUpdate )

	# ---------------------------------------------------------------
	# public:
	# ---------------------------------------------------------------
	def startFly( self, entityID, lastTime = 2 ) :
		self.__startTime = time.time()
		self.__lastTime = lastTime
		self.__onUpdate()
		self.visible = True

class FlyBatterText( RootGUI, Singleton ):

	__cg_bg = None

	def __init__( self ):
		Singleton.__init__( self )
		if FlyBatterText.__cg_bg is None :
			FlyBatterText.__cg_bg = GUI.load( "guis/general/skillnames/batter.gui" )
		bg = util.copyGuiTree( FlyBatterText.__cg_bg )
		uiFixer.firstLoadFix( bg )
		RootGUI.__init__( self, bg )
		self.h_dockStyle = "RIGHT"
		self.posZSegment = ZSegs.LMAX
		self.moveFocus = False
		self.escHide_ = False
		self.focus = False
		self.__stCurComb = bg.stCurComb
		self.__stCurComb.explicitSize = True
		self.__pyStCurComb = StaticText( self.__stCurComb )
		self.__pyStCurComb.focus = False
		self.__pyStCurComb.text = ""
		self.__pyBatter = PyGUI( bg.batter )
		self.__pyBatter.focus = False
		try :
			self.__pyStCurComb.font = "combtext.font"
		except :
			self.__pyStCurComb.font = "system_small.font"
			self.__pyStCurComb.font = "system_small.font"
		self.__unitSize = ( self.__stCurComb.width, self.__stCurComb.height )
		self.__primalSize = self.__unitSize
		self.__bgShader = bg.shader
		self.__bgShader.value = 1.0
#		self.__bgShader.speed = 0.5
		self.__textShader = bg.stCurComb.shader
		self.__textShader.value = 1.0
		self.__startTime = time.time()
		self.__lastTime = 0
		self.__textCBID = 0
		self.activable_ = False  # 窗口不被激活
		self.addToMgr( "flyBatterText" )

	def showHomingComb( self, count ):
		"""
		开始连击
		"""
		self.__bgShader.value = 1.0
		BigWorld.cancelCallback( self.__textCBID )
		self.__textCBID = BigWorld.callback( 0.0, Functor( self.__flashText, count ) )
		self.visible = True

	def updatePosition_( self, passTime ) :
		"""
		"""
		if passTime < 0.4 :										# 缩放时缓慢上升
			self.bottom -= 10
		else :													# 回复后快速上升
			self.bottom -= 35 * 0.45 ** self.__delta
			self.__delta += 1

	def __updateColor( self, passTime ) :
		"""
		"""
		if passTime > self.__lastTime / 2 :
			self.__textShader.value *= 0.55
			self.__bgShader.value *= 0.55

	def __updateSize( self, passTime ) :
		"""
		"""
		# 先放大后缩小，在前面0.1秒放到最大，在随后的0.15秒内恢复回原始大小
		self.__stCurComb.width = linearScale( self.__primalSize[0], passTime )
		self.__stCurComb.height = linearScale( self.__primalSize[1], passTime )
		self.__pyStCurComb.right = self.__pyBatter.left - 15.0

	def __onUpdate( self ) :
		passTime = time.time() - self.__startTime
		if passTime >= self.__lastTime :
			self.__pyStCurComb.visible = False
			BigWorld.cancelCallback( self.__textCBID )
			self.__textCBID = 0
			self.visible = False
		else :
			self.__updateColor( passTime )
			self.__updateSize( passTime )
			self.__textCBID = BigWorld.callback( 0.06, self.__onUpdate )

	def __flashText( self, count ):
		"""
		当前连击数
		"""
		self.__startTime = time.time()
		self.__lastTime = 2.0
		self.__textShader.value = 1.0
		self.__pyStCurComb.text = str( count )
		if count < 30:
			self.__pyStCurComb.font = "combtext.font"
			self.__pyBatter.texture = "guis/general/skillnames/batter.dds"
		else:
			self.__pyStCurComb.font = "combtext_0.font"
			self.__pyBatter.texture = "guis/general/skillnames/batter_0.dds"
		self.__pyBatter.right = self.right - 5.0
		units = len( str(count) )
		self.__primalSize = ( self.__unitSize[0]*units, self.__unitSize[1] )
		self.__pyStCurComb.visible = True
		self.__onUpdate()


class CounterText( FlyFadeText ):

	def __init__( self, explodeTime=0.1, maxScale=2.5 ):
		label = GUI.Text("")
		label.position.y = 0.3
		FlyFadeText.__init__( self, label )
		self._explodeTime = explodeTime
		self._maxScale = maxScale

	def init( self, text, font=Font.defFont, size=Font.defFontSize ) :
		"""
		"""
		self.gui.fontDescription({"size":size})
		FlyFadeText.init( self, text, font )

	def updateSize_( self, passTime ):
		label = self.getGui()
		label.width = linearZoomIn( self.primalSize_[0], passTime, self._explodeTime, self._maxScale )
		label.height = linearZoomIn( self.primalSize_[1], passTime, self._explodeTime, self._maxScale )

	def startFly( self, entityID, lastTime = 1.5 ) :
		"""
		"""
		self.startTime_ = time.time()
		self.lastTime_ = lastTime
		self.gui.explicitSize = True
		self.onUpdate_()
		self.visible = True
		GUI.addRoot( self.gui )

class Counter( Singleton ):

	def __init__( self ):
		self._array = None
		self._arrayIter = None
		self._alarm = ""
		self._counting_cbid = 0

	def build( self, start, stop, step=1, alarm="" ):
		"""生成计数序列"""
		self._array = xrange(start, stop, step)
		self._alarm = alarm

	def start( self ):
		"""开始计数"""
		self._arrayIter = self._array.__iter__()
		self.__stopCounting()
		self.__count()

	def __count( self ):
		try:
			num = self._arrayIter.next()
			pyText = CounterText()
			pyText.init(str(num), "dmgtext_n2r.font")
			pyText.startFly(0, 0.3)
			self._counting_cbid = BigWorld.callback( 1.0, self.__count )
		except StopIteration:
			if self._alarm:
				pyText = CounterText()
				pyText.init(self._alarm, size=17)
				shader = Font.createLimnShader( Font.LIMN_OUT, (255,0,0,255) )
				pyText.gui.addShader( shader )
				pyText.startFly(0, 1)

	def __stopCounting( self ):
		if self._counting_cbid:
			BigWorld.cancelCallback(self._counting_cbid)
			self._counting_cbid = 0


class FloatingText(DmgText):

	def initPosition( self ):
		pass

	def updatePosition_( self, passTime ) :
		pass

	def updateSize_( self, passTime ):
		"""
		"""
		# 先放大后缩小，在前面0.1秒放到最大，在随后的0.15秒内恢复回原始大小
		label = self.getGui()
		label.width = linearScale( self.primalSize_[0], passTime, 0.1, 0.15, 2.5 )
		label.height = linearScale( self.primalSize_[1], passTime, 0.1, 0.15, 2.1 )

	def startFly( self, entityID, text ) :
		"""
		"""
		self.init(text, "dmgtext_n2r.font")
		GUI.addRoot(self.gui)
		DmgText.startFly(self, entityID, 1.5, 1.5)
		entity = BigWorld.entities.get(entityID)
		if entity:
			screenWidth, screenHeight = BigWorld.screenSize()
			self.center = max(0, min(entity.getHeadPosition()[0], screenWidth))
			self.middle = max(0, min(entity.getHeadPosition()[1], screenHeight))


# --------------------------------------------------------------------
# implement FlyTextDevice class
# --------------------------------------------------------------------
class FlyTextDrive :
	"""
	event driver
	"""
	def __init__( self ) :
		self.__triggers = {}
		self.__triggers["EVT_ON_SHOW_MISS_ATTACK"] = self.__showMissAttack
		self.__triggers["EVT_ON_SHOW_DEADLY_ATTACK"] = self.__showDeadlyAttack
		self.__triggers["EVT_ON_HOMING_SPELL_COMBO"] = self.__showHomingComb
		self.__triggers["EVT_ON_SHOW_COUNT_DOWN"] = self.__showCountDown
		self.__triggers["EVT_ON_SHOW_FLOATING_TEXT"] = self.__showFloatingText

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

		createInsts( DmgText, 100 )										# 预创建飞扬文字的实例
		createInsts( TargetDmgText, 50 )
		createInsts( MagicText, 50 )
		createInsts( HealthText, 5 )
		createInsts( ExpText, 10 )
		createInsts( FlySkillName, 10 )
		createInsts( FlyRestText, 10 )
		createInsts( AccumText, 10 )
		createInsts( FloatingText, 50 )

	def __del__( self ) :
		self.dispose()

	def dispose( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __showMissAttack( self, entityID ) :
		"""
		闪避
		"""
		try : entity = BigWorld.entities[entityID]
		except : return
		visible = self.__getTextVisible( entityID, "hitDamage" )
		if not visible: return
		p = Pixie.create( "particles/hiteffect/miss.xml" )
		model = entity.getModel()
		if model is None: return
		model.node( "HP_head" ).attach( p )
		functor = Functor( self.__force, p )
		functor1 = Functor( self.__detach, p, entity )
		BigWorld.callback( 0.01, functor )
		BigWorld.callback( 3.0, functor1 )

	def __force( self, p, entity = None ):
		p.force()

	def __detach( self, p, entity ):
		try:
			entity.getModel().node( "HP_head" ).detach( p )
		except:
			pass

	def __showDeadlyAttack( self, entityID ) :
		"""
		暴击伤害
		"""
		visible = self.__getTextVisible( entityID, "hitDamage" )
		entity = BigWorld.entities.get( entityID, None )
		if entity is None:return
		if not visible: return
		p = Pixie.create( "particles/hiteffect/baoji.xml" )
		model = entity.getModel()
		if model is None: return
		model.node( "HP_head" ).attach( p )
		functor = Functor( self.__force, p )
		functor1 = Functor( self.__detach, p, entity )
		BigWorld.callback( 0.01, functor )
		BigWorld.callback( 3.0, functor1 )

	def __showHomingComb( self, count ):
		"""
		显示连击技能comb
		"""
#		combVisible = rds.viewInfoMgr.getSetting( "roleCombat", "homingComb" )
#		if not combVisible:return
		flyBatterText = FlyBatterText()
		flyBatterText.showHomingComb( count )

	def __getTextVisible( self, entityID, itemKey ):
		player = BigWorld.player()
		playerId = player.id
		actPet = player.pcg_getActPet()
		target = player.targetEntity
		petId = 0
		targetId = 0
		visible = True
		infoKey = ""
		if actPet:
			petId = actPet.id
		if target and target.id != playerId:
			targetId = target.id
		if entityID == playerId:
			infoKey = "roleCombat"
		elif entityID == petId:
			infoKey = "petCombat"
		if not entityID in [playerId, petId]:
			infoKey = "targetCombat"
		if infoKey == "":return visible
		else:
			visible = rds.viewInfoMgr.getSetting( infoKey, itemKey )
		return visible

	def __showCountDown( self, count, alarm="" ):
		"""
		显示倒计时
		@param	count : 计数值
		@param	alarm : 警报文字
		"""
		c = Counter()
		c.build( count, 0, -1, alarm )
		c.start()

	def __showFloatingText( self, entityID, text ):
		"""显示漂浮文本"""
		pyText = getInst(FloatingText)
		pyText.startFly(entityID, text)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )


# --------------------------------------------------------------------
# 预先创建实例
# --------------------------------------------------------------------
Fly_Text_Pool = {}
def createInsts( CLS, amount ) :
	global Fly_Text_Pool
	insts = Fly_Text_Pool.get( CLS )
	if insts is None :
		insts = []
		Fly_Text_Pool[ CLS ] = insts
	for i in xrange( amount ) :
		inst = CLS()
		inst.visible = False
		GUI.addRoot( inst.gui )
		insts.append( inst )

def getInst( CLS ) :
	global Fly_Text_Pool
	insts = Fly_Text_Pool.get( CLS )
	if insts is None :
		return None
	if len( insts ) == 0 :
		inst = CLS()
		inst.visible = False
		return inst
	return insts.pop()

def recycleInst( CLS, inst ):
	global Fly_Text_Pool
	insts = Fly_Text_Pool.get( CLS )
	if insts is not None :
		insts.append( inst )

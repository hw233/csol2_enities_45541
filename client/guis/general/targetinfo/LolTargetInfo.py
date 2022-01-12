# -*- coding: gb18030 -*-
#

import csdefine
import csconst
import GUIFacade
import BigWorld
import csstatus
import Const
from guis import *
from LabelGather import labelGather
from AbstractTemplates import Singleton
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from BuffItem import BuffItem

NAME_LIMIT_SHOW_LEN = 16 # NPC������ʾ��������
YXLM_BUFF_SOURCE_TYPES = (
	csdefine.BUFF_ORIGIN_YXLM_COEXISTENT,
	csdefine.BUFF_ORIGIN_YXLM,
	)

class LolTargetInfo( Singleton, RootGUI ):

	def __init__( self ):
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/targetinfo/lolcopy/bg.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.escHide_			= False				# �� esc ����������
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.addToMgr( "lolTargetInfo")

		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.moveFocus		 = False
		self.__target = None
		self.__pyBuffItems = []						# �������� buff ����
		self.__pyDuffItems = []						# �������� debuff ����
		self.__pySItems = []						# Ŀ�������buff����Ӣ�����˸���Boss��buff
		self.__reBuffsCBID = 0
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		self.__pyHead = PyGUI( wnd.head )

		self.__pyLbName = StaticText( wnd.lbName )
		self.__pyLbLevel = StaticText( wnd.lbLevel )
		self.__pyHPBar = ProgressBar( wnd.hpBar )
		self.__pyHPBar.clipMode = "RIGHT"

		self.__pyLevelBg = PyGUI( wnd.levelBg)
		self.__pyLevelBg.visible = True

		self.__pyLbHP = StaticText( wnd.lbHP )
		self.__pyLbHP.fontSize = 12
		self.__pyLbHP.text = ""
		self.__pyLbHP.h_anchor = 'CENTER'

		self.__pyLbComef = StaticText( wnd.lbComef )
		self.__pyLbComef.text = ""

		tempPySBuffs = []
		for name, item in wnd.children:
			if name.startswith( "sItem_"):
				index = int( name.split( "_")[1] )
				pySItem = BuffItem( item.item )
				tempPySBuffs.append( (index, pySItem) )
		tempPySBuffs.sort( key = lambda i : i[0] )
		self.__pySItems = [i[1] for i in tempPySBuffs]

		labelGather.setLabel( wnd.combText, "TargetInfo:main", "miComef" )

	def dispose( self ) :
		self.__deregisterTriggers()
		RootGUI.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ENTITY_HP_CHANGED"]		= self.__onHPChanged
		self.__triggers["EVT_ON_ENTITY_HP_MAX_CHANGED"]	= self.__onHPChanged
		self.__triggers["EVT_ON_TARGET_BUFFS_CHANGED"]	= self.__setBuffItems
		self.__triggers["EVT_ON_TARGET_MODEL_CHANGED"] = self.__onTargetModelChanged
		self.__triggers["EVT_ON_TARGET_POWER_CHANGED"] = self.__onTargetPowerChanged
		for eventMacro in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( eventMacro, self )

	def onShowTargetInfo( self, target ):
		RootGUI.hide( self )
		self.__target = target
		if target.getEntityType() in Const.DIRECT_TALK:	# �ɼ��㲻��ʾĿ����Ϣ by ����
			return
		title = target.getTitle()
		name = target.getName()
		if name == "":
			return
		if target.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) or \
		target.isEntityType( csdefine.ENTITY_TYPE_NPC ):
			if len( name ) > NAME_LIMIT_SHOW_LEN:
				name = "%s..."%name[:12]
		if hasattr( target, "level" ):
			level = target.getLevel()
			self.__onLevelChanged( target, 1, level )							# �������õȼ�
		self.__pyLbName.text = name							# ��������Ŀ������
		self.__setTargetFont()
		self.__onHPChanged( target, target.HP, target.HP_Max, target.HP )
		self.__pyHead.texture = target.getHeadTexture()		# ��������ͷ��
		self.__setBuffItems()								# �����趨BUFF
		self.__updateTargetPower( target.averageDamage() )
		self.show()

	def onHideTrargetInfo( self, target ) :
		"""
		����Ŀ��
		"""
		self.hide()

	# ---------------------------------------
	def __onHPChanged( self, entity, hp, hpMax, oldValue ) :
		"""
		Ŀ�� HP �ı��ʱ�򱻵���
		"""
		if entity != self.__target : return
		if hpMax > 0 :
			self.__pyHPBar.value = float( hp ) / hpMax
		else :
			self.__pyHPBar.value = 0
		if hp == 1 and hpMax == 1:
			self.__pyLbHP.text = ""
		else:
			self.__pyLbHP.text = "%d/%d" % ( hp, hpMax )

	def __onTargetModelChanged( self, entity, oldModel, newModel ):
		"""
		�Ƿ�������Ϣ
		"""
		if entity != self.__target:return
		headTexture = entity.getHeadTexture()
		if entity.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ): #������Ϣ״̬
			modelNumber = entity.currentModelNumber
			headTexture = g_npcmodel.getHeadTexture( modelNumber )
			self.__onLevelChanged( entity, 1, 0 )
			self.__onHPChanged( entity, 1, 1, 1 )
			self.__onMPChanged( entity, 1, 1 )
			self.__pyLbName.text = ""
			self.__pyClassMark.visible = False
		self.__pyHead.texture = headTexture

	def __onTargetPowerChanged( self, entityID, power ) :
		"""
		Ŀ���ս���������ı�
		"""
		if self.__target is None:return
		if entityID == self.__target.id :
			self.__updateTargetPower( power )

	def __onNameChanged( self, entityID, nameText ):
		"""
		���ָı�
		"""
		if self.__target and self.__target.id == entityID:
			self.__pyLbName.text = nameText

	def __setBuffItems( self ):
		"""
		ˢ������BUFF
		"""
		self.__clearAllBuffs()
 		self.__showTargetBuffs()

	def __showTargetBuffs( self ):
		"""
		��Ŀ�����ϵ�����buff��debuff����ʾ����
		"""
		buffInfos = []
		duffInfos = []
		yxlmBuffs = []
		if self.__target:
			for buffItem in self.__target.attrBuffItems:
				if self.__target.getSourceTypeByBuffIndex(buffItem.buffIndex) in YXLM_BUFF_SOURCE_TYPES:
					yxlmBuffs.append( buffItem )
				elif buffItem.baseItem.isMalignant():
					duffInfos.append( buffItem )
				else:
					buffInfos.append( buffItem )
		self.__updateSBuffs( yxlmBuffs )
		self.__updateBuffItems( duffInfos, self.__pyDuffItems )
		self.__updateBuffItems( buffInfos, self.__pyBuffItems )
		self.__layoutBuffs()

	def __cancelUpdateCallback( self ):
		"""
		ȡ��buff�Զ�����
		"""
		if self.__reBuffsCBID != 0:
			BigWorld.cancelCallback( self.__reBuffsCBID )
			self.__reBuffsCBID = 0

	def __updateBuffItems( self, buffItems, pyBuffItems ):
		"""
		����buff��Ϣ��������
		"""
		# ����Ѿ���BUFF��ʾ�������ˣ�����һ�¾�����
		for index, itemInfo in enumerate( buffItems ):
			if index < len( pyBuffItems ):
				pyBuffItems[ index ].update( itemInfo )
			else:
				self.__onAddBuff( itemInfo, pyBuffItems )

		# ��������BUFFͼ��
		n = len( pyBuffItems ) - len( buffItems )
		while n > 0:
			pyBuffItems.pop(-1).dispose()
			n = n - 1

	def __clearAllBuffs( self ):
		"""
		ɾ������BUFF / DeBuff
		"""
		self.__cancelUpdateCallback()
		self.__updateSBuffs([])
		for pyItem in self.__pyBuffItems :
			pyItem.dispose()
		for pyItem in self.__pyDuffItems :
			pyItem.dispose()
		self.__pyBuffItems = []
		self.__pyDuffItems = []

	def __onAddBuff( self, itemInfo, pyBuffItems ):
		"""
		����һ��BUFF / DeBuff
		"""
		item = GUI.load( "guis/general/targetinfo/common/buffItem.gui" )
		uiFixer.firstLoadFix( item )
		pyItem = BuffItem( item )
		self.addPyChild( pyItem )
		pyItem.update( itemInfo )
		pyBuffItems.append( pyItem )

	def __setTargetFont( self ):										# ��������������ɫ
		"""
		���ñ�ǩ��������ɫ
		"""
		# ���ݵȼ��Ĳ����ʾ��ͬ��������ɫ
		if not hasattr ( self.__target, "getLevel"):
			return
		dlevel = BigWorld.player().getLevel() - self.__target.getLevel()
		if dlevel <= -5 :
			self.__pyLbLevel.colour = 255, 0, 0, 255
		elif dlevel <= 4 :
			self.__pyLbLevel.colour = 255, 255, 255, 255
		elif dlevel  <= 25 :
			self.__pyLbLevel.colour = 0, 255, 0, 255
		else :
			self.__pyLbLevel.colour = 127, 127, 127, 255

	def __onLevelChanged( self, entity, oldLevel, level ):
		"""
		Ŀ��ȼ��ı��ʱ�򱻵���
		"""
		if entity != self.__target : return
		self.__setTargetFont()
		if level == "" or level == 0:
			self.__pyLevelBg.visible = False
			self.__pyLbLevel.text = ""
		else:
			self.__pyLevelBg.visible = True
			self.__pyLbLevel.text = str( level )

	def __layoutBuffs( self ) :
		"""
		�������� Buff / DeBuff ��λ��
		"""
		left = scale_util.getGuiLeft( self.gui.sItem_0 )
		top = scale_util.getGuiBottom( self.gui.sItem_0 ) + 2
		for idx, pyItem in enumerate( self.__pyBuffItems ):
			pyItem.left = left + idx * ( pyItem.width + 2 )
			pyItem.top = top

		for idx, pyItem in enumerate( self.__pyDuffItems ):
			pyItem.left = left + idx * ( pyItem.width + 2 )
			pyItem.top = top + pyItem.height + 5

	def __updateTargetPower( self, power ):
		"""
		����Ŀ���ս����ֵ
		"""
		self.__pyLbComef.text = str( power )

	# ---------------------------------------------------------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__target = None
		self.hide()

	def show( self ) :
		if self.__target is not None :
			RootGUI.show( self )

	def hide( self ) :
		#rds.targetMgr.unbindTarget( self.__target )
		self.__clearAllBuffs()
		self.__target = None
		RootGUI.hide( self )

	def __getPyBuffItemByIndex( self, buffIndex, pyBuffItems ):
		"""
		��ȡ�յ�����buff����
		"""
		for pyItem in pyBuffItems:
			if pyItem.itemInfo.buffIndex == buffIndex:
				return pyItem
		return None

	def __updateSBuffs( self, buffInfos ):
		"""
		���������buff
		"""
		buffAmount = len( buffInfos )
		for idx, pySItem in enumerate( self.__pySItems ):
			if idx < buffAmount:
				pySItem.update( buffInfos[idx] )
			else :
				pySItem.update( None )

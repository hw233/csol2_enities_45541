# -*- coding: gb18030 -*-
#
# $Id: MonsterName.py,v 1.13 2008-06-27 03:20:42 huangyongwei Exp $

"""
implement float name of the character
2009.02.13��tidy up by huangyongwei
"""

import csdefine
import event.EventCenter as ECenter
from guis import *
from guis.controls.StaticText import StaticText
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.PyGUI import PyGUI
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from FloatName import FloatName
from BubbleTip import BubbleTip
from LV_HP import LV_HP
from QuestMarks import QuestMarks
from NPCQuestSignMgr import npcQSignMgr
from guis.otheruis.FlyText import *
from guis.tooluis.CSRichText import CSRichText
from LabelGather import labelGather
from EnergyPanel import EnergyPanel
from DoubleName import DoubleName

class MonsterName( FloatName ) :
	__cg_wnd = None
	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/monstername.gui" )

	def __init__( self ) :
		if MonsterName.__cg_wnd is None:
			MonsterName.__cg_wnd = GUI.load( "guis/otheruis/floatnames/monstername.gui" )
		wnd = util.copyGuiTree(MonsterName.__cg_wnd)
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.viewInfoKey_ = "monster"
		self.isTarget = 0x00

		self.__persistence = False				# ʼ����ʾ�����Ϊ True������������Ƿ��ڹ������ϣ���ͷ�����ֶ���ʾ
		self.__initialize( wnd )

	def __initialize( self, wnd ) :
		
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleDoubleName( False )
		
		self.__pyLVHP = LV_HP( wnd.lvhp )
		self.__pyQstMarks = QuestMarks( wnd.qstMarks )
		self.__pySpecialSign = CSRichText( wnd.specialSign )
		self.__pySpecialSign.foreColor = ( 255, 255, 0,)
		self.__pyEnergyPanel = EnergyPanel( wnd.energyPanel )
		self.pyElements_ = [self.__pyLVHP, self.pyLbName_,self.__pyEnergyPanel, self.__pySpecialSign, self.__pyQstMarks]

	def dispose( self ) :
		self.__pyLVHP.dispose()
		self.__pyQstMarks.dispose()
		FloatName.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_ENTITY_LEVEL_CHANGED"] = self.__onLevelChanged
		self.triggers_["EVT_ON_NPC_QUEST_STATE_CHANGED"] = self.__onQuestStateChanged
		self.triggers_["EVT_ON_MONSTER_FIGHT_STATE_CHANGE"] = self.__onFightStateChange
		self.triggers_["EVT_ON_NPC_FLAGS_CHANGED"] = self.__onFlagsChanged   # flags�ı�
		self.triggers_["EVT_ON_SHOW_ACCUM_POINT"] = self.__onShowAccumPoint   #��ʾ����
		self.triggers_["EVT_ON_NPC_NAMECOLOR_CHANGED"] = self.__onNPCNameColorChanged
		self.triggers_["EVT_ON_BELONG_CHANGED"] = self.__onOwnerChanged		#belong�ı�
		self.triggers_["EVT_ON_MONSTER_ENERGY_CHANGED"] = self.__onMonsterEnergyChanged		#energy�ı�
		self.triggers_["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__onPlayerQuestStateChanged
		self.triggers_["EVT_ON_QUEST_LOG_ADD"] = self.__onPlayerAddQuest
		self.triggers_["EVT_ON_QUEST_LOG_REMOVED"]	= self.__onPlayerRemoveQuest
		FloatName.registerTriggers_( self )

	# -------------------------------------------------
	def __setNameColor( self ) :
		"""
		����������ɫ
		"""
		if not self.visible or self.entity_ == None : return
		player = BigWorld.player()
		colorName = 'c1'
		tongBDID = player.tong_dbID
		if self.entity_.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ) and \
		player.tong_isCityWarTong( tongBDID ): #����սmonster
			rightdbID = player.tongInfos.get( "right", 0 )
			leftdbID = player.tongInfos["left"]
			belong = self.entity_.belong
			defdbid = player.tongInfos.get( "defend", 0 )
			if defdbid > 0: #�з��ط�
				if tongBDID == belong: #ͬһ�����,��ɫ
					colorName = 'c47'
				else:
					if defdbid == belong: #���ط�
						colorName = "c8"#��ɫ
					else:
						if tongBDID == defdbid:
							colorName = "c8"#��ɫ
						else:
							colorName = "c48"
			else:
				if belong == tongBDID:
					colorName = 'c47'
				else:
					colorName = 'c48'
		elif self.entity_.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			relation = self.getRelation( self.entity_ )
			if relation == csdefine.RELATION_ANTAGONIZE:
				colorName = "c8"
			else:
				colorName = 'c47'
		elif self.entity_.isEntityType( csdefine.ENTITY_TYPE_XIAN_FENG ) or\
		self.entity_.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER ) or \
		self.entity_.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR ) or \
		self.entity_.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER ):
			relation = self.getRelation( self.entity_ )
			if relation == csdefine.RELATION_ANTAGONIZE:
				colorName = "c48"
			else:
				colorName = 'c47'
		elif self.entity_.isEntityType( csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE ):	#�����ս����
			relation = self.getRelation( self.entity_ )
			if relation == csdefine.RELATION_FRIEND:
				colorName = "c4"		#��ɫ
			else:
				colorName = 'c48'		#��ɫ
		else:
			nameColor = self.entity_.nameColor
			p_camp = player.getCamp()
			m_camp = self.entity_.getCamp()
			p_friendlyCamps = player.friendlyCamps
			m_friendlyCamps = self.entity_.friendlyCamps
			colorName = "c1"
			if nameColor == 0:
				colorName = "c48"
			elif nameColor == 3:
				colorName = "c6"
			elif nameColor == 4:
				colorName = "c47"
			else:
				if ( p_camp == m_camp ) or ( p_camp in m_friendlyCamps ) or ( m_camp in p_friendlyCamps ):
					colorName = "c47"
				else:
					colorName = "c48"
		self.pyLbName_.leftColor = cscolors[colorName]
	
	def __setHPBarColor( self, relation ):
		"""
		����Ѫ����ɫ
		"""
		player = BigWorld.player()
		if self.entity_.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ) and \
		player.tong_isCityWarTong( tongBDID ):
			if relation == csdefine.RELATION_FRIEND:
				color = "c4"
			else:
				color = "c48"
		elif self.entity_.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			if relation == csdefine.RELATION_FRIEND:
				color = "c4"
			else:
				color = "c48"
		elif self.entity_.isEntityType( csdefine.ENTITY_TYPE_XIAN_FENG ) or\
		self.entity_.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER ) or \
		self.entity_.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR ) or \
		self.entity_.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER ):
			if relation == csdefine.RELATION_FRIEND:
				color = "c4"
			else:
				color = "c48"
		else:
			nameColor = self.entity_.nameColor
			p_camp = player.getCamp()
			m_camp = self.entity_.getCamp()
			p_friendlyCamps = player.friendlyCamps
			m_friendlyCamps = self.entity_.friendlyCamps
			if nameColor == 0:	# Ĭ��ֵ
				if relation == csdefine.RELATION_FRIEND:
					color = "c4"
				else:
					color = "c48"
			elif nameColor == 3:
				color = "c6"
			elif nameColor == 4:
				color = "c4"
			else:
				if ( p_camp == m_camp ) or ( p_camp in m_friendlyCamps ) or ( m_camp in p_friendlyCamps ):
					color = "c4"
				else:
					color = "c48"
		self.__pyLVHP.color = cscolors[color]

	# -------------------------------------------------
	def __onLevelChanged( self, entity, oldLevel, newLevel ) :
		"""
		�ȼ��ı�ʱ������
		"""
		if self.entity_ == None or self.entity_.id == entity.id :
			self.__pyLVHP.level = newLevel
		self.layout_()

	def __updateViewInfo( self ):
		"""
		������Ϣ��ʾ���ã�����Ԫ�ؿɼ���
		"""
		if self.entity_ == None :return
		self.__persistence = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "persistence" )
		self.pyLbName_.toggleLeftName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" ) )
		self.__pyLVHP.toggleLevel( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "level" ) )
		self.__pyLVHP.toggleHPBar( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "HP" ) )
		self.__pyQstMarks.visible = not self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_QUEST )
		if self.visible == False : 
			self.visible = True
			self.__pyLVHP.visible = False
			self.pyLbName_.visible = False

		# ����Ŀ��δ�����ʾentity���ƹ���
		player = BigWorld.player()
		taskIndexMonsters = player.getTaskIndexMonsters()
		if hasattr( self.entity_, "className" ) and self.entity_.className in taskIndexMonsters:
			self.pyLbName_.toggleLeftName( True )

		if self.entity_.hasFlag( csdefine.ENTITY_FLAG_HEAD_ALWAYS_SHOW ):
			self.pyLbName_.toggleLeftName( True )
			self.__pyLVHP.toggleLevel( True )
			self.__pyLVHP.toggleHPBar( True )
		else:
			if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_NAME ):
				self.pyLbName_.visible = False
			if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_LEVEL ):
				self.__pyLVHP.toggleLevel( False )
				if not self.__persistence and not self.isTarget:
					self.__pyLVHP.toggleHPBar( False )
			if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_HPBAR ):
				self.__pyLVHP.toggleHPBar( False )
				if not self.__persistence and not self.isTarget:
					self.__pyLVHP.toggleLevel( False )
		if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_SHOW_NAME ):
			self.pyLbName_.toggleLeftName( True )

		if hasattr( self.entity_,"uiAttachsShow" ) and not self.entity_.uiAttachsShow:
			self.__pyLVHP.visible = False
			self.pyLbName_.visible = False
		if self.entity_.isEntityType( csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE ):
			if not self.entity_.belong:
				self.__pySpecialSign.visible = False
			elif self.entity_.belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
				self.__pySpecialSign.visible = True
				self.__pySpecialSign.text = labelGather.getText( "FloatName:monsterName", "attack" )
			elif self.entity_.belong == csdefine.CITY_WAR_FINAL_FACTION_DEFEND:
				self.__pySpecialSign.visible = True
				self.__pySpecialSign.text = labelGather.getText( "FloatName:monsterName", "defence" )
		else:
			self.__pySpecialSign.visible = False	
		if hasattr( self.entity_, "baseType") and self.entity_.baseType == csdefine.CITY_WAR_FINAL_BASE_BATTLE:
			self.__pyEnergyPanel.visible = True		
		else:
			self.__pyEnergyPanel.visible = False
		
		self.layout_()
	


	# -------------------------------------------------
	def __onQuestStateChanged( self, monster, id ) :
		"""
		����״̬�ı�ʱ������
		"""
		if self.entity_ == None or self.entity_.id != monster.id : return
		self.__pyQstMarks.flush()
		signStr = npcQSignMgr.getSignBySignID( id )
		self.__pyQstMarks.showMark( signStr )
		self.__updateViewInfo()

	def __onFightStateChange( self, monster ):
		"""
		ս��״̬�ı�,����Ѫ����ɫ
		"""
		if self.entity_ == None or self.entity_.id != monster.id : return
		relation = self.getRelation( monster )
		self.__setHPBarColor( relation )
		self.__pyQstMarks.flush()
		self.__updateViewInfo()

	def __onFlagsChanged( self, monster ):
		"""
		flags�ı䣬����Ѫ����ɫ
		"""
		if self.entity_ == None or self.entity_.id != monster.id: return
		relation = self.getRelation( monster )
		self.__setHPBarColor( relation )
		self.__updateViewInfo()

	def __onShowAccumPoint( self, entityID, accumPoint ):
		"""
		��ʾ������Ǯֵ
		"""
		if self.entity_ == None or entityID != self.entity_.id :return
		pyAccumText = getInst( AccumText )								# ���/ʧȥ����
		pyAccumText.init( str(accumPoint) )
		self.addPyChild( pyAccumText )
		pyAccumText.bottom = 16.0
		pyAccumText.center = self.__pyLVHP.center
		pyAccumText.startFly( entityID, 1.5 )

	def __onNPCNameColorChanged( self, entity ):
		"""
		nameColorֵ�ı�
		"""
		if self.entity_ == None or self.entity_.id != entity.id :return
		self.__setNameColor()
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
	
	def __onOwnerChanged( self, entity ):
		"""
		belong�ı�
		"""
		if self.entity_ == None or self.entity_.id != entity.id:return
		self.__setNameColor()
		self.__updateViewInfo()
		
	def __onMonsterEnergyChanged( self, entity ):
		"""
		energy�ı�
		"""
		if self.entity_ == None or self.entity_.id != entity.id:return
		self.__pyEnergyPanel.updateEnergy( entity.energy )

	def __onPlayerQuestStateChanged( self, questID, taskIndex ):
		"""
		quest state change
		"""
		if self.entity_ is None: return
		self.__updateViewInfo()

	def __onPlayerAddQuest( self, questID ):
		"""
		add quest
		"""
		if self.entity_ is None: return
		self.__updateViewInfo()

	def __onPlayerRemoveQuest( self, questID ):
		"""
		remove quest
		"""
		if self.entity_ is None: return
		self.__updateViewInfo()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onViewInfoChanged_( self, infoKey, itemKey, oldValue, value ) :
		if self.viewInfoKey_ != infoKey or self.entity_ == None: return
		if itemKey == "HP" :
			self.__pyLVHP.toggleHPBar( value )
		elif itemKey == "level" :
			self.__pyLVHP.toggleLevel( value )
		elif itemKey == "name":
			self.pyLbName_.toggleLeftName( value )
		elif itemKey == "persistence":
			self.__persistence = value
			self.visible = True
			if value == False:
				self.__pyLVHP.visible = False
				self.pyLbName_.visible = False
			else:
				self.pyLbName_.visible = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" )
				self.__pyLVHP.toggleLevel( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "level" ) )
				self.__pyLVHP.toggleHPBar( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "HP" ) )
		if rds.viewInfoMgr.getSetting( self.viewInfoKey_ , "persistence" ) == False:
			self.__pyLVHP.visible = False
			self.pyLbName_.visible = False
		FloatName.onViewInfoChanged_( self, infoKey, itemKey, oldValue, value )
		if self.entity_ == BigWorld.player().targetEntity :						# �����Ŀ�꣬һ����ʾ
			self.visible = True

		# ����Ŀ��δ�����ʾentity���ƹ���
		player = BigWorld.player()
		taskIndexMonsters = player.getTaskIndexMonsters()
		if hasattr( self.entity_, "className" ) and self.entity_.className in taskIndexMonsters:
			self.visible = True
			self.pyLbName_.toggleLeftName( True )

		if self.entity_.hasFlag( csdefine.ENTITY_FLAG_HEAD_ALWAYS_SHOW ):
			self.visible = True
			self.pyLbName_.toggleLeftName( True )
			self.__pyLVHP.toggleLevel( True )
			self.__pyLVHP.toggleHPBar( True )
		else:
			if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_NAME ):
				self.pyLbName_.visible = False
			if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_LEVEL ):
				self.__pyLVHP.toggleLevel( False )
				if not self.__persistence and not self.isTarget:
					self.__pyLVHP.toggleHPBar( False )
			if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_HPBAR ):
				self.__pyLVHP.toggleHPBar( False )
				if not self.__persistence and not self.isTarget:
					self.__pyLVHP.toggleLevel( False )
		if self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_SHOW_NAME ):
			self.visible = True
			self.pyLbName_.toggleLeftName( True )

		if hasattr( self.entity_,"uiAttachsShow" ) and not self.entity_.uiAttachsShow:
			self.__pyLVHP.visible = False
			self.pyLbName_.visible = False
		self.layout_()

	def onHPChanged_( self, hp, hpMax ) :
		"""
		����ֵ�ı�ʱ������
		"""
		rate = hpMax > 0 and float( hp ) / hpMax or 0
		self.__pyLVHP.hpValue = rate
	
	#--------------------------------------------------------------
	def showMsg_( self, msg, opGBLink = False ): #��̬��ʾ�������ݣ�ֻ��˵��ʱ����ʾ
		msg_temp = msg.split("/ltime")
		if len( msg_temp ) > 1 :
			msg = msg_temp[0]
			msg_lasttime = int(msg_temp[1])
		else :
			msg_lasttime = 5.0
		self.bubStyle = rds.viewInfoMgr.getSetting( "bubble", "style" ) #���ݷ��
		self.pyBubTip_ = getattr( self, "pyBubTip_", None )
		if self.pyBubTip_: #��֤һ��ֻ��һ������
			if self.pyBubTip_ in self.pyElements_:
				self.pyElements_.remove( self.pyBubTip_ )
				self.delPyChild( self.pyBubTip_ )
				self.pyBubTip_.dispose()
		if rds.viewInfoMgr.getSetting( "bubble", "visible" ) :			# �������ݲ��������������ˣ����NPC
			self.pyBubTip_ = BubbleTip()
			self.addPyChild( self.pyBubTip_ )
			self.pyElements_.append( self.pyBubTip_ )
			if rds.viewInfoMgr.getSetting( self.viewInfoKey_, "persistence" ) or self.isTarget :
				self.visible = True
			else:
				self.visible = False
			self.__updateViewInfo()
			self.pyBubTip_.visible = True
			self.pyBubTip_.show( msg, self.bubStyle, opGBLink )
			def fade() :
				self.pyBubTip_.hide()
				if self.pyBubTip_ in self.pyElements_:
					self.pyElements_.remove( self.pyBubTip_ )
				self.delPyChild( self.pyBubTip_ )
				self.pyBubTip_.dispose()
				self.__msgFadeCallback = 0
			self.__msgFadeCallback = BigWorld.callback( msg_lasttime, fade )
		self.layout_()
		
	def onAttachEntity_( self ):
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
		rate = self.entity_.HP_Max > 0 and float( self.entity_.HP ) / self.entity_.HP_Max or 0
		self.__pyLVHP.hpValue = rate
		self.visible = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "persistence" )
		
		
	def onDetachEntity_( self ):
		self.__pyLVHP.visible = False
		self.pyLbName_.visible = False
		self.__pyEnergyPanel.visible = False
		self.__pySpecialSign.visible = False
		self.__pyQstMarks.flush()
		self.__persistence = False
	
	def getRelation( self, monster ):
		"""
		��ȡ��������֮��Ĺ�ϵ
		"""
		player = BigWorld.player()
		if monster:
			return player.queryRelation( monster )
		return csdefine.RELATION_ANTAGONIZE

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		FloatName.onEnterWorld( self )
		self.__onLevelChanged( self.entity_, 0, self.entity_.getLevel() )
		self.visible = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "persistence" )
		if rds.targetMgr.getTarget() == self.entity_:	# ����պ���Ŀ��
			self.visible = True
		self.__updateViewInfo()
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
	# ---------------------------------------
	def onTargetFocus( self, *args ) :
		self.visible = True
		self.isTarget |= 0x01
		self.__updateViewInfo()
		if getattr( self, "pyBubTip_",None ):
			self.pyBubTip_.visible = rds.viewInfoMgr.getSetting( "bubble", "visible" )
		self.layout_()

	def onTargetBlur( self, *args ) :
		self.isTarget &= 0x10
		if BigWorld.player().targetEntity != self.entity_ and not self.__persistence :
			self.visible = False
			self.__updateViewInfo()
		if getattr( self, "pyBubTip_",None ):
			self.pyBubTip_.visible = rds.viewInfoMgr.getSetting( "bubble", "visible" )
		self.layout_()

	# ---------------------------------------
	def onBecomeTarget( self ) :
		self.visible = True
		self.isTarget |= 0x10
		self.__updateViewInfo()
		if getattr( self, "pyBubTip_",None ):
			self.pyBubTip_.visible = rds.viewInfoMgr.getSetting( "bubble", "visible" )
		self.layout_()
		

	def onLoseTarget( self ) :
		self.isTarget &= 0x01
		if not self.__persistence :
			self.visible = False
			self.__updateViewInfo()
		if getattr( self, "pyBubTip_",None ) :
			self.pyBubTip_.visible = rds.viewInfoMgr.getSetting( "bubble", "visible" )
		self.layout_()
	
	def flush( self ):
		"""
		ˢ��ģ�ͣ�����ģ�ͺ󣬽�ԭģ�͵�ͷ����ϢǨ�ƹ�ȥ��
		"""
		FloatName.flush( self )
		self.visible = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "persistence" )
		self.__updateViewInfo()

	def isMonsterName( self ):
		return True
		

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setVisible( self, visible ) :
		FloatName._setVisible( self, visible )
		self.__setNameColor()
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	visible = property( FloatName._getVisible, _setVisible )

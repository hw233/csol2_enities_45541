# -*- coding: gb18030 -*-
#
# $Id: RoleName.py,v 1.27 2008-06-27 03:20:42 huangyongwei Exp $

"""
implement float name of the character
2009.02.13��tidy up by huangyongwei
"""

import Const
import csconst
import csdefine
import event.EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from FloatName import FloatName
from RoleSigns import RoleSigns
from SignBoard import SignBoard
from DoubleName import DoubleName, TongName
from LabelGather import labelGather
from GlintFacade import glintFacade
from guis.otheruis.FlyText import *
from Function import Functor
from DoubleName import RoleDoubleName

PK_STATE_COLOR_MAP = {
	csdefine.PK_STATE_PROTECT			: ( 0, 255, 0, 255 ),
	csdefine.PK_STATE_ATTACK			: ( 153, 51, 0, 255 ),
	csdefine.PK_STATE_PEACE				: ( 255, 255, 255, 255 ),
	csdefine.PK_STATE_BLUENAME			: ( 0, 255, 255, 255 ),
	csdefine.PK_STATE_REDNAME			: ( 255, 0, 0, 255 ),
	csdefine.PK_STATE_ORANGENAME		: ( 255, 255, 0, 255 ),	# ԭ��������˵�е�С����������Ϊ����
	}

ROLE_RELATION_COLOR_MAP = {
	csdefine.RELATION_NONE			: ( 255, 255, 255, 255 ),	# ���κι�ϵ��һ������Ĭ��ֵ
	csdefine.RELATION_FRIEND		: ( 0, 255, 0, 255 ),		# ���ѹ�ϵ( ԭ����C_RELATION_FRIEND )
	csdefine.RELATION_NEUTRALLY		: ( 255, 255, 255, 255 ),	# ������ϵ( ԭ����C_RELATION_NEUTRALLY )
	csdefine.RELATION_ANTAGONIZE	: ( 255, 0, 255, 255 ),		# �жԹ�ϵ( ԭ����C_RELATION_ANTAGONIZE )
	csdefine.RELATION_NOFIGHT		: ( 0, 255, 0, 255 ),		# ��ս��ϵ
	}

GLINTNAME = labelGather.getText( "FloatName:role", "glintName" )

class RoleName( FloatName ) :
	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/rolename.gui" )

	_colors_map = { csdefine.RELATION_FRIEND: ( 0, 255, 0, 255 ),
					csdefine.RELATION_NEUTRALLY: ( 255, 255, 0, 255 ),
					csdefine.RELATION_ANTAGONIZE: ( 255, 0, 0, 255 ),
				}

	def __init__( self ) :
		wnd = GUI.load( "guis/otheruis/floatnames/rolename.gui" )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.viewInfoKey_ = "role"

		self.__corpsName = ""			# ��������
		self.__family = ""  			# ����
		self.__corpsDuty = ""			# ���ְ��
		self.__familyDuty = ""			# ����ְ��
		
		self.__targetFocus = False		#��ý���ʱ��ʾѪ��
		self.__becomeTarget = False		# ��Ϊtargetʱ��ʾѪ��

		self.__initialize( wnd )
#		self.__initElementsColor( role )

	def __initialize( self, wnd ) :
		
		self.pyLbName_ = RoleDoubleName( wnd.elemName )	
		self.pyLbName_.toggleDoubleName( False )
		
		self.__pyLbCorps = TongName( wnd.corpsName )			# ����������
		self.__pyLbCorps.toggleDoubleName( False )

		self.__pyLbFamily = DoubleName( wnd.familyName )		# �����������
		self.__pyLbFamily.toggleDoubleName( False )

		self.__pyHPBg = PyGUI( wnd.hpBg )						# HP bar
		self.__pyHPBg.visible = False
		self.__pyHPBar = ProgressBar( wnd.hpBg.hpBar )
#		rate = self.entity_.HP_Max > 0 and float( self.entity_.HP ) / self.entity_.HP_Max or 0
#		self.__pyHPBar.value = rate

		self.__pyLbSpecialSign = RoleSigns( wnd.lbSpecialSign )	# �������״̬��ǣ��ӳ������̣����ڣ���Ѫ��Ʒ��
		
		self.__pyFactionSign = PyGUI( wnd.factionSign )

		self.__pyHoldCity = StaticText( wnd.holdCity )
		self.__pyHoldCity.setFloatNameFont()

		self.pyElements_ = [self.__pyHPBg, self.__pyLbCorps, self.pyLbName_,\
		self.__pyFactionSign, self.__pyHoldCity, self.__pyLbSpecialSign]		# ͨ������Ԫ�ص�˳����Ե�����ɫͷ����ʾ���ݵ���������˳��

	def __initElementsColor( self, role ) :
		"""
		��������ʱ����ʼ�������ø�Ԫ�ص��ض���ɫ�������ڳ�ս������������ʾΪ��ɫ
		"""
		color = self.getShowColor( role )
		self.__setNameColor( color )
		if role.tong_holdCity != "" :
			self.__onSetHoldCity( role, role.tong_holdCity )
		player = BigWorld.player()
		self.visible = not role.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		if player.id != role.id :
			if role.level >= csconst.PK_PROTECT_LEVEL :
				#if player.isChallengeFamily( role.familyName ):
				#	self.__onFamilyChallenging( role.id )
				if player.tong_isRobWarEnemyTong( role.tong_dbID ) :			# ����ǰ���Ӷ�ս�ĵж԰���Ա
					self.__tongRobWarBeing( role )
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )
		faction = role.yiJieFaction
		self.__setFactionSign( faction )

	def dispose( self ) :
		self.__pyHPBar.dispose()
		self.__pyLbFamily.dispose()
		self.__pyLbCorps.dispose()
		self.__pyLbSpecialSign.dispose()
		FloatName.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	
	def __setFactionSign( self, faction ):
		if faction == csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN:
			self.__pyFactionSign.visible = True
			self.__pyFactionSign.texture = 'guis/general/spacecopyabout/spaceCopyYiJieZhanChang/blue.dds'
		elif faction == csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI:
			self.__pyFactionSign.visible = True
			self.__pyFactionSign.texture = 'guis/general/spacecopyabout/spaceCopyYiJieZhanChang/green.dds'
		elif faction == csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN:
			self.__pyFactionSign.visible = True
			self.__pyFactionSign.texture = 'guis/general/spacecopyabout/spaceCopyYiJieZhanChang/red.dds'
		else:
			self.__pyFactionSign.visible = False
		self.__updateViewInfo()
			
	def __setNameColor( self, color ) :
		"""
		����������ֵ���ɫ
		"""
		if color is not None:
			self.pyLbName_.leftColor = color
	
	def __setHPBarColor( self, relation ):
		"""
		����Ѫ����ɫ
		"""
		color = self._colors_map.get( relation, ( 255, 255, 255, 255 ) )
		self.__pyHPBar.color = color

	def __updateViewInfo( self ) :
		"""
		����
		"""
		if self.entity_ == None:return
		if self.entity_.onFengQi: return
		self.pyLbName_.toggleLeftName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" ))
		if self.__targetFocus or self.__becomeTarget:
			self.__pyHPBg.visible = True		#ֻҪ�������ȥ���������������Ѫ��
		else:
			self.__pyHPBg.visible = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "HP" )
		if self.entity_.getTitle() != "":
			self.pyLbName_.toggleRightName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "title" ))
		if self.entity_.isJoinTong():
			self.__pyLbCorps.toggleDoubleName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "guild" ))
		if self.entity_._isVend() :
			self.__onSetSignBoard( self.entity_.id )
		self.layout_()

	def __getEntitySignboard( self ) :
		vendSignboard = self.entity_.vendSignboard
		if vendSignboard == "":
			vendSignboard = labelGather.getText( "FloatName:role", "signBoard" )%self.entity_.getName()
		return vendSignboard

	# ----------------------------------------------------------------
	# pravite
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_ROLE_CORPS_NAME_CHANGED"] = self.__onCorpsNameChanged
		self.triggers_["EVT_ON_ROLE_CORPS_GRADE_CHANGED"] = self.__onCorpsDutyChanged		# ������ɫ�İ��ְ��ı�
#		self.triggers_["EVT_ON_TOGGLE_TONG_UPDATE_GRADE"] = self.__onPCorpsDutyChange		# ��ɫ����İ��ְ��ı�
		self.triggers_["EVT_ON_TOGGLE_TONG_INIT_DUTY_NAME"] = self.__onInitTongDutyName		# ������Ա���ְ�����Ƴ�ʼ��
		self.triggers_["EVT_ON_TOGGLE_TONG_UPDATE_DUTY_NAME"] = self.__onUpdateTongDutyName # ����ĳ�����ְ������
		self.triggers_["EVT_ON_ENTITY_PK_STATE_CHANGED"] = self.__onPkStateChanged
		#self.triggers_["EVT_ON_ENTITY_SPECIAL_SIGN_CHANGED"] = self.__onSpecialSignChanged
		self.triggers_["EVT_ON_ROLE_SIGN_CHANGED"] = self.__showSpecialSign
		self.triggers_["EVT_ON_TOGGLE_HAS_TONG_SIGN"] = self.__showTongSign
		self.triggers_["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onTeammateAdded
		self.triggers_["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onTeammateLeft
		self.triggers_["EVT_ON_TEAM_CAPTAIN_CHANGED"] = self.__onTeamCaptainChanged
		self.triggers_["EVT_ON_TEAM_DISBANDED"] = self.__onTeamDisbanded
#		self.triggers_["EVT_ON_VEND_SIGNBOARD_NUMBER_CHANGE"] = self.__onSignNumChange 	# ��̯������ͼ�ı�
		self.triggers_["EVT_ON_VEND_ON_SET_SIGNBOARD"] = self.__onSetSignBoard
		self.triggers_["EVT_ON_VEND_SIGNBOARD_NAME_CHANGED"] = self.__onSignNameChange	# ��̯�������Ƹı�
		self.triggers_["EVT_ON_VEND_RESET_SIGNBOARD"] = self.__onReSetSignBoard 		# ��̯����
		self.triggers_["EVT_ON_FAMILY_CHALLENGING"] = self.__onFamilyChallenging		# ������ս��
		self.triggers_["EVT_ON_FAMILY_CHALLENGE_OVER"] = self.__onFamilyChallengeOver	# ������ս����
		self.triggers_["EVT_ON_TONG_ROB_WAR_BEING"] = self.__tongRobWarBeing			# ����Ӷ�ս��ʼ
		self.triggers_["EVT_ON_TONG_ROB_WAR_OVER"] = self.__tongRobWarOver				# ����Ӷ�ս����
		self.triggers_["EVT_ON_ROLE_COMPETITION_BEING"] = self.__roleCompetitionBeing	# ���˾�����ʼ
		self.triggers_["EVT_ON_ROLE_COMPETITION_OVER"] = self.__roleCompetitionOver		# ���˾�������
		self.triggers_["EVT_ON_ENTITY_QIECUOID_CHANGED"] = self.__onQieCuoTargetChange	# �д��ɫ
		self.triggers_["EVT_OPEN_TONG_SET_HOLD_CITY"] = self.__onSetHoldCity 			#ռ�����
		self.triggers_["EVT_ON_ROLE_HAS_HIDEINFO_FLAG"] = self.__onHasHideFlag			# �Ƿ�������ͷ����Ϣ���
		self.triggers_["EVT_ON_ROLE_EXP_CHANGED"] = self.showExpValue_       			# �������־�����Ϣ
		self.triggers_["EVT_ON_ROLE_PKMODE_CHANGED"] = self.__onPKModeChanged
		self.triggers_["EVT_ON_ROLE_HAS_SAFEAREA_FLAG"] = self.__onRoleSafeChanged
		self.triggers_["EVT_ON_ROLE_ACTWORD_CHANGED"] = self.__onRoleActWordChanged
		self.triggers_["EVT_ON_ROLE_TITLENAME_CHANGE"] = self.__onRoleTitleNameChanged
		self.triggers_["EVT_ON_FENGQI_ON_ENTER"]  = self.__onEnterFengQi				# ����ҹս����ս��
		self.triggers_["EVT_ON_FENGQI_ON_EXIT"]  = self.__onExitFengQi					# �뿪ҹս����ս��
		self.triggers_["EVT_ON_FENGQI_SET_INTERGRAL"]  = self.__onSetFengQiIntegral					# �뿪ҹս����ս��
		self.triggers_["EVT_ON_ENTITY_PK_CHANGED"] = self.__onPKTargetChange	# PK��ɫ
		self.triggers_["EVT_ON_ROLE_SYSPKMODE_CHANGED"] = self.__onSysModeChange	# ϵͳPK�ı�
		self.triggers_["EVT_ON_YIJIE_FACTION_CHANGED"] = self.__onYijieFactionChanged	# ���ս���Ŵ��ڵ���Ӫ�ı�ص�	
		self.triggers_["EVT_ON_ENTER_CITYWAR_SPACE_ROLE_NAME"] = self.__onEnterCityWar	# �����ս�ص�
		self.triggers_["EVT_ON_ROLE_LEAVE_CITYWAR_SPACE"] = self.__onLeaveCityWar	# �뿪��ս�ص�
		self.triggers_["EVT_ON_PET_MODEL_INFO_CHANGED"] = self.__onPetModelInfoChanged
		self.triggers_["EVT_ON_ENTER_CAMP_FHLT_SPACE"] = self.__onEnterCFhlt	#������Ӫ�������
		self.triggers_["EVT_ON_LEAVE_FHLT_SPACE"] = self.__onExitCFhlt			#�뿪��Ӫ�������

		FloatName.registerTriggers_( self )

	# -------------------------------------------------
	def __onCorpsNameChanged( self, role, oldName, newName ) :
		if self.entity_ == None or self.entity_ != role : return
		self.corpsName = newName
		self.__updateViewInfo()

	def __onCorpsDutyChanged( self, role, oldGrade, newGrade ) :
		if self.entity_ == None or self.entity_ != role or newGrade == 0 : return
		player = BigWorld.player()
		gradeName = Const.TONG_GRADE_MAPPING[ newGrade ]
		if role.tong_dbID == player.tong_dbID:
			gradeNick = player.tong_dutyNames.get( newGrade, None )
			if gradeNick is not None:
				gradeName = gradeNick
		self.corpsDuty = gradeName
		self.__onSetHoldCity( role, role.tong_holdCity )

	def __onInitTongDutyName( self, dutyKey, name ):
		if self.entity_ == None:return
		player = BigWorld.player()
		memberInfos = player.tong_memberInfos
		if self.entity_.tong_dbID == player.tong_dbID \
			and self.entity_.isJoinTong(): #�а�Ტ����ͬһ�����
			tongGrade = self.entity_.tong_grade
			if tongGrade == dutyKey:
				self.corpsDuty = name
		self.__updateViewInfo()

	def __onUpdateTongDutyName( self, dutyKey, name ):
		self.__onInitTongDutyName( dutyKey, name )

	def __onSetHoldCity( self, role, city ) :
		if self.entity_ == None or self.entity_ != role : return
		if self.entity_.onFengQi: return
		if city == "" :
			self.__pyHoldCity.visible = False
		else :
			cityName = labelGather.getText( "FloatName:role", "unknowCity" )
			cityArea = rds.mapMgr.getWholeArea( city, self.entity_.position[1] )
			if cityArea is not None :
				cityName = cityArea.name
			if self.entity_.tong_grade == csdefine.TONG_DUTY_CHIEF:
				self.__pyHoldCity.text = labelGather.getText( "FloatName:role", "cityMaster" )%cityName
			else:
				self.__pyHoldCity.text = cityName
			self.__pyHoldCity.visible = True
			self.__pyHoldCity.color = 255, 200, 0, 255
		self.onEnterWorld()
		self.layout_()

	def __showSpecialSign( self, role, sign, isShow ) :
		"""
		�������ͷ��������
		"""
		if self.entity_ == None or self.entity_.id != role.id : return
		self.__pyLbSpecialSign.showSign( role.id, sign, isShow )
		self.layout_()

	def __showTongSign( self, role, path, isShow ):
		"""
		�������ͷ������� by ����
		"""
		if self.entity_ == None or self.entity_ != role : return
		self.__pyLbCorps.tongIcon = path
		self.__pyLbCorps.iconVisible = isShow
		self.layout_()


	def __onPkStateChanged( self, entity ):
		"""
		���� PK ״̬���ý�ɫ������ɫ
		"""
		if self.entity_ == None or self.entity_.id != entity.id:
			return
		color = self.getShowColor( entity )
		self.__setNameColor( color )
		relation = self.getRelation( entity )
		self.__setHPBarColor( relation )
		
	def __reSetTeamSign( self ):
		"""
		�����������200m��Χ�������־
		"""
		if self.entity_ == None:return
		player = BigWorld.player()
		if player.onFengQi: return
		entities = player.entitiesInRange( 200, cnd = lambda ent : ent.getEntityType() == csdefine.ENTITY_TYPE_ROLE )
		for entity in entities:
			entity.flashTeamSign()		# ���·Ƕӳ���Ա���
		
	def __onTeamCaptainChanged( self, entityID ):
		"""
		�ӳ��ı�ʱ����
		"""
		if self.entity_ == None:return
		if entityID == self.entity_.id and \
		entityID != BigWorld.player().id:
			self.viewInfoKey_ = "teammate"
			
		self.__reSetTeamSign()

	def __onTeammateAdded( self, joinor ) :
		"""
		�ж��ѽ�����ʱ����
		"""
		if self.entity_ == None :return
		if joinor.objectID == self.entity_.id:
			self.viewInfoKey_ = "teammate"
			self.__reSetTeamSign()
			self.__updateViewInfo()
			self.entity_.updateVisibility()
			if self.entity_.vehicle :
				self.entity_.vehicle.updateVisibility()
			relation = self.getRelation( self.entity_ )
			self.__setHPBarColor( relation )

	def __onTeammateLeft( self, objectID ) :
		"""
		�����뿪����ʱ����
		"""
		if self.entity_ == None:return
		if objectID == self.entity_.id and \
		objectID != BigWorld.player().id:
			self.viewInfoKey_ = "role"
			self.__updateViewInfo()
			self.entity_.updateVisibility()
			if self.entity_.vehicle :
				self.entity_.vehicle.updateVisibility()
			relation = self.getRelation( self.entity_ )
			self.__setHPBarColor( relation )
		self.__reSetTeamSign()

	def __onTeamDisbanded( self ) :
		"""
		�����ɢ�����
		"""
		if self.entity_ == None:return
		player = BigWorld.player()
		if self.entity_.id != player.id:
			self.viewInfoKey_ = "role"
		self.__reSetTeamSign()
		self.__updateViewInfo()
		self.entity_.updateVisibility()
		if self.entity_.vehicle :
			self.entity_.vehicle.updateVisibility()
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )

	def __onSetSignBoard( self, entityID ):
		if self.entity_ == None or entityID != self.entity_.id:return
		for pyElement in self.pyElements_:
			pyElement.visible = False
		self.pySignBoard_ = getattr( self, "pySignBoard_", None )
		if self.pySignBoard_ is None:
			self.pySignBoard_ = SignBoard()
			self.addPyChild( self.pySignBoard_ )
			self.pyElements_.append( self.pySignBoard_ )		# ֻ��ʾ����
		signNum = self.entity_.vendSignboardNumber
		if signNum == "" :
			signNum = -1
		self.pySignBoard_.setSignNumber( signNum )
		signboard = self.__getEntitySignboard()
		self.pySignBoard_.setBoardName( signboard )
		self.pySignBoard_.visible = True
		self.layout_()

	def __onSignNameChange( self, entityID, name ):
		if self.entity_ == None or entityID != self.entity_.id:return
		if hasattr( self, "pySignBoard_" ):
			self.pySignBoard_.setBoardName( name )

	def __onReSetSignBoard( self, entityID ):
		if self.entity_ == None or entityID != self.entity_.id:return
		if hasattr( self, "pySignBoard_" ) and self.pySignBoard_ in self.pyElements_:
			self.pyElements_.remove( self.pySignBoard_ )
			self.delPyChild( self.pySignBoard_ )
			self.pySignBoard_.dispose()
			self.pySignBoard_ = None
		self.__updateViewInfo()

	def __onFamilyChallenging( self, entityID ):
		"""
		������ս��
		"""
		if self.entity_ == None or entityID != self.entity_.id:return
		self.__pyLbFamily.color = self.__getFamilyNameColor()

	def __onFamilyChallengeOver( self, entityID ) :
		"""
		������ս����
		"""
		if self.entity_ == None or entityID != self.entity_.id:return
		self.__pyLbFamily.color = self.__getFamilyNameColor()

	def __getFamilyNameColor( self ):
		"""
		��ü���������ɫ
		"""
		if self.entity_.level < csconst.PK_PROTECT_LEVEL:
			return 255, 255, 0, 255
		#if BigWorld.player().isChallengeFamily( self.entity_.familyName ):
		#	return cscolors["c8"]
		#else:
		return 255, 255, 0, 255

	def __tongRobWarBeing( self, entity ) :
		"""
		���ڽ��а���Ӷ�ս���ı����������ɫ
		"""
		if self.entity_ == None or self.entity_.id != entity.id : return
		color = cscolors["c33"]
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )

	def __tongRobWarOver( self, entity ) :
		"""
		����Ӷ�ս�������ָ����������ɫ
		"""
		if self.entity_ == None or self.entity_.id != entity.id : return
		color = PK_STATE_COLOR_MAP[ self.entity_.pkState ]
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )

	def __roleCompetitionBeing( self ):
		"""
		���ڽ��и��˾������ı����������ɫ
		"""
		if self.entity_ == None or self.entity_.id != BigWorld.player().id :
			color = self.getShowColor( self.entity_ )
			self.__setNameColor( color )
			relation = self.getRelation( self.entity_ )
			self.__setHPBarColor( relation )

	def __roleCompetitionOver( self ) :
		"""
		���˾����������ָ����������ɫ
		"""
		if self.entity_ == None or self.entity_.id != BigWorld.player().id :
			color = PK_STATE_COLOR_MAP[ self.entity_.pkState ]
			self.__setNameColor( color )
			relation = self.getRelation( self.entity_ )
			self.__setHPBarColor( relation )

	def __onQieCuoTargetChange( self, oldTargetID, newTargetID ) :
		"""
		���ڽ����д裬�ı����������ɫ
		"""
		if self.entity_ == None or self.entity_.id not in [ oldTargetID, newTargetID ]: return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )

	def __onEnterCityWar( self, entity ) :
		"""
		�����ս
		"""
		if self.entity_ == None or self.entity_.id != entity.id : return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
		
	def __onLeaveCityWar( self, entity ):
		"""
		�뿪��ս���� �ָ����������ɫ��Ѫ��
		"""
		if self.entity_ == None or self.entity_.id != entity.id : return
		color = PK_STATE_COLOR_MAP[ self.entity_.pkState ]
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation ) 

	def __onEnterCFhlt( self, entity, remainTime, tongInfos ):
		"""
		������Ӫ�������
		"""
		if self.entity_ == None or self.entity_.id != entity.id : return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
	
	def __onExitCFhlt( self, entity ):
		"""
		�뿪��Ӫ�������
		"""
		if self.entity_ == None or self.entity_.id != entity.id : return
		color = PK_STATE_COLOR_MAP[ self.entity_.pkState ]
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation ) 
		self.__pyBtnCFhlt.visible = False
		
	def __onPKTargetChange( self, id ) :
		"""
		PK���˫����ɫ��Ϊ��ɫ
		"""
		if self.entity_ == None or self.entity_.id not in [ id, BigWorld.player().id ]:
			return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
	
	def __onSysModeChange( self, role, newVal ):
		"""
		ϵͳpkģʽ�ı�
		"""
		if self.entity_ == None or role.id != self.entity_.id:return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
	
	def __onYijieFactionChanged( self, faction ):
		"""
		��Ӫ�ı�ص�
		"""
		self.__setFactionSign( faction )
	
	def __onHasHideFlag( self, entity, hasHideFlag ):
		"""
		�Ƿ�������ͷ����Ϣ���
		"""
		if self.entity_ == None or self.entity_.id != entity.id:return
		self.visible = not hasHideFlag
	
	def __onPKModeChanged( self, role, pkMode ):
		"""
		��ɫPKģʽ�ı�
		"""
		if self.entity_ == None or role.id != self.entity_.id:return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		relation = self.getRelation( self.entity_ )
		self.__setHPBarColor( relation )
	
	def __onRoleSafeChanged( self, role, safeFlag ):
		"""
		��ɫ��ʶ�ı䣬��Ҫ������pk��ʶ
		"""
		if self.entity_ == None or role.id != self.entity_.id: return
		player = BigWorld.player()
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )
	
	def __onRoleActWordChanged( self, role, old, new ):
		"""
		��ɫactWord�ı�֪ͨ
		"""
		if self.entity_ == None or role.id != self.entity_.id: return
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )
	
	def __onRoleTitleNameChanged( self, role, titleName, titleColor = None ):
		"""
		��ɫ�ƺŸı�
		"""
		if self.entity_ == None or role.id != self.entity_.id: return
		self.title = titleName
		if titleColor :
			self.pyLbName_.rightColor = titleColor
		else :
			self.pyLbName_.rightColor = 0, 255, 255, 255

	def __onEnterFengQi( self, role ):
		"""
		����ҹս����ս��
		"""
		if self.entity_ == None or self.entity_.id != role.id: return
		# ֻ��ʾ���ֺ�����
		color = cscolors["c8"]
		integral = BigWorld.player().fengQiIntegrals.get( role.id, 0 )
		self.__setNameColor( color )					# ������ɫ��Ϊ��ɫ
		self.fName = labelGather.getText( "FloatName:role", "fengQiName" )
		self.pyLbName_.toggleLeftName( True )  		# ��������������ʾ
		self.__pyHPBg.visible = False					# Ѫ��
		self.pyLbName_.toggleRightName( False )			# �ƺ�
		self.__pyHoldCity.visible = True
		self.__pyHoldCity.text = "��%d��"%integral
		self.__pyHoldCity.color = 255, 255, 255, 255
		self.__pyLbCorps.toggleDoubleName( False )		# ���
		self.entity_.teamSignSettingChanged( False )	# ������
		self.layout_()

	def __onExitFengQi( self, role ):
		"""
		�뿪ҹս����ս��
		"""
		if self.entity_ == None or self.entity_.id != role.id: return
		color = self.getShowColor( self.entity_ )
		self.__setNameColor( color )
		self.fName = self.entity_.getName()
		self.entity_.flashTeamSign()
		self.__pyHoldCity.visible = False
		if role.tong_holdCity != "" :
			self.__onSetHoldCity( role, role.tong_holdCity )
		self.__updateViewInfo()
		self.layout_()
	
	def __onSetFengQiIntegral( self, roleID, integral ):
		"""
		������ʾ
		"""
		if self.entity_ == None or self.entity_.id != roleID:return
		if not self.entity_.onFengQi: return
		self.__pyHoldCity.text = "��%d��"%integral

	def __onPetModelInfoChanged( self ):
		"""
		"""
		if self.entity_ == None:return
		self.entity_.visibilitySettingChanged( "role", rds.viewInfoMgr.getSetting( "role", "model" ) )

	# ----------------------------------------------------------------
	# protect
	# ----------------------------------------------------------------
	def onViewInfoChanged_( self, infoKey, itemKey, oldValue, value ) :
		"""
		��ʾ��Ϣ�ı�ʱ������
		"""
		if self.entity_ == None or self.viewInfoKey_ != infoKey : return
		player = BigWorld.player()
		if player.onFengQi: return
		if itemKey == "guild" :
			if self.entity_.isJoinTong():
				self.__pyLbCorps.toggleDoubleName( value )
		elif itemKey == "HP" :
			self.__pyHPBg.visible = value
		elif itemKey == "sign":
			if self.viewInfoKey_ == "teammate":
				self.entity_.flashTeamSign()
			elif self.viewInfoKey_ == "role":
				self.entity_.teamSignSettingChanged( value )
			elif self.viewInfoKey_ =="player":
				player.teamSignSettingChanged( value )
		elif itemKey == "model":
			if self.viewInfoKey_ == "teammate" and BigWorld.player().isTeamMember( self.entity_.id ):
				self.entity_.visibilitySettingChanged( infoKey, value )
			elif self.viewInfoKey_ == "role":
				self.entity_.visibilitySettingChanged( infoKey, value )
				ECenter.fireEvent( "EVT_ON_ROLE_MODEL_INFO_CHANGED" )
		FloatName.onViewInfoChanged_( self, infoKey, itemKey, oldValue, value )

	def onHPChanged_( self, hp, hpMax ) :
		rate = hpMax > 0 and float( hp ) / hpMax or 0
		self.__pyHPBar.value = rate
	
	def showExpValue_( self, value, reason, lastTime = 1.8 ) :
		"""
		�����ȡ
		"""
		if reason == csdefine.CHANGE_EXP_INITIAL:
			return
		entityID = BigWorld.player().id
		visible = self.getTextVisible( entityID, "expObtain" )
		if not visible: return
		pid = BigWorld.player().id
		if pid == self.entity_.id :
			if value > 0 :
				text = ":+" + str( value )
			else :
				text = ":" + str( value )
			pyFlyText = getInst( ExpText )								# ���/ʧȥ����
			pyFlyText.init( text )
			self.addPyChild( pyFlyText )
			pyFlyText.startFly( pid, lastTime )
			
	def onAttachEntity_( self ):
		if self.entity_.id == BigWorld.player().id :
			self.viewInfoKey_ = "player"
		elif BigWorld.player().isTeamMember( self.entity_.id ) :
			self.viewInfoKey_ = "teammate"
		self.__initElementsColor( self.entity_ )
		rate = self.entity_.HP_Max > 0 and float( self.entity_.HP ) / self.entity_.HP_Max or 0
		self.__pyHPBar.value = rate
		
	def onDetachEntity_( self ):
		self.__pyHPBg.visible = False
		self.__pyLbCorps.toggleDoubleName( False )
		self.pyLbName_.visible = False
		self.__pyFactionSign.visible = True
		self.__pyHoldCity.visible = False
		self.__pyLbSpecialSign.hideAllSign()
		self.__corpsName = ""		
		self.__family = ""  		
		self.__corpsDuty = ""			
		self.__familyDuty = ""		
		
		self.__targetFocus = False		
		self.__becomeTarget = False		
		self.__updateViewInfo()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		FloatName.onEnterWorld( self )
		player = BigWorld.player()

		if self.entity_.getTitleColor( self.entity_.title ) is not None :
			self.pyLbName_.rightColor = self.entity_.getTitleColor( self.entity_.title )

		if self.entity_.isJoinTong():
			gradeName = Const.TONG_GRADE_MAPPING[ self.entity_.tong_grade ]
			if self.entity_.tong_dbID == player.tong_dbID: #ͬһ�����
				tongGrade = self.entity_.tong_grade
				gradeNick = player.tong_dutyNames.get( tongGrade, None )
				if gradeNick is not None:
					gradeName = gradeNick
			self.corpsDuty = gradeName
			self.__onCorpsNameChanged( self.entity_, "", self.entity_.tongName )

		if self.entity_.onFengQi:
			self.__onEnterFengQi( self.entity_ )

	def onTargetFocus( self ) :
		self.__targetFocus = True
		self.__updateViewInfo()

	def onTargetBlur( self ) :
		self.__targetFocus = False
		self.__updateViewInfo()


	def onBecomeTarget( self ) :
		self.__becomeTarget = True
		self.__updateViewInfo()

	def onLoseTarget( self ) :
		self.__becomeTarget = False
		self.__updateViewInfo()

	# -------------------------------------------------
	def flush( self ):
		"""
		ˢ��ģ��
		"""
		FloatName.flush( self )
		if self.entity_.onFengQi:		# �����ҹս����ս������������
			self.__onEnterFengQi( self.entity_ )

	# -------------------------------------------------
	def getShowColor( self, role ):
		"""
		���Ӧ����ʾ��������ֵ���ɫ
		"""
		if hasattr( role, "onFengQi" ) and role.onFengQi: return  # ҹս����ս������ʾΪ��ɫ
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		tong_dbID = 0
		if hasattr( role, "tong_dbID" ):
			tong_dbID = role.tong_dbID
		cwTongInfos = player.tongInfos
		dTongDBID = 0
		if cwTongInfos.has_key( "defend" ):
			dTongDBID = cwTongInfos["defend"]
		if player.tong_isCityWarTong( tong_dbID ):
			if dTongDBID > 0: #�з��ط�
				if pTongDBID == tong_dbID: #ͬһ�����,��ɫ
					return cscolors["c4"]
				else:
					if tong_dbID == dTongDBID: #���ط�
						return cscolors["c8"]	#��ɫ
					else:
						if pTongDBID == dTongDBID:
							return cscolors["c8"]	#��ɫ
						else:
							return cscolors["c48"]	#��ɫ
			else:
				if tong_dbID == pTongDBID:
					return cscolors["c4"]
				else:
					return cscolors["c8"]
		if player.qieCuoTargetID == role.id:
			return cscolors["c8"]
			
		if role.id in player.pkTargetList.keys():
			return cscolors["c8"]

		if player.tong_isRobWarEnemyTong( role.tong_dbID ) :
			return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]

		relation = player.queryRelation( role )

		if player.hasFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE ):						# ������Ӿ��������⾺��
			if player.canPk( role ) :
				return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			else :
				return ROLE_RELATION_COLOR_MAP[ relation ]
		else :
			compState = None
			try :
				compState = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
			except :
				pass
			if compState == csdefine.SPACE_TYPE_ROLE_COMPETITION :					# ���˾���
				return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_TONG_COMPETITION :				# ��Ὰ��
				if role.pkState == csdefine.PK_CONTROL_PROTECT_PEACE:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				elif role.tongName == player.tongName:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_TONG_ABA:
				if role.tongName != player.tongName:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_YXLM or compState == csdefine.SPACE_TYPE_YXLM_PVP:							#Ӣ�����˸���
				if role.id in player.teamMember:				#���Լ�����
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN:
				if role.tongName == player.tongName:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					return ( 255, 0, 0, 255 )
			elif compState == csdefine.SPACE_TYPE_TONG_TURN_WAR:			#��ᳵ��ս
				if role.id in player.teamMember:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					relation = self.getRelation( role )
					return self._colors_map.get( relation, ( 255, 255, 255, 255 ) )
			elif compState == csdefine.SPACE_TYPE_CITY_WAR_FINAL:		#���ս����
				pBelong = player.getCityWarTongBelong( pTongDBID )
				rBelong = player.getCityWarTongBelong( role.tong_dbID )
				if pBelong == rBelong:	#���˰�ᣬ��ɫ
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_FRIEND ]
				else:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ] 
			elif compState == csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN:
				pCamp = player.getCamp()
				rCamp = role.getCamp()
				if pCamp == rCamp:		#ͬһ����Ӫ��ɫ
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_FRIEND ]
				else:					#��ͬ��Ӫ��ɫ
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ] 
			else :
				return PK_STATE_COLOR_MAP[ role.pkState ]
	
	def getRelation( self, role ):
		"""
		��ȡ�����������ɫ�Ĺ�ϵ,ֻ��2��
		"""
		player = BigWorld.player()
		if role.id == player.id:
			return csdefine.RELATION_FRIEND
		else:
			if self.canPlayerPkRole( role ) and \
			self.canRolePkPlayer():
				return csdefine.RELATION_ANTAGONIZE
			elif not self.canPlayerPkRole( role ) and \
			self.canRolePkPlayer():
				return csdefine.RELATION_NEUTRALLY
			elif self.canPlayerPkRole( role ) and \
			not self.canRolePkPlayer():
				return csdefine.RELATION_NEUTRALLY
			else:
				return csdefine.RELATION_FRIEND
	
	def canPlayerPkRole( self, role ):
		"""
		�Լ��Ƿ�PK�������
		"""
		player = BigWorld.player()
		return player.canPk( role ) and \
		player.currAreaCanPk() and \
		role.currAreaCanPk()
	
	def canRolePkPlayer( self ):
		"""
		��������Ƿ����PK�Լ�
		"""
		return self.entity_.canPkPlayer() and \
		self.entity_.currAreaCanPk() and \
		BigWorld.player().currAreaCanPk()

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCorpsName( self ) :
		return self.__corpsName

	def _setCorpsName( self, name ) :
		self.__corpsName = name
		if name == "" :
			self.__pyLbCorps.toggleDoubleName( False )
		else :
			name = labelGather.getText( "FloatName:role", "tongName")%name
			self.__pyLbCorps.leftName = name
			self.__pyLbCorps.color = 246, 204, 59, 255
			self.__pyLbCorps.toggleDoubleName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "guild" ) )
		self.layout_()

	def _getCorpsDuty( self ) :
		return self.__corpsDuty

	def _setCorpsDuty( self, duty ) :
		duty = labelGather.getText( "FloatName:role", "dutyName" )%duty
		self.__corpsDuty = duty
		self.__pyLbCorps.rightName = duty


	def _setFName( self, name ) :
		FloatName._setFName( self, name )
		if name.startswith( GLINTNAME ) :
			glintFacade.addPyGlitteryUI( self.pyLbName_ )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	fName = property( FloatName._getFName, _setFName )
	corpsName = property( _getCorpsName, _setCorpsName, "" )
	corpsDuty = property( _getCorpsDuty, _setCorpsDuty, "" )

# -*- coding: gb18030 -*-
#
# $Id: RoleCredit.py,v 1.5 2008-09-02 02:49:05 songpeifang Exp $


import BigWorld
import time
from bwdebug import *
import csdefine
import csconst
import csstatus
import ECBExtend

import SkillTargetObjImpl
from TitleMgr import TitleMgr
from Resource.SkillLoader import g_skills
from FactionMgr import factionMgr						# npc��������

g_titleLoader = TitleMgr.instance()



class RoleCredit:
	"""
	��ɫ���������ƺš�����interface
	"""
	def __init__( self ):
		"""
		"""
		# self.prestige
		# self.prestigeSwitch	# �������أ�UINT32���ݣ�ǰ25λÿһλ��Ӧһ�������������Ƿ�����1Ϊ������0Ϊ�رա�
		if len( self.prestige ) > 0: return
		self.prestige.initPrestigeDefalut()

	def addPrestige( self, factionID, value ):
		"""
		��������

		@param factionID : ����id
		@type factionID : UINT8
		@param value : ���ӵ�����ֵ
		@type value : INT32
		"""
		#--------- ����Ϊ������ϵͳ���ж� --------#
		gameYield = self.wallow_getLucreRate()
		if value >=0:
			value = value * gameYield
		#--------- ����Ϊ������ϵͳ���ж� --------#

		if not self.prestige.has_key( factionID ):
			self.prestige.turnOnPrestige( factionID, value )
			self.client.turnOnPrestige( factionID, self.prestige.getPrestige( factionID ) )
			return

		oldprestigeValue = self.prestige.getPrestige( factionID )

		if not self.prestige.addPrestige( factionID, value ):
			self.statusMessage( csstatus.PRESTIGE_UPPER_LIMIT, factionMgr.getName( factionID ) )
			return
		self.client.prestigeUpdate( int( factionID ), value )
		if factionID == 37 or factionID == 38:
			self.updateDartTitle( factionID, self.title == 0 )	# �����ھֳƺ�
		else:
			self.updateConfigTitle( factionID, oldprestigeValue, self.title == 0 )	# �������óƺ�

		self.onPlayerPrestigeChanged()

	def updateConfigTitle( self, factionID, oldprestigeValue, directSelect ):
		"""
		����ͨ�����ÿ��Ƶĳƺ� by����
		"""
		titleID = g_titleLoader.getTitleIDByCredit( factionID, self.prestige.getPrestige( factionID ) )
		if titleID < 0: return
		elif titleID == 0:
			self.checkAndRemoveTitle( factionID, oldprestigeValue )
			return
		self.addTitle( titleID )
		self.checkAndRemoveTitle( factionID, oldprestigeValue )
		if directSelect: self.selectTitle( self.id, titleID )


	def isPrestigeOpen( self, factionID ):
		"""
		����Ƿ�������Ӧ����������
		"""
		return self.prestige.has_key( factionID )


	def getPrestige( self, factionID ):
		"""
		��ö�ӦfactionID����������

		@param factionID : ����id
		@type factionID : STRING
		"""
		if not self.isPrestigeOpen( factionID ):		# �����һ�û�п����������������������������� 2008-11-12 gjx
			self.prestige.turnOnPrestige( factionID, 0 )
			self.client.turnOnPrestige( factionID, self.prestige.getPrestige( factionID ) )
		return self.prestige.getPrestige( factionID )


	def requestSelfPrestige( self ):
		"""
		�������������ݵ��ͻ���
		"""
		for factionID, value in self.prestige.iteritems():
			self.client.receivePrestige( factionID, value )
		self.client.onInitialized( csdefine.ROLE_INIT_PRESTIGE )


	def getPretigeLevel( self, factionID ):
		"""
		��ö�ӦfactionID�����������ȼ�

		PRESTIGE_ENEMY				=			1	# ���
		PRESTIGE_STRANGE			=			2	# �䵭
		PRESTIGE_NEUTRAL			=			3	# ����
		PRESTIGE_FRIENDLY			=			4	# ����
		PRESTIGE_RESPECT			=			5	# ����
		PRESTIGE_ADMIRE				=			6	# �羴
		PRESTIGE_ADORE				=			7	# ���
		"""
		value = self.getPrestige( factionID )
		return value < -3000 and csdefine.PRESTIGE_ENEMY \
			or value < 1    and csdefine.PRESTIGE_STRANGE \
			or value < 3000  and csdefine.PRESTIGE_NEUTRAL \
			or value < 9000  and csdefine.PRESTIGE_FRIENDLY \
			or value < 21000 and csdefine.PRESTIGE_RESPECT \
			or value < 42000 and csdefine.PRESTIGE_ADMIRE \
			or csdefine.PRESTIGE_ADORE


	# --------------------------------------------------------------------
	# about title
	# --------------------------------------------------------------------
	def addTitle( self, titleID ):
		"""
		���������һ���ƺ�

		@param titleID : �ƺŵ�ID
		@type titleID : UINT8
		"""
		if titleID in self.titles or titleID == csdefine.TITLE_NONE : return
		titleData = g_titleLoader.getData( titleID )
		order = titleData[ "order" ]
		for title in self.titles[:]:
			if order == g_titleLoader.getOrder( title ):
				self.removeTitle( title )
		self.titles.append( titleID )
		self.client.onTitleAdded( titleID )
		if g_titleLoader.isTimeLimit( titleID ):	# ����Ǹ���ʱ�޵ĳƺţ���ʼ��ʱ
			tempTime = titleData[ "limitTime" ] + time.time()
			timerID = self.addTimer( titleData[ "limitTime" ], 0, ECBExtend.TITLE_TIMER_CBID )
			self.titleLimitTime.append( { "titleID":titleID, "time":tempTime, "timerID":timerID } )

	def setTitleLimitTime( self, titleID, limitTime ):
		"""
		�������ĳһ����ʱ�޳ƺŵ�ʱ�ޡ�
		��Щ�ƺ���Ҫ����һ��ʱ����֪���೤ʱ���Ƴ�����Ҫ����һ�óƺ�ʱ�����Ƴ�ʱ�ޡ�

		@param titleID : �ƺŵ�ID
		@type titleID : UINT8
		@param limitTime : �ƺŵĻ��ʱ��
		@type limitTime : INT64
		"""
		hasTimeTitle = False
		for tempDict in self.titleLimitTime:
			if tempDict[ "titleID" ] == titleID:
				hasTimeTitle = True
				self.cancel( tempDict[ "timerID" ] )
				tempDict[ "timerID" ] = self.addTimer( limitTime, 0, ECBExtend.TITLE_TIMER_CBID )
				tempDict[ "time" ] = limitTime + time.time()
		if not hasTimeTitle:
			tempDict = {}
			tempDict[ "titleID" ] = titleID
			tempDict[ "timerID" ] = self.addTimer( limitTime, 0, ECBExtend.TITLE_TIMER_CBID )
			tempDict[ "time" ] = limitTime + time.time()
			self.titleLimitTime.append( tempDict )

	def selectTitle( self, srcEntityID, titleID ):
		"""
		Exposed method.
		���ѡ��һ���ƺ�

		@param titleID : �ƺŵ�ID
		@type titleID : UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "self.id != srcEntityID" )
			return
		if titleID == self.title:
			return
		if titleID == 0:	# ȡ���ƺ�
			self._changeTitle( self.title, titleID, "" )
		if titleID not in self.titles:	# �ж�titleID�����Ƿ�Ϸ�
			HACK_MSG("")
			return
		if g_titleLoader.getSkillID( titleID ) and self.intonating():	# ����˳ƺ���buff����ʱ��������ļ��ܣ���ô����������ƺš�
			self.statusMessage( csstatus.TITLE_CANT_CHANGE_SKILL_BUSY )
			return

		oldTitle = self.title
		# ����Ҽ��϶�Ӧ��buff��buffID�����ã������û����ҵ�titleString
		titleType = g_titleLoader.getType( titleID )
		titleName = g_titleLoader.getName( titleID )

		# �ɱ�ƺŴ�����Ҫ��baseȥȡ�ƺ�����
		if titleID in[csdefine.TITLE_TEACH_PRENTICE_ID, csdefine.TITLE_ALLY_ID, csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]:
			self.setTemp( "title_isWield", True )
			self.base.sendTitleName( titleID )
			return

		self._changeTitle( oldTitle, titleID, titleName )


	def _changeTitle( self, oldTitle, titleID, titleName ):
		"""
		�ı�ƺţ����иı�ƺŵ���ڡ�

		����һЩ��Ҫbase���ݲ������ɵĳƺţ����Ա����첽����

		@param oldTitle : �ɳƺŵ�ID
		@type oldTitle : UINT16
		@param titleID : �ƺŵ�ID
		@type titleID : UINT16
		@param titleName : �ƺ�
		@type titleName : STRING
		"""
		self.titleName = titleName
		self.title = titleID
		if oldTitle != 0:	# ����ɳƺŲ�Ϊ��
			# ��Ͼɳƺŵ�buff
			oldSkillID = g_titleLoader.getSkillID( oldTitle )
			if oldSkillID:
				self.clearBuff( [ csdefine.BUFF_INTERRUPT_CHANGE_TITLE ] )

		if titleID == 0:	# ȡ��ѡ��ǰ�ƺţ��ָ���δѡ��ƺ�״̬
			return

		skillID = g_titleLoader.getSkillID( titleID )
		if skillID:		# ��ӵ�ǰ�ƺ����buff
			skill = g_skills[ skillID ]
			if skill is None:
				self.statusMessage( csstatus.SKILL_NOT_EXIST )
				return
			target = SkillTargetObjImpl.createTargetObjEntity( self )
			state = skill.useableCheck( self, target )
			if state != csstatus.SKILL_GO_ON:
				self.statusMessage( state )
				return
			skill.use( self, target )


	def removeTitle( self, titleID ):
		"""
		�Ƴ���ҵ�һ���ƺ�

		@param titleID : �ƺŵ�ID
		@type titleID : UINT8
		"""
		if not titleID in self.titles:
			ERROR_MSG( "Could not remove such title id %i because it does not exist in player( %s )'s titles!" % ( titleID, self.getName() ) )
			return
		self.titles.remove( titleID )
		self.client.onTitleRemoved( titleID )
		if self.title == titleID:
			self._changeTitle( self.title, 0, "" )
		for temp in self.titleLimitTime:
			if temp[ "titleID" ] == titleID:
				self.cancel( temp[ "timerID" ] )
				self.titleLimitTime.remove( temp )
				break


	def onTitleAddTimer( self, controllerID, userData ):
		"""
		�����ʱ�����ƵĳƺŵĻص�
		"""
		for temp in self.titleLimitTime:
			if temp[ "time" ] - time.time() < 1.0:		# ���������1������
				self.removeTitle( temp[ "titleID" ] )
				break

	def title_onLogin( self ):
		"""
		������ߣ����óƺ�
		"""
		isCurTitle = False					# �Ƿ�ǰʹ�õĳƺŵ�����
		for temp in self.titleLimitTime:	# ���ƺ��Ƿ���
			temp["timerID"] = 0
			if temp[ "time" ] - time.time() < 0.3:		# ���������0.3������
				if temp["titleID"] == self.title:
					isCurTitle = True
				self.removeTitle( temp[ "titleID" ] )
			else:
				timerID = self.addTimer( temp[ "time" ] - time.time(), 0, ECBExtend.TITLE_TIMER_CBID )
				temp["timerID"] = timerID

		if not self.title or isCurTitle:	# ��ǰû��ѡ��ƺ� ���� ��ǰѡ�еĳƺŵ����ˣ�����
			DEBUG_MSG( "player( %s ) have not wielded title." % ( self.getName() ) )
			return

		# �ɱ�ƺŴ�����Ҫ��baseȥȡ�ƺ�����
		if self.title in[csdefine.TITLE_TEACH_PRENTICE_ID, csdefine.TITLE_ALLY_ID, csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]:
			self.setTemp( "title_isWield", False )
			self.base.sendTitleName( self.title )
		else:
			self.titleName = g_titleLoader.getName( self.title )

	def getDartTitleID( self, factionID, questStyle ):
		"""
		������ҵ��ھ������õ�������ھ��еĳƺ�ID
		@param id : �ھ�������id
		@type id : STRING
		"""
		if questStyle == csdefine.QUEST_TYPE_ROB:
			titleID = [ csdefine.TITLE_NOVICIATE_LANLUHU_X, csdefine.TITLE_NOVICIATE_LANLUHU_C ]
			return titleID[factionID-37]
		if not self.isPrestigeOpen( factionID ):
			titleID = [ csdefine.TITLE_NOVICIATE_NEW_DART_X, csdefine.TITLE_NOVICIATE_NEW_DART_C ]
			return titleID[factionID-37]
		# self.dartRepuValue = self.getPrestige( factionID )		#����ھ�����
		titleID = [csdefine.TITLE_NONE, csdefine.TITLE_NONE]

		presLevel_X = self.getPretigeLevel( 37 )
		presLevel_C = self.getPretigeLevel( 38 )
		presLevel = presLevel_X > presLevel_C and presLevel_X or presLevel_C
		factionID = presLevel_X > presLevel_C and 37 or 38
		if presLevel == csdefine.PRESTIGE_NEUTRAL:		#"������"
			titleID = [ csdefine.TITLE_NOVICIATE_CHANGZISHOU_X, csdefine.TITLE_NOVICIATE_CHANGZISHOU_C ]
		if presLevel == csdefine.PRESTIGE_FRIENDLY:		#"������ʦ"
			titleID = [ csdefine.TITLE_NOVICIATE_NEW_DART_X, csdefine.TITLE_NOVICIATE_NEW_DART_C ]
		elif presLevel == csdefine.PRESTIGE_RESPECT:	#"��ʦ"
			titleID = [ csdefine.TITLE_NOVICIATE_WUSHI_X, csdefine.TITLE_NOVICIATE_WUSHI_C ]
		elif presLevel == csdefine.PRESTIGE_ADMIRE:		#"��ͷ"
			titleID = [ csdefine.TITLE_NOVICIATE_DART_HEAD_X, csdefine.TITLE_NOVICIATE_DART_HEAD_C ]
		elif presLevel >= csdefine.PRESTIGE_ADORE:		#"����"
			titleID = [ csdefine.TITLE_NOVICIATE_DART_KING_X, csdefine.TITLE_NOVICIATE_DART_KING_C ]

		if factionID == 37:return titleID[0]	# ��¡�ھ�������37
		elif factionID == 38:return titleID[1]	# ��ƽ�ھ�������38
		else:return csdefine.TITLE_NONE

	def removeDartTitle( self ):
		"""
		�����ҵ��ھֳƺţ������ھֵĳƺŶ������
		"""
		if not self.titles:
			return
		for titleID in self.titles:
			if titleID >= csdefine.TITLE_NOVICIATE_LANLUHU_X and titleID <= csdefine.TITLE_NOVICIATE_LANLUHU_C:
				self.removeTitle( titleID )

	def getMyTeachTitle( self ):
		"""
		����Լ���߼����ʦ���ƺ�
		"""
		teachTitle = {}
		for titleID in self.titles:
			if g_titleLoader.isTeachTitle( titleID ):
				teachTitle[titleID] = g_titleLoader.getTeachCreditRequire( titleID )

		if teachTitle == {}: return 0
		list = sorted( teachTitle.values(), reverse = True )  #�Ӵ�С����
		myTeachTitle = list[0]	#ȡ����
		for id in teachTitle.keys():
			if teachTitle.get( id ) == myTeachTitle:
				return id
		return 0

	def getOpposeDartPrestige( self, id ):
		"""
		��ö����ھֵ�id
		@param id : �ھ�������id
		@type id : STRING
		"""
		if id == 38:
			return 37
		return 38

	def setPrestige( self,  factionID, value ):
		"""
		��������ֵ
		"""
		currentPrestige = self.getPrestige( factionID )
		self.addPrestige( factionID, value - currentPrestige )

	def checkAndRemoveTitle( self, factionID, oldprestigeValue ):
		"""
		����ʱ��ȥ���߼��ƺ� by����
		"""
		nowpreValue = self.prestige.getPrestige( factionID )
		if nowpreValue == oldprestigeValue: return
		oldTitleID = g_titleLoader.getTitleIDByCredit( factionID, oldprestigeValue )
		titleID = g_titleLoader.getTitleIDByCredit( factionID, nowpreValue )
		if oldTitleID not in self.titles or oldTitleID == titleID: return
		if abs( oldprestigeValue ) > abs( nowpreValue ) :
			self.removeTitle( oldTitleID )

	def updateDartTitle( self, factionID, directSelect = False ):
		"""
		�������ڳƺ�
		"""
		titleID = self.getDartTitleID( factionID, csdefine.QUEST_TYPE_DART )	#ȡ��������ھ��е����ڳƺ�ID
		if titleID in self.titles:
			return
		self.removeDartTitle()
		#titleID = self.getDartTitleID( factionID, csdefine.QUEST_TYPE_DART )	#ȡ��������ھ��е����ڳƺ�ID
		self.addTitle( titleID )												#�������ڳƺ�
		if directSelect:
			self.selectTitle( self.id, titleID )

	def onPlayerPrestigeChanged( self ):
		"""
		�����ı��Ĵ���
		"""
		self.client.onPrestigeChange()

	def hasTitle( self, titleID ):
		"""
		"""
		return titleID in self.titles

	def receiveTitleName( self, titleID, titleString ):
		"""
		Define method.
		���տɱ�ƺ�����
		"""
		oldTitle = self.title
		try:
			titleName = g_titleLoader.getName( titleID ) % titleString
		except:
			ERROR_MSG( "�����ڵ�titleID( %i )." % titleID )
			return
		if self.queryTemp( "title_isWield", False ):
			self._changeTitle( oldTitle, titleID, titleName )
		else:
			self.titleName = titleName
		self.removeTemp( "title_isWield" )

	def getPrestigeByName( self, name ):
		"""
		�����������ֻ�ȡ������Ŀǰֻ����GM����
		"""
		factionID = factionMgr.getIDByName( name )
		if factionID:
			return self.getPrestige( factionID )
		return None

	def addPrestigeByName( self, name, value ):
		"""
		����������������������Ŀǰֻ����GM����
		"""
		factionID = factionMgr.getIDByName( name )
		if factionID:
			self.addPrestige( factionID, value )
	
	def resetPrestige( self ):
		"""
		��������������Ŀǰֻ����GM����
		"""
		self.prestige.clear()


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/08/30 10:17:04  wangshufeng
# �������ݽṹ��������Ӧ��������
#
# Revision 1.3  2008/08/22 09:09:27  songpeifang
# ����˻�����ںͽ��ڵĳƺŵĽӿ�
#
# Revision 1.2  2008/07/19 01:57:16  wangshufeng
# ��ӳƺ�ϵͳ
#
# Revision 1.1  2008/07/14 04:13:33  wangshufeng
# add new interface��RoleCredit
#
#
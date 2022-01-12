# -*- coding: gb18030 -*-

# from common
import csdefine

# from cell
import Const
import ECBExtend

CONST_ACTIVITY_PICK_ANIMA_SKILLID = 721038001

class RoleCopyInterface:
	def __init__( self ):
		pass
	
	#---------------------------------------------------
	# ʰȡ�����淨
	#---------------------------------------------------
	def pickAnima_reqStart( self, exposed ):
		"""
		exposed method.
		�ͻ���������Ϸ��ʼ
		"""
		if not self.hackVerify_( exposed ):
			return
		
		self.removeAllBuffsBySkillID( Const.ACTIVITY_STOP_MOVE_SKILL, [ csdefine.BUFF_INTERRUPT_NONE, ] )
		self.systemCastSpell( CONST_ACTIVITY_PICK_ANIMA_SKILLID )
	
	def pickAnima_onEnd( self ):
		"""
		define method
		�淨����
		"""
		spaceCell = self.getCurrentSpaceCell()
		
		if spaceCell:
			spaceCell.onGameOver( self.planesID, self )

		self.removeAllBuffsBySkillID( CONST_ACTIVITY_PICK_ANIMA_SKILLID, [ csdefine.BUFF_INTERRUPT_NONE, ] )
		self.systemCastSpell( Const.ACTIVITY_STOP_MOVE_SKILL ) #���������ƶ�
	
	def pickAnima_confirmQuitSpace( self, exposed ):
		"""
		exposed method.
		�ͻ��������˳����λ
		"""
		if not self.hackVerify_( exposed ):
			return
		
		self.removeAllBuffByID( CONST_ACTIVITY_PICK_ANIMA_SKILLID, [ csdefine.BUFF_INTERRUPT_NONE, ] ) #��ֹ���󣬽���һ��BUFFɾ��
		self.removeAllBuffsBySkillID( Const.ACTIVITY_STOP_MOVE_SKILL, [ csdefine.BUFF_INTERRUPT_NONE, ] ) #�Ƴ�����BUFF
		self.enterPlane( "fu_ben_hai_dao_001" )

	#---------------------------------------------------
	# ���ظ���
	#---------------------------------------------------
	def fangShou_addAreaGearStartMark( self, areaName ) :
		"""
		<define method>
		���ظ������������ؿ������
		"""
		self.setTemp( areaName, True )
		self.fangShou_addAreaBuff( areaName )
	
	def fangShou_onEnterCopy( self ) :
		"""
		<define method>
		���븱��
		"""
		checkPosTimer = self.addTimer( 0, Const.COPY_FANG_SHOU_CHECK_POSITION_CYCLE, ECBExtend.COPY_FANG_SHOU_CHECK_ROLE_POSITION_CBID )		# ��ӷ��ظ���������λ�� timer
		self.setTemp( "fangShou_checkRolePosTimer", checkPosTimer )
		currentArea = self.fangShou_getCurrentArea()
		self.setTemp( "lastFangShouArea", currentArea )
		for spellID in Const.COPY_FANG_SHOU_BUFF_SPELLS[ Const.COPY_FANG_SHOU_AREA_FORTH ] :
			self.spellTarget( spellID, self.id )						# ���븱���������һ��Ǳ�ܼ� 100% ��Buff
	
	def fangShou_onLeaveCopy( self ) :
		"""
		<define method>
		�뿪����
		"""
		checkPosTimer = self.queryTemp( "fangShou_checkRolePosTimer" ) 
		if checkPosTimer :
			self.cancel( checkPosTimer )													# �������ظ���������λ�� timer
		
		for itemID in Const.COPY_FANG_SHOU_SPECAIL_ITEMS :
			count = self.countItemTotal_( itemID )
			self.removeItemTotal( itemID, count, csdefine.DELETE_ITEM_NORMAL )				# ����˴θ�����ʰȡ���������
		
		for skillID in Const.COPY_FANG_SHOU_CLEAR_BUFF_SPELLS :
			self.spellTarget( skillID, self.id )											# ��ո������� Buff
		
		# �Ƴ����ܴ��ڵ� tempMapping
		for areaName in Const.COPY_FANG_SHOU_BUFF_SPELLS :
			self.removeTemp( areaName )
		self.removeTemp( "fangShou_checkRolePosTimer" )
		self.removeTemp( "lastFangShouArea" )
	
	def onTimer_FangShouCheckRolePos( self, timerID, cbID ) :
		"""
		���ظ���������λ��timer�ص�
		"""
		currentArea = self.fangShou_getCurrentArea()
		if self.queryTemp( "lastFangShouArea" ) == currentArea :
			return
		if self.fangShou_AreaGearStartCheck( currentArea ) :
			self.fangShou_addAreaBuff( currentArea )						# ����������ҿ����ļ��ϵ�ǰ����� buff
		else :
			self.fangShou_addAreaBuff( Const.COPY_FANG_SHOU_AREA_FORTH )	# û��������ػ��������δ������ȫ���ϵ�������� buff
		
		self.setTemp( "lastFangShouArea", currentArea )
	
	def fangShou_getCurrentArea( self ) :
		"""
		��ȡ��ǰ���ڷ��ظ�������
		"""
		z = self.position.z
		currentArea = ""
		if z > Const.COPY_FANG_SHOU_AERA_POS_Z_FIRST :
			currentArea = Const.COPY_FANG_SHOU_AREA_FIRST
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_SECOND :
			currentArea = Const.COPY_FANG_SHOU_AREA_SECOND
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_THRID :
			currentArea = Const.COPY_FANG_SHOU_AREA_THRID
		else :
			currentArea = Const.COPY_FANG_SHOU_AREA_FORTH
		return currentArea
	
	def fangShou_addAreaBuff( self, areaName ) :
		"""
		��ӷ�������buff
		"""
		if areaName == Const.COPY_FANG_SHOU_AREA_FORTH :					# ���������������buff
			for spellID in Const.COPY_FANG_SHOU_CLEAR_BUFF_SPELLS :
				self.spellTarget( spellID, self.id )
		
		for spellID in Const.COPY_FANG_SHOU_BUFF_SPELLS[ areaName ] :
			self.spellTarget( spellID, self.id )
	
	def fangShou_AreaGearStartCheck( self, areaName ) :
		"""
		���ظ�����������Ƿ������
		"""
		return self.queryTemp( areaName, False )
	
	def fangShou_onDestroy( self ) :
		"""
		�����ٵ�ʱ����������
		ע�⣬��ʱself.isDestroyed��Ȼ��False
		"""
		self.fangShou_onLeaveCopy()
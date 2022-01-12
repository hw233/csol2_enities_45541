# -*- coding:gb18030 -*-
#
# by ganjinxing 2012-02-24
# ��Ϸ���ù�����˵����
# ���Ŀ�꣺
# Ӧ�������е���Ϸ���÷������滻����ǰ����Ϸ���ã�
# ������ʱ�ָ����޸�ǰ�����á����ÿ�ָ���ռ���Ӧ�õ���Ϸ����
# ����������ҽ���ÿռ�ʱ���Զ�ѯ������Ƿ�Ӧ�����÷�������
# ����ҽ��ܣ����Զ�Ӧ������ָ���ķ�����������뿪�ÿռ�ʱ��
# ����Ϸ���ûָ����޸�ǰ�����á�
#
# ��ƽṹ��
# �����󲿷���ɣ�������(GameSettingMgr)��������(�̳���SetterBase)��
# ������������غ�Ӧ����Ϸ���÷�����������������Ϸ���õľ��������
# ��ͨ�������µ���������ִ���µ���Ϸ��������滻�ͻָ�������Ŀǰ֧��
# ����Ϸ�����������
# 1��ͨ�� BigWorld.setWatcher �����õ���Ϸ����
# 2��ͨ�� viewInfoMgr.changeSetting �����õ���Ϸ����

# bigworld
import BigWorld
# common
import csstatus
import Language
from bwdebug import ERROR_MSG
# client
import Define
from MessageBox import *
from ViewInfoMgr import viewInfoMgr
# config
from config.client.msgboxtexts import Datas as mbmsgs


class GameSettingMgr :
	_inst = None

	def __init__( self ) :
		assert self.__class__._inst is None, "Invote the instance() method."
		self.__currSettingID = None							# ��ǰӦ�õ�����
		self.__originSetting = {}							# ����ԭʼ����
		self.__customSettings = {}							# �Զ������ã�{ settingID : settingSect }
		self.__spacesSettingMap = {}						# ��ͼ��Ӧ�����ã�{ spaceLabel : settingID }

	@classmethod
	def instance( CLS ) :
		if CLS._inst is None :
			CLS._inst = CLS()
		return CLS._inst

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initSettings( self, cfgPath = "" ) :
		"""
		"""
		if cfgPath == "" :
			cfgPath = "config/client/CustomGameSetting.xml"
		sect = Language.openConfigSection( cfgPath )
		if sect is None :
			ERROR_MSG( "Open %s failed!" % cfgPath )
			return
		for sSect in sect.values() :
			settingID = sSect.asInt
			self.__customSettings[ settingID ] = sSect["options"]
			spacesLabel = sSect["spaces"].readStrings( "item" )
			for spaceLabel in spacesLabel :
				self.__spacesSettingMap[ spaceLabel ] = settingID
		Language.purgeConfig( cfgPath )

	def onPlayerEnterSpace( self ) :
		"""
		��ҽ���ĳ���ռ�
		ע�⣺��Ҹս���һ���ռ�ʱ������getSpaceLabel�õ�����None��
		����Ҫ��ʱһ�������ж�
		"""
		BigWorld.callback( 3.0, self.useCurrentSpaceSetting )

	def onPlayerLeaveSpace( self ) :
		"""
		����뿪ĳ���ռ�
		"""
		spaceLabel = BigWorld.player().getSpaceLabel()
		if self.spaceHasCustomSetting( spaceLabel ) :
			self.recoverSetting( self.getSpaceSettingID( spaceLabel ) )

	def onPlayerOffline( self ) :
		"""
		��ҵ���
		"""
		self.recoverCurrentSetting()

	# -------------------------------------------------
	# ����ʵ�ַ���
	# -------------------------------------------------
	def useCurrentSpaceSetting( self ) :
		"""
		Ӧ�õ�ǰ�ռ������
		"""
		spaceLabel = BigWorld.player().getSpaceLabel()
		self.useSpaceSetting( spaceLabel )

	def useSpaceSetting( self, spaceLabel ) :
		"""
		Ӧ��ָ���ռ������
		"""
		settingID = self.getSpaceSettingID( spaceLabel )
		if settingID is not None :
			self.useSettingByID( settingID )

	def useSettingByID( self, settingID, needConfirm = True ) :
		"""
		Ӧ��ָ��ID������
		"""
		self.recoverCurrentSetting()									# ͬһʱ��ֻ��Ӧ��һ�����ã������Ȱѵ�ǰ��Ӧ�ûָ�
		appSetting = self.__getApplicableOptions( settingID )
		if len( appSetting ) == 0 :
			return
		if needConfirm :
			def confirmCallback( res ) :
				if res == RS_OK :
					self.__applySetting( settingID )
			#appContent = "\n" + self.__formatContents( [ s.readString("content") for s in appSetting ] )
			#msg = mbmsgs[0x0f00] % appContent
			showMessage( mbmsgs[0x0f00], "", MB_OK_CANCEL, confirmCallback, gstStatus = Define.GST_IN_WORLD )
		else :
			self.__applySetting( settingID )

	def spaceHasCustomSetting( self, spaceLabel ) :
		"""
		����ͼ�Ƿ�����Զ������Ϸ����
		"""
		return self.__spacesSettingMap.has_key( spaceLabel )

	def getSpaceSettingID( self, spaceLabel ) :
		"""
		��ȡ�ռ���Զ�����Ϸ����
		"""
		return self.__spacesSettingMap.get( spaceLabel )

	def hasSetting( self, settingID ) :
		"""
		����Ƿ����ĳ��ID��Ӧ������
		"""
		return self.__customSettings.has_key( settingID )

	def getCurrentSettingID( self ) :
		"""
		���ص�ǰ������ID
		"""
		return self.__currSettingID

	def recoverCurrentSetting( self ) :
		"""
		�ָ�����Ӧ�õ�����ΪӦ��ǰ������
		"""
		self.recoverSetting( self.__currSettingID )

	def recoverSetting( self, settingID ) :
		"""
		�ָ�����Ӧ�õ�����ΪӦ��ǰ������
		"""
		if self.__currSettingID and self.__currSettingID == settingID :
			self.__recoverSetting( settingID )
			self.__currSettingID = None
			self.__originSetting.clear()

	def clear( self ) :
		"""
		�����������
		"""
		self.recoverCurrentSetting()
		self.__customSettings.clear()
		self.__spacesSettingMap.clear()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __formatContents( self, contents ) :
		"""
		��ʽ����ʾ�޸����ݵ��ı�
		"""
		return "\n".join( contents )

	def __buildSetter( self, optionSect ) :
		"""
		�����������õ�ʵ��
		"""
		setterClass = SETTER_MAP.get( optionSect.readString( "script" ) )
		if setterClass is None :
			ERROR_MSG( "Setter %s is not existed!" % optionSect.readString( "script" ) )
			return None
		return setterClass.inst()

	def __getApplicableOptions( self, settingID ) :
		"""
		��ȡ��Ӧ�õ�����
		"""
		result = []
		settingSect = self.__customSettings.get( settingID )
		if settingSect is None :
			ERROR_MSG( "Game setting %i is not existed!" % settingID )
			return result 											# []
		for optionSect in settingSect.values() :
			setter = self.__buildSetter( optionSect )
			if setter and setter.applyCheckout( optionSect ) :		# ����Ƿ���ҪӦ�ô�����
				result.append( optionSect )							# �ѿ�Ӧ������ӵ��б�
		return result

	def __applySetting( self, settingID ) :
		"""
		Ӧ������
		"""
		settingSect = self.__customSettings.get( settingID )
		if settingSect is None :
			ERROR_MSG( "Game setting %i is not existed!" % settingID )
			return
		#appContents = []
		for optionSect in settingSect.values() :
			setter = self.__buildSetter( optionSect )
			if setter and setter.applyCheckout( optionSect ) :		# ����Ƿ���ҪӦ�ô�����
				origin = setter.apply( optionSect )
				self.__originSetting[ optionSect.asString ] = origin
		#		appContents.append( optionSect.readString("content") )
		self.__currSettingID = settingID
		#argStr = "\n" + self.__formatContents( appContents )
		#BigWorld.player().statusMessage( csstatus.GAME_SETTING_MGR_APPLY_REPORT, argStr )

	def __recoverSetting( self, settingID ) :
		"""
		�ָ���֮ǰ������
		"""
		settingSect = self.__customSettings.get( settingID )
		if settingSect is None :
			ERROR_MSG( "Game setting %i is not existed!" % settingID )
			return
		for optionSect in settingSect.values() :
			origin = self.__originSetting.get( optionSect.asString )
			if origin is None :
				continue
			setter = self.__buildSetter( optionSect )
			if setter and setter.revertCheckout( optionSect ) :		# ����Ƿ���Ҫ�ָ�������
				setter.revert( optionSect, origin )


gameSettingMgr = GameSettingMgr.instance()


# --------------------------------------------------------------------
# setters
# --------------------------------------------------------------------
class SetterBase :
	__insts = {}

	def __init__( self ) :
		assert SetterBase.__insts.get( self.__class__ ) is None,\
			"Please invoke the class method inst to get instance."
		SetterBase.__insts[self.__class__] = self

	@classmethod
	def inst( CLS ) :
		if not CLS.__insts.has_key( CLS ) :
			CLS.__insts[CLS] = CLS()
		return CLS.__insts[CLS]

	@staticmethod
	def translateValue( vType, value ) :
		"""
		����ָ�����������ͣ����ַ���ת��Ϊ��Ӧ��ֵ
		"""
		if type( value ) is vType :
			return value
		elif vType is bool :
			return eval( value.capitalize() )
		else :
			return vType( value )

	def apply( self, optionSect ) :
		"""
		Ӧ���趨����Ϸ
		"""
		pass

	def revert( self, optionSect, origin ) :
		"""
		�ָ�����
		"""
		pass

	def parse( self, optionSect ) :
		"""
		�����ý���Ϊʵ����Ҫ������
		"""
		pass

	def compare( self, optionSect ) :
		"""
		����ǰֵ������ֵ���жԱȣ���ͬ�򷵻�0��С�򷵻�-1�����򷵻�1
		"""
		return 0

	def applyCheckout( self, optionSect ) :
		"""
		����Ƿ���ҪӦ�ø����ã�Ĭ������£������ǰ���ô��ڻ��ߵ���
		Ԥ���õ�ֵ������Ҫ�޸ġ�
		"""
		return self.compare( optionSect ) == -1

	def revertCheckout( self, optionSect ) :
		"""
		����Ƿ���Ҫ�ָ������ã�Ĭ������£������ǰ���õ���Ԥ���õ�ֵ��
		����Ҫ�ָ����޸�ǰ��ֵ��
		"""
		return self.compare( optionSect ) == 0


class SetterWatcher( SetterBase ) :
	"""
	ͨ������BigWorld.setWatcher�������õ�����
	"""
	_SETTING_MAP = {
		"max_particles_count" : "Chunks/Particles Lod/MAX pixie count",		# �����������
		"particles_distance" : "Chunks/Particles Lod/Distance",				# ���������Ӿ���
	}

	def apply( self, optionSect ) :
		"""
		Ӧ���趨����Ϸ
		"""
		label, value, vType = self.parse( optionSect )
		origin = BigWorld.getWatcher( label )
		BigWorld.setWatcher( label, value )
		return SetterBase.translateValue( vType, origin )					# ��������ǰ��ֵ

	def revert( self, optionSect, origin ) :
		"""
		�ָ�����
		"""
		label, value = self.parse( optionSect )[:2]
		if origin != value :
			BigWorld.setWatcher( label, origin )

	def parse( self, optionSect ) :
		"""
		�����ý���Ϊʵ����Ҫ������
		"""
		label = SetterWatcher._SETTING_MAP.get( optionSect.asString )
		vType = eval( optionSect.readString( "type" ) )
		value = optionSect.readString( "value" )
		value = SetterBase.translateValue( vType, value )
		return ( label, value, vType )

	def compare( self, optionSect ) :
		"""
		����ǰֵ������ֵ���жԱȣ���ͬ�򷵻�0��С�򷵻�-1�����򷵻�1
		"""
		label, value, vType = self.parse( optionSect )
		current = BigWorld.getWatcher( label )
		current = SetterBase.translateValue( vType, current )
		return cmp( current, value )


class SetterViewInfo( SetterBase ) :
	"""
	ͨ������viewInfoMgr.changeSetting�������õ�����
	"""
	def apply( self, optionSect ) :
		"""
		Ӧ���趨����Ϸ
		"""
		infoKey, itemKey, value, vType = self.parse( optionSect )
		origin = viewInfoMgr.getSetting( infoKey, itemKey )
		viewInfoMgr.changeSetting( infoKey, itemKey, value )
		return SetterBase.translateValue( vType, origin )

	def revert( self, optionSect, origin ) :
		"""
		�ָ�����
		"""
		infoKey, itemKey, value = self.parse( optionSect )[:3]
		if origin != value :
			viewInfoMgr.changeSetting( infoKey, itemKey, origin )

	def parse( self, optionSect ) :
		"""
		�����ý���Ϊʵ����Ҫ������
		"""
		infoKey, itemKey = optionSect.asString.split( "_" )
		vType = eval( optionSect.readString( "type" ) )
		value = optionSect.readString( "value" )
		value = SetterBase.translateValue( vType, value )
		return ( infoKey, itemKey, value, vType )

	def compare( self, optionSect ) :
		"""
		����ǰֵ������ֵ���жԱȣ���ͬ�򷵻�0��С�򷵻�-1�����򷵻�1
		"""
		infoKey, itemKey, value, vType = self.parse( optionSect )
		current = viewInfoMgr.getSetting( infoKey, itemKey )
		return cmp( current, value )


SETTER_MAP = {
	"watcher"	: SetterWatcher,
	"viewinfo"	: SetterViewInfo,
}

# -*- coding: gb18030 -*-
#
# $Id: Sound.py,v 1.27 2008-08-26 08:01:10 yangkai Exp $

"""
implement sound manager class

2006/06/08: writen by panguankong
"""

import BigWorld
import Language
from bwdebug import *
from gbref import rds
from event.EventCenter import *
from Function import Functor
import Const

test = False
class Sound :
	__inst = None

	gb_audioSect = { "switchvocality" : 1,
					 "vocalityvolume" : 1.0,
					 "switcheffect"   : 1,
					 "effectvolume"   : 1.0,
					 "switchbgeffect" : 1,
					 "bgeffectvolume" : 1.0,
					 "mastervolume"   : 1.0
					}

	def __init__( self ):
		assert Sound.__inst is None		# ��ֹ�������ʵ��
		self.__pyBgSound = None
		self.__pyVoice = None
		self.__pyBgEffect = None
		self.__pyFightSound = None
		self.isBgplay = False
		self.bgVol = 0.0
		self.isEffplay = False
		self.effVol = 0.0
		self.isBgEffPlay = False
		self.bgEffVol = 0.0
		self.masterVol = 0.0
		self.isPlayFightSound = False
		self.__bgLocked = False			# ������������
		self.__bgEffLocked = False		# ������Ч����
		self.__gossipSound = None		# ��ǰ���ŵĶԻ���Ч
		self.__delayStopcbid = 0
		self.__delayPlaycbid = 0
		self.__delayStopBgEffcdid = 0
		self.__delayPlayBgEffcbid = 0
		self.__delayStopFightcdid = 0
		self.__delayPlayFightcdid = 0

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = Sound()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def lockBgPlay( self, locked ) :
		"""
		����/�����������ֲ���
		һ���������������ֽ������ٽ����κβ���������ֹͣ���л���
		"""
		self.__bgLocked = locked

	def lockBgEffectPlay( self, locked ):
		"""
		����/����������Ч����
		һ��������������Ч�������ٽ����κβ���������ֹͣ���л���
		"""
		self.__bgEffLocked = locked

	# -------------------------------------------------
	def playVocality( self, name, pyModel ):
		"""
		����3D����
		@param name:			�ļ���
		@type name:			string
		@param pyModel:		����������ģ��
		@type pyModel:			pyModel
		"""
		if pyModel is None: return
		sound = pyModel.getSound( name )
		if sound is not None:
			if self.isEffplay:
				sound.volume = self.effVol
				sound.play()
			else:
				sound.stop()
		return sound

	def stopVocality( self, name, pyModel ):
		"""
		ֹͣ��������
		"""
		if pyModel is None: return

		sound = pyModel.getSound( name )
		if sound is not None: sound.stop()

	def stopVocalitySound( self, pySound ):
		"""
		ֹͣ��������
		"""
		pySound.stop()

	# -------------------------------------------------
	def playUI( self, name ):
		"""
		����UI����
		@param name:			�ļ���
		@type name:			string
		"""
		if rds.statusMgr.isBusy() :
			return False
		sound = BigWorld.getSound( name )
		if sound is not None:
			if self.isEffplay:
				sound.volume = self.effVol
				sound.play()
			else:
				sound.stop()
			return True
		return False

	def play2DSound( self, name, isGossipVoice = False ):
		"""
		����2D��Ч,Ϊ������Ч�¼����ӵĺ���,�ܽ�����Ч����Ӱ��
		@param name:			����·����
		@type name:			string
		@param isGossipVoice:			�Ƿ�Ϊ�Ի�����
		@type isGossipVoice:			bool
		add by wuxo 2011-9-5
		"""
		sound = BigWorld.getSound( name )
		player = BigWorld.player()
		if sound is not None:
			if self.isEffplay:
				sound.volume = self.effVol
				sound.play()
				if isGossipVoice:
					self.__gossipSound = sound
					duration = sound.duration
					BigWorld.callback( duration, player.resetsSoundPriority )
			else:
				sound.stop()
		elif isGossipVoice:
			player.resetsSoundPriority()

	def stop2DSound(self,name):
		"""
		ֹͣ��Ϊname��2D��Ч�Ĳ���
		add by wuxo 2011-9-5
		"""
		sound = BigWorld.getSound( name )
		if sound is not None:
			sound.stop()

	# -------------------------------------------------
	def playVoice( self, name ) :
		"""
		���űȽϳ�������
		"""
		self.__pyVoice = BigWorld.getSound( name )
		if self.__pyVoice is not None :
			self.__pyVoice.play()

	def switchVoice( self, name ) :
		"""
		�л�����
		"""
		if self.__pyVoice is not None :
			self.stopVoice()
		self.playVoice( name )

	def stopVoice( self ):
		"""
		ֹͣ��������
		"""
		if self.__pyVoice:
			self.__pyVoice.stop()
			self.__pyVoice = None

	# -------------------------------------------------
	def playFightMusic( self ):
		"""
		����ս��״̬�±�������
		"""
		if self.__pyFightSound:		# �ϸ����ֻ�ûֹͣ
			self.__delayPlayFightMusic()
			if self.__delayStopFightcdid > 0:
				BigWorld.cancelCallback( self.__delayStopFightcdid )
				self.__delayStopFightcdid = 0
			return

		self.__pyFightSound = BigWorld.getSound( Const.FIGHT_MUSIC_PATH )
		if self.__pyFightSound:
			self.setBgPlay( False )		# ֹͣ��������
			self.setBgEffPlay( False )	# ֹͣ������Ч
			self.isPlayFightSound = True
			self.__pyFightSound.volume = self.bgVol
			if self.bgVol > 0.0:
				self.__pyFightSound.play()

	def stopFightMusic( self ):
		"""
		ֹͣս��״̬�±������֣����û�����ֹ�ķ�ʽ
		"""
		if self.__pyFightSound is None: return
		if self.__delayPlayFightcdid > 0:	# ȡ�����ܴ��ڵĽ���ص�
			BigWorld.cancelCallback( self.__delayPlayFightcdid )
			self.__delayPlayFightcdid = 0
		vol = self.__pyFightSound.volume
		vol -= 0.1
		self.__pyFightSound.volume = vol
		if vol <= 0.0:
			self.__pyFightSound.stop()
			self.__pyFightSound = None
			self.isPlayFightSound = False
			self.__delayStopFightcdid = 0
			self.setBgPlay( True )		# ������������
			self.setBgEffPlay( True )	# ����������Ч
			return
		self.__delayStopFightcdid = BigWorld.callback( 0.5, self.stopFightMusic )

	def __delayPlayFightMusic( self ):
		"""
		����ս����������
		"""
		if self.__pyFightSound is None: return
		vol = self.__pyFightSound.volume
		vol += 0.1
		if vol >= self.bgVol:
			vol = self.bgVol
		self.__pyFightSound.volume = vol
		if vol >= self.bgVol: return
		self.__delayPlayFightcdid = BigWorld.callback( 0.5, self.__delayPlayFightMusic )

	# -------------------------------------------------
	def playMusic( self, name ):
		"""
		���ű�������

		@param name: �����ļ�����·��
		@type  name: STRING
		"""
		if self.__bgLocked : return
		self.__pyBgSound = BigWorld.getSound( name )
		if self.__pyBgSound:
			self.__pyBgSound.volume = self.bgVol
			if self.isBgplay:
				self.__pyBgSound.play()

	def switchMusic( self, name ):
		"""
		�л���������
		���������playMusic ��֮ͬ������ playMusic �������岢��������
		����������Ỻ����ֹ��ǰ���ڲ��ŵ������ٽ��Ų����л�������
		����ʱ�䶨Ϊ3��
		@param name: �����ļ�����·��
		@type  name: STRING
		"""
		if self.__bgLocked : return
		if self.__pyBgSound is None:
			self.playMusic( name )
		elif self.__pyBgSound.name != name.split( "/" )[-1]:	# ��ͬ�����ֲ��л�
			if self.__delayStopcbid > 0:
				BigWorld.cancelCallback( self.__delayStopcbid )
				self.__delayStopcbid = 0
			bgVol = self.bgVol
			functor = Functor( self.__delayStopMusic, name, bgVol )
			self.__delayStopcbid = BigWorld.callback( 0.0, functor )

	def __delayStopMusic( self, name, bgVol ):
		"""
		����ر�����
		"""
		bgVol -= 0.1
		self.__pyBgSound.volume = bgVol
		if bgVol <= 0.0:
			self.stopMusic()
			if self.__delayPlaycbid > 0:
				BigWorld.cancelCallback( self.__delayPlaycbid )
				self.__delayPlaycbid = 0
			functor = Functor( self.__delayPlayMusic, name, bgVol )
			self.__delayPlaycbid = BigWorld.callback( 0.0, functor )
			return
		functor = Functor( self.__delayStopMusic, name, bgVol )
		self.__delayStopcbid = BigWorld.callback( 0.5, functor )
	
	def __delayPlayMusic( self, name, bgVol ):
		"""
		���岥������
		"""
		
		if self.__pyBgSound is None:
			self.playMusic( name )
		if self.__pyBgSound is None: return
		bgVol += 0.1
		self.__pyBgSound.volume = bgVol
		if bgVol >= self.bgVol:
			return
		functor = Functor( self.__delayPlayMusic, name, bgVol )
		self.__delayPlaycbid = BigWorld.callback( 0.5, functor )

	def stopMusic( self ):
		"""
		ֹͣ���ֲ���
		"""
		if self.__bgLocked : return
		if self.__pyBgSound:
			self.__pyBgSound.stop()
			self.__pyBgSound = None

	# -------------------------------------------------
	def playBgEffect( self, name ):
		"""
		���ű�����Ч

		@param name: �����ļ�����·��
		@type  name: STRING
		"""
		if self.__bgEffLocked: return
		if self.__pyBgEffect: return
		self.__pyBgEffect = BigWorld.getSound( name )
		if self.__pyBgEffect:
			self.__pyBgEffect.volume = self.bgEffVol
			if self.isBgEffPlay:
				self.__pyBgEffect.play()

	def switchBgEffect( self, name ):
		"""
		�л�������Ч
		���������playBgEffect��֮ͬ������playBgEffect�������岢��������
		����������Ỻ����ֹ��ǰ���ڲ��ŵ���Ч�ٽ��Ų����л�����Ч
		@param name: �����ļ�����·��
		@type  name: STRING
		"""
		if self.__bgEffLocked: return
		if self.__pyBgEffect is None:
			self.playBgEffect( name )
		elif self.__pyBgEffect.name != name.split( "/" )[-1]:	# ��ͬ����Ч���л�
			if self.__delayStopBgEffcdid > 0:
				BigWorld.cancelCallback( self.__delayStopBgEffcdid )
				self.__delayStopBgEffcdid = 0
			bgEffVol = self.bgEffVol
			functor = Functor( self.__delayStopBgEffect, name, bgEffVol )
			self.__delayStopBgEffcdid = BigWorld.callback( 0.0, functor )

	def __delayStopBgEffect( self, name, bgEffVol ):
		"""
		����رձ�����Ч
		"""
		bgEffVol -= 0.1
		self.__pyBgEffect.volume = bgEffVol
		if bgEffVol <= 0.0:
			self.stopBgEffect()
			if self.__delayPlayBgEffcbid > 0:
				BigWorld.cancelCallback( self.__delayPlayBgEffcbid )
				self.__delayPlayBgEffcbid = 0
			functor = Functor( self.__delayPlayBgEffect, name, bgEffVol )
			self.__delayPlayBgEffcbid = BigWorld.callback( 0.0, functor )
			return
		functor = Functor( self.__delayStopBgEffect, name, bgEffVol )
		self.__delayStopBgEffcdid = BigWorld.callback( 0.5, functor )

	def __delayPlayBgEffect( self, name, bgEffVol ):
		"""
		���岥�ű�����Ч
		"""
		if self.__pyBgEffect is None:
			self.playBgEffect( name )
		if self.__pyBgEffect is None: return
		bgEffVol += 0.1
		self.__pyBgEffect.volume = bgEffVol
		if bgEffVol >= self.bgEffVol: return
		functor = Functor( self.__delayPlayBgEffect, name, bgEffVol )
		self.__delayPlayBgEffcbid = BigWorld.callback( 0.5, functor )

	def stopBgEffect( self ):
		"""
		ֹͣ������Ч����
		"""
		if self.__bgEffLocked : return
		if self.__pyBgEffect:
			self.__pyBgEffect.stop()
			self.__pyBgEffect = None

	# -------------------------------------------------
	def setVocalityVol( self, vol ):
		self.effVol = vol

	def setBgVol( self, vol ):
		self.bgVol = vol
		if self.__pyBgSound:
			self.__pyBgSound.volume = vol
		if self.__pyFightSound:
			self.__pyFightSound.volume = vol

	def setBgEffVol( self, vol ):
		self.bgEffVol = vol
		if self.__pyBgEffect:
			self.__pyBgEffect.volume = vol

	def setMasterVol( self, vol ) :
		self.masterVol = vol
		BigWorld.setMasterVolume( vol )

	def setEffPlay( self, checked ):
		self.isEffplay = checked

	def setBgPlay( self, checked ):
		self.isBgplay = checked
		if self.__pyBgSound and not self.isPlayFightSound:
			if checked:
				self.__pyBgSound.play()
			else:
				self.__pyBgSound.stop()
		if self.__pyFightSound and self.isPlayFightSound:
			if checked:
				self.__pyFightSound.play()
			else:
				self.__pyFightSound.stop()

	def setBgEffPlay( self, checked ):
		if self.isPlayFightSound: return
		self.isBgEffPlay = checked
		if self.__pyBgEffect:
			if checked:
				self.__pyBgEffect.play()
			else:
				self.__pyBgEffect.stop()

	def initAudioSetting( self, cfgSect ):#�����ʼ��ʱ�������������

		subsect = cfgSect["audiosetting"]
		if subsect is None:
			sect = cfgSect
			audioSect = sect.createSection( "audiosetting" )
			for tag ,value in self.gb_audioSect.iteritems():
				if tag == "switchvocality" or tag == "switcheffect" or tag == "switchbgeffect":
					audioSect.writeBool( tag, self.gb_audioSect[tag] )
				else:
					audioSect.writeFloat( tag, self.gb_audioSect[tag] )

		self.sect = cfgSect["audiosetting"]
		self.isBgplay = self.sect.readBool( "switchvocality" )
		self.bgVol = self.sect.readFloat( "vocalityvolume" )
		self.isEffplay = self.sect.readBool( "switcheffect" )
		self.effVol = self.sect.readFloat( "effectvolume" )
		self.isBgEffPlay = self.sect.readBool( "switchbgeffect" )
		self.bgEffVol = self.sect.readFloat( "bgeffectvolume" )
		self.masterVol = self.sect.readFloat( "mastervolume" )

		BigWorld.setMasterVolume( self.masterVol )

	def rollBackSect( self, tag, val ):
		if self.sect.has_key( tag ):
			if tag == "switchvocality" or tag == "switcheffect":
				 self.sect.writeBool( tag, val )
			else:
				 self.sect.writeFloat( tag, val )

	def getAudioval( self, tag ):
		if self.sect is None :
			if self.gb_audioSect.has_key( tag ):
				value = self.gb_audioSect[tag]
				return value
		else:
			if self.sect.has_key( tag ):
				if tag == "switchvocality" or tag == "switcheffect":
					value = self.sect.readBool( tag )
				else:
					value = self.sect.readFloat( tag )
				return value

	def onWindowsActive( self, active ):
		"""
		���ڵ�ʧ����ص�
		"""
		if active:
			vol = self.masterVol
		else:
			vol = 0
		BigWorld.setMasterVolume( vol )

	def getGossipSound( self ):
		"""
		��ȡ��ǰ���ŵĶԻ�����
		"""
		return self.__gossipSound


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
soundMgr = Sound.instance()

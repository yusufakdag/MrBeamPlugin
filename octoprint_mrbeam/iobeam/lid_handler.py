import logging
import time
import threading
from subprocess import call

# don't crash on a dev computer where you can't install picamera
try:
	from picamera import PiCamera

	PICAMERA_AVAILABLE = True
except:
	PICAMERA_AVAILABLE = False
	logging.getLogger("octoprint.plugins.mrbeam.iobeam.lidhandler").warn(
		"Could not import module picamera. Disabling camera integration.")

from octoprint_mrbeam.iobeam.iobeam_handler import IoBeamEvents
from octoprint.events import Events as OctoPrintEvents


# singleton
_instance = None

def lidHandler(plugin):
	global _instance
	if _instance is None:
		_instance = LidHandler(plugin._event_bus,
							   plugin._settings)
	return _instance


# This guy handles lid Events
# Honestly, I'm not sure if we need a separate handler for this...
class LidHandler(object):
	def __init__(self, event_bus, settings):
		self._event_bus = event_bus
		self._settings = settings
		self._logger = logging.getLogger("octoprint.plugins.mrbeam.iobeam.lidhandler")

		imagePath = self._settings.getBaseFolder("uploads") + '/' + self._settings.get(["cam", "localFilePath"])
		self._photo_creator = PhotoCreator(imagePath)
		self._worker = None

		self._subscribe()

	def _subscribe(self):
		self._event_bus.subscribe(IoBeamEvents.LID_OPENED, self.onEvent)
		self._event_bus.subscribe(IoBeamEvents.LID_CLOSED, self.onEvent)
		self._event_bus.subscribe(OctoPrintEvents.SHUTDOWN, self.onEvent)

	def onEvent(self, event, payload):
		self._logger.debug("onEvent() event: %s, payload: %s", event, payload)
		if event == IoBeamEvents.LID_OPENED:
			self._logger.debug("onEvent() LID_OPENED")
			self._worker = threading.Thread(target=self._photo_creator.work)
			self._worker.daemon = True
			self._worker.start()
		elif event == IoBeamEvents.LID_CLOSED:
			self._logger.debug("onEvent() LID_CLOSED")
			self._photo_creator.active = False
		elif event == OctoPrintEvents.SHUTDOWN:
			self._photo_creator.active = False


class PhotoCreator(object):
	def __init__(self, path):
		self.imagePath = path
		self.tmpPath = self.imagePath + ".tmp"
		self.active = True
		self.last_photo = 0
		self.camera = None
		self._logger = logging.getLogger("octoprint.plugins.mrbeam.iobeam.lidhandler.PhotoCreator")

	def work(self):
		try:
			self.active = True
			if not PICAMERA_AVAILABLE:
				self._logger.warn("PiCamera is not available, not able to capture pictures.")
				self.active = False
				return

			# TODO activate lights inside the working area

			self._prepare_cam()

			while self.active:
				self._capture()
				self._move_tmp_image()
				time.sleep(1)
			# now = time.time()
			# if now - self.last_photo >= 2:
			# 	self._capture()
			# 	pass
			# else:
			# 	time.sleep(2 - (now - self.last_photo))

			self._close_cam()
		except:
			self._logger.exception("Uggghhhh.... ")

	# TODO deactive light inside the working area

	def _prepare_cam(self):
		try:
			now = time.time()

			self.camera = PiCamera()
			# self.camera.resolution = (2592, 1944)
			self.camera.resolution = (1024, 768)
			self.camera.vflip = True
			self.camera.hflip = True
			self.camera.brightness = 70
			self.camera.color_effects = (128, 128)
			self.camera.start_preview()

			self._logger.debug("_prepare_cam() prepared in %ss", time.time() - now)
		except:
			self._logger.exception("_prepare_cam() Exception while preparing camera:")

	def _capture(self):
		try:
			now = time.time()
			self.camera.capture(self.tmpPath, format='jpeg', resize=(1000, 800))
			self._logger.debug("_capture() captured picture in %ss", time.time() - now)
		except:
			self._logger.exception("Exception while taking picture from camera:")

	def _move_tmp_image(self):
		returncode = call(['mv', self.tmpPath, self.imagePath])
		if returncode != 0:
			self._logger.warn("_move_tmp_image() returncode is %s (sys call, should be 0)", returncode)

	def _close_cam(self):
		if self.camera is not None:
			self.camera.close()
			self._logger.dbug("_close_cam() Camera closed ")

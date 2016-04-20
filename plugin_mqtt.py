from plugin import Plugin
import paho.mqtt.client as mqtt

class Plugin_mqtt(Plugin):
	def __init__(self,host,port,topic):
		self.mqttc = mqtt.Client(clean_session=True)
		self.mqttc.connect_async(host,port,60)
		self.mqttc.loop_start()
		self.topic=topic

	def _publish_balance(self,matomat):
		self.mqttc.publish(self.topic,matomat.total_balance()/100)

	def pay(self,matomat):
		self._publish_balance(matomat)

	def sale(self,matomat):
		self._publish_balance(matomat)

	def undo(self,matomat):
		self._publish_balance(matomat)


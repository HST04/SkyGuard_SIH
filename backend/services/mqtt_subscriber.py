import asyncio
import json
import logging
from typing import Any, Optional

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from config import settings
from models.schemas import TelemetryPayload
from services.telemetry_ingestion import telemetry_ingestion

logger = logging.getLogger("mqtt_subscriber")


class MQTTSubscriber:
    def __init__(self) -> None:
        self._client: Optional[mqtt.Client] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=settings.MQTT_CLIENT_ID,
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.connect_async(
            settings.MQTT_BROKER_HOST,
            settings.MQTT_BROKER_PORT,
            keepalive=60,
        )
        self._client.loop_start()
        logger.info(
            "MQTT subscriber starting for %s:%s topic=%s",
            settings.MQTT_BROKER_HOST,
            settings.MQTT_BROKER_PORT,
            settings.MQTT_TOPIC,
        )

    def stop(self) -> None:
        if self._client is None:
            return
        self._client.disconnect()
        self._client.loop_stop()
        self._client = None
        logger.info("MQTT subscriber stopped")

    def _on_connect(
        self,
        client: mqtt.Client,
        _userdata: Any,
        _flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        _properties: Optional[mqtt.Properties],
    ) -> None:
        if reason_code.is_failure:
            logger.error("MQTT broker rejected connection: %s", reason_code)
            return
        client.subscribe([(settings.MQTT_TOPIC, settings.MQTT_QOS), ("skyguard/incident", settings.MQTT_QOS)])
        logger.info("MQTT subscriber connected and subscribed to %s and skyguard/incident", settings.MQTT_TOPIC)

    def _on_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        _properties: Optional[mqtt.Properties],
    ) -> None:
        if reason_code != mqtt.MQTT_ERR_SUCCESS:
            logger.warning("MQTT subscriber disconnected: %s; retrying", reason_code)

    def _on_message(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        message: mqtt.MQTTMessage,
    ) -> None:
        try:
            raw_payload = json.loads(message.payload.decode("utf-8"))
            if isinstance(raw_payload, dict) and "trigger_packet" in raw_payload:
                target_data = raw_payload["trigger_packet"]
            else:
                target_data = raw_payload
            payload = TelemetryPayload.model_validate(target_data)
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
            logger.error("Discarding invalid MQTT packet on %s: %s", message.topic, exc)
            return

        if self._loop is None:
            logger.error("Discarding MQTT packet because event loop is unavailable")
            return
        future = asyncio.run_coroutine_threadsafe(
            telemetry_ingestion.ingest(payload), self._loop
        )
        future.add_done_callback(self._log_ingestion_failure)

    @staticmethod
    def _log_ingestion_failure(future: Any) -> None:
        try:
            future.result()
        except Exception:
            logger.exception("MQTT telemetry ingestion failed")


mqtt_subscriber = MQTTSubscriber()

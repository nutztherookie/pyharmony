import json
import logging

from xml.etree import cElementTree as ET

from .xmpp import BaseXMPPClient

log = logging.getLogger(__name__)


class HarmonyClient(BaseXMPPClient):
    """An XMPP client for connecting to the Logitech Harmony Hub."""

    def __init__(self, hostname, port, session_token):
        jid = '%s@connect.logitech.com/gatorade' % session_token

        super(HarmonyClient, self).__init__(jid, session_token)

        self.connect(address=(hostname, port), disable_starttls=True, use_ssl=False)
        self.result = None

    async def get_config(self):
        """Retrieves the Harmony device configuration.

        :returns: A nested dictionary containing activities, devices, etc.
        """

        # Wait until the session has been started.
        await self.session_bind_event.wait()

        iq = self.Iq()
        iq['type'] = 'get'
        action_cmd = ET.Element('oa')
        action_cmd.attrib['xmlns'] = 'connect.logitech.com'
        action_cmd.attrib['mime'] = 'vnd.logitech.harmony/vnd.logitech.harmony.engine?config'
        iq.set_payload(action_cmd)

        # TODO: Catch IqError & IqTimeout
        result = await iq.send()
        payload = result.get_payload()

        assert len(payload) == 1
        action_cmd = payload[0]

        assert action_cmd.attrib['errorcode'] == '200'
        device_list = action_cmd.text

        return json.loads(device_list)

    async def get_current_activity(self):
        """Retrieves the current activity.

        :rtype: int
        :returns: A int with the activity ID.
        """

        # Wait until the session has been started.
        await self.session_bind_event.wait()

        iq = self.Iq()
        iq['type'] = 'get'
        action_cmd = ET.Element('oa')
        action_cmd.attrib['xmlns'] = 'connect.logitech.com'
        action_cmd.attrib['mime'] = 'vnd.logitech.harmony/vnd.logitech.harmony.engine?getCurrentActivity'
        iq.set_payload(action_cmd)

        result = await iq.send()
        payload = result.get_payload()

        assert len(payload) == 1
        action_cmd = payload[0]

        assert action_cmd.attrib['errorcode'] == '200'
        activity = action_cmd.text.split("=")

        return int(activity[1])

    async def start_activity(self, activity_id):
        """Starts an activity.

        :param int activity_id: An int identifying the activity to start.

        :returns: A nested dictionary containing activities, devices, etc.
        """

        # Wait until the session has been started.
        await self.session_bind_event.wait()

        iq = self.Iq()
        iq['type'] = 'get'
        action_cmd = ET.Element('oa')
        action_cmd.attrib['xmlns'] = 'connect.logitech.com'
        action_cmd.attrib['mime'] = ('harmony.engine?startactivity')
        action_cmd.text = 'activityId=' + str(activity_id) + ':timestamp=0'
        iq.set_payload(action_cmd)

        result = await iq.send()
        payload = result.get_payload()

        assert len(payload) == 1
        action_cmd = payload[0]
        return action_cmd.text

    async def turn_off(self):
        """Turns the system off if it's on, otherwise it does nothing."""

        activity = self.get_current_activity()

        if activity != -1:
            self.start_activity(-1)
        return True
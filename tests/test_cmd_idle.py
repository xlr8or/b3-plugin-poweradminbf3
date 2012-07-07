# -*- encoding: utf-8 -*-
import logging
from mock import Mock
from b3.parsers.frostbite2.protocol import CommandFailedError
from tests import Bf3TestCase
from b3.config import CfgConfigParser
from poweradminbf3 import Poweradminbf3Plugin

class Test_cmd_idle(Bf3TestCase):

    def setUp(self):
        super(Test_cmd_idle, self).setUp()
        self.conf = CfgConfigParser()
        self.conf.loadFromString("""[commands]
idle: 40
        """)
        self.p = Poweradminbf3Plugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

        self.p.error = Mock(wraps=self.p.error)
        logging.getLogger('output').setLevel(logging.DEBUG)



    def test_no_argument_while_unknown(self):
        self.console.write.expect(('vars.idleTimeout',)).thenRaise(CommandFailedError(['foo']))
        self.superadmin.connects("god")
        self.superadmin.message_history = []
        self.superadmin.says("!idle")
        self.assertEqual(['Idle kick is [unknown]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()


    def test_no_argument_while_on(self):
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['600'])
        self.superadmin.connects("god")
        self.superadmin.message_history = []
        self.superadmin.says("!idle")
        self.assertEqual(['Idle kick is [10 min]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()


    def test_no_argument_while_off(self):
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['0'])
        self.superadmin.connects("god")
        self.superadmin.message_history = []
        self.superadmin.says("!idle")
        self.assertEqual(['Idle kick is [OFF]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()


    def test_with_argument_foo(self):
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['0'])
        self.superadmin.connects("god")
        self.superadmin.message_history = []
        self.superadmin.says("!idle f00")
        self.assertEqual(["unexpected value 'f00'. Available modes : on, off or a number of minutes"], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()


    def test_with_argument_on_while_already_on(self):
        self.p._last_idleTimeout = str(17*60)
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['600'])
        self.superadmin.connects("god")

        self.superadmin.message_history = []
        self.superadmin.says("!idle on")

        self.assertEqual(['Idle kick is already ON and set to 10 min'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()


    def test_with_argument_on_while_already_off(self):
        self.p._last_idleTimeout = str(17*60)
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['0'])
        self.console.write.expect(('vars.idleTimeout', str(17*60)))
        self.superadmin.connects("god")

        self.superadmin.message_history = []
        self.assertEqual(str(17*60), self.p._last_idleTimeout)
        self.superadmin.says("!idle on")

        self.assertEqual(['Idle kick is now [17 min]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()



    def test_on_off_on_15_on_off(self):
        self.superadmin.connects("god")
        self.assertEqual(300, self.p._last_idleTimeout)

        # ON
        self.console.write.reset_mock()
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['0'])
        self.console.write.expect(('vars.idleTimeout', 300))
        self.superadmin.message_history = []
        self.superadmin.says("!idle on")
        self.assertEqual(['Idle kick is now [5 min]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()
        self.assertEqual(300, self.p._last_idleTimeout)

        # OFF
        self.console.write.reset_mock()
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['300'])
        self.console.write.expect(('vars.idleTimeout', 0))
        self.superadmin.message_history = []
        self.superadmin.says("!idle off")
        self.assertEqual(['Idle kick is now [OFF]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()
        self.assertEqual('300', self.p._last_idleTimeout)

        # ON
        self.console.write.reset_mock()
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['0'])
        self.console.write.expect(('vars.idleTimeout', '300'))
        self.superadmin.message_history = []
        self.superadmin.says("!idle on")
        self.assertEqual(['Idle kick is now [5 min]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()
        self.assertEqual('300', self.p._last_idleTimeout)

        # 15
        self.console.write.reset_mock()
        self.console.write.expect(('vars.idleTimeout',)).thenReturn(['300'])
        self.console.write.expect(('vars.idleTimeout', 15*60))
        self.superadmin.message_history = []
        self.superadmin.says("!idle 15")
        self.assertEqual(['Idle kick is now [15 min]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()
        self.assertEqual('300', self.p._last_idleTimeout)

        # ON
        self.console.write.reset_mock()
        self.console.write.expect(('vars.idleTimeout',)).thenReturn([str(15*60)])
        self.superadmin.message_history = []
        self.superadmin.says("!idle on")
        self.assertEqual(['Idle kick is already ON and set to 15 min'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()
        self.assertEqual('300', self.p._last_idleTimeout)

        # OFF
        self.console.write.reset_mock()
        self.console.write.expect(('vars.idleTimeout',)).thenReturn([str(15*60)])
        self.console.write.expect(('vars.idleTimeout', 0))
        self.superadmin.message_history = []
        self.superadmin.says("!idle off")
        self.assertEqual(['Idle kick is now [OFF]'], self.superadmin.message_history)
        self.assertFalse(self.p.error.called)
        self.console.write.verify_expected_calls()
        self.assertEqual(str(15*60), self.p._last_idleTimeout)
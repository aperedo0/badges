"""Scheduling tests do not send messages, start timers or touch badge files."""
import copy
import unittest

import scheduled_resume as scheduler
import overnight_runtime as runtime


class ScheduledStartTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(thread_id='owner thread', authorization='one request',
                           target_epoch=20000)
        self.state = dict(status='scheduled', thread_id='owner thread',
                          schedule_authorization='one request',
                          owner_authorized_resume_epoch=20000,
                          checkpoint_seq=0,
                          deadline_epoch=None)
        self.progress = dict(status='scheduled', schedule_authorization='one request',
                             scheduled_resume_epoch=20000)

    def test_cannot_start_early(self):
        original = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            scheduler.activate(self.state, self.progress, self.config, 19999.99)
        self.assertEqual(self.state, original)

    def test_starts_only_once_at_authorized_time(self):
        scheduler.activate(self.state, self.progress, self.config, 20000)
        self.assertEqual(self.state['phase'], 'ready')
        self.assertEqual(self.progress['status'], 'working')
        self.assertIsNone(self.state['deadline_epoch'])
        with self.assertRaises(ValueError):
            scheduler.activate(self.state, self.progress, self.config, 20001)

    def test_paused_or_cancelled_state_never_starts(self):
        for status in ['paused', 'cancelled', 'complete', 'window_expired']:
            state = dict(self.state, status=status)
            with self.assertRaises(ValueError):
                scheduler.activate(state, self.progress, self.config, 20000)
        self.progress['status'] = 'paused'
        with self.assertRaises(ValueError):
            scheduler.activate(self.state, self.progress, self.config, 20000)

    def test_changed_authorization_never_starts(self):
        self.config['authorization'] = 'another request'
        with self.assertRaises(ValueError):
            scheduler.activate(self.state, self.progress, self.config, 20000)

    def test_full_work_and_break_after_delayed_start(self):
        scheduler.activate(self.state, self.progress, self.config, 20000)
        runtime.begin(self.state, 20000)
        self.assertEqual(self.state['work_until_epoch'], 21800)
        runtime.advance(self.state, 21800)
        self.assertEqual(self.state['phase'], 'break')
        self.assertEqual(self.state['break_until_epoch'], 23000)
        with self.assertRaises(ValueError):
            runtime.begin(self.state, 22999)
        runtime.advance(self.state, 23000)
        runtime.begin(self.state, 23000)
        self.assertEqual(self.state['work_until_epoch'], 24800)
        self.assertIsNone(self.state['deadline_epoch'])


if __name__ == '__main__':
    unittest.main()

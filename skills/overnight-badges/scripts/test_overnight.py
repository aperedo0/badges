"""Exercise real saved state, scheduling boundaries and mocked recovery."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import overnight as job

NOW = 1800000000.0
THREAD = '12345678-1234-4234-8234-123456789abc'


class OvernightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='badge skill test ')
        self.addCleanup(self.temp.cleanup)
        self.run = job.Run(Path(self.temp.name) / 'run with spaces')
        self.run.init(THREAD, ['moon', 'phoenix'], now=NOW)
        self.rollout = Path(self.temp.name) / 'rollout.jsonl'
        self.event('task_started')

    def event(self, kind, message=''):
        with self.rollout.open('a') as handle:
            handle.write(json.dumps({'type': 'event_msg', 'payload': {'type': kind, 'message': message}}) + '\n')
        os.utime(self.rollout, (NOW, NOW))

    def state(self, offset=0):
        return self.run.update(now=NOW + offset)

    def artifacts(self):
        files = {}
        for name in job.ARTIFACTS:
            p = Path(self.temp.name) / (name + '.artifact')
            p.write_text('test evidence')
            files[name] = str(p)
        return files

    def test_exact_work_and_break_boundaries(self):
        self.assertEqual(self.state(job.WORK - 1)['phase'], 'work')
        self.assertEqual(self.state(job.WORK)['phase'], 'break')
        self.assertEqual(self.state(job.WORK + job.BREAK - 1)['phase'], 'break')
        ready = self.state(job.WORK + job.BREAK)
        self.assertEqual(ready['phase'], 'ready')
        self.assertEqual(ready['block'], 1)

    def test_cannot_begin_early_and_resume_never_resets_window(self):
        with self.assertRaises(ValueError):
            self.run.update(job.begin, now=NOW + 20)
        old_deadline = self.state()['deadline_epoch']
        state = self.run.update(job.begin, now=NOW + job.WORK + job.BREAK)
        self.assertEqual(state['block'], 2)
        self.assertEqual(state['work_until_epoch'], NOW + 2 * job.WORK + job.BREAK)
        self.assertEqual(state['deadline_epoch'], old_deadline)

    def test_reinitializing_saved_work_is_rejected(self):
        self.run.update(lambda s, t: job.checkpoint(s, t, badge='moon', next_action='Inspect saved gem', blend='/tmp/saved.blend'), now=NOW + 10)
        before = self.run.path.read_bytes()
        with self.assertRaises(ValueError):
            self.run.init(THREAD, ['different'], now=NOW + 100)
        self.assertEqual(before, self.run.path.read_bytes())
        self.assertEqual(self.state(100)['next_action'], 'Inspect saved gem')

    def test_offline_time_does_not_fabricate_work_blocks(self):
        state = self.state(7200)
        self.assertEqual(state['phase'], 'ready')
        self.assertEqual(state['block'], 1)
        self.assertEqual(state['deadline_epoch'], NOW + 18000)

    def test_deadline_is_not_completion(self):
        state = self.state(18000)
        self.assertEqual(state['status'], 'window_expired')
        self.assertFalse((self.run.root / 'COMPLETE').exists())
        self.assertEqual(state['badges']['moon']['status'], 'pending')
        with self.assertRaises(ValueError):
            self.run.update(job.begin, now=NOW + 18001)

    def test_done_needs_review_and_all_artifacts(self):
        files = self.artifacts()
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.done(s, t, 'moon', files, False), now=NOW)
        Path(files['turn']).unlink()
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.done(s, t, 'moon', files, True), now=NOW)
        with self.assertRaises(ValueError):
            self.run.update(job.complete, now=NOW)

    def test_completed_badges_are_not_restarted(self):
        files = self.artifacts()
        self.run.update(lambda s, t: job.done(s, t, 'moon', files, True), now=NOW)
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.checkpoint(s, t, badge='moon'), now=NOW + 1)
        self.run.update(lambda s, t: job.done(s, t, 'phoenix', files, True), now=NOW + 1)
        state = self.run.update(job.complete, now=NOW + 2)
        self.assertEqual(state['status'], 'complete')
        self.assertEqual(job.check(self.run, Path('/nonexistent'), '/fake', now=NOW + 3)['action'], 'stop')

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_healthy_activity_does_not_queue(self, queue, online):
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 20)['action'], 'working')
        queue.assert_not_called()

    @patch.object(job.subprocess, 'run')
    @patch.object(job, 'online', return_value=False)
    def test_offline_checks_preserve_clock_and_recover(self, online, queue):
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 10)['action'], 'offline')
        queue.assert_not_called()
        self.assertTrue(self.state(10)['had_outage'])
        self.assertEqual(self.state(10)['work_until_epoch'], NOW + job.WORK)
        online.return_value = True
        queue.return_value = subprocess.CompletedProcess([], 0, '', '')
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 600)['action'], 'queue')

    @patch.object(job.subprocess, 'run')
    @patch.object(job, 'online', return_value=True)
    def test_break_and_busy_work_are_protected(self, online, queue):
        self.event('error', 'network connection failed')
        self.run.update(lambda s, t: job.checkpoint(s, t, next_action='Wait for tracked render', busy_minutes=8), now=NOW + 600)
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 1000)['action'], 'busy')
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + job.WORK)['action'], 'break')
        queue.assert_not_called()

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_queue_is_once_per_activity_and_exact_thread(self, queue, online):
        queue.return_value = subprocess.CompletedProcess([], 0, '', '')
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 901)['action'], 'queue')
        argv = queue.call_args.args[0]
        self.assertEqual(argv[:4], ['/fake', 'queue', '--thread', THREAD])
        self.assertIn(str(self.run.path), argv[-1])
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 1200)['action'], 'already_queued')
        self.assertEqual(queue.call_count, 1)

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_failed_delivery_can_retry_next_check(self, queue, online):
        queue.return_value = subprocess.CompletedProcess([], 1, '', '')
        job.check(self.run, self.rollout, '/fake', now=NOW + 901)
        job.check(self.run, self.rollout, '/fake', now=NOW + 1501)
        self.assertEqual(queue.call_count, 2)
        self.assertNotIn('last_queue_basis', self.state(1501))

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_break_end_wakes_once_without_starting_another_worker(self, queue, online):
        queue.return_value = subprocess.CompletedProcess([], 0, '', '')
        result = job.check(self.run, self.rollout, '/fake', now=NOW + job.WORK + job.BREAK)
        self.assertEqual(result['action'], 'queue')
        self.assertEqual(self.state(job.WORK + job.BREAK)['phase'], 'ready')
        self.assertEqual(queue.call_args.args[0][1], 'queue')

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_account_error_is_not_retried_as_a_connection(self, queue, online):
        self.event('error', 'stream failed: usage limit reached')
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=NOW + 10)['action'], 'attention')
        self.assertEqual(self.state(10)['status'], 'needs_attention')
        queue.assert_not_called()

    def test_new_turn_clears_old_connection_error(self):
        self.event('error', 'connection timed out')
        self.assertEqual(job.rollout_activity(self.rollout)['failure'], 'connection')
        self.event('task_started')
        self.assertIsNone(job.rollout_activity(self.rollout)['failure'])

    @patch.object(job.subprocess, 'run')
    @patch.object(job, 'online', return_value=True)
    def test_deadline_during_probe_prevents_queue(self, online, queue):
        with patch.object(job.time, 'time', side_effect=[NOW + 901, NOW + 18000]):
            self.assertEqual(job.check(self.run, self.rollout, '/fake')['action'], 'changed_before_queue')
        queue.assert_not_called()
        self.assertEqual(self.state(18000)['status'], 'window_expired')

    @patch.object(job.subprocess, 'run')
    def test_new_checkpoint_during_probe_prevents_duplicate_work(self, queue):
        def activity():
            self.run.update(lambda s, t: job.checkpoint(s, t, next_action='Work already resumed'), now=NOW + 901)
            return True
        with patch.object(job, 'online', side_effect=activity):
            result = job.check(self.run, self.rollout, '/fake', now=NOW + 901)
        self.assertEqual(result['action'], 'changed_before_queue')
        queue.assert_not_called()

    @patch.object(job, 'online')
    @patch.object(job.subprocess, 'run')
    def test_paused_run_never_queues(self, queue, online):
        self.run.update(lambda s, t: s.update(status='paused'), now=NOW)
        self.assertEqual(job.check(self.run, Path('/missing'), '/fake', now=NOW + 100)['action'], 'stop')
        queue.assert_not_called()
        online.assert_not_called()

    def test_all_reviewed_work_can_record_completion_after_expiry(self):
        files = self.artifacts()
        for badge in ['moon', 'phoenix']:
            self.run.update(lambda s, t: job.done(s, t, badge, files, True), now=NOW)
        result = self.run.update(job.complete, now=NOW + 18001)
        self.assertEqual(result['status'], 'complete')

    @patch.object(job, 'online')
    @patch.object(job.subprocess, 'run')
    def test_dry_run_does_not_modify_state_probe_or_queue(self, queue, online):
        before = self.run.path.read_bytes()
        result = job.check(self.run, self.rollout, '/fake', dry_run=True, now=NOW + 901)
        self.assertEqual(result['action'], 'queue')
        self.assertEqual(self.run.path.read_bytes(), before)
        queue.assert_not_called()
        online.assert_not_called()

    def test_concurrent_checkpoints_preserve_state(self):
        program = ("import sys;sys.path.insert(0,sys.argv[1]);import overnight;"
                   "r=overnight.Run(sys.argv[2]);"
                   "[r.update(lambda s,t:overnight.checkpoint(s,t,next_action='Saved'),now=float(sys.argv[3])) for _ in range(5)]")
        args = [sys.executable, '-c', program, str(Path(job.__file__).parent), str(self.run.root), str(NOW)]
        workers = [subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(3)]
        for worker in workers:
            stdout, stderr = worker.communicate(timeout=10)
            self.assertEqual(worker.returncode, 0, stderr.decode())
        state = self.state()
        self.assertEqual(state['checkpoint_seq'], 15)
        self.assertEqual(set(state['badges']), {'moon', 'phoenix'})


if __name__ == '__main__':
    unittest.main()

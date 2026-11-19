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
        self.run.init(THREAD, ['moon', 'phoenix'], hours=5, now=NOW, pacing='breaks')
        self.rollout = Path(self.temp.name) / 'rollout.jsonl'
        self.event('task_started')

    def event(self, kind, message=''):
        with self.rollout.open('a') as handle:
            handle.write(json.dumps({'type': 'event_msg', 'payload': {'type': kind, 'message': message}}) + '\n')
        os.utime(self.rollout, (NOW, NOW))

    def state(self, offset=0):
        return self.run.update(now=NOW + offset)

    def artifacts(self, review='SHIPPABLE: yes\n\nCLOSENESS: 92\n'):
        files = {}
        for name in job.ARTIFACTS:
            p = Path(self.temp.name) / (name + '.artifact')
            p.write_text(review if name == 'review' else 'test evidence')
            files[name] = str(p)
        return files

    def test_exact_work_and_break_boundaries(self):
        self.assertEqual(self.state(job.WORK - 1)['phase'], 'work')
        self.assertEqual(self.state(job.WORK)['phase'], 'break')
        self.assertEqual(self.state(job.WORK + job.BREAK - 1)['phase'], 'break')
        ready = self.state(job.WORK + job.BREAK)
        self.assertEqual(ready['phase'], 'ready')
        self.assertEqual(ready['block'], 1)

    def test_default_run_has_no_overall_time_limit(self):
        other = job.Run(Path(self.temp.name) / 'unlimited')
        initial = other.init(THREAD, ['moon'], now=NOW, pacing='breaks')
        self.assertIsNone(initial['deadline_epoch'])
        late = other.update(now=NOW + 10 * 86400)
        self.assertEqual(late['status'], 'active')
        self.assertEqual(late['phase'], 'ready')
        resumed = other.update(job.begin, now=NOW + 10 * 86400)
        self.assertIsNone(resumed['deadline_epoch'])
        self.assertEqual(resumed['work_until_epoch'], NOW + 10 * 86400 + job.WORK)

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
            self.run.update(lambda s, t: job.done(s, t, 'moon', files, ''), now=NOW)
        Path(files['turns']).unlink()
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.done(s, t, 'moon', files, 'kept 7 pieces'), now=NOW)
        with self.assertRaises(ValueError):
            self.run.update(job.complete, now=NOW)

    def test_completed_badges_are_not_restarted(self):
        files = self.artifacts()
        self.run.update(lambda s, t: job.done(s, t, 'moon', files, 'kept 7 pieces'), now=NOW)
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.checkpoint(s, t, badge='moon'), now=NOW + 1)
        self.run.update(lambda s, t: job.done(s, t, 'phoenix', files, 'kept 7 pieces'), now=NOW + 1)
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
        self.assertEqual(argv[:5], ['/fake', 'queue', '--thread', THREAD, '--resume'])
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
            self.run.update(lambda s, t: job.done(s, t, badge, files, 'kept 7 pieces'), now=NOW)
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

    def test_review_verdict_reads_real_report_formats(self):
        v = job.review_verdict
        self.assertEqual(v('SHIPPABLE: yes\n\nCLOSENESS: 91\nTOP FIXES: ...'), (True, 91))
        self.assertEqual(v('Fresh review of version 12: CLOSENESS 66. Ruby too dark'), (False, 66))
        self.assertEqual(v('Shippable: yes in the supplied views. Original mockup closeness80/100.'), (True, 80))
        self.assertEqual(v('Not yet shippable because of streaks. Original mockup closeness92/100.'), (False, 92))
        self.assertEqual(v('SHIPPABLE: yes for the gem revision. Requested gem improvement: 92/100.'), (True, None))
        self.assertEqual(v('SHIPPABLE: no\nCLOSENESS: 95'), (False, 95))

    def test_done_requires_shippable_and_ninety(self):
        for review in ['SHIPPABLE: no\nCLOSENESS: 95', 'SHIPPABLE: yes\nCLOSENESS: 89',
                       'SHIPPABLE: yes for the gem revision. Requested gem improvement: 92/100.']:
            files = self.artifacts(review)
            with self.assertRaises(ValueError):
                self.run.update(lambda s, t: job.done(s, t, 'moon', files, 'kept 7 pieces'), now=NOW)
        state = self.run.update(lambda s, t: job.done(s, t, 'moon', self.artifacts(), 'merged 12 meshes into 7, same look'), now=NOW)
        self.assertEqual(state['badges']['moon']['closeness'], 92)
        self.assertIn('same look', state['badges']['moon']['reduction'])

    def test_blocked_badges_let_the_run_complete(self):
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.block(s, t, 'moon', ' '), now=NOW)
        self.run.update(lambda s, t: job.block(s, t, 'moon', 'three versions with no gain', '/tmp/cmp.png'), now=NOW)
        with self.assertRaises(ValueError):
            self.run.update(job.complete, now=NOW + 1)
        self.run.update(lambda s, t: job.done(s, t, 'phoenix', self.artifacts(), 'kept 7 pieces'), now=NOW + 1)
        state = self.run.update(job.complete, now=NOW + 2)
        self.assertEqual(state['status'], 'complete')
        self.assertEqual(state['badges']['moon']['blocked_reason'], 'three versions with no gain')

    def test_done_badge_cannot_be_blocked_and_checkpoint_unblocks(self):
        self.run.update(lambda s, t: job.block(s, t, 'phoenix', 'owner edits unsaved in Blender'), now=NOW)
        state = self.run.update(lambda s, t: job.checkpoint(s, t, badge='phoenix', next_action='Owner saved; continue'), now=NOW + 1)
        self.assertEqual(state['badges']['phoenix']['status'], 'working')
        self.assertNotIn('blocked_reason', state['badges']['phoenix'])
        self.run.update(lambda s, t: job.done(s, t, 'moon', self.artifacts(), 'kept 7 pieces'), now=NOW + 2)
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.block(s, t, 'moon', 'late doubt'), now=NOW + 3)

    def test_pause_cancel_resume(self):
        self.assertEqual(self.run.update(job.pause, now=NOW)['status'], 'paused')
        self.assertEqual(self.run.update(lambda s, t: job.resume(s, t), now=NOW + 1)['status'], 'active')
        self.assertEqual(self.run.update(job.cancel, now=NOW + 2)['status'], 'cancelled')
        with self.assertRaises(ValueError):
            self.run.update(lambda s, t: job.resume(s, t), now=NOW + 3)
        other = job.Run(Path(self.temp.name) / 'expired')
        other.init(THREAD, ['moon'], hours=1, now=NOW)
        other.update(job.pause, now=NOW)
        with self.assertRaises(ValueError):
            other.update(lambda s, t: job.resume(s, t), now=NOW + 7200)
        self.assertEqual(other.update(lambda s, t: job.resume(s, t, 2), now=NOW + 7200)['status'], 'active')

    def test_init_defaults_to_continuous_in_the_badges_workspace(self):
        other = job.Run(Path(self.temp.name) / 'continuous')
        state = other.init(THREAD, ['moon'], now=NOW)
        self.assertEqual(state['pacing'], 'continuous')
        self.assertEqual(state['workspace'], str(Path(job.WORKSPACE).resolve()))
        with self.assertRaises(ValueError):
            job.Run(Path(self.temp.name) / 'bad').init(THREAD, ['moon'], now=NOW, pacing='naps')

    def test_continuous_pacing_never_breaks(self):
        other = job.Run(Path(self.temp.name) / 'continuous')
        other.init(THREAD, ['moon'], now=NOW)
        state = other.update(now=NOW + job.WORK)
        self.assertEqual((state['phase'], state['block']), ('work', 2))
        state = other.update(now=NOW + 10 * job.WORK)
        self.assertEqual(state['phase'], 'work')
        self.assertGreaterEqual(state['work_until_epoch'], NOW + 10 * job.WORK)
        with self.assertRaises(ValueError):
            other.update(job.begin, now=NOW + 10 * job.WORK)
        state = other.update(lambda s, t: job.checkpoint(s, t, next_action='simulator build', busy_minutes=50), now=NOW + 10 * job.WORK)
        self.assertEqual(state['busy_until_epoch'], NOW + 10 * job.WORK + 3000)

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_continuous_run_queues_only_when_stale(self, queue, online):
        other = job.Run(Path(self.temp.name) / 'continuous')
        other.init(THREAD, ['moon'], now=NOW)
        queue.return_value = subprocess.CompletedProcess([], 0, '', '')
        self.assertEqual(job.check(other, self.rollout, '/fake', now=NOW + 300)['action'], 'working')
        self.assertEqual(job.check(other, self.rollout, '/fake', now=NOW + job.STALE + 1)['action'], 'queue')
        self.assertEqual(queue.call_count, 1)

    @patch.object(job, 'online', return_value=True)
    @patch.object(job.subprocess, 'run')
    def test_ready_wake_is_not_repeated_while_the_thread_writes(self, queue, online):
        queue.return_value = subprocess.CompletedProcess([], 0, '', '')
        ready = NOW + job.WORK + job.BREAK
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=ready)['action'], 'queue')
        # the woken thread writes to its rollout, which used to look like new activity every time
        for k in range(1, 5):
            self.event('agent_message')
            os.utime(self.rollout, (ready + 60 * k, ready + 60 * k))
            self.assertEqual(job.check(self.run, self.rollout, '/fake', now=ready + 60 * k + 30)['action'], 'already_queued')
        self.assertEqual(queue.call_count, 1)
        # idle for the stale time after its last write: one more wake is allowed
        last = ready + 240
        self.assertEqual(job.check(self.run, self.rollout, '/fake', now=last + job.STALE + 1)['action'], 'queue')
        self.assertEqual(queue.call_count, 2)

    @patch.object(job.subprocess, 'run')
    def test_queue_cli_requires_resume_support(self, run):
        cli = Path(self.temp.name) / 'codex'
        cli.write_text('#!/bin/sh\n')
        run.return_value = subprocess.CompletedProcess([], 0, 'Usage: queue --thread X --message Y', '')
        with self.assertRaises(ValueError):
            job.queue_cli(str(cli))
        run.return_value = subprocess.CompletedProcess([], 0, 'Usage: queue --thread X --message Y --resume', '')
        self.assertEqual(job.queue_cli(str(cli)), str(cli.resolve()))


if __name__ == '__main__':
    unittest.main()

def check_pose_report36(report):
    assert report.get('full_frame_screen_complete') is True, 'Motion screen did not finish'
    assert [p['frame'] for p in report.get('frames', [])] == list(range(0,491,10)), 'Motion screen did not test all50 poses'
    assert not report.get('unclassified'), 'Motion screen found an unclassified contact'
    return True

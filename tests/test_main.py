from main import CodeTour

def test_tour(capsys):
    CodeTour.tour('dummy_commit', 'dummy_repository')
    captured = capsys.readouterr()
    assert "Starting tour from commit dummy_commit in repository dummy_repository" in captured.out
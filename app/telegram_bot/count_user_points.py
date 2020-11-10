class TestCounter:
    """Count user's points from the testing."""

    def __init__(self, count=0):
        self.count = count

    def add_point(self, point):
        self.count += point

    @property
    def show_total(self):
        return self.count
  
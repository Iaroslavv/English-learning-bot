class UserPoints:
    """Count user points."""

    def __init__(self, count=0):
        self.count = count
    
    def add_point(self, point):
        self.count += point

    @property
    def show_points(self):
        return self.count

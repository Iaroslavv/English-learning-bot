


class UserPoints:
    points = 0

    def __init__(self):
        self.points = 0
    
    @staticmethod
    def add_point(self):
        self.point += 1

    @staticmethod
    def show_points(self):
        return self.point

points = UserPoints(0)
points.add_point(1)
print(points.show_points())
class TestCounter:
    """Count user's points from the testing."""
    level = "Type in the command '/choose level'"

    def __init__(self, count=0, level=level):
        self.count = count
        self.level = level

    def add_point(self, point):
        self.count += point

    @property
    def show_total(self):
        if self.count <= 10:
            total = f"Your level is beginner. {self.count}/50 are correct!{self.level}"
        if 10 < self.count <= 16:
            total = f"Your level is elementary. {self.count}/50 are correct! {self.level}"
        if 16 < self.count <= 25:
            total = f"Your level is pre-intermediate.{self.count}/50 are correct!{self.level}"
        if 25 < self.count <= 34:
            total = f"Your level is itermediate. {self.count}/50 are correct! {self.level}"
        if 34 < self.count <= 43:
            total = f"Your level is upper-intermediate. {self.count}/50 are correct!{self.level}"
        if 43 < self.count <= 50:
            total = f"Your level is advanced. {self.count}/50 are correct!{self.level}"
        return total

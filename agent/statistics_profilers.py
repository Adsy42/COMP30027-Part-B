import csv


def profiler_wrapper(func):
    def wrapper(self, *args, **kwargs):
        action = func(self, *args, **kwargs)  # Call the original method to get the action
        # Calculate board control value for the action
        board_control_value = self.board_control(self.my_colour, self.my_board)
        # Write the action and its board control value to a CSV file
        with open('profile_statistics.csv', mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([action, board_control_value])
        return action
    return wrapper

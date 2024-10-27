class Event:
    def __init__(self, start_time, end_time):
        if start_time >= end_time:
            raise ValueError
        self.start_time = start_time
        self.end_time = end_time

class Calendar:
    def __init__(self):
        self.__events = []
    def get_events(self):
        return self.__events
    def add_event(self, event):
        if type(event) is not Event:
            raise TypeError
        self.__events.append(event)

class AdventCalendar(Calendar):
    def __init__(self, year):
        self.year = year
        # super().__init__()
    
# class AdventCalendar(Calendar):
#     def __init__(self, year):
#         self.year = year
#         self.__events = []
#     def get_events(self):
#         return self.__events


## Part A
# event = Event(10, 20)
# print(f"Start: {event.start_time}, End: {event.end_time}")
# try:
#     invalid_event = Event(20, 10)
#     print("Success")
# except ValueError:
#     print("Created an invalid event")

## Part B
# calendar = Calendar()
# print(calendar.get_events())
# calendar.add_event(Event(10, 20))
# print(calendar.get_events()[0].start_time)
# try:
#     calendar.add_event("not an event")
# except TypeError:
#     print("Invalid event")
    
## Part C
advent_calendar = AdventCalendar(2022)
print(advent_calendar.get_events())
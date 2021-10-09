#!/usr/bin/env python3

import platform
import time
import datetime
import ephem
import subprocess


def get_ephem_observer():
    obs = ephem.Observer()

    obs.date = datetime.date.today()

    obs.lat = str(49.022269)
    obs.lon = str(8.760951)
    obs.elev = 194.8414459228516

    return obs


def get_event(obs, event):
    if event == "midnight":
        return datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    return ephem.localtime(get_event_utc(obs, event))


def get_event_utc(obs, event):
    obs.horizon = "0"
    if event == "sunrise":
        return obs.next_rising(ephem.Sun())
    if event == "noon":
        return obs.next_transit(ephem.Sun())
    if event == "sunset":
        return obs.next_setting(ephem.Sun())

    print("Function get_event_utc has gotten some wrong value:\nobs: " + obs + "\nevent: " + event)
    return False


def get_next_event(timespan_in_minutes, obs=get_ephem_observer()):
    now = datetime.datetime.now()  # current date and time
    events = ["sunrise", "noon", "sunset", "midnight"]

    next_event = "none"  # set as none in the beginning, will either not be used, or changed later
    seconds_till_next_event = 24 * 60 * 60 + 10  # seconds of a day plus ten seconds, any event is nearer than that

    for event in events:
        # if timediff < 0 event has passed, need to check if its still within timespan
        timediff = (get_event(obs, event) - now).total_seconds()

        # and not event == "midnight" ## not necessary since midnight is checked last either way
        if abs(timediff) <= ( timespan_in_minutes / 2 * 60):
            # returns: current event, time from event till now/ or time until event, event is ongoing.
            return event, timediff, True

        if 0 <= timediff < seconds_till_next_event:
            next_event = event
            seconds_till_next_event = timediff

    return next_event, seconds_till_next_event, False  # if it arrives here it will always be false.


def timelapse(event, end_time, seconds_between_pictures=120, verbose=False, raw=False, stats=False):
    print("Starting timelapse for event <" + event + ">. current time: " + str(datetime.datetime.now()))

    while (end_time - datetime.datetime.now()).total_seconds() >= 0:
        now = datetime.datetime.now()
        if platform.node() == "raspberrypi":
            subprocess.run(["bash", "/home/pi/timelapse/get_temp.sh", "1"])

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
            command = "raspistill --nopreview " \
                      + ("--verbose " if verbose else "") \
                      + ("--raw " if raw else "") \
                      + ("--stats " if stats else "") \
                      + "--output \"/home/pi/timelapse/" + event + "/" + timestamp + ".jpg\""
            subprocess.run(command, shell=True)

            subprocess.run(["bash", "/home/pi/timelapse/get_temp.sh", "2"])
        else:
            print("You can only do this on the raspberrypi")

        time_to_sleep = int((now - datetime.datetime.now()).total_seconds()) + seconds_between_pictures
        print("Sleeping for <" + str(time_to_sleep) + "> seconds")
        time.sleep(time_to_sleep)

    print("Finished timelapse for event <" + event + ">. current time: " + str(datetime.datetime.now()))


def main(timespan, my_obs):
    while True:
        current_event, seconds_till_event, event_ongoing = get_next_event(timespan_in_minutes=timespan, obs=my_obs)

        if current_event == "midnight": # no timelapse for midnight
            print("All events for today are over, sleeping until after midnight for <" + str(int(seconds_till_event) + 60) + "> seconds.")
            time.sleep(seconds_till_event + 60)  # sleep past midnight, waits for next day and checks for next events
        else:
            if not event_ongoing:  # sleep until it is time to start the timelapse
                print("No event ongoing, next event is <" + current_event + "> in <" + str(
                    int(seconds_till_event)) + "> seconds. \n Going to sleep for <" + str(
                    int(seconds_till_event - 90 * 60)) + "> seconds.")
                time.sleep(int(seconds_till_event - 90 * 60))

            print("Event ongoing, current event is <" + current_event + "> since <" + str(
                90 * 60 - abs(int(seconds_till_event))) + "> seconds.")

            event_end_time = datetime.datetime.now() + datetime.timedelta(minutes=timespan)
            timelapse(current_event, event_end_time, verbose=True, raw=True, stats=True)


if __name__ == "__main__":
    print("Starting raspberypi_event_timelapse.py")
    # timespan in minutes, my_obs is an epehm observer
    main(timespan=180, my_obs=get_ephem_observer())


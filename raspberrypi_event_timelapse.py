#!/usr/bin/env python3

import platform
import time
import datetime
import ephem
import subprocess

# timespan before and after event in seconds
TIMESPAN = 60 * 60

LOG = True
def log(s, ERROR=False):
    if ERROR or LOG: print("<" + str(datetime.datetime.now()) + "> ::" + ("ERROR" if ERROR else "DEBUG") + ":: " + s)

def get_ephem_observer():
    obs = ephem.Observer()

    obs.date = datetime.date.today()

    obs.lat = str(49.022269)
    obs.lon = str(8.760951)
    obs.elev = 194.8414459228516

    obs.horizon = "0"

    return obs


def get_event(obs, event):
    if event == "midnight":
        return datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    return ephem.localtime(get_event_utc(obs, event))


def get_event_utc(obs, event):
    if event == "sunrise":
        return obs.next_rising(ephem.Sun())
    if event == "noon":
        return obs.next_transit(ephem.Sun())
    if event == "sunset":
        return obs.next_setting(ephem.Sun())

    log("Function get_event_utc has gotten some wrong value:\nobs: " + obs + "\nevent: " + event, ERROR=True)
    return False

def begin(event_time):
    return event_time - datetime.timedelta(seconds=TIMESPAN)

def end(event_time):
    return event_time + datetime.timedelta(seconds=TIMESPAN)

def wait_time(time):
    return (time - datetime.datetime.now()).total_seconds()


# get_next_event
#   - timespan_in_minutes := int
# returns
#   - currently ongoing or next event if none ongoing
#   - event time
#   - bool if event is ongoing
def get_next_event():
    obs=get_ephem_observer()

    log("Checking for next event.")
    events = ["sunrise", "noon", "sunset", "midnight"]

    next_event = "none"  # set as none in the beginning, will either not be used, or changed later
    next_event_time = datetime.datetime.now() + datetime.timedelta(days=1) # tomorrow
    ongoing = False

    for event in events:
        event_time = get_event(obs, event)

        log("Event " + event + " is at <" + str(event_time) + ">.")

        seconds_till_event = (event_time - datetime.datetime.now()).total_seconds()
        log("Event " + event + " is in <" + str(seconds_till_event) + "> seconds.")
        if abs(seconds_till_event) <= TIMESPAN:
            next_event = event
            next_event_time = event_time
            ongoing = True

        if not ongoing and datetime.datetime.now() <= event_time < next_event_time:
            next_event = event
            next_event_time = event_time

    log("Next event is " + next_event + " at <" + str(next_event_time) + ">" + (", Event is currently ongoing." if ongoing else "."))
    log("Event start time is <" + str(begin(next_event_time)) + ">.")
    log("Event end time is <" + str(end(next_event_time)) + ">.")
    return next_event, next_event_time, ongoing


def timelapse(event, event_time, seconds_between_pictures=120, verbose=False, raw=False, stats=False):
    log("Starting timelapse for event " + event + ".")

    while end(event_time) >= datetime.datetime.now():
        now = datetime.datetime.now()

        timestamp = now.strftime("%Y-%m-%d-%H-%M")
        command = "raspistill --nopreview " \
                      + ("--verbose " if verbose else "") \
                      + ("--raw " if raw else "") \
                      + ("--stats " if stats else "") \
                      + "--output \"/home/pi/timelapse/" + event + "/" + timestamp + ".jpg\""

        if platform.node() == "raspberrypi":

            subprocess.run(["bash", "/home/pi/timelapse/scripts/save_temp.sh", "1"])
            subprocess.run(command, shell=True)

            subprocess.run(["bash", "/home/pi/timelapse/scripts/save_temp.sh", "2"])
        else:
            log(command)

        time_to_sleep = int((now - datetime.datetime.now()).total_seconds()) + seconds_between_pictures
        time.sleep(time_to_sleep)

    log("Finished timelapse for event " + event + ".")


def main():

    while True:
        current_event, event_time, event_ongoing = get_next_event()

        if current_event == "midnight":  # no timelapse for midnight
            log("All events for today are over. Sleeping until after midnight.")
            log("Going to sleep for <" + str(
                wait_time(end(event_time))) + "> seconds, until <" + str(end(event_time)) + ">.")
            time.sleep(wait_time(end(event_time)))  # sleep past midnight, waits for next day and checks for next events
        else:
            if not event_ongoing:  # sleep until it is time to start the timelapse
                log("Going to sleep for <" + str(
                    wait_time(begin(event_time))) + "> seconds, until <" + str(begin(event_time)) + ">.")
                time.sleep(wait_time(begin(event_time)))
                log("Event is now starting, current event is " + current_event + ". Event end time is <" + str(end(event_time)) + ">.")

            if platform.node() == "raspberrypi":
                timelapse(current_event, event_time, verbose=False, raw=False, stats=True)
            else:
                log("You can only do this on the raspberrypi", ERROR=True)
                time.sleep(wait_time(end(event_time)))


if __name__ == "__main__":
    log("Starting raspberrypi_event_timelapse.py")
    main()

# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests

from datetime import datetime, date, timedelta
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Hello!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class SummarizeEventsIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SummarizeEventsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        latit = 45.571912
        longit = -122.727936
        location_key = 2187576
        accu_api_key = "t6ZAidzVdD52x3tTYzAzYBxATNgtltNd"
        
        greeting_output = ""
        todayTime = datetime.today()
        todayTime = todayTime - timedelta(hours=8)
        todayTimeString = todayTime.strftime("%H:%M")
        todayTimeString = ("11:45")
        todayTimeFormat = datetime.strptime(todayTimeString, "%H:%M")
        morning = datetime.strptime("11:59", "%H:%M")
        afternoon = datetime.strptime("17:00", "%H:%M")
        if (todayTimeFormat < morning):
            greeting_output = "Good morning! "
        elif (todayTimeFormat < afternoon):
            greeting_output = "Good afternoon! "
        else:
            greeting_output = "Good Evening! {} ".format(todayTimeString)
        
        
        api_url = "https://api.openweathermap.org/data/2.5/weather?lat=45.571912&lon=-122.727936&appid=7eb188e1221725a672ba92172ff57c52&units=imperial"
        get_json = requests.get(api_url).json()
        
        get_weather = get_json['main']
        
        curr_temp = round(get_weather['temp'])
        feels_temp = round(get_weather['feels_like'])
        curr_weather_output = "The weather is {} degrees F outside right now, and it feels like {} degrees. ".format(curr_temp, feels_temp)
        
        api_url = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/2187576?apikey=t6ZAidzVdD52x3tTYzAzYBxATNgtltNd"
        get_json2 = requests.get(api_url).json()
        
        min_max_output = ""
        precip_output = ""
        
        # 0 = forecast temp
        # 1 = precip boolean
        # 2 = precip type
        # 3 = precip intensity
        # 4 = precip chance
        hour_forecast_12 = []
        for eachHour in get_json2:
            hour_forecast = []
            hour_forecast.append(eachHour['Temperature']['Value'])
            hour_forecast.append(eachHour['HasPrecipitation'])
            if(eachHour['HasPrecipitation']):
                hour_forecast.append(eachHour['PrecipitationType'])
                hour_forecast.append(eachHour['PrecipitationIntensity'])
                hour_forecast.append(eachHour['PrecipitationProbability'])
            else:
                hour_forecast.append("None")
                hour_forecast.append("None")
                hour_forecast.append(0)
            hour_forecast_12.append(hour_forecast)
        
        temps = []
        chances = []
        
        for v in hour_forecast_12:
            temps.append(v[0])
            chances.append(v[4])
        
        high_temp = round(max(temps))
        low_temp = round(min(temps))
        avg_precip_chance = round(sum(chances) / len(chances))
        max_precip_chance = max(chances)
        max_precip_chance_type = ""
        max_precip_chance_intens = ""
        
        for v in hour_forecast_12:
            if(max_precip_chance == v[4]):
                max_precip_chance_type = v[2]
                max_precip_chance_intens = v[3]
        
        max_precip_chance_intens = max_precip_chance_intens.lower()
        max_precip_chance_type = max_precip_chance_type.lower()
        
        realistic_precip_chance = round((avg_precip_chance + max_precip_chance) / 2)
        
        min_max_output = "For the next 12 hours, there is a forecasted high of {} degrees, with a low of {}. ".format(high_temp, low_temp)
        precip_output = ""
        if(realistic_precip_chance == 0):
            precip_output = "There is also no chance of rain for the next several hours. "
        elif(realistic_precip_chance < 25):
            precip_output = "There is only about a {} percent chance of {} with most of it being {} for the next several hours. ".format(realistic_precip_chance, max_precip_chance_type, max_precip_chance_intens)
        elif(realistic_precip_chance < 66):
            precip_output = "There is a {} percent chance of {} with most of it being {} for the next several hours. ".format(realistic_precip_chance, max_precip_chance_type, max_precip_chance_intens)
        else:
            precip_output = "There is a solid {} percent chance of {} with most of it being {} for the next several hours. You should probably dress appropriately. ".format(realistic_precip_chance, max_precip_chance_type, max_precip_chance_intens)

        outlook_url = 'https://api.jsonbin.io/v3/b/638bec4ee0fc777dc54f9a04'
        headers = {
          'X-Master-Key': '$2b$10$.Q0rNw26yebTGuFFOKNIpe.z/WP.iQb.DeSzsWcbq8smJzMcXUqXC'
        }
        req = requests.get(outlook_url, headers=headers)
        
        record = req.json()
        weekEvents = record['record']['value']
        
        eventsList = []
        for ev in weekEvents:
            eventDets = []
            eventDets.append(ev['subject'])
            eventDets.append(ev['bodyPreview'])
            timeStartString = datetime.strptime(ev['start']['dateTime'][11:16], "%H:%M")
            timeEndString = datetime.strptime(ev['end']['dateTime'][11:16], "%H:%M")
            rTimeStartString = timeStartString.strftime("%I:%M %p")
            rTimeEndString = timeEndString.strftime("%I:%M %p")
            eventDets.append(rTimeStartString)
            eventDets.append(rTimeEndString)
            dateStartString = ev['start']['dateTime'][:10]
            eventDets.append(dateStartString)
            eventDets.append(ev['location']['displayName'])
            eventsList.append(eventDets)
        
        today = date.today()
        todayDate = today.strftime("%Y-%m-%d")
        todayDate = "2022-12-05"
        
        classList = []
        classes_output = ""
        c_output = ""
        
        for a in eventsList:
            if(a[1] == "Class" and todayDate == a[4]):
                classList.append(a)
        totalClasses = len(classList)
        
        if(totalClasses == 0):
            classes_output = "You have no classes today. "
        else:
            classes_output = "You have {} classes today: ".format(totalClasses)
            for idx, c in enumerate(classList):
                if(totalClasses == 1):
                    c_output = c_output + ("{} in {} from {} to {}. ".format(c[0], c[5], c[2], c[3]))
                elif(idx == (totalClasses-1) and totalClasses != 1):
                    c_output = c_output + ("and {} in {} from {} to {}. ".format(c[0], c[5], c[2], c[3]))
                else:
                    c_output = c_output + ("{} in {} from {} to {}, ".format(c[0], c[5], c[2], c[3]))
        
        total_classes_output = classes_output + c_output
        
        meetingList = []
        meetings_output = ""
        m_output = ""
        
        for b in eventsList:
            if(b[1] == "Meeting" and todayDate == b[4]):
                meetingList.append(b)
        totalMeetings = len(meetingList)
        
        if(totalMeetings == 0):
            meetings_output = "You also have no meetings today. "
        else:
            meetings_output = "You also have {} meetings today: ".format(totalMeetings)
            for idx, c in enumerate(meetingList):
                if(c[5] != "online"):
                    if(totalMeetings == 1):
                        m_output = m_output + ("{} in {} from {} to {}. ".format(c[0], c[5], c[2], c[3]))
                    elif(idx == (totalMeetings-1) and totalMeetings != 1):
                        m_output = m_output + ("and {} in {} from {} to {}. ".format(c[0], c[5], c[2], c[3]))
                    else:
                        m_output = m_output + ("{} in {} from {} to {}, ".format(c[0], c[5], c[2], c[3]))
                else:
                    if(totalMeetings == 1):
                        m_output = m_output + ("{} which is an online call from {} to {}. ".format(c[0], c[2], c[3]))
                    elif(idx == (totalMeetings-1) and totalMeetings != 1):
                        m_output = m_output + ("and {} which is an online call from {} to {}. ".format(c[0], c[2], c[3]))
                    else:
                        m_output = m_output + ("{} which is an online call from {} to {}, ".format(c[0], c[2], c[3]))
        
        total_meetings_output = meetings_output + m_output
        
        google_url = 'https://api.jsonbin.io/v3/b/638c2d7accc1f33a9e63661e'
        headers2 = {
          'X-Master-Key': '$2b$10$.Q0rNw26yebTGuFFOKNIpe.z/WP.iQb.DeSzsWcbq8smJzMcXUqXC'
        }
        req2 = requests.get(google_url, headers=headers2)
        response = req2.json()
        weekTasks = response['record']['items']
        
        taskList = []
        for t in weekTasks:
            taskDets = []
            if(t['description'] == "task"):
                taskDets.append(t['summary'])
                taskDate = t['start']['dateTime'][:10]
                taskDets.append(datetime.strptime(taskDate, "%Y-%m-%d"))
                rTaskTime = datetime.strptime(t['start']['dateTime'][11:16], "%H:%M")
                taskTime = rTaskTime.strftime("%I:%M %p")
                taskDets.append(taskTime)
            taskList.append(taskDets)
        
        today = date.today()
        todayDate = today.strftime("%Y-%m-%d")
        todayDate = "2022-12-05"
        todayDateVar = datetime.strptime(todayDate, "%Y-%m-%d")
        
        todayTasks = []
        restWeekTasks = []
        for m in taskList:
            if(m[1] == todayDateVar):
                todayTasks.append(m)
            elif(m[1] > todayDateVar):
                restWeekTasks.append(m)
        
        totalTodayTasks = len(todayTasks)
        totalWeekTasks = len(restWeekTasks)
        
        task_output = ""
        if(totalTodayTasks == 0):
            task_output = "You have no tasks to complete today. "
        else:
            task_output = "You have {} tasks to complete today: ".format(totalTodayTasks)
        for idx, n in enumerate(todayTasks):
            if(totalTodayTasks == 1):
                task_output = task_output + "{} to be done at about {}. ".format(n[0], n[2])
            elif(totalTodayTasks != 1 and idx == (totalTodayTasks-1)):
                task_output = task_output + "and {} to be done at about {}. ".format(n[0], n[2])
            else:
                task_output = task_output + "{} to be done at about {}, ".format(n[0], n[2])
        
        if(totalWeekTasks == 0):
            task_output = task_output + "And, you have no tasks to do the rest of the week. "
        else:
            task_output = task_output + "And you have {} tasks to do throughout the week: ".format(totalWeekTasks)
        for idx, p in enumerate(restWeekTasks):
            if(totalWeekTasks == 1):
                task_output = task_output + "{}. ".format(p[0])
            elif(totalWeekTasks != 1 and idx == (totalWeekTasks-1)):
                task_output = task_output + "and {}. ".format(p[0])
            else:
                task_output = task_output + "{}, ".format(p[0])

        inside_output = "It is currently 68 degrees inside, so it is significantly cooler outside and will be that way throughout the day. "

        speak_output = greeting_output + curr_weather_output + inside_output + min_max_output + precip_output + total_classes_output + total_meetings_output + task_output
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SummarizeEventsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
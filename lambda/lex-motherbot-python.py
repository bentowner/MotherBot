"""
 This Lex Code Hook Interface serves a bot which manages parental events as appointments.
 Bot, Intent, and Slot models can be found in the Lex Console as part of 'MotherBot'.

"""

import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message,
            'responseCard': response_card
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message,
            'responseCard': response_card
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def build_response_card(title, subtitle, options):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    if options is not None:
        buttons = []
        for i in range(min(5, len(options))):
            buttons.append(options[i])

    return {
        'contentType': 'application/vnd.amazonaws.card.generic',
        'version': 1,
        'genericAttachments': [{
            'title': title,
            'subTitle': subtitle,
            'buttons': buttons
        }]
    }


""" --- Helper Functions --- """


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def increment_time_by_thirty_mins(appointment_time):
    hour, minute = map(int, appointment_time.split(':'))
    return '{}:00'.format(hour + 1) if minute == 30 else '{}:30'.format(hour)


def generate_car_price(location, days, age, car_type):
    """
    Generates a number within a reasonable range that might be expected for a flight.
    The price is fixed for a given pair of locations.
    """

    car_types = ['economy', 'standard', 'midsize', 'full size', 'minivan', 'luxury']
    base_location_cost = 0
    for i in range(len(location)):
        base_location_cost += ord(location.lower()[i]) - 97

    age_multiplier = 1.10 if age < 25 else 1
    # Select economy is car_type is not found
    if car_type not in car_types:
        car_type = car_types[0]

    return days * ((100 + base_location_cost) + ((car_types.index(car_type.lower()) * 50) * age_multiplier))


def generate_hotel_price(location, nights, room_type):
    """
    Generates a number within a reasonable range that might be expected for a hotel.
    The price is fixed for a pair of location and roomType.
    """

    room_types = ['queen', 'king', 'deluxe']
    cost_of_living = 0
    for i in range(len(location)):
        cost_of_living += ord(location.lower()[i]) - 97

    return nights * (100 + cost_of_living + (100 + room_types.index(room_type.lower())))


def get_random_int(minimum, maximum):
    """
    Returns a random integer between min (included) and max (excluded)
    """
    min_int = math.ceil(minimum)
    max_int = math.floor(maximum)

    return random.randint(min_int, max_int - 1)


def get_availabilities(date):
    """
    Helper function which in a full implementation would  feed into a backend API to provide query schedule availability.
    The output of this function is an array of 30 minute periods of availability, expressed in ISO-8601 time format.

    In order to enable quick demonstration of all possible conversation paths supported in this example, the function
    returns a mixture of fixed and randomized results.

    On Mondays, availability is randomized; otherwise there is no availability on Tuesday / Thursday and availability at
    10:00 - 10:30 and 4:00 - 5:00 on Wednesday / Friday.
    """
    day_of_week = dateutil.parser.parse(date).weekday()
    availabilities = []
    available_probability = 0.3
    if day_of_week == 0:
        start_hour = 10
        while start_hour <= 16:
            if random.random() < available_probability:
                # Add an availability window for the given hour, with duration determined by another random number.
                appointment_type = get_random_int(1, 4)
                if appointment_type == 1:
                    availabilities.append('{}:00'.format(start_hour))
                elif appointment_type == 2:
                    availabilities.append('{}:30'.format(start_hour))
                else:
                    availabilities.append('{}:00'.format(start_hour))
                    availabilities.append('{}:30'.format(start_hour))
            start_hour += 1

    if day_of_week == 2 or day_of_week == 4:
        availabilities.append('10:00')
        availabilities.append('16:00')
        availabilities.append('16:30')

    return availabilities


def isvalid_car_type(car_type):
    car_types = ['economy', 'standard', 'midsize', 'full size', 'minivan', 'luxury']
    return car_type.lower() in car_types


def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland']
    return city.lower() in valid_cities


def isvalid_room_type(room_type):
    room_types = ['queen', 'king', 'deluxe']
    return room_type.lower() in room_types


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def is_available(appointment_time, duration, availabilities):
    """
    Helper function to check if the given time and duration fits within a known set of availability windows.
    Duration is assumed to be one of 30, 60 (meaning minutes).  Availabilities is expected to contain entries of the format HH:MM.
    """
    if duration == 30:
        return appointment_time in availabilities
    elif duration == 60:
        second_half_hour_time = increment_time_by_thirty_mins(appointment_time)
        return appointment_time in availabilities and second_half_hour_time in availabilities

    # Invalid duration ; throw error.  We should not have reached this branch due to earlier validation.
    raise Exception('Was not able to understand duration {}'.format(duration))


def get_duration(appointment_type):
    appointment_duration_map = {'cleaning': 30, 'root canal': 60, 'whitening': 30}
    return try_ex(lambda: appointment_duration_map[appointment_type.lower()])


def get_availabilities_for_duration(duration, availabilities):
    """
    Helper function to return the windows of availability of the given duration, when provided a set of 30 minute windows.
    """
    duration_availabilities = []
    start_time = '10:00'
    while start_time != '17:00':
        if start_time in availabilities:
            if duration == 30:
                duration_availabilities.append(start_time)
            elif increment_time_by_thirty_mins(start_time) in availabilities:
                duration_availabilities.append(start_time)

        start_time = increment_time_by_thirty_mins(start_time)

    return duration_availabilities


def get_day_difference(later_date, earlier_date):
    later_datetime = dateutil.parser.parse(later_date).date()
    earlier_datetime = dateutil.parser.parse(earlier_date).date()
    return abs(later_datetime - earlier_datetime).days


def add_days(date, number_of_days):
    new_date = dateutil.parser.parse(date).date()
    new_date += datetime.timedelta(days=number_of_days)
    return new_date.strftime('%Y-%m-%d')


def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_book_appointment(appointment_type, date, appointment_time):
    if appointment_type and not get_duration(appointment_type):
        return build_validation_result(False, 'AppointmentType', 'I did not recognize that, can I book you a root canal, cleaning, or whitening?')

    if appointment_time:
        if len(appointment_time) != 5:
            return build_validation_result(False, 'Time', 'I did not recognize that, what time would you like to book your appointment?')

        hour, minute = appointment_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            return build_validation_result(False, 'Time', 'I did not recognize that, what time would you like to book your appointment?')

        if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(False, 'Time', 'Our business hours are ten a.m. to five p.m.  What time works best for you?')

        if minute not in [30, 0]:
            # Must be booked on the hour or half hour
            return build_validation_result(False, 'Time', 'We schedule appointments every half hour, what time works best for you?')

    if date:
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand that, what date works best for you?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'Date', 'Appointments must be scheduled a day in advance.  Can you try a different date?')
        elif dateutil.parser.parse(date).weekday() == 5 or dateutil.parser.parse(date).weekday() == 6:
            return build_validation_result(False, 'Date', 'Our office is not open on the weekends, can you provide a work day?')

    return build_validation_result(True, None, None)


def build_time_output_string(appointment_time):
    hour, minute = appointment_time.split(':')  # no conversion to int in order to have original string form. for eg) 10:00 instead of 10:0
    if int(hour) > 12:
        return '{}:{} p.m.'.format((int(hour) - 12), minute)
    elif int(hour) == 12:
        return '12:{} p.m.'.format(minute)
    elif int(hour) == 0:
        return '12:{} a.m.'.format(minute)

    return '{}:{} a.m.'.format(hour, minute)


def build_available_time_string(availabilities):
    """
    Build a string eliciting for a possible time slot among at least two availabilities.
    """
    prefix = 'We have availabilities at '
    if len(availabilities) > 3:
        prefix = 'We have plenty of availability, including '

    prefix += build_time_output_string(availabilities[0])
    if len(availabilities) == 2:
        return '{} and {}'.format(prefix, build_time_output_string(availabilities[1]))

    return '{}, {} and {}'.format(prefix, build_time_output_string(availabilities[1]), build_time_output_string(availabilities[2]))


def build_options(slot, appointment_type, date, booking_map):
    """
    Build a list of potential options for a given slot, to be used in responseCard generation.
    """
    day_strings = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if slot == 'AppointmentType':
        return [
            {'text': 'cleaning (30 min)', 'value': 'cleaning'},
            {'text': 'root canal (60 min)', 'value': 'root canal'},
            {'text': 'whitening (30 min)', 'value': 'whitening'}
        ]
    elif slot == 'Date':
        # Return the next five weekdays.
        options = []
        potential_date = datetime.date.today()
        while len(options) < 5:
            potential_date = potential_date + datetime.timedelta(days=1)
            if potential_date.weekday() < 5:
                options.append({'text': '{}-{} ({})'.format((potential_date.month), potential_date.day, day_strings[potential_date.weekday()]),
                                'value': potential_date.strftime('%A, %B %d, %Y')})
        return options
    elif slot == 'Time':
        # Return the availabilities on the given date.
        if not appointment_type or not date:
            return None

        availabilities = try_ex(lambda: booking_map[date])
        if not availabilities:
            return None

        availabilities = get_availabilities_for_duration(get_duration(appointment_type), availabilities)
        if len(availabilities) == 0:
            return None

        options = []
        for i in range(min(len(availabilities), 5)):
            options.append({'text': build_time_output_string(availabilities[i]), 'value': build_time_output_string(availabilities[i])})

        return options


def validate_book_car(slots):
    pickup_city = try_ex(lambda: slots['PickUpCity'])
    pickup_date = try_ex(lambda: slots['PickUpDate'])
    return_date = try_ex(lambda: slots['ReturnDate'])
    driver_age = safe_int(try_ex(lambda: slots['DriverAge']))
    car_type = try_ex(lambda: slots['CarType'])

    if pickup_city and not isvalid_city(pickup_city):
        return build_validation_result(
            False,
            'PickUpCity',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(pickup_city)
        )

    if pickup_date:
        if not isvalid_date(pickup_date):
            return build_validation_result(False, 'PickUpDate', 'I did not understand your departure date.  When would you like to pick up your car rental?')
        if datetime.datetime.strptime(pickup_date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'PickUpDate', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')

    if return_date:
        if not isvalid_date(return_date):
            return build_validation_result(False, 'ReturnDate', 'I did not understand your return date.  When would you like to return your car rental?')

    if pickup_date and return_date:
        if dateutil.parser.parse(pickup_date) >= dateutil.parser.parse(return_date):
            return build_validation_result(False, 'ReturnDate', 'Your return date must be after your pick up date.  Can you try a different return date?')

        if get_day_difference(pickup_date, return_date) > 30:
            return build_validation_result(False, 'ReturnDate', 'You can reserve a car for up to thirty days.  Can you try a different return date?')

    if driver_age is not None and driver_age < 18:
        return build_validation_result(
            False,
            'DriverAge',
            'Your driver must be at least eighteen to rent a car.  Can you provide the age of a different driver?'
        )

    if car_type and not isvalid_car_type(car_type):
        return build_validation_result(
            False,
            'CarType',
            'I did not recognize that model.  What type of car would you like to rent?  '
            'Popular cars are economy, midsize, or luxury')

    return {'isValid': True}


def validate_hotel(slots):
    location = try_ex(lambda: slots['Location'])
    checkin_date = try_ex(lambda: slots['CheckInDate'])
    nights = safe_int(try_ex(lambda: slots['Nights']))
    room_type = try_ex(lambda: slots['RoomType'])

    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(location)
        )

    if checkin_date:
        if not isvalid_date(checkin_date):
            return build_validation_result(False, 'CheckInDate', 'I did not understand your check in date.  When would you like to check in?')
        if datetime.datetime.strptime(checkin_date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'CheckInDate', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')

    if nights is not None and (nights < 1 or nights > 30):
        return build_validation_result(
            False,
            'Nights',
            'You can make a reservations for from one to thirty nights.  How many nights would you like to stay for?'
        )

    if room_type and not isvalid_room_type(room_type):
        return build_validation_result(False, 'RoomType', 'I did not recognize that room type.  Would you like to stay in a queen, king, or deluxe room?')

    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """


def make_appointment(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    appointment_type = intent_request['currentIntent']['slots']['AppointmentType']
    date = intent_request['currentIntent']['slots']['Date']
    appointment_time = intent_request['currentIntent']['slots']['Time']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    booking_map = json.loads(try_ex(lambda: output_session_attributes['bookingMap']) or '{}')

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_book_appointment(appointment_type, date, appointment_time)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                build_response_card(
                    'Specify {}'.format(validation_result['violatedSlot']),
                    validation_result['message']['content'],
                    build_options(validation_result['violatedSlot'], 'appointment_type', date, booking_map)
                )
            )

        if not appointment_type:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'AppointmentType',
                {'contentType': 'PlainText', 'content': 'What type of appointment would you like to schedule?'},
                build_response_card(
                    'Specify Appointment Type', 'What type of appointment would you like to schedule?',
                    build_options('AppointmentType', appointment_type, date, None)
                )
            )

        if appointment_type and not date:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Date',
                {'contentType': 'PlainText', 'content': 'When would you like to schedule your {}?'.format(appointment_type)},
                build_response_card(
                    'Specify Date',
                    'When would you like to schedule your {}?'.format(appointment_type),
                    build_options('Date', 'appointment_type', date, None)
                )
            )

        if appointment_type and date:
            # Fetch or generate the availabilities for the given date.
            booking_availabilities = try_ex(lambda: booking_map[date])
            if booking_availabilities is None:
                booking_availabilities = get_availabilities(date)
                booking_map[date] = booking_availabilities
                output_session_attributes['bookingMap'] = json.dumps(booking_map)

            appointment_type_availabilities = get_availabilities_for_duration(get_duration(appointment_type), booking_availabilities)
            if len(appointment_type_availabilities) == 0:
                # No availability on this day at all; ask for a new date and time.
                slots['Date'] = None
                slots['Time'] = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots,
                    'Date',
                    {'contentType': 'PlainText', 'content': 'We do not have any availability on that date, is there another day which works for you?'},
                    build_response_card(
                        'Specify Date',
                        'What day works best for you?',
                        build_options('Date', 'appointment_type', date, None)
                    )
                )

            message_content = 'What time on {} works for you? '.format(date)
            if appointment_time:
                output_session_attributes['formattedTime'] = build_time_output_string(appointment_time)
                # Validate that proposed time for the appointment can be booked by first fetching the availabilities for the given day.  To
                # give consistent behavior in the sample, this is stored in sessionAttributes after the first lookup.
                if is_available(appointment_time, get_duration(appointment_type), booking_availabilities):
                    return delegate(output_session_attributes, slots)
                message_content = 'The time you requested is not available. '

            if len(appointment_type_availabilities) == 1:
                # If there is only one availability on the given date, try to confirm it.
                slots['Time'] = appointment_type_availabilities[0]
                return confirm_intent(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots,
                    {
                        'contentType': 'PlainText',
                        'content': '{}{} is our only availability, does that work for you?'.format
                                   (message_content, build_time_output_string(appointment_type_availabilities[0]))
                    },
                    build_response_card(
                        'Confirm Appointment',
                        'Is {} on {} okay?'.format(build_time_output_string(appointment_type_availabilities[0]), date),
                        [{'text': 'yes', 'value': 'yes'}, {'text': 'no', 'value': 'no'}]
                    )
                )

            available_time_string = build_available_time_string(appointment_type_availabilities)
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'Time',
                {'contentType': 'PlainText', 'content': '{}{}'.format(message_content, available_time_string)},
                build_response_card(
                    'Specify Time',
                    'What time works best for you?',
                    build_options('Time', 'appointment_type', date, None)
                )
            )

        return delegate(output_session_attributes, slots)

    # Book the appointment.  In a real bot, this would likely involve a call to a backend service.
    duration = get_duration(appointment_type)
    booking_availabilities = booking_map[date]
    if booking_availabilities:
        # Remove the availability slot for the given date as it has now been booked.
        booking_availabilities.remove(appointment_time)
        if duration == 60:
            second_half_hour_time = increment_time_by_thirty_mins(appointment_time)
            booking_availabilities.remove(second_half_hour_time)

        booking_map[date] = booking_availabilities
        output_session_attributes['bookingMap'] = json.dumps(booking_map)
    else:
        # This is not treated as an error as this code sample supports functionality either as fulfillment or dialog code hook.
        logger.debug('Availabilities for {} were null at fulfillment time.  '
                     'This should have been initialized if this function was configured as the dialog code hook'.format(date))

    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Okay, I have booked your appointment.  We will see you at {} on {}'.format(build_time_output_string(appointment_time), date)
        }
    )


def book_hotel(intent_request):
    """
    Performs dialog management and fulfillment for booking a hotel.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """

    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    checkin_date = try_ex(lambda: intent_request['currentIntent']['slots']['CheckInDate'])
    nights = safe_int(try_ex(lambda: intent_request['currentIntent']['slots']['Nights']))

    room_type = try_ex(lambda: intent_request['currentIntent']['slots']['RoomType'])
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Load confirmation history and track the current reservation.
    reservation = json.dumps({
        'ReservationType': 'Hotel',
        'Location': location,
        'RoomType': room_type,
        'CheckInDate': checkin_date,
        'Nights': nights
    })

    session_attributes['currentReservation'] = reservation

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_hotel(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                build_response_card(
                    'Specify Time',
                    'What time works best for you?',
                    build_options('Time', 'appointment_type', date, None)
                )
            )

        # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  Pass price
        # back in sessionAttributes once it can be calculated; otherwise clear any setting from sessionAttributes.
        if location and checkin_date and nights and room_type:
            # The price of the hotel has yet to be confirmed.
            price = generate_hotel_price(location, nights, room_type)
            session_attributes['currentReservationPrice'] = price
        else:
            try_ex(lambda: session_attributes.pop('currentReservationPrice'))

        session_attributes['currentReservation'] = reservation
        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    # Booking the hotel.  In a real application, this would likely involve a call to a backend service.
    logger.debug('bookHotel under={}'.format(reservation))

    try_ex(lambda: session_attributes.pop('currentReservationPrice'))
    try_ex(lambda: session_attributes.pop('currentReservation'))
    session_attributes['lastConfirmedReservation'] = reservation

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, I have placed your reservation.   Please let me know if you would like to book a car '
                       'rental, or another hotel.'
        }
    )


def book_car(intent_request):
    """
    Performs dialog management and fulfillment for booking a car.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    slots = intent_request['currentIntent']['slots']
    pickup_city = slots['PickUpCity']
    pickup_date = slots['PickUpDate']
    return_date = slots['ReturnDate']
    driver_age = slots['DriverAge']
    car_type = slots['CarType']
    confirmation_status = intent_request['currentIntent']['confirmationStatus']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    last_confirmed_reservation = try_ex(lambda: session_attributes['lastConfirmedReservation'])
    if last_confirmed_reservation:
        last_confirmed_reservation = json.loads(last_confirmed_reservation)
    confirmation_context = try_ex(lambda: session_attributes['confirmationContext'])

    # Load confirmation history and track the current reservation.
    reservation = json.dumps({
        'ReservationType': 'Car',
        'PickUpCity': pickup_city,
        'PickUpDate': pickup_date,
        'ReturnDate': return_date,
        'CarType': car_type
    })
    session_attributes['currentReservation'] = reservation

    if pickup_city and pickup_date and return_date and driver_age and car_type:
        # Generate the price of the car in case it is necessary for future steps.
        price = generate_car_price(pickup_city, get_day_difference(pickup_date, return_date), driver_age, car_type)
        session_attributes['currentReservationPrice'] = price

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_book_car(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                build_response_card(
                    'Specify Time',
                    'What time works best for you?',
                    build_options('Time', 'appointment_type', 'date', 'None')
                )
            )

        # Determine if the intent (and current slot settings) has been denied.  The messaging will be different
        # if the user is denying a reservation he initiated or an auto-populated suggestion.
        if confirmation_status == 'Denied':
            # Clear out auto-population flag for subsequent turns.
            try_ex(lambda: session_attributes.pop('confirmationContext'))
            try_ex(lambda: session_attributes.pop('currentReservation'))
            if confirmation_context == 'AutoPopulate':
                return elicit_slot(
                    session_attributes,
                    intent_request['currentIntent']['name'],
                    {
                        'PickUpCity': None,
                        'PickUpDate': None,
                        'ReturnDate': None,
                        'DriverAge': None,
                        'CarType': None
                    },
                    'PickUpCity',
                    {
                        'contentType': 'PlainText',
                        'content': 'Where would you like to make your car reservation?'
                    },
                    build_response_card(
                        'Specify Time',
                        'What time works best for you?',
                        build_options('Time', 'appointment_type', 'date', 'None')
                    )
                )

            return delegate(session_attributes, intent_request['currentIntent']['slots'])

        if confirmation_status == 'None':
            # If we are currently auto-populating but have not gotten confirmation, keep requesting for confirmation.
            if (not pickup_city and not pickup_date and not return_date and not driver_age and not car_type)\
                    or confirmation_context == 'AutoPopulate':
                if last_confirmed_reservation and try_ex(lambda: last_confirmed_reservation['ReservationType']) == 'Hotel':
                    # If the user's previous reservation was a hotel - prompt for a rental with
                    # auto-populated values to match this reservation.
                    session_attributes['confirmationContext'] = 'AutoPopulate'
                    return confirm_intent(
                        session_attributes,
                        intent_request['currentIntent']['name'],
                        {
                            'PickUpCity': last_confirmed_reservation['Location'],
                            'PickUpDate': last_confirmed_reservation['CheckInDate'],
                            'ReturnDate': add_days(
                                last_confirmed_reservation['CheckInDate'], last_confirmed_reservation['Nights']
                            ),
                            'CarType': None,
                            'DriverAge': None
                        },
                        {
                            'contentType': 'PlainText',
                            'content': 'Is this car rental for your {} night stay in {} on {}?'.format(
                                last_confirmed_reservation['Nights'],
                                last_confirmed_reservation['Location'],
                                last_confirmed_reservation['CheckInDate']
                            )
                        }
                    )

            # Otherwise, let native DM rules determine how to elicit for slots and/or drive confirmation.
            return delegate(session_attributes, intent_request['currentIntent']['slots'])

        # If confirmation has occurred, continue filling any unfilled slot values or pass to fulfillment.
        if confirmation_status == 'Confirmed':
            # Remove confirmationContext from sessionAttributes so it does not confuse future requests
            try_ex(lambda: session_attributes.pop('confirmationContext'))
            if confirmation_context == 'AutoPopulate':
                if not driver_age:
                    return elicit_slot(
                        session_attributes,
                        intent_request['currentIntent']['name'],
                        intent_request['currentIntent']['slots'],
                        'DriverAge',
                        {
                            'contentType': 'PlainText',
                            'content': 'How old is the driver of this car rental?'
                        },
                        build_response_card(
                            'Specify Time',
                            'What time works best for you?',
                            build_options('Time', 'appointment_type', date, None)
                        )
                    )
                elif not car_type:
                    return elicit_slot(
                        session_attributes,
                        intent_request['currentIntent']['name'],
                        intent_request['currentIntent']['slots'],
                        'CarType',
                        {
                            'contentType': 'PlainText',
                            'content': 'What type of car would you like? Popular models are '
                                       'economy, midsize, and luxury.'
                        },
                        build_response_card(
                            'Specify Time',
                            'What time works best for you?',
                            build_options('Time', 'appointment_type', date, None)
                        )
                    )

            return delegate(session_attributes, intent_request['currentIntent']['slots'])

    # Booking the car.  In a real application, this would likely involve a call to a backend service.
    logger.debug('bookCar at={}'.format(reservation))
    del session_attributes['currentReservationPrice']
    del session_attributes['currentReservation']
    session_attributes['lastConfirmedReservation'] = reservation
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, I have placed your reservation.'
        }
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'CanICall':
        return make_appointment(intent_request)
    elif intent_name == 'CanIGOTO':
        return make_appointment(intent_request)
    elif intent_name == 'CanISee':
        return make_appointment(intent_request)
    elif intent_name == 'MeetAFriend':
        return make_appointment(intent_request)
    elif intent_name == 'BookHotel':
        return book_hotel(intent_request)
    elif intent_name == 'BookCar':
        return book_car(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)

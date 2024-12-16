from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review
from .models import CarMake, CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """ Handle login requests and authenticate user. """
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data["status"] = "Authenticated"

    return JsonResponse(response_data)


def logout_request(request):
    """ Handle logout request. """
    if request.method == "GET":
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = ""
        logout(request)
        return JsonResponse({"userName": username, "status": "Logged Out"})

    return JsonResponse({"error": "Invalid request method."}, status=400)


@csrf_exempt
def registration(request):
    """ Handle user registration. """
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    try:
        User.objects.get(username=username)
        return JsonResponse(
            {
                "userName": username,
                "error": "Already Registered"
            }
        )
    except User.DoesNotExist:
        logger.debug(f"{username} is a new user.")

    user = User.objects.create_user(
        username=username, first_name=first_name, last_name=last_name,
        password=password, email=email
    )
    login(request, user)
    return JsonResponse(
        {
            "userName": username,
            "status": "Authenticated"
        }
    )


def get_dealerships(request, state="All"):
    """ Fetch and return a list of dealerships based on state. """
    if state != "All":
        endpoint = f"/fetchDealers/{state}"
    else:
        endpoint = "/fetchDealers"

    dealerships = get_request(endpoint)

    if dealerships is None:
        print("Dealerships is None")
    elif not isinstance(dealerships, list):
        print(f"Dealerships is not a list: {dealerships}")
    else:
        print(f"Dealerships data: {dealerships}")

    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """ Fetch and process reviews for a specific dealer. """
    if not dealer_id:
        return JsonResponse(
            {
                "status": 400,
                "message": "Bad Request: Dealer ID is required."
            },
            status=400
        )

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    print(f"Fetching reviews for dealer ID: {dealer_id}")

    try:
        reviews = get_request(endpoint)
        if not reviews:
            print("No reviews found or API returned None.")
            return JsonResponse(
                {
                    "status": 404,
                    "message": "No reviews found for the specified dealer."
                },
                status=404
            )

        for review_detail in reviews:
            review_text = review_detail.get('review', '')
            if review_text:
                sentiment_response = analyze_review_sentiments(review_text)
                print(f"Sentiment analysis response: {sentiment_response}")

                if sentiment_response and 'sentiment' in sentiment_response:
                    sentiment = sentiment_response['sentiment']
                    review_detail['sentiment'] = sentiment

                else:
                    print("Error: Sentiment analysis error")
                    review_detail['sentiment'] = "unknown"
            else:
                print("No review text found for this entry.")
                review_detail['sentiment'] = "unknown"

        return JsonResponse({"status": 200, "reviews": reviews}, status=200)

    except Exception as e:
        print(
            f"Error while fetching or processing reviews: {e}"
        )
        return JsonResponse(
            {
                "status": 500,
                "message": "Internal Server Error"
            },
            status=500
        )


def get_dealer_details(request, dealer_id):
    """ Fetch and return details of a specific dealer. """
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse(
            {
                "status": 200,
                "dealer": dealership
            }
        )

    return JsonResponse(
        {
            "status": 400,
            "message": "Bad Request"
        }
    )


def add_review(request):
    """ Handle review submission. """
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            print(f"Error posting review: {e}")
            return JsonResponse(
                {
                    "status": 401,
                    "message": "Error in posting review"
                }
            )

    return JsonResponse({"status": 403, "message": "Unauthorized"})


def get_cars(request):
    """ Get list of cars from database. """
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        }
        for car_model in car_models
        ]

    return JsonResponse({"CarModels": cars})

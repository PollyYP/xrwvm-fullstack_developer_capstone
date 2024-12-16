# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

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


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    if request.method == "GET":
        # Log out the user
        username = request.user.username if request.user.is_authenticated else ""
        logout(request)
        # Prepare response data
        data = {"userName": username, "status": "Logged Out"}
        return JsonResponse(data)
    else:
        # Return an error response for non-POST requests
        return JsonResponse({"error": "Invalid request method."}, status=400)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)

    # Validate the response
    if dealerships is None:
        print("Dealerships is None")
    elif not isinstance(dealerships, list):
        print(f"Dealerships is not a list: {dealerships}")
    else:
        print(f"Dealerships data: {dealerships}")

    return JsonResponse({"status": 200, "dealers": dealerships})


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    """
    Fetch and process reviews for a specific dealer.
    """
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request: Dealer ID is required."}, status=400)

    # Construct the API endpoint for fetching reviews
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    print(f"Fetching reviews for dealer ID: {dealer_id}")  # Debug log

    try:
        # Fetch reviews using get_request
        reviews = get_request(endpoint)
        if not reviews:
            print("No reviews found or API returned None.")  # Debug log
            return JsonResponse({"status": 404, "message": "No reviews found for the specified dealer."}, status=404)

        # Process each review
        for review_detail in reviews:
            review_text = review_detail.get('review', '')
            if review_text:
                sentiment_response = analyze_review_sentiments(review_text)
                print(f"Sentiment analysis response: {sentiment_response}")  # Debug log

                # Add sentiment to review details
                if sentiment_response and 'sentiment' in sentiment_response:
                    review_detail['sentiment'] = sentiment_response['sentiment']
                else:
                    print("Error: Sentiment analysis failed or returned incomplete data.")  # Debug log
                    review_detail['sentiment'] = "unknown"
            else:
                print("No review text found for this entry.")  # Debug log
                review_detail['sentiment'] = "unknown"

        # Return processed reviews
        return JsonResponse({"status": 200, "reviews": reviews}, status=200)

    except Exception as e:
        print(f"Error while fetching or processing reviews: {e}")  # Debug log
        return JsonResponse({"status": 500, "message": "Internal Server Error"}, status=500)


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})

# weather-app

## Description
<p align="center">
<img src="https://github.com/vadant1000/weather-app/blob/master/myapp.gif" width="80%"></p>
An application that shows the weather for a selected city. Implemented using the flask framework, html, css.

## About the project
- The project used an [OpenWeather API](https://openweathermap.org/api).
- So that the weather cards do not disappear after the page is reloaded, I used **SQLAlchemy** to save each city that the user has added.
- Also with the help of the database I was able to implement deleting cards and handling error "The city has already been added to the list!".
- Using the api, I check the existence of the city and handle the error "The city doesn't exist!".
- Depending on the time in the city, I display a certain card.

# Documentation

This markdown file is provided as a single point of information for several questions. 
Most of them are provided within the different files, e.g. documentation of code in the modules.
However, as the repository gets bigger with each commit, I try to give a good overall overview 
additionally to the README for this project.

_Known Bug (Hint)_: The application hasn't been developed to work responsive, therefore the application doesn't
look to good when used in a window size with a widht below 1300px. I'm going to fix this soon.

## Table of Contents

- [1. Project Definition](#1-project-definition)
  * [1.1 High Level Overview](#11-high-level-overview)
  * [1.2 The Problem](#12-the-problem)
  * [1.3 Metrics](#13-metrics)
- [2. Analysis](#2-analysis)
  * [2.1 Features](#21-features)
  * [2.2 Data Visualizations](#22-data-visualizations)
- [3. Methodology](#3-methodology)
  * [3.1 Preprocessing Steps](#31-preprocessing-steps)
  * [3.2 Implementation](#32-implementation)
  * [3.3 Model results](#33-model-results)
- [4. Discussion](#4-discussion)
- [5. Next Steps](#5-next-steps)  



---

## 1. Project Definition

### 1.1 High Level Overview
Being able to predict the future of a companies performance is a dream for many data scientists and business analysts.
It's known to be an extremely complicated problem, as there are so many (hidden or known) variables which have an input
for the stock prices. Some ideas for possible features are:
- the performance of the company measured in past financial data (bilance sheets, OHLC-data, ...)
- sentiment analysis in social media for the products of the company or the general opinion at the moment
- what famous & important people say about the company
- trends in development
- trends for industries
- ...
  
This repository contains code and data for a **overly-simplified** Stock Price Predictor for the S&P 500 Index.
The goal is to develop a web-application which offers a little user interface, where the user can input some stock
data (=symbols like 'GOOG' or 'AMZN') and get predicted prices for the next day. The result by now is shown in the 
following screenshot:  
<img src="images/example_screenshot.JPG">  

  
The goal of this project is to develop a simple prototype which gives me some ideas how to further develop and optimize
a potential application, e.g. in functionality. Additionally, I not only wanted to create the application as a prototype,
but furthermore as a baseline for future development. More on this in the next sections.   

The S&P 500 Predictor consists of hundreds of artificial neural networks, one for each stock (that was able to perform well
enough, bad models were excluded).



### 1.2 The Problem
As already mentioned, the goal is to create a model which is able to predict "well" on future performances of companies 
based on some data. The problem I'm facing during developing the application is to get to a point where I can say with
a certain confidence, that the model is good enough to predict prices which will lead to profitable results when used
as a trading engine. **Right now, the problem isn't solved - I wouldn't recommend to use the model as a predictor for future
prices, even though it performs well on past data**. The model simply isn't facing all the variance that occurs when predicting
future performances (as I'm only including a few financial features). However, as this was meant to be a prototype/baseline, 
I can say that I'm pleased with the results by now :)

### 1.3 Metrics
To measure the performance of the models, the [RMSE](http://statweb.stanford.edu/~susan/courses/s60/split/node60.html) 
metric is used. RMSE stands for the Root Mean Squarred Error, a metric which is used to calculate the performance of
regression models by first calculating the squarred error of a prediction (-> SE), then taking the mean over the (batch of) data 
(-> MSE), and finally calculating the Root to compensate the square (-> RMSE). The advantage of this metric is that it is 
able to punish large errors much more than small errors, and I definitely want to avoid big errors when predicting stock prices!
If you want to get further details, I recommend the following medium article: 
[MAE and RMSE — Which Metric is Better?](https://medium.com/human-in-a-machine-world/mae-and-rmse-which-metric-is-better-e60ac3bde13d)

--- 

## 2. Analysis

### 2.1 Features
The Features used for Stock Price Prediction are the following:
- Date: day of the observation
- Open: price of the share at opening of the stock market ("first value of the day")
- High: highest price of the share during the day
- Low: lowest price of the share during the day
- Close: price of the share when the stock market closed ("last value of the day")
- Ex-Dividend: time period between the announcement and payment of a dividend
- Split-Ratio: the ratio of shares outstanding compared to what was originally available before a stock split (i.e. when 
Amazon doubled it's amount of shares, as a consequence the prices had to be adjusted)
- Adjusted Open (High, Low, Close): adjusted price after split
- Volume: amount of shares traded that day

The target is the Adjusted Close for the next day.

As an example, the first 10 rows of the data for google look like the following:  
<img src="images/example_data_goog.JPG">  

Extract of the summary statistics for google:  
<img src="images/example_stats_goog_1.JPG">  
<img src="images/example_stats_goog_2.JPG">  


### 2.2 Data Visualizations
Example Stock History for Google:
<img src="images/ohlc_google.JPG">  
This image shows the how the stock price changed for Google shares; the different colors (which are honestly hard to differentiate)
show the difference in Open, High, Low and Close.

The model's goal is to predict a price for the next day given the today's feature values. Acting as if we tried to predict
future values in the past (kind of time-travelling ;) ), the (Google) model is able to perform quite well:
<img src="images/graph_notebook_goog.JPG">  
Of course this shouldn't be accepted without any critical considerations. Looking closely at the image, we can see that the 
predictions are good, but always a little "too late" (the orange graph is following the blue one). Therefore, the model can be used
to predict values given that there is a momentum (the model is able to see that high prices today will most likely lead
to high prices tomorrow etc.). What the model most likely won't detect is a crisis, a rapid fall of the prices!  
Still, I believe that this prototype has potential to be used as a baseline - enriching the data with social media content etc.
it might be possible to "move" the predictions a little to the left on the x-axis (which means we'd actually be able to
build predictions of the performance).


---

## 3. Methodology

### 3.1 Preprocessing Steps
The data is being collected via the Quandl API. A Script calls the API-url for every one of the 500+ companies which
exist in the Index. The Dates have to be transformed from Strings to Datetime Objects. The target value (Adjusted Close
price for the next day) needs to be read from the following row. As each column is numerical, the data can directly be
scaled and stored. 

### 3.2 Implementation

The implementation of the S&P500 Predictor can be mainly split into two stages:
1. Training the models (artificial neural networks) for stock price prediction and wrapping them in the SP500 Predictor
2. Building the [Django](https://www.djangoproject.com/) Web Application in order to access the Predictor via a GUI.

During the first part, the preprocessed data will be used to train one neural network for each stock symbol using PyTorch.
The resulting models will be evaluated against the RMSE metric. Those steps can be divided into sub-steps:
1. Implementing a tool which handles data requests so that we can get the access to the data for each stock symbol
(-> DataHandler)
2. Define the network architecture for _all_ models (see below), including its loss function to optimize parameters.
3. For each stock symbol, train a neural network n times and evaluate its results against the RMSE - log the results.
4. After the n epochs, if the model reached the RMSE threshold of an error 1/10 the size of the latest stock price, 
it is considered to be a well performing model* and therefore will be used in the SP500 Predictor. If not, it will not be
included.
5. Store all models

The second part was more related to software engineering, in order to get the web application up and running.
Using Django, which expects a composite webapp to be a collection of multiple modular applications, 
my web application consists mainly of a single application which provides a HTML template which will be dynamically
changed given user inputs. This also can be divided into sub-steps:
1. Start a new project using Django and add a new application (see [documentation](https://docs.djangoproject.com/en/2.1/intro/tutorial01/) 
for reference)
2. In the appliation, build a view file which loads the SP500 Predictor with all its models that have before been considered
to be well performing whenever the Server gets started.
3. Build a function which is able to handle user requests (in this case the Stock Symbols or a number of recommendations).
4. Build the HTML Template (see [documentation](https://docs.djangoproject.com/en/1.7/topics/templates/) for reference).
This prototype is using [Chart.js](https://www.chartjs.org/) in order to provide some visualizations of the results. The
predictions itself will be shown in a table.
5. _optional:_ add some css styling rules

After all, it's important to check package dependencies. For this rather simple project, there have been used an awful lot of
packages (active or passive through other packages); as I didn't deploy this application on a server accessible through an URL,
I decided to create a file which can be used for installment on a local machine. If you want to build a predictor yourself and you
want to make it accessible for other users, you should at least provide all the packages needed in a list or instruction. This
minimizes the number of headaches caused through technical errors ;)

`*` a model which reached an RMSE of 1/10 of the latest stock price is considered to be well performing, as the error is
low in relation to the current stock prices for the company's share. For instance:  
the stock symbol FE had a value of 34 USD, therefore the model was accepted as useable if it predicted the correct value
of the next day with an error of max 3.4 USD.


### 3.3 Model results
The architecture for the artificial neural networks is simple and pretty much straightforward. Using PyTorch, I developed
a 2-Layer Feed Forward Neural Network (-> 1 Input Layer, 1 Hidden Layer and 1 Output Layer; the Input Layer often gets neglected
when talking about the number of layers, therefore it's called a 2-Layer Neural Network). In the following, I'm going to 
explain the details of the architecture. It's easier to do this by first showing the code for the architecture:
<img src="images/nn_architecture.JPG">   
- using only 2 Layers: as I already stated, I wanted to use this predictor as a prototype. Using only 2 layers with 128 / 64 neurons
makes it much more time-efficient to train multiple models; training a single model for 50 epochs took me roughly 5 to 50 seconds; 
the whole training session for all models was done in roughly 10 hours. Additionally, I kept in mind that too much layers/neurons in a FFN
can cause massive [overfitting](https://elitedatascience.com/overfitting-in-machine-learning), which would make the model useless.
- using Batch Normalization: this is known to be kind of a "free lunch" in Machine Learning (even though we all know that ["there is
no such thing as a free lunch"](https://en.wikipedia.org/wiki/There_ain%27t_no_such_thing_as_a_free_lunch)). For each batch of data,
the inputs in the batch itself get normalized (mean of 0, sigma of 1). As a consequence, the model can much more easily learn on the data.
The downside of using BN is the extra effort in implementing the model, as there are some things which have to be considered additionally 
(e.g. that the model will throw an error when the size of a batch is 1, which might occur at the end of a training session when there's only
one row of data left to train the model). I compared the results of the model using BN vs. the model not using BN, and the results clearly
showed that using BN is the right decision here.
- using Dropout: just as Batch Normalization, Dropout is known to be a "thing" you can add to the network without thinking about it too much.
Dropout makes it possible to "block" neurons with a probability of p (given in the code), which prevents some edges/weights to be
dominant. As a result, the model is much less prone to Overfitting!
- using ReLU as an activation function: Honestly, this one is rather random than a scientific choice; I tried several activation functions
on an example model (predicting prices for Amazon), and it showed that using ReLU was the best fit. In future development, I'd have to spend
some more time choosing the right activation function.

The resulting architecture led to many great models. As an example, take a look at an extract of the training for the Google model:  
<img src="images/start_goog.JPG">   
...  

<img src="images/end_goog.JPG">  

## 4. Discussion
I think that it's always hard to explain why a model works or doesn't work that you implemented yourself. Some of my ideas are the following:
- I reduced the number of models used drastically; the ones which weren't able to "convince" me during training weren't selected at all. 
Of course, this doesn't have to be the optimal solution, as I'm missing out on a lot of possible companies to use when trading! However,
this method gives me better confidence when making predictions, as I know that the models which are being used were performing well on past data.
- I tried to build an architecture which prevents Overfitting; compared to some other models I developed earlier which didn't use these
 techniques, the models now are capable of predicting on values the model hasn't seen before (new price-highs and lows, new dates).
- The data is "complete"; as I'm only using companies of the S&P 500 universe, all the data I collected as complete (no missing data) and in
a standardized format. This made it really easy for me to develop many models really fast. When I'm going to include several other data sources,
this won't be given anymore, and I know that this will be a big challenge for me!

It's also been quite challenging for me as a beginner in Frontend-/Backend-Development to create the web application, but this is
just something caused by my lack of skills in this area. I think it's super important that if you have a great model / set of models that 
it's useable in a "nice" way. Personally, I'd already be happy using the model through a CLI; however, as I wanted to make this application
accessible for many users (also those with lacking knowledge in programming, command line interfaces etc.), therefore it's been important
to me to develop a GUI.

## 5. Next Steps
In my personal opinion, I believe that the project has been successful. I can use the application as a beta-version and improve
it to for example use it in my portfolio - for this however, I'm going to further improve it within the next months. The next steps
are:
1. Refactor all the code: there are some code smells which I'm not so happy with in the code, for example hard-coded paths.
I'll rebuild those parts, restructure the project and create some general tools which I can use for further projects.
2. Rebuild the application: As I'm trying to learn how to build web apps full-stack, I'm going to rebuild the app with Django REST Api (Backend)
and Angular (Frontend). Additionally, I'll use better visualization tools like Highcharts.js.
3. Improve the models: I'll collect some more data (Twitter Streams etc.) and try to build well performing models for them. As suggested
by an anonymous Udacity Reviewer (thanks a lot for the help! ;) ), I'm going to improve the architecture of the neural network; I'll
try to use an artificial neural network which uses [LSTM Cells](http://colah.github.io/posts/2015-08-Understanding-LSTMs/) in order to
improve the models performance using time series data. Additionally, I hope that adding some layers and/or neurons in combination with
the LSTM Cells improve the quality of the results.
4. Improve the overall application: When I'm content with the performance of my model, I'll try to add functionalities like
building a trading strategy, building a portfolio etc. Maybe I'm going to build a "recommender system lite" for this functionality :)
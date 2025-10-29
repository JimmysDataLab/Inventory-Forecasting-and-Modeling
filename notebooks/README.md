M5 - Forecasting Project

calendar.csv - Contains the dates on which products are sold. The dates are in a yyyy/dd/mm format.

sales_train_validation.csv - Contains the historical daily unit sales data per product and store [d_1 - d_1913].

sell_prices.csv - Contains information about the price of the products sold per store and date.

 sales_train_evaluation.csv - Available one month before competition deadline. Will include sales [d_1 - d_1941]

--> Validation - d1 to d1913 

--> Evaluation- d1 to 1941 

--> Calendar - d1 to 1969

Remarks: 
1)1969 - 1913 = 56 days = 2 months —> we are predicting the sales for 1 month.

2)Above mentioned 2 months is the reason for submission data set is having 2 set of 28 days.

3)The calendar data, which includes both past and future dates, can be merged with our existing dataset of days.This merging helps us progress with analysis.

4)Accuracy and Uncertainity are 2 different parallel competitions for using different metrics.


Training and validation:

Method 1: we can split the sales_train_validation dataset into training set (70%) and validation (30%). Testing can be done by data of  28 days from evaluation dataset (d_1914 - d_1941)

Method 2: Training and validation can be done by k means cross validation method from validation dataset. Testing can be performed using the similar method mentioned above.

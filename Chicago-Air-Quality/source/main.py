from __future__ import print_function
from pprint import pprint
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

from create_new_features import *
from readdata import read_training_set, read_testing_set


if __name__ == "__main__":

    # import training data as dataframe
    dfTrain = read_training_set('../data/TRAINING_DATA.txt')
    # print(dfTrain.describe())
    # print(dfTrain.head())

    # import test data as dataframe
    dfTest = read_testing_set('../data/TESTING_DATA.txt')

    # DATA EXPLORATION
    # scatterplot of all features including the additional variables 'time of day' and 'day index'
    cols = ['s02', 'car.count', 'wind.velocity', 'wind.direction',
            'time.of.day', 'day.index', 'temperature.1', 'temperature.30']
    sns.pairplot(dfTrain[cols], height = 3, kind = "reg")
    plt.tight_layout()
    plt.savefig("scatterplot_of_covariates.png")
    plt.show()

    # # plot correlation heatmap for variables in cols
    sns.set()
    f, ax = plt.subplots(figsize = (9, 6))
    cm = np.corrcoef(dfTrain[cols].values.T)
    hm = sns.heatmap(cm, annot = True, fmt = '.2f', linewidths = .5, ax = ax,
                     annot_kws = { 'size':14 },
                     yticklabels = cols,
                     xticklabels = cols)
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom+0.5,top+0.5)
    plt.savefig("covariate_correlation_heatmap.png")
    plt.show()

    # temperature.1 and temperature.30 variables are too highly correlated at 0.99
    # so we combine them together into one feature:
    dfTrain["temperature"] = dfTrain["temperature.1"].multiply(dfTrain["temperature.30"], axis = "index")
    dfTest["temperature"] = dfTest["temperature.1"].multiply(dfTest["temperature.30"], axis = "index")

    # we can drop the 2 originals now as having one vs the other does not add value to our model:
    dfTrain = dfTrain.drop(["temperature.1", "temperature.30"], axis = 1)
    dfTest = dfTest.drop(["temperature.1", "temperature.30"], axis = 1)

    # FEATURE EXTRACTION & ENGINEERING
    # See "create_new_features.py" for details
    # function below creates lists of days, weekdays, months, and days of year variables for feature creation
    convert_dayIndex_to_variables(dfTrain)

    # time of week: weekday vs weekend
    create_weeks_feature()
    weeks = pd.Series(weeks)
    dfTrain['times.of.week'] = weeks

    # quarters 1, 2, 3, 4 (starting from 01/01/2010 + 30 days + day.index to figure out actual day of year)
    create_quarters_feature()
    quarters = pd.Series(quarters)
    dfTrain['quarters'] = quarters

    # months are calculated using start_date of february 1st 2010 + dayIndex to figure out
    # the actual month of the entry.
    # Seasons are computed using the correct months for seasons of the Northern Hemisphere
    create_seasons_feature()
    seasons = pd.Series(seasons)
    dfTrain['seasons'] = seasons

    # using time.of.day, figure out the actual category of time of day (morning, afternoon, evening, night)
    create_time_of_day_feature(dfTrain)
    times_of_day = pd.Series(times_of_day)
    dfTrain['times.of.day'] = times_of_day

    # Do the same for dfTest set
    convert_dayIndex_to_variables(dfTest)

    create_weeks_feature()
    weeks = pd.Series(weeks)
    dfTest['times.of.week'] = weeks

    create_quarters_feature()
    quarters = pd.Series(quarters)
    dfTest['quarters'] = quarters

    create_seasons_feature()
    seasons = pd.Series(seasons)
    dfTest['seasons'] = seasons

    create_time_of_day_feature(dfTest)
    times_of_day = pd.Series(times_of_day)
    dfTest['times.of.day'] = times_of_day

    # drop unused features
    dfTrain = dfTrain.drop(["wind.direction", "day.index", "time.of.day"], axis = 1)
    dfTest = dfTest.drop(["wind.direction", "day.index", "time.of.day"], axis = 1)

    # LABEL ENCODING
    # replace weekday vs weekend values with 0 (weekday) or 1 (weekend)
    binarize_time_of_week = dfTrain['times.of.week'].replace({ 'weekday', 'weekend' }, value = { 0, 1 }, inplace = True)
    binarize_time_of_week = dfTest['times.of.week'].replace({ 'weekday', 'weekend' }, value = { 0, 1 }, inplace = True)

    # use pandas get_dummies which uses OneHotEncoding for the time of day and seasons variables
    dfTrain = pd.get_dummies(dfTrain, columns = ['times.of.day', 'seasons'], prefix = ['time', 'season'])
    dfTest = pd.get_dummies(dfTest, columns = ['times.of.day', 'seasons'], prefix = ['time', 'season'])


    # LINEAR REGRESSION MODEL
    # from sklearn.linear_model import LinearRegression
    # lr = LinearRegression()
    X_train = dfTrain.drop(['s02', 'time_night', 'season_winter'], axis = 'columns')
    X_test = dfTest.drop(['time_night', 'season_winter'], axis = 'columns')
    y_train = dfTrain['s02']

    # scale features using standard scalar
    from sklearn.preprocessing import StandardScaler

    stdsc = StandardScaler()
    X_train_std = stdsc.fit_transform(X_train)
    X_test_std = stdsc.transform(X_test)

    # ######################################################################
    import statsmodels.api as sm
    from statsmodels.sandbox.regression.predstd import wls_prediction_std

    # train linear regression model on in-sample data
    X = sm.add_constant(X_train_std)
    model = sm.OLS(y_train, X).fit()

    # print model summary stats
    model.summary()
    print("Model Summary: ", model.summary())
    print('\nR-squared: ', round(model.rsquared,5))
    
    # Plot residuals against fitted values
    import statsmodels.formula.api as smf
    from statsmodels.graphics.gofplots import ProbPlot

    plt.style.use('seaborn')
    plt.rc('font', size=18)
    plt.rc('figure', titlesize=20)
    plt.rc('axes', labelsize=17)
    plt.rc('axes', titlesize=20)

    # fitted values (need a constant term for intercept)
    model_fitted_y = model.fittedvalues
    model_residuals = model.resid
    model_norm_residuals = model.get_influence().resid_studentized_internal

    # absolute squared normalized residuals
    model_norm_residuals_abs_sqrt = np.sqrt(np.abs(model_norm_residuals))
    # absolute residuals
    model_abs_resid = np.abs(model_residuals)

    plot_lm_1 = plt.figure(1)
    plot_lm_1.set_figheight(8)
    plot_lm_1.set_figwidth(12)

    plot_lm_1.axes[0] = sns.residplot(model_fitted_y, 's02', data=dfTrain,
                              lowess=True,
                              scatter_kws={'alpha': 0.5},
                              line_kws={'color': 'red', 'lw': 1, 'alpha': 0.8})
    plot_lm_1.axes[0].set_title('Residuals vs Fitted')
    plot_lm_1.axes[0].set_xlabel('Fitted values')
    plot_lm_1.axes[0].set_ylabel('Residuals')

    abs_resid = model_abs_resid.sort_values(ascending=False)
    abs_resid_top_3 = abs_resid[:3]
    for i in abs_resid_top_3.index:
        plot_lm_1.axes[0].annotate(i, xy=(model_fitted_y[i], model_residuals[i]))
    plt.savefig("fitted_vs_residuals.png")
    plt.show()

    # predict out-of-sample values (X_test_standardized)
    X = sm.add_constant(X_test_std)
    y_pred = model.predict(X)

    # reshape and write to excel
    y_pred = np.reshape(y_pred, (-1, 1))
    y_pred = pd.DataFrame(y_pred)
    y_pred.columns = ['s02']
    y_pred.to_csv("predictions.csv")

    # display prediction summary in console output
    y_pred_console = model.get_prediction(X)
    print("Prediction Summary on TESTING_DATA: ", y_pred_console.summary_frame())

    # plot regressors
    fig = plt.figure(figsize=(24,16))
    plt.rc('xtick', labelsize=15)
    plt.rc('ytick', labelsize=15)
    plt.rc('axes', labelsize=16)
    plt.rc('axes', titlesize=16)
    fig = sm.graphics.plot_partregress_grid(model, fig=fig)
    plt.savefig("regressors.png")
    plt.show()


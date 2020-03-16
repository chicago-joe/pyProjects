import featuretools as ft
import numpy as np
import pandas as pd

train = pd.read_csv("train_data.csv")
test = pd.read_csv("test_data.csv")

# DATA PREPARATION ---------------------------------------------------------------
# saving identifiers
test_Item_Identifier = test['Item_Identifier']
test_Outlet_Identifier = test['Outlet_Identifier']
sales = train['Item_Outlet_Sales']
train.drop(['Item_Outlet_Sales'], axis=1, inplace=True)

# combine train and test set
combi = train.append(test, ignore_index = True)

# check missing values
combi.isnull().sum()

# imputing missing data
combi['Item_Weight'].fillna(combi['Item_Weight'].mean(), inplace = True)
combi['Outlet_Size'].fillna("missing", inplace = True)

# DATA PREPROCESSING ---------------------------------------------------------
combi['Item_Fat_Content'].value_counts()

# convert to binary variable using "Low Fat" and "Regular" categories
fat_content_dict = {'Low Fat':0, 'Regular':1, 'LF':0, 'reg':1, 'low fat':0}

combi['Item_Fat_Content'] = combi['Item_Fat_Content'].replace(fat_content_dict, regex=True)


# FEATURE ENGINEERING WITH FEATURETOOLS ---------------------------------------
# create a unique identifier feature in the dataset
combi['id'] = combi['Item_Identifier'] + combi['Outlet_Identifier']
combi.drop(['Item_Identifier'], axis=1, inplace=True)

# create entity set 'es'
es = ft.EntitySet(id = 'sales')
es.entity_from_dataframe(entity_id = 'bigmart', dataframe = combi, index = 'id')
#
# # split dataset into multiple tables
es.normalize_entity(base_entity_id = 'bigmart',
                    new_entity_id = 'outlet', index = 'Outlet_Identifier',
                    additional_variables = ['Outlet_Establishment_Year',
                                            'Outlet_Size',
                                            'Outlet_Location_Type',
                                            'Outlet_Type'])

print('\n', es, '\n')

# Deep Feature Synthesis
feature_matrix, feature_names = ft.dfs(entityset = es,
                                       target_entity = 'bigmart',
                                       max_depth = 2,
                                       verbose = True)
# view new features
print(feature_matrix.columns)
print('\n', feature_matrix.head())

# sort dataframe on id variable
feature_matrix = feature_matrix.reindex(index=combi['id'])
feature_matrix = feature_matrix.reset_index()

# export new features to csv:
feature_matrix.to_csv('new_feature_matrix.csv')


# Model Building -------------------------------------------------------------
# predict Item_Outlet_Sales using LogisticRegression
from catboost import CatBoostRegressor

# convert categorical variables to string format
categorical_features = np.where(feature_matrix.dtypes == 'object')[0]

for i in categorical_features:
    feature_matrix.iloc[:,i] = feature_matrix.iloc[:,i].astype('str')

# split matrix into train and test sets
feature_matrix.drop(['id'], axis=1, inplace=True)
train = feature_matrix[:8523]
test = feature_matrix[8523:]

# # remove unnecessary vars
train.drop(['Outlet_Identifier'], axis=1, inplace=True)
test.drop(['Outlet_Identifier'], axis=1, inplace=True)

# # identify cat features
categorical_features = np.where(train.dtypes == 'object')[0]

# Training and Validation ---------------------------------
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(train, sales,
                                                    test_size = 0.25,
                                                    random_state = 11)


# Model Eval ----------------------------------------------------
model_cat = CatBoostRegressor(iterations = 100, learning_rate = 0.30,
                                 depth = 6, eval_metric = 'RMSE', random_seed=7)

# training the model
model_cat.fit(X_train, y_train, cat_features=categorical_features, use_best_model=True)

# Score
print('\n',"The RMSE score on the validation set is: \n ",
      # f'result: {value:{width}.{precision}}'
      f'{model_cat.score(X_test, y_test):{0}.{6}}')


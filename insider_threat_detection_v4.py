#Importing the necessary Libraries
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest


pd.options.display.max_rows = 100

# read logon file into the programme
device = pd.read_csv('device.csv')
print(device.head(15))

logon = pd.read_csv('logon.csv')
print(logon.head(15))

file = pd.read_csv('file.csv')
print(file.head(15))

# cleaning data for use in anomaly decision.
#mode: is the 10days for example _ the time the user logs in most in say ten days: Time with the highest frequency
#mean - average time of the scenario of the user - just to clean the data


# normalizing data for the device dataset

# there are three hypothesis that need to be observed in order to detect fraudulent activity among the user
# 1. Do they connect their device after closing hour
# 2. How long it takes for them to disconnect their device from the pc
# 3. Are there any user connecting device to more than one pc

#creates a new column 'time' in the 'device' DataFrame, extracting and retaining only the time component from the 'date' column.
#This is part of cleaning the data
device['time'] = pd.to_datetime(device['date']).dt.time


device_on_connection = device.loc[device['activity'] == 'Connect']
device_on_disconnection = device.loc[device['activity'] == 'Disconnect']
print(device_on_connection.shape)
print(device_on_disconnection.shape)

#The code groups the 'device_on_connection' DataFrame by 'user', calculates the minimum and maximum 'time' 
# for each user, and prints the first 5 rows of the resulting DataFrame
device_on_connection_stats = device_on_connection.groupby('user')['time'].agg([min, max]).reset_index()
print(device_on_connection_stats.head())

#calculate the mode time at which user connect to the system
conn_mode = device_on_connection.groupby('user')['time'].agg(lambda x: x.value_counts().index[0]).reset_index()

#calculate the mean connect
device_on_connection['hour'] = pd.to_datetime(device_on_connection['date']).dt.hour 
conn_mean = device_on_connection.groupby('user')['hour'].mean().reset_index()
conn_mean['hour'] = conn_mean['hour'].astype(int)
conn_mean['hour'] = pd.to_datetime(conn_mean['hour'], format='%H').dt.time
print(conn_mean.head())

#To add mode and mean columns to the device_on)connection...DataFrame based off calculated mode and mean times
device_on_connection_stats['mode'] = conn_mode['time']
device_on_connection_stats['mean'] = conn_mean['hour']
print(device_on_connection_stats.head())


#Converts timestamp to integer value representing seconds.
def dtt2timestamp(dtt):
    ts = (dtt.hour * 60 + dtt.minute) * 60 + dtt.second
    return ts


# Cleaning the data for Anomaly detection
#This part applies the 'dtt2timestamp' function to convert the timestamp columns to integer values.
device_on_connection_stats_sec = device_on_connection_stats
con_min_ts = [dtt2timestamp(dtt) for dtt in device_on_connection_stats_sec['min']]
con_max_ts = [dtt2timestamp(dtt) for dtt in device_on_connection_stats_sec['max']]
con_mode_ts = [dtt2timestamp(dtt) for dtt in device_on_connection_stats_sec['mode']]
con_mean_ts = [dtt2timestamp(dtt) for dtt in device_on_connection_stats_sec['mean']]

#New columns 'min_ts', 'max_ts', 'mode_ts', and 'mean_ts' are added to 'device_on_connection_stats_sec', 
#and the original timestamp columns are dropped.
device_on_connection_stats_sec['min_ts'] = con_min_ts
device_on_connection_stats_sec['max_ts'] = con_max_ts
device_on_connection_stats_sec['mode_ts'] = con_mode_ts
device_on_connection_stats_sec['mean_ts'] = con_mean_ts
device_on_connection_stats_sec = device_on_connection_stats_sec.drop(['min', 'max','mode','mean'], axis=1)


logon['time'] = pd.to_datetime(logon['date']).dt.time
logon_on_connection = logon.loc[logon['activity'] == 'Logon']
logon_on_disconnection = logon.loc[logon['activity'] == 'Logoff']
logon_on_connection_stats = logon_on_connection.groupby('user')['time'].agg([min, max]).reset_index()
print(logon_on_connection_stats.head())


#logon_on_connection.groupby('user')['time']: Groups the logon data by user and selects the 'time' column.
#.agg(lambda x: x.value_counts().index[0]): For each user, calculates the mode (most frequent value) of logon times.
#.reset_index(): Resets the index to make the result more manageable.


log_conn_mode = logon_on_connection.groupby('user')['time'].agg(lambda x: x.value_counts().index[0]).reset_index()
logon_on_connection['hour'] = pd.to_datetime(logon_on_connection['date']).dt.hour #Creates a new 'hour' column by extracting the hour component from the 'date' column. This represents the hour of the day when logon events occurred.

#logon_on_connection.groupby('user')['hour']: Groups the logon data by user and selects the 'hour' column.
#.mean(): Calculates the mean (average) logon hour for each user.
#.reset_index(): Resets the index for a cleaner result.
log_conn_mean = logon_on_connection.groupby('user')['hour'].mean().reset_index()
log_conn_mean['hour'] = log_conn_mean['hour'].astype(int) # astype(int) Converts the 'hour' values to integers.
log_conn_mean['hour'] = pd.to_datetime(log_conn_mean['hour'], format='%H').dt.time #
print(conn_mean.head())

logon_on_connection_stats['mode'] = log_conn_mode['time']
logon_on_connection_stats['mean'] = log_conn_mean['hour']
print(logon_on_connection_stats.head())


# Logon Anomaly detection
#These lines convert timestamps to integer values and create new columns in 'logon_on_connection_stats_sec'.
logon_on_connection_stats_sec = logon_on_connection_stats
con_min_ts = [dtt2timestamp(dtt) for dtt in logon_on_connection_stats_sec['min']]
con_max_ts = [dtt2timestamp(dtt) for dtt in logon_on_connection_stats_sec['max']]
con_mode_ts = [dtt2timestamp(dtt) for dtt in logon_on_connection_stats_sec['mode']]
con_mean_ts = [dtt2timestamp(dtt) for dtt in logon_on_connection_stats_sec['mean']]
logon_on_connection_stats_sec['min_ts'] = con_min_ts
logon_on_connection_stats_sec['max_ts'] = con_max_ts
logon_on_connection_stats_sec['mode_ts'] = con_mode_ts
logon_on_connection_stats_sec['mean_ts'] = con_mean_ts
logon_on_connection_stats_sec = logon_on_connection_stats_sec.drop(['min', 'max','mode','mean'], axis=1)
#Columns from 'logon_on_connection_stats_sec' are added to 'device_on_connection_stats_sec'.
device_on_connection_stats_sec['log_max_ts']  = logon_on_connection_stats_sec['max_ts']   
device_on_connection_stats_sec['log_mode_ts'] = logon_on_connection_stats_sec['mode_ts']


#file = pd.read_csv('file.csv')
#print(file)

file['time'] = pd.to_datetime(file['date']).dt.time
# print(file.shape)
# print(file_on_disconnection.shape)

file_stats = file.groupby('user')['time'].agg([min, max]).reset_index()
print(file_stats.head())

#calculate the mode time at which user connect to the system
conn_mode = file.groupby('user')['time'].agg(lambda x: x.value_counts().index[0]).reset_index()

file['hour'] = pd.to_datetime(file['date']).dt.hour
conn_mean = file.groupby('user')['hour'].mean().reset_index()
conn_mean['hour'] = conn_mean['hour'].astype(int)
conn_mean['hour'] = pd.to_datetime(conn_mean['hour'], format='%H').dt.time
print(conn_mean.head())

file_stats['mode'] = conn_mode['time']
file_stats['mean'] = conn_mean['hour']
print(file_stats.head())

# convert timestamp to integer value
# def dtt2timestamp(dtt):
#     ts = (dtt.hour * 60 + dtt.minute) * 60 + dtt.second
#     return ts
#This lines up is a repetition

# Anomaly detection
file_stats_sec = file_stats
con_min_ts = [dtt2timestamp(dtt) for dtt in file_stats_sec['min']]
con_max_ts = [dtt2timestamp(dtt) for dtt in file_stats_sec['max']]
con_mode_ts = [dtt2timestamp(dtt) for dtt in file_stats_sec['mode']]
con_mean_ts = [dtt2timestamp(dtt) for dtt in file_stats_sec['mean']]

file_stats_sec['min_ts'] = con_min_ts
file_stats_sec['max_ts'] = con_max_ts
file_stats_sec['mode_ts'] = con_mode_ts
file_stats_sec['mean_ts'] = con_mean_ts
file_stats_sec = file_stats_sec.drop(['min', 'max','mode','mean'], axis=1)

device_on_connection_stats_sec['file_max_ts']  = file_stats_sec['max_ts']   
device_on_connection_stats_sec['file_mode_ts'] = file_stats_sec['mode_ts']

device_on_connection_stats_sec.dropna()
device_on_connection_stats_sec.drop(device_on_connection_stats_sec.tail(9).index,inplace = True)
print(file_stats_sec.shape)
print(device_on_connection_stats_sec.shape)

anomaly_inputs = ['max_ts', 'mode_ts', 'log_max_ts', 'log_mode_ts','file_max_ts', 'file_mode_ts' ]
file_anomaly_inputs = ['file_max_ts', 'file_mode_ts']
log_anomaly_inputs = ['log_max_ts', 'log_mode_ts']
device_anomaly_inputs = ['max_ts', 'mode_ts']

model_If = IsolationForest(contamination=0.1, random_state = 12)
model_If.fit(device_on_connection_stats_sec[anomaly_inputs])
device_on_connection_stats_sec['anomaly_scores'] = model_If.decision_function(device_on_connection_stats_sec[anomaly_inputs])
device_on_connection_stats_sec['anomaly'] = model_If.predict(device_on_connection_stats_sec[anomaly_inputs])
print(device_on_connection_stats_sec)

'''Explanation of Training below - For Device Dataset'''
#model_If.fit: Initiates the training process for the Isolation Forest model
#(model_If) on the data provided.
#device_on_connection_stats_sec[device_anomaly_inputs]: Selects specific columns ('max_ts' and 'mode_ts') from the DataFrame
#device_on_connection_stats_sec' to be used as inputs for model training.
#model_If.decision_function: Calculates the anomaly score for each data point based on the Isolation Forest model. This score indicates how much of an anomaly each data point is.
#Assigns these anomaly scores to a new column called 'device_anomaly_scores' in the 'device_on_connection_stats_sec' DataFrame.
#model_If.predict: Predicts whether each data point is an inlier (1) or an outlier/anomaly (-1) based on the Isolation Forest model.
#Assigns these predicted labels to a new column called 'device_anomaly' in the 'device_on_connection_stats_sec' DataFrame.


model_If.fit(device_on_connection_stats_sec[device_anomaly_inputs])
device_on_connection_stats_sec['device_anomaly_scores'] = model_If.decision_function(device_on_connection_stats_sec[device_anomaly_inputs])
device_on_connection_stats_sec['device_anomaly'] = model_If.predict(device_on_connection_stats_sec[device_anomaly_inputs])

#explanation as above
model_If.fit(device_on_connection_stats_sec[log_anomaly_inputs])
device_on_connection_stats_sec['log_anomaly_scores'] = model_If.decision_function(device_on_connection_stats_sec[log_anomaly_inputs])
device_on_connection_stats_sec['log_anomaly'] = model_If.predict(device_on_connection_stats_sec[log_anomaly_inputs])

model_If.fit(device_on_connection_stats_sec[file_anomaly_inputs])
device_on_connection_stats_sec['file_anomaly_scores'] = model_If.decision_function(device_on_connection_stats_sec[file_anomaly_inputs])
device_on_connection_stats_sec['file_anomaly'] = model_If.predict(device_on_connection_stats_sec[file_anomaly_inputs])

print(device_on_connection_stats_sec)

#############

def outlier_plot(data, anomaly, outlier_method_name, x_var, y_var, xaxis_limits=[0,1], yaxis_limits=[0,1]):
    print(f'Outlier Method: {outlier_method_name}')

    #method = f'{outlier_method_name}_anomaly'

    print(f"Number of anomalous values { len(data[data[anomaly]== -1])}")
    print(f"Number of non anomalous value {len(data[data[anomaly] == 1])}")
    print(f'Total Number of Values: {len(data)}')

    g = sns.FacetGrid(data, col=anomaly, height=4, hue=anomaly, hue_order=[1,-1])
    g.map(sns.scatterplot, x_var, y_var)
    g.fig.suptitle(f'Outlier Method: {outlier_method_name}', y=1.10, fontweight='bold')
    g.set(xlim = xaxis_limits, ylim= yaxis_limits)
    axes = g.axes.flatten()
    axes[0].set_title(f"Outliers\n{len(data[data[anomaly] == -1])} points")
    axes[1].set_title(f"Inliers\n{len(data[data[anomaly] == 1])} points")

    plt.show()

    return g

#generating outlier plots for device dataset anomaly
outlier_plot(device_on_connection_stats_sec, 'device_anomaly', "Isolation Forest", "max_ts", "mode_ts", [0, 200000], [0, 100000] )

#generating outlier plots for log dataset anomaly
outlier_plot(device_on_connection_stats_sec, 'log_anomaly',  "Isolation Forest", "log_max_ts", "log_mode_ts", [0, 200000], [0, 100000] )

#generating outlier plots for file dataset anomaly
outlier_plot(device_on_connection_stats_sec, 'file_anomaly', "Isolation Forest", "file_max_ts", "file_mode_ts", [0, 200000], [0, 100000] )


palette = ['#ff7f0e', '#1f77b4']

sns.pairplot(device_on_connection_stats_sec, vars=anomaly_inputs, hue = 'anomaly', palette = palette)

plt.show()



'''
Explanation of the Training - Device Dataset

model_If.fit(device_on_connection_stats_sec[device_anomaly_inputs]):

model_If.fit: Initiates the training process for the Isolation Forest model (model_If) on the data provided.
device_on_connection_stats_sec[device_anomaly_inputs]: Selects specific columns ('max_ts' and 'mode_ts') from the DataFrame 'device_on_connection_stats_sec' to be used as inputs for model training.
device_on_connection_stats_sec['device_anomaly_scores'] = model_If.decision_function(device_on_connection_stats_sec[device_anomaly_inputs]):

model_If.decision_function: Calculates the anomaly score for each data point based on the Isolation Forest model. This score indicates how much of an anomaly each data point is.
Assigns these anomaly scores to a new column called 'device_anomaly_scores' in the 'device_on_connection_stats_sec' DataFrame.
device_on_connection_stats_sec['device_anomaly'] = model_If.predict(device_on_connection_stats_sec[device_anomaly_inputs]):

model_If.predict: Predicts whether each data point is an inlier (1) or an outlier/anomaly (-1) based on the Isolation Forest model.
Assigns these predicted labels to a new column called 'device_anomaly' in the 'device_on_connection_stats_sec' DataFrame.

'''




import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Define file paths for local data storage
commit_csv_path = "data/raw/git_commits_sample.csv"
pull_request_csv_path = "data/raw/git_pull_requests_sample.csv"
jira_csv_path = "data/raw/jira_issues_sample.csv"

# Function to load commits from local CSV
def get_commits():
    try:
        commits = pd.read_csv(commit_csv_path)
        return commits
    except FileNotFoundError:
        print("Commit data file not found.")
        return pd.DataFrame()

# Function to load pull requests from local CSV
def get_pull_requests():
    try:
        pull_requests = pd.read_csv(pull_request_csv_path)
        return pull_requests
    except FileNotFoundError:
        print("Pull request data file not found.")
        return pd.DataFrame()

# Function to load JIRA issues from local CSV
def get_jira_issues():
    try:
        jira_issues = pd.read_csv(jira_csv_path)
        return jira_issues
    except FileNotFoundError:
        print("JIRA issues data file not found.")
        return pd.DataFrame()

# Example usage
commits = get_commits()
pull_requests = get_pull_requests()
jira_issues = get_jira_issues()

# Print some example data
print("Commits:", commits.head())
print("Pull Requests:", pull_requests.head())
print("JIRA Issues:", jira_issues.head())


# Convert to DataFrame
commits_df = pd.DataFrame(commits)
pull_requests_df = pd.DataFrame(pull_requests)
jira_df = pd.DataFrame(jira_issues)
print(pull_requests_df.head())

# Convert datetime columns to datetime type
commits_df['timestamp'] = pd.to_datetime(commits_df['timestamp'])

pull_requests_df['created_at'] = pd.to_datetime(pull_requests_df['created_at'])
pull_requests_df['merged_at'] = pd.to_datetime(pull_requests_df['merged_at'])
jira_df['created_at'] = pd.to_datetime(jira_df['created_at'])
jira_df['resolved_at'] = pd.to_datetime(jira_df['resolved_at'])

# Calculate time differences (e.g., time spent on tasks or pull requests)
commits_df['commit_day'] = commits_df['timestamp'].dt.date
pull_requests_df['pr_merge_time'] = (pull_requests_df['merged_at'] - pull_requests_df['created_at']).dt.total_seconds() / 3600  # in hours
jira_df['resolution_time'] = (jira_df['resolved_at'] - jira_df['created_at']).dt.total_seconds() / 3600  # in hours


print(pull_requests_df.columns)
# Show processed data
print("Commits Data:\n", commits_df.head())
print("Pull Requests Data:\n", pull_requests_df.head())
print("Jira Data:\n", jira_df.head())

pull_requests_df = pull_requests_df.dropna(subset=['pr_merge_time'])

# Example: using time spent on pull requests (PR merge times) as a feature for clustering
activity_data = pull_requests_df[['pr_merge_time']]

print(activity_data.columns)
# Apply K-Means clustering (let's assume we want 3 clusters)
kmeans = KMeans(n_clusters=3, random_state=42)
pull_requests_df['cluster'] = kmeans.fit_predict(activity_data)

# Visualize the clusters
plt.scatter(pull_requests_df['pr_merge_time'], np.zeros_like(pull_requests_df['pr_merge_time']), c=pull_requests_df['cluster'], cmap='viridis')
plt.xlabel('Pull Request Merge Time (hours)')
plt.title('Developer Activity Clustering (Pull Requests)')
plt.show()

print("Clustered Data:\n", pull_requests_df[['author', 'pr_merge_time', 'cluster']])
# 3.2. Time-Series Analysis (ARIMA)
# Now let's apply a simple ARIMA model to predict future commit times.


from statsmodels.tsa.arima.model import ARIMA

# Assume commits_df has a column 'commit_time' which is already in datetime format
commits_df.set_index('commit_time', inplace=True)
commits_df_resampled = commits_df.resample('D').size()  # Resample by day and count commits

# Fit an ARIMA model
model = ARIMA(commits_df_resampled, order=(1, 1, 1))  # ARIMA(p,d,q)
model_fit = model.fit()

# Make a forecast
forecast = model_fit.forecast(steps=10)
print("Forecasted Commits:", forecast)

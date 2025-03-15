import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("main_data.csv")

data = load_data()

# Convert date
data['dteday'] = pd.to_datetime(data['dteday'])

# Sidebar for filters
# Determine date range
min_date = data['dteday'].min()
max_date = data['dteday'].max()

# Sidebar for date filter
with st.sidebar:
    st.image("https://c8.alamy.com/comp/2NAGMWM/cartoon-illustration-of-boy-character-riding-a-bicycle-2NAGMWM.jpg")
    start_date, end_date = st.date_input(
        label='Date Range', 
        min_value=min_date, 
        max_value=max_date, 
        value=[min_date, max_date]
    )

main_df = data[(data['dteday'] >= pd.Timestamp(start_date)) & (data['dteday'] <= pd.Timestamp(end_date))]

# Daily visualization
st.title("Bike Rental Dashboard 🚲")

# Resample monthly data
monthly_rentals_df = data.resample(rule='M', on='dteday').agg({
    "cnt_x": "sum",
    "registered_x": "sum",
    "casual_x": "sum"
}).reset_index()
 
# Format date
monthly_rentals_df['dteday'] = monthly_rentals_df['dteday'].dt.strftime('%Y-%m')

# Calculate total rentals & registered users
st.subheader('Monthly Bike Rentals 🚲')

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_rentals_df['cnt_x'].sum()
    st.metric("Total Rentals", value=total_orders)

with col2:
    total_registered = monthly_rentals_df['registered_x'].sum()
    st.metric("Total Registered Users", value=total_registered)

# Monthly rentals visualization
fig, ax = plt.subplots(figsize=(16, 8))

# Total Rentals
ax.plot(
    monthly_rentals_df["dteday"], 
    monthly_rentals_df["cnt_x"], 
    marker='o', 
    linewidth=3, 
    color="#1976D2", 
    label="Total Rentals"
)

# Registered Users
ax.plot(
    monthly_rentals_df["dteday"], 
    monthly_rentals_df["registered_x"], 
    marker='s', 
    linewidth=2, 
    color="#FF9800", 
    label="Registered Users"
)

# Casual Users
ax.plot(
    monthly_rentals_df["dteday"], 
    monthly_rentals_df["casual_x"], 
    marker='^', 
    linewidth=2, 
    color="#4CAF50", 
    label="Casual Users"
)

# Formatting
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.set_xlabel('Month', fontsize=15)
ax.set_ylabel('Number of Rentals', fontsize=15)
ax.set_title('Monthly Bike Rentals', fontsize=18)
ax.legend(fontsize=12)
ax.grid()

st.pyplot(fig)

# Hourly rentals by season
st.subheader("Hourly Bike Rentals by Season")

fig, ax = plt.subplots(2, 2, figsize=(18, 12))

seasons = {
    1: "Winter",
    2: "Spring",
    3: "Summer",
    4: "Fall"
}

for i, (season, name) in enumerate(seasons.items()):
    row, col = divmod(i, 2)
    season_df = main_df[main_df['season_x'] == season]

    sns.barplot(x='hr', y='cnt_y', data=season_df, ax=ax[row, col], color='#1f77b4')
    ax[row, col].set_title(f'Hourly Bike Rentals in {name}')
    ax[row, col].set_xlabel('Hour of Day')
    ax[row, col].set_ylabel('Total Rentals')
    ax[row, col].tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)

# Pastikan max_value lebih besar dari 4000
max_value = main_df['cnt_x'].max()
if max_value <= 4000:
    max_value = 4001  # Hindari nilai duplikat

# Manual Grouping for Rental Categories
main_df['rental_category'] = pd.cut(main_df['cnt_x'], bins=[0, 1000, 4000, max_value],
                                    labels=['Low', 'Medium', 'High'], include_lowest=True)

# Grouping Data for Visualization

grouped_day_df = main_df.groupby(['season_x', 'rental_category']).size().reset_index(name='count')

main_df['time_of_day'] = pd.cut(main_df['hr'], bins=[0, 6, 12, 18, 24],
                                labels=['Early Morning', 'Morning', 'Afternoon', 'Evening'], right=False)

grouped_hour_df = main_df.groupby(['season_x', 'time_of_day']).size().reset_index(name='count')

# Visualization
st.title("Advanced Analysis with Manual Grouping")

st.subheader("Bike Rental Categories by Season")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='season_x', y='count', hue='rental_category', data=grouped_day_df, palette='viridis')
ax.set_xlabel('Season')
ax.set_ylabel('Number of Days')
plt.title('Bike Rental Categories by Season')
st.pyplot(fig)

st.subheader("Bike Rental Patterns by Time of Day")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='season_x', y='count', hue='time_of_day', data=grouped_hour_df, palette='coolwarm')
ax.set_xlabel('Season')
ax.set_ylabel('Number of Rentals')
plt.title('Bike Rental Patterns by Time of Day (Based on Season)')
st.pyplot(fig)

st.caption("copyright 2023")


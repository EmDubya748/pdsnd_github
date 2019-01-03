"""
Created on Thu Dec 20 11:40:59 2018

@author: MichaelWei
"""
from timeit import default_timer as timer
import pandas as pd
import datetime as dt

pd.set_option('display.max_columns', 200)

CITY_DATA = {'Chicago': 'chicago.csv', 
             'New York City': 'new_york_city.csv',
             'Washington': 'washington.csv',
             'test_MCW': 'test_MCW-6.csv'}

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July']

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday']

HOURS = ['1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', 
         '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 AM',
         '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM',
         '7 PM', '8 PM', '9 PM', '10 PM', '11 PM', '12 PM']

CURRENT_YEAR = int(dt.datetime.now().year)

SEPARATOR_WIDTH = 75

def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - pandas DataFrame containing city data filtered by month and day
        df_overdue - pandas DataFrame containing instances of users that returned a bike after 3 days
        df_underage - pandas DataFrame containing instances of users that are under a threshold of 16 years old
    """
    min_duration = 240
    max_duration = 259200
    df = pd.read_csv(CITY_DATA[city])

    # Convert Start Times to datetimes
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    
    # Create Month column
    df['Month'] = df['Start Time'].dt.month
    
    # Create the day of week column
    df['day_of_week'] = df['Start Time'].dt.weekday
    
    df['Start Hour'] = df['Start Time'].dt.hour
    
    # Filter by month first, if applicable
    if month != 'All':
        month = MONTHS.index(month) + 1
        df = df[df['Month'] == month]

    
    # Filter by day of week, if applicable
    if day != 'All':
        day = DAYS.index(day)
        df = df[df['day_of_week'] == day]
        
    # Check for NaN values
    null_vals = df.isnull().sum()
    
    # Just drop the User Type NaNs
    # Keeping thee Gender and Birth Year NaNs, because sometimes a User might chose to
    # not provide that information
    df = df[pd.notnull(df['User Type'])]
    
    # Flag the bikes that have been out for more than 3 days
    df_overdue = df[df['Trip Duration'] > max_duration]
    
    # Filter out anomalies in the Trip Duration column
    # Impose limits of minimum 4 minute (240 seconds) trip time and maximum of 3 days (259200 seconds)
    # Assume that all bikes can be rented out based on a 3 day pass
    
    df = df[(df['Trip Duration'] > min_duration) & (df['Trip Duration'] < max_duration)]
    
    # Filter out anomalies in the Age data if we're looking at Chicago or New York City
    # Assuming that people can still bike near the end of life span (100 years)
    
    if city in ['Chicago', 'New York City']:
        age_min = 16
        age_max = 100
        
        max_year = df['Start Time'].dt.year.max() - age_min
        min_year = df['Start Time'].dt.year.max() - age_max
        
        df_underage = df[df['Birth Year'] < min_year]
        df = df[(df['Birth Year'] > min_year) & (df['Birth Year'] < max_year)]
    
    else:
        df_underage = None
    
    return df, df_overdue, df_underage

def getCityFilter():
    """
    Sets the city filter
    Args:
        N/A
    Returns:
        (str) user_city - name of the filter city selected by the user
    
    """
    user_city = input('Would you like to see data for Chicago, New York City, or Washington? ')
    print()
    
    # Hidden option of 1, 2, 3 in case a user inputs that by accident
    while user_city[0] not in ['C', 'c', '1', 'N', 'n', '2', 'W', 'w', '3']:
         
        user_city = input('Please enter a valid city (Chicago, New York City, or Washington): ')
    
    if user_city[0].upper() in ['C', '1']:
        # User input is discernible to be Chicago
        user_city = 'Chicago'
    elif user_city[0].upper() in ['N', '2']:
        user_city = 'New York City'
    elif user_city[0].upper() in ['W', '3']:
        user_city = 'Washington'
    
    return user_city

def getTypeFilter():
    """
    Sets the type of filter to be 'Month', 'Day', 'Both', or 'None'
    
    Args:
        N/A
    Returns:
        (str) user_type - name of the filter type selected by the user
    """
    user_type = input('Would you like to filter by month, day, both, or none at all? ')
    print()
    
    # Hidden option of 1, 2, 3, 4 in case a user inputs that by accident
    while user_type[0] not in ['M', 'm', '1', 'D', 'd', '2', 'B', 'b', '3', 'N', 'n', '4']:
        
        user_type = input('Please enter a valid filter type (month, day, both, or none): ')

    if user_type[0].upper() in ['M', '1']:
        user_type = 'Month'
    elif user_type[0].upper() in ['D', '2']:
        user_type = 'Day'
    elif user_type[0].upper() in ['B', '3']:
        user_type = 'Both'
    elif user_type[0].upper() in ['N', '4']:
        user_type = 'None'
        
    return user_type

def getTimeFilter(filter_type):
    """
    Sets the month and day filters
    Args:
        (str) filter_type - type of filter to analyze
    Returns:
        (tuple) (user_month, user_day) - month and day to filter by
    """
    if filter_type == 'Month' or filter_type == 'Both':
        
        user_month = input('Select a month (January, February, etc.): ')
        
        # Note: Although most of the data is between January and June, there are a few data points in July
        while user_month[:3].capitalize() not in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                                                  '1', '2', '3', '4', '5', '6', '7']:
            
            user_month = input('Please select a valid month (January through July): ')
            
        # Fix month filter to be the desired format
        if user_month[:3].capitalize() in ['Jan', '1']:
            user_month = 'January'
        elif user_month[:3].capitalize() in ['Feb', '2']:
            user_month = 'February'
        elif user_month[:3].capitalize() in ['Mar', '3']:
            user_month = 'March'
        elif user_month[:3].capitalize() in ['Apr', '4']:
            user_month = 'April'
        elif user_month[:3].capitalize() in ['May', '5']:
            user_month = 'May'
        elif user_month[:3].capitalize() in ['Jun', '6']:
            user_month = 'February'
        elif user_month[:3].capitalize() in ['Jul', '7']:
            user_month = 'July'
        
    if filter_type == 'Day' or filter_type == 'Both':
        
        user_day = input('Select a day (Monday, Tuesday, etc.): ')
        
        while user_day[:2].capitalize() not in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su',
                                                  '1', '2', '3', '4', '5', '6', '7']:
            user_day = input('Please select a valid day (Monday, Tuesday, etc.): ' )
        
        if user_day[:2].capitalize() in ['Mo', '1']:
            user_day = 'Monday'
        elif user_day[:2].capitalize() in ['Tu', '2']:
            user_day = 'Tuesday'
        elif user_day[:2].capitalize() in ['We', '3']:
            user_day = 'Wednesday'
        elif user_day[:2].capitalize() in ['Th', '4']:
            user_day = 'Thursday'
        elif user_day[:2].capitalize() in ['Fr', '5']:
            user_day = 'Friday'
        elif user_day[:2].capitalize() in ['Sa', '6']:
            user_day = 'Saturday'
        elif user_day[:2].capitalize() in ['Su', '7']:
            user_day = 'Sunday'
        
    if filter_type == 'None':
        user_month = 'All'
        user_day = 'All'
        return (user_month, user_day)
    
    elif filter_type == 'Both':
        return (user_month, user_day)
        
    elif filter_type == 'Month':
        user_day = 'All'
        return (user_month, user_day)
    
    elif filter_type == 'Day':
        user_month = 'All'
        return (user_month, user_day)
    
def time_stats(df, filter_type, filter_month, filter_day):
    """
    Basic function for time related statistics (popular month, popular day, popular hour)
    
    Args:
        (df) df - pandas DataFrame filtered by user criteria
        (str) filter_type - type of filter selected by user
        (str) filter_month - name of month to filter by
        (str) filter_day - name of day to filter by
    Returns:
        (popular_month, month_count) - tuple of the most popular month and the frequency
        (popular_day, day_count) - tuple of the most popular day and the frequency
        (popular_hour, hour_count) - tuple of the most popular hour and the frequency
    """
    print('-' * SEPARATOR_WIDTH)
    print('Calculating Time Statistics:\n')
    
    start = timer()
    
    popular_month = 'N/A'
    popular_day = 'N/A'
    
    month_count = 'N/A'
    day_count = 'N/A'
    
    # Most common start hour:
    # Will always get a most common start hour in the data, regardless of filter
    popular_hour = df['Start Hour'].mode()[0]
    hour_count = df['Start Hour'].value_counts()[popular_hour]
    
    
    popular_hour = HOURS[popular_hour]
    
    if filter_month == 'All':
        popular_month = df['Month'].mode()
        popular_month = df['Month'].mode()[0]
        month_count = df['Month'].value_counts()[popular_month]
        
        # Grab the actual name of the month
        popular_month = MONTHS[popular_month - 1]
                
        
    if filter_day == 'All':
        popular_day = df['day_of_week'].mode()
        
        popular_day = df['day_of_week'].mode()[0]
        day_count = df['day_of_week'].value_counts()[popular_day]
        
        # Grab the actual name of the day
        popular_day = DAYS[popular_day]
        
    if filter_type == 'None':
        print('Most popular month is {}, with a count of {}.'.format(popular_month, month_count))
        print('Most popular day is {}, with a count of {}.'.format(popular_day, day_count))
    elif filter_type == 'Month':
        print('Most popular day is {}, with a count of {}.'.format(popular_day, day_count))
    elif filter_type == 'Day':
        print('Most popular month is {}, with a count of {}.'.format(popular_month, month_count))
        
    # Will always get a most popular hour, so this comes after determining if there is a filter_month and/or filter_day
    print('Most popular hour is {}, with a count of {}.'.format(popular_hour, hour_count))
        
    end = timer()
    print('Computation time: {:.4f} seconds.'.format(end - start))
    
    # Return values so that we could potentially put them in an end summary
    return (popular_month, month_count), (popular_day, day_count), (popular_hour, hour_count)

def station_stats(df):
    """
    Basic function for station related statistics (Popular Start Station, Popular End Station, Popular Start-End Combination)
    
    Args:
        (df) df - pandas DataFrame filtered by user criteria
    Returns:
        (popular_start, start_count) - tuple of the most popular start station and frequency
        (popular_end, end_count) - tuple of the most popular end station and frequency
        (popular_combo, combo_count) - tuple of the most popular start-end station route and frequency
    """
    print('-' * SEPARATOR_WIDTH)
    print('Calculating Trip Start/Destination statistics:\n')
    
    start = timer()
    
    popular_start = df['Start Station'].mode()
    start_count = df['Start Station'].value_counts()[popular_start[0]]
    
    if len(popular_start) == 1:
        # Note: This is to give an actual count value to the mode, instead of just returning the mode value
        print('The most common Start Station is:', popular_start[0])
        print('With a count of:', start_count)
        
    elif len(popular_start) > 1:
        print('Note: Multiple Start Station Modes detected ({} modes), with a count of {}. Here are the most common Start Stations:'.format(len(popular_start), start_count))
        
        for start in popular_start:
            print(start)
            
    print()
    
    popular_end = df['End Station'].mode()
    end_count = df['End Station'].value_counts()[popular_end[0]]
        
    if len(popular_end) == 1:
        print('The most common End Station is:', popular_end[0])
        print('With a count of:', end_count)
        
    elif len(popular_end) > 1:
        print('Note: Multiple End Station Modes detected ({} modes), with a count of {}. Here are the most common End Stations:'.format(len(popular_end), end_count))
        
        for end in popular_end:
            print(end)
    
    print()
    
    df['Combos'] = df['Start Station'] + ' to ' + df['End Station']
    popular_combo = df['Combos'].mode()
    combo_count = df['Combos'].value_counts()[popular_combo[0]]

    if len(popular_combo) == 1:
        print('The most common Start Station-End Station combination is:', popular_combo[0])
        print('With a count of:', combo_count)
    
    elif len(popular_combo) > 1:
        print('Note: Multiple Start Station-End Station combination modes detected ({} modes), with a count of {}. Here are the most common trips:\n'.format(len(popular_combo), combo_count))
        
        for i in range(len(popular_combo)):
            print(popular_combo[i])
            
    print()
    
    end = timer()
    
    print('Computation time: {:.4f} seconds.'.format(end - start))
    
    return (popular_start, start_count), (popular_end, end_count), (popular_combo, combo_count)

def trip_duration_stats(df, df_overdue):
    """
    Basic function for trip duration related statistics (Cummulative Trip Duration, Trip Duration Mean, Trip Duration Std Dev, Trip Duration Median)
    
    Args:
        (df) df - pandas DataFrame filtered by user criteria
        (df) df_overdue - pandas DataFrame showing the number of bikes with trip durations over 3 days
    Returns:
        (int) total_trip - Cummulative time of all trips
        (float) mean_trip - Mean trip duration
        (float) std_dev_trip - Standard Deviation of trip durations
        (float) median_trip - Median of trip durations
    """
    print('-' * SEPARATOR_WIDTH)
    print('Calculating Trip Duration statistics:\n')
    
    start = timer()
    
    total_trip = df['Trip Duration'].sum()
    total_trip_hours = total_trip / 3600
    
    print('Cummulative Trip Duration: {} seconds ({:.0f} hours)'.format(total_trip, total_trip_hours))
    
    mean_trip = df['Trip Duration'].mean()
    mean_trip_min = mean_trip / 60
    
    print('Mean Trip Duration: {:.0f} seconds ({:.1f} minutes)'.format(mean_trip, mean_trip_min))
    
    std_dev_trip = df['Trip Duration'].std()
    std_dev_trip_min = std_dev_trip / 60
    
    print('Standard Deviation Trip Duration: {:.0f} seconds ({:.1f} minutes)'.format(std_dev_trip, std_dev_trip_min))
    
    median_trip = df['Trip Duration'].median()
    median_trip_min = median_trip / 60
    
    print('Median Trip Duration: {:.0f} seconds ({:.1f} minutes)\n'.format(median_trip, median_trip_min))
    
    # Max Trip ; See if the data makes sense
    max_trip = df['Trip Duration'].max()
    max_trip_min = max_trip / 60
    
    print('Max Trip Duration: {:.0f} seconds ({:.1f} minutes)\n'.format(max_trip, max_trip_min))
    
    # Min Trip
    min_trip = df['Trip Duration'].min()
    min_trip_min = min_trip / 60
    
    print('Min Trip Duration: {:.0f} seconds ({:.1f} minutes)\n'.format(min_trip, min_trip_min))
    
    end = timer()
    
    overdue_bikes = df_overdue.count()
    
    print('Count of overdue bikes: {}\n'.format(overdue_bikes[0]))
    
    print('Computation time: {:.4f} seconds'.format(end - start))
    
    return total_trip, mean_trip, std_dev_trip, median_trip

def user_stats(df, df_underage, filter_city):
    """
    Basic function for user demographic related statistics, depending on if Gender and Birth Year information is available
    
    Args:
        (df) df - pandas DataFrame filtered by user criteria
        (df) df_underage - pandas DataFrame showing the users that are under 16
        (str) filter_city - name of the city selected by the user to filter by
    Returns:
        (list) output_data - list containing number of subscribers, number of customers, number of males, number of females, 
                             earliest birth year, most recent birth year, number of underage users, average duration for customers,
                             average duration for subscribers, median duration for customers, median duration for subscribers,
                             gender breakdown of user type (user_gender)
        For Washington:
        (list) output_data - list containing number of subscribers, number of customers, average duration for customers, average
                             duration for subscribers, median duration for customers, median duration for subscribers
    """
    print('-' * SEPARATOR_WIDTH)
    print('Calculating User Demographic Statistics:\n')
    
    start = timer()
    
    num_subscribers = df[df['User Type'] == 'Subscriber'].count()
    num_customers = df[df['User Type'] == 'Customer'].count()
    print('There were {} subscribers and {} customers during this time frame.'.format(num_subscribers[0], num_customers[0]))
    
    # Depending on if we're looking at Chicago or New York City, pull the Gender and Birthyear data
    num_males = 'N/A'
    num_females = 'N/A'
    earliest_birthyear = 'N/A'
    recent_birthyear = 'N/A'
    underage_users = [None]
    avg_duration_cust = 'N/A'
    avg_duration_sub = 'N/A'
    median_duration_cust = 'N/A'
    median_duration_sub = 'N/A'
    user_gender = 'N/A'
    
    if filter_city in ['Chicago', 'New York City']:
        # Base User Statistics
        num_males = df[df['Gender'] == 'Male'].count()
        num_females = df[df['Gender'] == 'Female'].count()
        
        earliest_birthyear = df['Birth Year'].min()
        recent_birthyear = df['Birth Year'].max()
        
        print('There were {} males and {} females during this time frame.'.format(num_males[0], num_females[0]))
        print('The earliest birth year was in {:.0f}.'.format(earliest_birthyear))
        print('The most recent birth year was in {:.0f}.'.format(recent_birthyear))
        
        # Additional User Statistics
        # Implement functionality to see this if the user wants, or not
        
        see_additional = input('Would you like to see additional User Demographic information (y/n)? ')
        see_additional = see_additional.capitalize()
        
        while see_additional[0] not in ['Y', 'Yes', 'N', 'No', 'no', 'n']:
            see_additional = input('Please enter a valid option: ')
        
        if see_additional[0] in ['Y', 'Yes']:
            print('-' * SEPARATOR_WIDTH)
            print('Additional User Statistics Initiated:')
            
            grouped = df.groupby('User Type')
            
            underage_users = df_underage.count()
            
            print('Number of underage users: {} (Hopefully these users had a Parent/Guardian with them!)\n'.format(underage_users[0]))
            
            avg_duration_cust = grouped['Trip Duration'].mean()[0]
            avg_duration_sub = grouped['Trip Duration'].mean()[1]
            
            avg_duration_cust_min = avg_duration_cust / 60
            avg_duration_sub_min = avg_duration_sub / 60
            
            print('Mean trip duration for a customer: {:.0f} seconds ({:.1f} minutes)'.format(avg_duration_cust, avg_duration_cust_min))
            print('Mean trip duration for a subscriber: {:.0f} seconds ({:.1f} minutes)\n'.format(avg_duration_sub, avg_duration_sub_min))
            
            median_duration_cust = grouped['Trip Duration'].median()[0]
            median_duration_sub = grouped['Trip Duration'].median()[1]
            
            median_duration_cust_min = median_duration_cust / 60
            median_duration_sub_min = median_duration_sub / 60
            
            print('Median trip duration for a customer: {:.0f} seconds ({:.1f} minutes)'.format(median_duration_cust, median_duration_cust_min))
            print('Median trip duration for a subscriber: {:.0f} seconds ({:.1f} minutes)\n'.format(median_duration_sub, median_duration_sub_min))
            
            # How many customers are male vs female
            user_gender = df.groupby(['User Type', 'Gender'])
            
            # Note: Just printing out the table, because it doesn't make sense to write out a sentence for each data point
            # A paragraph/sentence form of out put would be too verbose
            print('Here is a summary of the User Type breakdown by Gender:')
            print(user_gender[['User Type', 'Gender']].count()['User Type'])
            print()
            
            # Get the Birth Years into a list
            average_age = CURRENT_YEAR - user_gender['Birth Year'].mean().round(1)
            median_age = CURRENT_YEAR - user_gender['Birth Year'].median().round(1)
            std_dev_age = user_gender['Birth Year'].std().round(1)
            
            print('Here is a summary of Average Age data broken down by Gender:')
            print(average_age)
            print()
            
            print('And here is a summary of the Median Age data broken down by Gender:')
            print(median_age)
            print()
                      
            print('Lastly, here is a summary of Stardard Deviation data broken down by Gender:')
            print(std_dev_age)
            print()
            
        output_data = [num_subscribers[0], num_customers[0], num_males, num_females, earliest_birthyear, recent_birthyear,
                       underage_users[0], avg_duration_cust, avg_duration_sub, median_duration_cust, median_duration_sub,
                       user_gender]
        
    elif filter_city == 'Washington':
        print('Sorry, no Gender or Birth Year data are available for Washington.')
        
        see_additional = input('But would you like to see additional User Demographic information (y/n)? ')
        see_additional = see_additional.capitalize()
        
        while see_additional[0] not in ['Y', 'Yes', 'N', 'No', 'n', 'no']:
            see_additional = input('Please enter a valid option: ')
        
        if see_additional[0] in ['Y', 'Yes']:
            print('-' * SEPARATOR_WIDTH)
            print('Additional User Statistics Initiated:')
            
            grouped = df.groupby('User Type')
            
            avg_duration_cust = grouped['Trip Duration'].mean()[0]
            avg_duration_sub = grouped['Trip Duration'].mean()[1]
            
            avg_duration_cust_min = avg_duration_cust / 60
            avg_duration_sub_min = avg_duration_sub / 60
            
            print('Mean trip duration for a customer: {:.0f} seconds ({:.1f} minutes)'.format(avg_duration_cust, avg_duration_cust_min))
            print('Mean trip duration for a subscriber: {:.0f} seconds ({:.1f} minutes)\n'.format(avg_duration_sub, avg_duration_sub_min))
            
            median_duration_cust = grouped['Trip Duration'].median()[0]
            median_duration_sub = grouped['Trip Duration'].median()[1]
            
            median_duration_cust_min = median_duration_cust / 60
            median_duration_sub_min = median_duration_sub / 60
            
            print('Median trip duration for a customer: {:.0f} seconds ({:.1f} minutes)'.format(median_duration_cust, median_duration_cust_min))
            print('Median trip duration for a subscriber: {:.0f} seconds ({:.1f} minutes)\n'.format(median_duration_sub, median_duration_sub_min))
        
        output_data = [num_subscribers[0], num_customers[0], avg_duration_cust, avg_duration_sub, 
                       median_duration_cust, median_duration_sub]

    end = timer()
    
    print('Computation time: {:.4f} seconds.'.format(end - start))
    
    return output_data
    
def plot_data(df, filter_city, filter_type, filter_month, filter_day):
    """
    Basic function for plotting all pertinent statistics, depending on whether the user has matplotlib installed, and depending on filter city and type
    Args:
        (df) df - pandas DataFrame filtered by user criteria
        (str) filter_city - name of the city selected by the user to filter by
        (str) filter_type - type of filter selected by user
        (str) filter_month - name of month to filter by
        (str) filter_day - name of day to filter by
    Returns:
        N/A
    """
    try:
        
        import matplotlib.pyplot as plt
    
        see_data = input('Would you like to see plots of the data (y/n)? ')
        see_data = see_data.upper()
        
        while see_data not in ['Y', 'N', 'YES', 'NO']:
            see_data = input('Please enter a valid option for data visualization (y/n): ')
            see_data = see_data.upper()
    
        if see_data in ['N', 'NO', 'X', 'x']:
            return None    
    
        print('-' * SEPARATOR_WIDTH)
        
        if filter_city in ['Chicago', 'New York City']:
            hour_counts = df.groupby(['Start Hour'])['Start Hour'].count()
            trip_minutes = df[df['Trip Duration'] < 21600]
            trip_minutes['Trip Duration'] = trip_minutes['Trip Duration'] / 60
            bins = pd.cut(trip_minutes['Trip Duration'], [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360])
            trip_frequencies = trip_minutes['Trip Duration'].groupby(bins).agg(['count'])
            
            ages = CURRENT_YEAR - df['Birth Year']
            gender_breakdown = df.groupby(['User Type', 'Gender']).size()
            
            if filter_type == 'Both':
                fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(10, 8))
                fig.tight_layout()
                fig.suptitle('{}: {}s in {}'.format(filter_city, filter_day, filter_month))
                
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
                
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()
                
                ages.plot.hist(bins = 15, ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_title('User Ages')
                axes[1, 0].set_xlabel('Age (years)')
                axes[1, 0].set_ylabel('Frequency')
                
                gender_breakdown.plot.bar(ax = axes[1, 1], color='#4682B4')
                axes[1, 1].set_title('Gender Breakdown')
                axes[1, 1].set_ylabel('Frequency')
                
                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=0.6)
                plt.show()
                
            elif filter_type == 'None': 
                fig, axes = plt.subplots(nrows = 3, ncols = 2, figsize=(10, 9))
                fig.tight_layout()
                fig.suptitle('{}: All Data (No Time Filter)'.format(filter_city))
                
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
                
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()
                
                month_counts = df.groupby(['Month'])['Month'].count()
                month_counts.plot.bar(ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_xticklabels(tuple(MONTHS[:6]), rotation='vertical')
                axes[1, 0].set_title('Usage by Month')
                axes[1, 0].set_ylabel('Frequency')
        
                day_counts = df.groupby(['day_of_week'])['day_of_week'].count()
                day_counts.plot.bar(ax = axes[1, 1], color='#4682B4')
                axes[1, 1].set_xticklabels(tuple(DAYS), rotation='vertical')
                axes[1, 1].set_title('Usage by Week')
                axes[1, 1].set_xlabel('Day of Week')
                axes[1, 1].set_ylabel('Frequency')
        
                ages.plot.hist(bins = 15, ax = axes[2, 0], color='#4682B4')
                axes[2, 0].set_title('User Ages')
                axes[2, 0].set_xlabel('Age (years)')
                axes[2, 0].set_ylabel('Frequency')
        
                gender_breakdown.plot.bar(ax = axes[2, 1], color='#4682B4')
                axes[2, 1].set_title('Gender Breakdown')
                axes[2, 1].set_ylabel('Frequency')
        
                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=1.0)
                plt.show()
                
            elif filter_type == 'Month':
                fig, axes = plt.subplots(nrows = 3, ncols = 2, figsize=(10, 9))
                fig.tight_layout()
                fig.suptitle('{}: {} (All days)'.format(filter_city, filter_month))
                
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
                
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()
                
                day_counts = df.groupby(['day_of_week'])['day_of_week'].count()
                day_counts.plot.bar(ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_xticklabels(tuple(DAYS), rotation='vertical')
                axes[1, 0].set_title('Usage by Week ({})'.format(filter_month))
                axes[1, 0].set_xlabel('Day of Week')
                axes[1, 0].set_ylabel('Frequency')
                
                ages.plot.hist(bins = 15, ax = axes[1, 1], color='#4682B4')
                axes[1, 1].set_title('User Ages')
                axes[1, 1].set_xlabel('Age (years)')
                axes[1, 1].set_ylabel('Frequency')
                
                gender_breakdown.plot.bar(ax = axes[2, 0], color='#4682B4')
                axes[2, 0].set_title('Gender Breakdown')
                axes[2, 0].set_ylabel('Frequency')
                
                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=1.0)
                plt.show()
                
            elif filter_type == 'Day':
                fig, axes = plt.subplots(nrows = 3, ncols = 2, figsize=(10, 9))
                fig.tight_layout()
                fig.suptitle('{}: {} (All months)'.format(filter_city, filter_day))
                
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
            
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()
                
                month_counts = df.groupby(['Month'])['Month'].count()        
                month_counts.plot.bar(ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_xticklabels(tuple(MONTHS[:6]), rotation='vertical')
                axes[1, 0].set_title('Usage by Month ({}s)'.format(filter_day))
                axes[1, 0].set_ylabel('Frequency')
                
                ages.plot.hist(bins = 15, ax = axes[1, 1], color='#4682B4')
                axes[1, 1].set_title('User Ages')
                axes[1, 1].set_xlabel('Age (years)')
                axes[1, 1].set_ylabel('Frequency')
                
                gender_breakdown.plot.bar(ax = axes[2, 0], color='#4682B4')
                axes[2, 0].set_title('Gender Breakdown')
                axes[2, 0].set_ylabel('Frequency')
                
                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=1.0)
                plt.show()
                
        else:
            # Plot stuff for the Washington data
            hour_counts = df.groupby(['Start Hour'])['Start Hour'].count()
            
            trip_minutes = df[df['Trip Duration'] < 21600]
            trip_minutes['Trip Duration'] = trip_minutes['Trip Duration'] / 60
            bins = pd.cut(trip_minutes['Trip Duration'], [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360])
            trip_frequencies = trip_minutes['Trip Duration'].groupby(bins).agg(['count'])
            
            if filter_type == 'Both':
                fig, axes = plt.subplots(1, 2, figsize=(8, 4))
                fig.tight_layout()
                fig.suptitle('{}: {}s in {}'.format(filter_city, filter_day, filter_month))
                
                hour_counts.plot.bar(ax = axes[0], color='#4682B4')
                axes[0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0].set_title('Usage by Hour')
                axes[0].set_xlabel('Start Hour')
                axes[0].set_ylabel('Frequency')
                
                trip_frequencies.plot.bar(ax = axes[1], color='#4682B4')
                axes[1].set_title('Trip Duration Frequencies')
                axes[1].set_xlabel('Trip Duration (hour)')
                axes[1].set_ylabel('Frequency')
                axes[1].get_legend().remove()
                
                fig.subplots_adjust(bottom=0.1, top=0.85, wspace=0.25, hspace=0.7)
                plt.show()
                
            elif filter_type == 'None':
                fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(10, 9))
                fig.tight_layout()
                fig.suptitle('{}: All Data (No Time Filter)'.format(filter_city))
                
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
                
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()                
                
                month_counts = df.groupby(['Month'])['Month'].count()        
                month_counts.plot.bar(ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_xticklabels(tuple(MONTHS[:6]), rotation='vertical')
                axes[1, 0].set_title('Usage by Month')
                axes[1, 0].set_ylabel('Frequency')
        
                day_counts = df.groupby(['day_of_week'])['day_of_week'].count()
                day_counts.plot.bar(ax = axes[1, 1], color='#4682B4')
                axes[1, 1].set_xticklabels(tuple(DAYS), rotation='vertical')
                axes[1, 1].set_title('Usage by Week')
                axes[1, 1].set_xlabel('Day of Week')
                axes[1, 1].set_ylabel('Frequency')
                
                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=0.6)
                plt.show()
                
            elif filter_type == 'Month':
                fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(10, 9))     
                fig.tight_layout()
                fig.suptitle('{}: {} (All days)'.format(filter_city, filter_month))
                
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
                
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()
                
                day_counts = df.groupby(['day_of_week'])['day_of_week'].count()
                day_counts.plot.bar(ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_xticklabels(tuple(DAYS), rotation='vertical')
                axes[1, 0].set_title('Usage by Week')
                axes[1, 0].set_xlabel('Day of Week')
                axes[1, 0].set_ylabel('Frequency')
                
                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=0.5)
                plt.show()
                
            elif filter_type == 'Day':
                fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(10, 9))
                fig.tight_layout()
                fig.suptitle('{}: {} (All months)'.format(filter_city, filter_day))
            
                hour_counts.plot.bar(ax = axes[0, 0], color='#4682B4')
                axes[0, 0].set_xticklabels(tuple(HOURS), rotation='vertical')
                axes[0, 0].set_title('Usage by Hour')
                axes[0, 0].set_xlabel('Start Hour')
                axes[0, 0].set_ylabel('Frequency')
            
                trip_frequencies.plot.bar(ax = axes[0, 1], color='#4682B4')
                axes[0, 1].set_title('Trip Duration Frequencies')
                axes[0, 1].set_xlabel('Trip Duration (min)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].get_legend().remove()
                
                month_counts = df.groupby(['Month'])['Month'].count()        
                month_counts.plot.bar(ax = axes[1, 0], color='#4682B4')
                axes[1, 0].set_xticklabels(tuple(MONTHS[:6]), rotation='vertical')
                axes[1, 0].set_title('Usage by Month')
                axes[1, 0].set_ylabel('Frequency')

                fig.subplots_adjust(bottom=0.1, top=0.9, wspace=0.25, hspace=0.5)
                plt.show()
    except:
        print('Looks like matplotlib is not installed')
        
def printData(df):
    """
    Basic function to display 5 lines of the data
    Args:
        (df) df - pandas DataFrame filtered by user criteria
    Returns:
        N/A
    """
    indx = 0
    df.reset_index(drop=True, inplace=True)
    
    user_input = input('Would you like to display 5 lines of data (y/n)? ')
    user_input = user_input.upper()
    
    while user_input not in ['YES', 'Y', 'NO', 'N']:
        user_input = input('Please enter a valid option (y/n): ')
        user_input = user_input.upper()
    
    while user_input not in ['NO', 'N']:
        print('-' * SEPARATOR_WIDTH)
        print(df.loc[indx:(indx + 5), :])
        indx += 5
        
        user_input = input('Print 5 more lines (y/n)? ')
        user_input = user_input.upper()
        
        while user_input not in ['YES', 'Y', 'NO', 'N']:
            # Force an input similar to Yes or No
            user_input = input('Please enter a valid option (y/n): ')
            user_input = user_input.upper()

def main():
    """
    Main function handling overall control flow
    Args:
        N/A
    Returns:
        N/A
    """
    keep_on = True
    
    print('Howdy! Welcome to the US Bikeshare Data Analysis Program!')

    while keep_on:
    
        filter_city = getCityFilter()

        filter_type = getTypeFilter()
    
        filter_month, filter_day = getTimeFilter(filter_type)
        
        df, df_overdue, df_underage = load_data(filter_city, filter_month, filter_day)
        
        print('-' * SEPARATOR_WIDTH)
        print('Filter Summary:')
        print('Filter City:', filter_city)
        print('Filter Type:', filter_type)
        
        if filter_type.capitalize() == 'Both':
            print('Filter Time: {}, {}'.format(filter_month, filter_day))
        elif filter_type.capitalize() == 'None':
            print('Filter Time: All days')
        elif filter_type.capitalize() == 'Month':
            print('Filter Time: {} (All days)'.format(filter_month))
        elif filter_type.capitalize() == 'Day':
            print('Filter Time: {} (All months)'.format(filter_day))
        
        print('Data Points:', len(df))
    
        # Calculate Time Statistics
        popular_month, popular_day, popular_hour = time_stats(df, filter_type, filter_month, filter_day)
        print()
             
        # Calculate Station Statistics
        popular_start, popular_end, popular_combo = station_stats(df)
        
        # Calculate Trip Duration
        cummulative_trip, mean_trip, std_dev_trip, median_trip = trip_duration_stats(df, df_overdue)
        
        # Calculate User Demographic Statistics
        user_stats(df, df_underage, filter_city)
        
        plot_data(df, filter_city, filter_type, filter_month, filter_day)
        
        # Functionality to print out the raw data in 5 line increments
        printData(df)
        
        user_continue = input('Would you like to continue the program and filter by other values (y/n)? ')
        user_continue = user_continue.upper()
        
        while user_continue not in ['YES', 'Y', 'NO', 'N']:
            user_continue = input('Please enter a valid option (y/n): ')
            user_continue = user_continue.upper()
            
        if user_continue in ['YES', 'Y']:
            keep_on = True
        else:
            keep_on = False

main()
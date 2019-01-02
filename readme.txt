Explore US Bikeshare Data

bikeshare-MCW is a Python script used to explore US Bikeshare Data and output various statistics based on user input, and which city we are examining. 

Getting Started:

    Prerequisites:
        Python
        pandas

Questions answered:

    1) What is the most popular month? What is the most popular day? What is the most popular hour?

    2) What is the most popular start station? What is the most popular end station? What is the most popular        start-end station combination?

    3) What is the mean, standard deviation, and median of the trip durations? What is the max trip duration and        minimum trip duration?

    4a) What are the basic user demographics? What is the number of males compared with number of females? What is           age of the youngest and oldest user? How many users are under an age limit of 16?

     b) How long does a customer rent a bike compared with a subscriber in terms of mean and median? How many of         these users have rented a bike longer than 3 days?

     c) What is the gender breakdown of a customer compared with a subscriber? What is the mean, median, and                 standard deviations of age within both User Type and Gender? (Chicago and New York City only)

Notes and Assumptions:

1) Took out the months after July. There are a few data points in July

2) Used proper capitalization because the data show them with proper capitalization (e.g. Male and Female, not male and female)

3) Only dropped User Type NaNs. Users may chose to not provide Gender or Birth Year information

4) Filtered out anamalies in the Trip Duration  column. Limits are based on 4 minute (240 seconds) trip time and maximum of 3 days (259,200 seconds)

Assumes that all bikes can be rented out based on a 3 day pass

(Source: https://www.capitalbikeshare.com/pricing/day-passes)

5) Filtered out anamalies in the Age data if we're looking at Chicago or New York City (Not provided in Washington). The data show that for Chicago, most recent birth year is 2016 and earliest birth year is 1899 (Didn't know 1 year olds can rent bikes, and that vampires are interested in Bike Sharing programs). New York City data show most recent birth year is 2001 and earliest birth year is 1885.

Assumes that people can still bike near the end of a 100 year life span

Minimum age is 16, based on example terms of conditions

(Source: https://app.socialbicycles.com/networks/42/terms)

6) This program detects if there are multiple Start, End, or Start-End Station modes for a city. If so, it outputs all of them and the count

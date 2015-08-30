# What's in the code?

This is a proof-of-concept code, which was used in an open code challenge by Helen (www.helen.fi, https://www.helen.fi/challenge). As far as I know this code achieved the best monetary result, and found the optimum solution. This code however did not win the competition, because it is coded in Python and not in Matlab/Excel.

The aim of the competition was to find optimum charge and discharge times for a big battery energy storage system, which is connected to the grid. The code operates on the presumption, that prices of Nord Pool Spot's ELSPOT (day-ahead-market) is also available in ELBAS for the battery operated system.

It should be mentioned, that the 2014 price data of FI area differs on two lines of the actual market data, because the code does not take summer saving time into account. Hence small modifications were done to price data. Results are also included for the normal data.

This was first time that I used recursion algorithm on a non trivial code. Pretty cool :).


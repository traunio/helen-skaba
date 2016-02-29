# Copyright (c) 2015: Tapani Raunio

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

###########################
##
##  Tested with python 3.4.2
##  To use in Python interactive mode: 
##	>>> import helen_skaba
## 	>>> events=helen_skaba.yearlyProfit()
##
##  Then data in inputname file is read and output is written to outputname file
##  
##
############################



# global variables
diff=0.7 # 80 % of original charge is retained. sell_price*diff must be greater than buy_price
bess_cap=1 # MWh
bess_init_price=0 # Price of the initial charge of BESS
inputname='elspot_2014_fi.txt' 
outputname='results_2014_fi.txt'

import copy

# Example optimization class. This is not used in the code at all.
class DumbOptimize():

	# Function calculates single buy and single sell
	# Variables:
	# time - price list
	# returns dictionary with buy and sell orders
	def bess_empty(self,time): # BESS is emtpy
		
		money=[]
		for i in range(len(time)-1):
			sell_p=max(time[i+1:])
			buy_p=time[i]
			
			if sell_p*diff>buy_p: # price difference must be good enough
				money.append(sell_p-buy_p)
			else:
				money.append(0)

		# there is no money to be made
		if max(money)==0:
			return {}
		buytime=money.index(max(money))   # Finding the optimal charging hour
		selltime=time.index(max(time[buytime+1:])) # And checking the discharging time
		
		return {buytime:selltime}

	# Function for single charge, but BESS is full in start	
	# Only best sell time is searched
	def bess_full(self,time, price):
		
		sell_p=max(time)
		
		if sell_p*diff > price:
			return {-1:time.index(sell_p)}
		else:
			print("No sell time found",price,time)
			return {} # no sell time found, we return empty dictionary.


# Function does not work with smaller than 2 time lengths
# Function's sole purpose is to find the maxima and minima within given prices
# Returns maxima and minima indices, type [int],[int]
# This function could be further developed a bit. Now it picks always the 
# first price as minimum even if the next value in the vector is equal.
def peak(prices):
	# finding local maxs and mins
	maxs=[]
	mins=[]
	
	if len(prices)<2:
		return [],[]
	
	first=True
		
	for i in range(len(prices)-1):
		if first:
			if prices[i+1]>prices[i]:
				mins.append(i)				
			elif prices[i+1]<prices[i]:
				maxs.append(i)
			else:
				k=i+1 
				# we need the while loop, if there are one or more identical values in the vector
				while prices[i]==prices[k] and k+1<len(prices):
					k+=1
				if k+1>len(prices):
					break	# prices is flat till the end
				if prices[k]>prices[i]:
					mins.append(i)
				else:
					maxs.append(i)
			first=False
		else:
		
			if prices[i-1]<prices[i] and prices[i]>prices[i+1]:
				maxs.append(i)
			elif prices[i-1]<prices[i] and prices[i]==prices[i+1]:
				k=i+1
				while prices[i]==prices[k] and k+1<len(prices):
					k+=1
				if prices[k]<=prices[i]:
					maxs.append(i)
			elif prices[i-1]>prices[i] and prices[i]<prices[i+1]:
				mins.append(i)
			elif prices[i-1]>prices[i] and prices[i]==prices[i+1]:
				k=i+1
				while prices[i]==prices[k] and k+1<len(prices):
					k+=1
				if prices[k]>=prices[i]:
					mins.append(i)
	
	# finally we check the end
	
	if prices[-1]>prices[-2]:
		maxs.append(len(prices)-1)
	elif prices[-1]<prices[-2]:
		mins.append(len(prices)-1)
	
	return maxs,mins
	

## This class handles the optimization. Algorithm uses brute force,
## so it will start to slow down with too big junks of prices
## It probably could be improved by implementing lookup table, but is currenty
## fast enough.
## Although the algorithm is sound, I give no guarantees, that value calculation 
## is correct
class Optimize():

	# def __init__(self,prices):
		# self.prices=prices
		
	# ##input options includes the possible buys and sells in dictionary {int:[int]}
	def recursive(self,options):
		
		# This is for debugging. We should not end up here
		if len(options)==0: # if there are no option, so path and profit are zero
			print("For some reason, there were no options. Probably a bug")
			print("Prices are",self.prices)
			return {},0
		
		if len(options)==1: # only one buy option left. Next find out the best sell price.
			buy_p,sell_p=options.popitem()
			bestprice=[]
			
			for a in sell_p:
				bestprice.append(diff*self.prices[a]-self.prices[buy_p])
			
			
			return {buy_p:sell_p[bestprice.index(max(bestprice))]},max(bestprice)
				
		# Next calculate other possibilities. There are at least two possible buy moments
		firstkey=sorted(options.keys())[0]
		sell_ops=options[firstkey]
		values=[]
		paths=[]
		
		for a in sell_ops:
			
			new_opts=copy.deepcopy(options)
			# remove buying options, when we buy at 'firstkey' and sell at 'a'
			del new_opts[firstkey]
			removes=[]
			for b in new_opts.keys():
				if b<a:
					removes.append(b)
			for b in removes:
				del new_opts[b]
						
			# calculating the value of all available sell_ops
			if len(new_opts)==0: # 
				values.append(diff*self.prices[a]-self.prices[firstkey])
				paths.append({})
			else:
				# Here we use recursion to find out the optimal path
				temppath,temp=self.recursive(new_opts)
				temp+=diff*self.prices[a]-self.prices[firstkey]
				values.append(temp)
				paths.append(temppath)									
			
		# finally we calculate the option of not buying in this minimum
		new_opts=copy.deepcopy(options)
		del new_opts[firstkey]
		temppath,nobuy=self.recursive(new_opts)
		# print("Option no buy",firstkey,". Value:",nobuy)
		
		if nobuy>=max(values): 		
			return temppath,nobuy # buying is not optimal
		else:				
			# we check the optimal path and return items
			best_sell=values.index(max(values))
			best_path=paths[best_sell]
			best_path[firstkey]=sell_ops[best_sell]
			
			return best_path,values[best_sell]
				
	# This algorithm finds the optimal buying and selling times with given pricess
	# Note, algorithm does not buy, if a selling point is not known
	# Sell_price*diff must be greater than buy_price	
	# Return optimal buy and sell indices. Return type is a dictionary, 
	# with key being buy time, and value the sell-time, i.e. {int:int}	
	def bess_empty(self,prices): #BESS is empty

		maxs,mins=peak(prices) # finding the peaks and bottoms
		# print("Maxs",maxs,"Mins",mins) # for debugging
		
		if len(mins)==0 or len(maxs)==0:
			return {} # we cannot buy and sell
			
		# if maxs[0]<mins[0]:
			# maxs.pop(0) # we don't care for the first max, because bess is empty
			# if len(maxs)==0:
				# return {}  # we cannot buy and sell
		
		if mins[-1]>maxs[-1]: # we don't care for the last min
			mins.pop()		# this is also needed for prices[a+1:] reference to work
		
		# here we check for valid buy prices, with the possibility to make money	
		validmins=[] 
		validmaxs=[]

		for a in mins:
			if prices[a]<diff*max(prices[a+1:]):
				validmins.append(a)
				temp=[]
				
				for b in maxs:
					if prices[a]<diff*prices[b] and b>a:
						temp.append(b)
				
				validmaxs.append(temp)		

		if len(validmins)==0 or len(validmaxs)==0:
			return {} # we cannot buy and sell
		
		# next we create a dictionary with possible sell prices
		sell_mat=dict(zip(validmins,validmaxs))
		
		# debug code
		# print("Validmaxs",validmaxs)
		# print("Validmins",validmins)
		# print("Dict",sell_mat)
				
		self.prices=prices
		result,profit=self.recursive(sell_mat)
		# print("With path",result,"profits are",profit)
		return result # we return the optimal path

	## BESS if full in the beginning with 'price'
	## This is for situation, when next day prices are known.
	## Takes prices (list) and charge price as argument and return the optimal
	## buys and sells. The first buy index is -1, meaning that BESS is full already
	## Return type: {int:int}
	def bess_full(self,prices,price): 

		shift=4000 # this is an artifical price, for first buy. 

		# we create an artificial negative price, in order to ensure
		# our optimization recursion buys at 0. This shifts also all the price
		# indices forward, so we have to correct this in the end
		prices.insert(0,-shift)
		maxs,mins=peak(prices) # finding the peaks and bottoms
		
		if len(mins)==0 or len(maxs)==0: # there are no price differences
			return {} # we cannot buy and sell
				
		# we don't care for the last min, if there is no max afterwards, 
		# because we don't buy blindly 
		if mins[-1]>maxs[-1]: 
			mins.pop()
		
		# here we check for valid buy prices, with the possibility to make money	
		validmins=[0]  # the index, when bess was full. We insert it here, 
		validmaxs=[]
		
		mins.pop(0) # we remove zero, because it is separately checked for validmins

		
		# here we filter the possible maxima for our artificial minimum
		# Note these are defined with real prices
		temp=[]
		for b in maxs:
			if price<diff*prices[b]:
				temp.append(b)
				
		
		validmaxs.append(temp)
			
		for a in mins:
			if prices[a]<diff*max(prices[a+1:]):
				validmins.append(a)
				temp=[]
				
				for b in maxs:
					if prices[a]<diff*prices[b] and b>a:
						temp.append(b)
				
				validmaxs.append(temp)
			
			
		# next we create a dictionary with possible buy and sell prices
		sell_mat=dict(zip(validmins,validmaxs))
				
		self.prices=prices
		valuepath,profit=self.recursive(sell_mat) # recursing the reulst

		# Finally we correct the buy and sell indices. If the code fails here,
		# there is a failure in the optimization. Increasing "shift" should help.
		del prices[0]
		truepath={}	
		truepath[-1]=valuepath[0]-1
		del valuepath [0]
		for k in sorted(valuepath.keys()):
			v=valuepath[k]
			truepath[k-1]=v-1
		
		# debug
		# print("Real profit is",profit-price-shift,"Optimal path:",truepath)
		return truepath # we return the optimal path	
		

		
## This helper function calculates the profit, buying and selling and cycles.
## The used optimization algorithm are in class Optimize(). Example of another 
## and dumb algorithm is in class DumbOptimize().
## This function returns buy and sell events.
def yearlyProfit():
	# price data is in file called inputname (defined in the global parameters
	
	vuosi=open(inputname,'r')
	dates=[]
	prices=[]

	vuosi.readline()
		
	for a in vuosi:
		line=a.split()
		if len(line)<1:
			continue
		dates.append("%s %s" % (line[0],line[1]))
		
		## Sadly this is needed. Nordpoolspot has couple data points, which
		## must be edited for the function to work
		try:
			value=float(line[-1].strip())
		except ValueError:
			print("Problem with data. Not a valid value at",dates[-1])			
			return []
		prices.append(float(line[-1].strip()))
	
	vuosi.close()

	# we'll make a sanity test here for the data.
	# if the data does not include all hours, the new spot prices available
	# at 12.42 CET does not function correctly.
	# If the provided data does not have exactly 24 lines for each day
	# the optimization is called 
	settis={x.split()[-1] for x in dates[::24]}
	if len(settis)>1: 
		print("There is a mismatch in data")
		findit=[x.split()[-1] for x in dates[::24]]
		results=dates[::24]
		for i in range(len(findit)-1):
			if findit[i]!=findit[i+1]:
				print("Mismatch",results[i],results[i+1])
	
	# first 24 h	
	timedata=prices[:24]
	headers=dates[:24]
	del prices[:24]
	del dates[:24]
	bess_full=True 	# Here we presume, that BESS is full in the beginning
	bess_price=bess_init_price # price of the first charge
	profit=0.0
	firstRound=True
	
	cycles=0
	events=[] # mostly for debugging purposes
	
	# The optimization algorith is in class Optimize. Also other implementation
	# are possible, such as DumbOptimize(), which is provided as an example.
	algo=Optimize() 
	
	while len(timedata)>0:
	
		if bess_full:			
			dik=algo.bess_full(timedata,bess_price)
			if -1 not in dik: # for debugging
				print("Algorithm has failed with BESS full. Problem with",dates[0])				
		else:
			dik=algo.bess_empty(timedata)
		
		if firstRound:
			inittime=0
			firstRound=False
		else:
			inittime=-11 # prices are usually from 13.00 CET to next day's midnight
			
		# For debugging purposes
		# print(headers[0],headers[-1])
		# print(dik,inittime)	
		
		# processing buy&sell orders until 13.00 CET
		for k in sorted(dik.keys()):
			v=dik[k]
		
			# processing buy/sell orders until 13.00 CET
			if k>=0 and k+inittime<13: # if k==-1, the buying has already been processed
				events.append("Buy order %s. Price: %f" % (headers[k],timedata[k]))
				if bess_full: #debug code. Bess should not be full
					print("We try to buy, even though BESS is charged",headers[k])
					print("Last events:",events[-2:]) 
					print("Dikkis:",dik)
					print("Dates",headers[0],headers[-1])
					print("Prices",timedata,bess_price)
					
				
				bess_full=True
				bess_price=timedata[k]
						
	
			if v+inittime<13:
				events.append("Sell order %s. Price: %f" % (headers[v],timedata[v]))
				# print(events[-1])
				cycles+=1
				profit+=(timedata[v]*diff-bess_price)*bess_cap
				
				if bess_full!=True :	# debug code
					print("We try to sell, even though BESS is empty",headers[k])
					print("Last events:",events[-2:]) 
					print("Dikkis:",dik)
					print("Dates",headers[0],headers[-1])
					print("Prices",timedata,bess_price)
				
				bess_full=False
				bess_price=0
			
		# updating timedata		
		if len(prices)>=24:
			timedata=timedata[-11:] + prices[:24]
			headers=headers[-11:]+ dates[:24]
			inittime=-11
			del prices[:24]
			del dates[:24]
		elif len(prices)==0:
			
				
			# We'll process the last trades
			for k in sorted(dik.keys()):
				v=dik[k]
				
				# processing buy/sell orders until 13.00 CET
				if k+inittime>=13:
					events.append("Last buy order %s. Price: %f" % (headers[k],timedata[k]))
					
					if bess_full: # debug code
						print("We try to last buy, even though BESS is charged", headers[k])
					
					bess_full=True
					bess_price=timedata[k]					
		
				if v+inittime>=13:
					events.append("Last sell order %s. Price: %f" % (headers[v],timedata[v]))
					cycles+=1
					profit+=(timedata[v]*diff-bess_price)*bess_cap
					
					
					if bess_full!=True :	# debug code
						print("We try to last buy, even though BESS is charged",headers[k])
					
					bess_full=False
					bess_price=0	
			del timedata[:]
		else: # this part is not tested. Should work, I suppose
			timedata=timedata[-11:] + prices[:]
			headers=headers[-11:]+ dates[:]			
			del prices[:]
			del dates[:]

	output=open(outputname,'w') # we open file for result writing
	output.write("Profit made %s\n" % profit)
	output.write("Total cycles %s\n\n" % cycles)
	for line in events:
		output.write("%s\n" % line)
				
	output.close()
	print("Profit made", profit)
	print("Cycles ", cycles)
	return events


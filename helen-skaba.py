# Pohdintaa Helenin skabasta:
# - Skaban idea on käyttää spottihintatietoja maksimoida tuloja.
# - Huutokaupalla ja vastaavalla ei ole oikeastaan mitään väliä? Ehkä
# - Joten homma on puhdasta optimointia oston ja myynnin suhteen.

# global variables
diff=1.2 # at least 20 % price difference between buying (charging) and selling (loading)



# Algorithm finds one charging hour and one discharging hour
# Variables:
# time - known price list
# returns dictionary with buy and sell orders
def singlecharge(time): # BESS is emtpy
	
	money=[]
	for i in range(len(time)-1):
		sell_p=max(time[i+1:])
		buy_p=time[i]
		
		if sell_p>diff*buy_p:
			money.append(sell_p-buy_p)
		else:
			money.append(0)
			
	buytime=money.index(max(money))
	selltime=time.index(max(time[buytime+1:]))
	
	return {buytimes:selltime}
	
	

	
	
	
	
	

	


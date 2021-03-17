import numpy as np
import matplotlib.animation as ani
import matplotlib.pyplot as plt 

# colors:
RED = (0.96, 0.10, 0.10) #infected
GREEN = (0, 0.86, 0) #mild recovered
BLACK = (0, 0, 0)     #dead
GREY = (0.78, 0.78, 0.78)  #uninfected
BLUE = (0,0,0.86)
GREENBLUE = (0,0.86,0.86) #severe recovered

#PARAMETERS FOR ANY VIRUS--->
COVID19_PARAMS = {
  "r0" : 2.28, #number of infections one person can spread
  "incubation" : 5, #incubation period
  "percent_mild" : 0.8, #per of population with mild symp
  "mild_recovery" : (7,14), #range of days for slow or fast mild recovery
  "percent_severe" : 0.2,
  "severe_recovery" : (21,42),
  "severe_death" : (14,56), #range of days for slow or fast death from severe symptoms
  "fatality_rate" : 0.034, #per of population with death as outcome from severe symp
  "serial_interval" : 5 #interval between consevutive waves of the spread of virus
}

class Virus():
  def __init__(self,params):
    #create disk plot
    self.fig = plt.figure()
    self.axes = self.fig.add_subplot(111,projection = "polar")    #disk polar coordinate wise 1by 1 grid: 111
    self.axes.grid(False)   #remove gridpoints and ticks
    self.axes.set_xticklabels([])
    self.axes.set_yticklabels([])
    self.axes.set_ylim(0,1) #radius of whole plot  = 1

    #annotate
    self.day_txt = self.axes.annotate(
      "DAY : 0", xy = [np.pi *0.5,1], ha = 'center', va = 'bottom'  #fig is at bottom of text
    )
    self.infected_txt = self.axes.annotate(
      "INFECTED : 0", xy = [3 * np.pi *0.5,1], ha = 'center', va = 'top', color = RED #fig is at top of text
    )
    self.dead_txt = self.axes.annotate(
      "\nDEAD : 0", xy = [3 * np.pi *0.5,1], ha = 'center', va = 'top', color = BLACK
    )
    self.recovered_txt = self.axes.annotate(
      "\n\nRECOVERED : 0", xy = [3 * np.pi *0.5,1], ha = 'center', va = 'top',color = GREENBLUE
    )

    #creating variables:
    self.days = 0
    self.total_infected = 0
    self.current_infected = 0
    self.ndead = 0
    self.nrecovered = 0
    self.nsevererecovered =0
    #initializing parameters from give virus dictionary
    self.r0 = params["r0"]
    #percentage mild and severe symptomss:
    self.percentmild = params["percent_mild"]
    self.percentsevere = params["percent_severe"]
    #number of days for recovery or death in each case: 
    self.mildfast = params["mild_recovery"][0] + params["incubation"]
    self.mildslow = params["mild_recovery"][1] + params["incubation"]
    self.severefast = params["severe_recovery"][0] + params["incubation"]
    self.severeslow = params["severe_recovery"][1] + params["incubation"]
    self.deathfast = params["severe_death"][0] + params["incubation"]
    self.deathslow = params["severe_death"][1] + params["incubation"]

    #percentage fatal symptoms and interval between consecutive waves of virus spread:
    self.fatalityrate = params["fatality_rate"]
    self.serialinterval = params["serial_interval"]

    #dictionary containing mild recovery indiviuals cases for an year span:
    #dictionary comprehension:
    self.mild = {i: {"thetas": [],"rs":[]} for i in range(self.mildfast,365)}
    #here 2 dict within the severe recovery and severe death individual cases for an year span: 
    self.severe = {
    "recovery":{i: {"thetas": [], "rs": []} for i in range(self.severefast,365)},
    "death":{i: {"thetas": [], "rs": []} for i in range(self.deathfast,365)}
    }

    #regarding the waves of virus spread num of ppl exposed berfore and after a given wave:
    self.exposedbefore = 0
    self.exposedafter = 1
    
    #calls the first case of virus in a given population
    self.initial_population()

  def initial_population(self):
    population = 4500
    #initializes the fist case of virus:
    self.current_infected = 1
    self.total_infected = 1
      
    #creates population individuals and assigns them their spots on the disk with rs,theta as coordinates,
    #and indice for specifying the individual
    #all 3 are numpy arrays (lists)
    self.indices = np.arange(0,population) +0.5
    self.rs = np.sqrt(self.indices/population)
    self.thetas = np.pi * (1 + 5**0.5) * self.indices

    #plots the dots on the disk with initial grey color uninfected
    self.plot = self.axes.scatter(self.thetas,self.rs,s =5, color = GREY)
    #colors the fist case dot as red infected
    self.plot = self.axes.scatter(self.thetas[0],self.rs[0],s =5, color = RED)
    #stores his record in the mild recovery dict with mildfast recovery (theta and radius)
    self.mild[self.mildfast]["thetas"].append(self.thetas[0])
    self.mild[self.mildfast]["rs"].append(self.rs[0])

  #now we spread the virus when the given interval comes:
  #THIS IS A GENERATOR FUNCTION!!!----------------------------
  def spreadvirus(self,i):
    population = 4500
    self.exposedbefore = self.exposedafter

    if self.days % self.serialinterval == 0 and self.exposedbefore < population:
      self.new_num_infected = round(self.r0 * self.total_infected)
      self.exposedafter += round(self.new_num_infected * 1.1)  #10% ppl extra who arent contracted by the virus at all
      if self.exposedafter > population:
        self.new_num_infected = round((population - self.exposedbefore) *0.9)
        self.exposedafter = population

      #add the newly infected ppl to the data:
      self.current_infected += self.new_num_infected
      self.total_infected += self.new_num_infected

      #assign these new num infected to random indiviuals:
      self.new_infected_indices = list(
        np.random.choice(
          range(self.exposedbefore, self.exposedafter), size = self.new_num_infected, replace = False)
      )
      #assigning variable thetas and rs with values from the self thetas and self rs list created for disk population
      thetas = [self.thetas[i] for i in self.new_infected_indices]
      rs = [self.rs[i] for i in self.new_infected_indices]

      #plot the red color before assigning symptoms and recovery day:
      if len(self.new_infected_indices) :
        self.axes.scatter(thetas,rs,s=5,color= RED)

      #assign symptoms to the ppl: (INSIDE THE IF CONDITION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
      self.assignsymptoms()

    #day is incremented:(inside the function only this line of code)
    self.days +=1

    self.updatevalues()
    self.update_text()
    #end of function-------------------

  def assignsymptoms(self):
    #now mild and severe cases for the newly infected people:
    num_mild_cases = round(self.percentmild * self.new_num_infected)
    num_severe_cases = round(self.percentsevere * self.new_num_infected)

    #random choose set of indices from newly infected indicies that gets assigned mild and severe symptoms respectively
    #this is the outcome list
    self.mild_indices = np.random.choice(
      self.new_infected_indices, num_mild_cases, replace = False
    )      
      
    #now left over indices fall in two categories, first collect the left over indices
    remaining_indices = [
      i for i in self.new_infected_indices if i not in self.mild_indices
    ]

    #now we assign people who get severe recovery  or die from the remaining indices
    #percentage of people who recover are:
    percent_severe_recovery = 1 - self.fatalityrate / self.percentsevere

    #these asrethe severe recoverd people from remaining indices:
    num_severe_recovery = round(percent_severe_recovery * num_severe_cases)

    #these are the two outcome lists
    self.severe_indices = []
    self.death_indices = []
    if remaining_indices:
      self.severe_indices = np.random.choice(
        remaining_indices, num_severe_recovery, replace = False
      )
      self.death_indices = [
        i for i in remaining_indices if i not in self.severe_indices
      ]

    #now we need to assign the exact day the outcome appears for the 3 lists (mild_indices,severe, death):
    #for mild lower and upper bounds
    low = self.days + self.mildfast
    high = self.days + self.mildslow

    #now 3 loops respectively:
    #loop over mild indices and assign random recovery day:
    for m in self.mild_indices:
      recovery_day =  np.random.randint(low,high)
      m_thetas = self.thetas[m]
      m_rs = self.rs[m]
      #update self.mild dict with thte info:
      self.mild[recovery_day]["thetas"].append(m_thetas)
      self.mild[recovery_day]["rs"].append(m_rs)

    low = self.days + self.severefast
    high = self.days + self.severeslow
    for s in self.severe_indices:
      recovery_day =  np.random.randint(low,high)
      s_thetas = self.thetas[s]
      s_rs = self.rs[s]
      self.severe["recovery"][recovery_day]["thetas"].append(s_thetas)
      self.severe["recovery"][recovery_day]["rs"].append(s_rs)
      
    low = self.days + self.deathfast
    high = self.days + self.deathslow
    for d in self.death_indices:
      d_day =  np.random.randint(low,high)
      d_thetas = self.thetas[d]
      d_rs = self.rs[d]
      self.severe["death"][d_day]["thetas"].append(d_thetas)
      self.severe["death"][d_day]["rs"].append(d_rs)
    #end of funciton------------------------------------------------

  def updatevalues(self): 
    #for mild,severe recovery and deaths:
    if self.days >= self.mildfast:
      #store the thetas and rs for mild cases in below variables to plot them simply on the plot
      thetas = self.mild[self.days]["thetas"]
      rs = self.mild[self.days]["rs"]      
      self.axes.scatter(thetas,rs,s =5,color = GREEN)
      self.nrecovered += len(thetas)
      self.current_infected -= len(thetas)

    if self.days >= self.severefast:
      thetas = self.severe["recovery"][self.days]["thetas"]
      rs = self.severe["recovery"][self.days]["rs"]      
      self.axes.scatter(thetas,rs,s =5,color = BLUE)
      self.nsevererecovered += len(thetas)
      self.current_infected -= len(thetas)

    if self.days >= self.deathfast:
      thetas = self.severe["death"][self.days]["thetas"]
      rs = self.severe["death"][self.days]["rs"]      
      self.axes.scatter(thetas,rs,s =5,color = BLACK)
      self.ndead += len(thetas)
      self.current_infected -= len(thetas)
    #end of function----------------------------------------------
  
  def update_text(self):
    self.day_txt.set_text("DAY : {}".format(self.days))
    self.infected_txt.set_text("INFECTED : {}".format(self.current_infected))
    self.dead_txt.set_text("\nDEAD : {}".format(self.ndead))
    self.recovered_txt.set_text("\n\nMILD_RECOVERED : {} SEVERE_RECOVERED : {}".format(self.nrecovered,self.nsevererecovered))
    #end of function-----------------------------------------

  #generator func:
  def gen(self):
    while self.ndead + self.nrecovered  + self.nsevererecovered < self.total_infected:
      yield

  def animateplot(self):
    self.anim = ani.FuncAnimation(
      self.fig,
      self.spreadvirus, #generator func
      frames= self.gen, #argument for spread virus (no. of times its going to be called 'i')
      repeat = True,
      interval =50
    )

#calls the funciton
def main():
  coronavirus = Virus(COVID19_PARAMS)
  coronavirus.animateplot()
  plt.show()

if __name__ == "__main__":
  main()
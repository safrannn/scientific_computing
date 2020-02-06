import numpy as np
import matplotlib.pyplot as plt
import random as random

class Dataset(object):
    def __init__(self):
        # tera-byte types
        self.package_type = [1,2,3,4]
        # price per package transmission in $
        self.package_price = [210,350,400,500]
        # time needed to send the package type according to the respective package
        self.package_timeTransmission = [1,3,5,10]
        # country listed
        self.country = ["USA","China","Germany","Japan","Switzerland"]
        # total hours
        self.total_hours = 48


class Package(object):
    def __init__(self,package_type = 0,package_time = 0, country_name = ""):
        # import dataset
        self.data = Dataset()
        
        # initialize parameters
        self.package_type = self.data.package_type[random.randrange(4)]
        self.package_time = self.data.package_timeTransmission[self.package_type - 1]
        self.package_price = self.data.package_price[self.package_type - 1]
        
        self.country_number = random.randrange(5)
        self.country_name = self.data.country[self.country_number]


class Satellite(object):
    def __init__(self):
        # import dataset
        self.data = Dataset()
        # add simulatoin parameters
        self.channel1 = Package()
        self.channel2 = Package()
        self.channel1_activation = []
        self.channel2_activation = []
        for i in range(49):
            self.channel1_activation.append(0)
            self.channel2_activation.append(0)
        
        self.queue = []
        self.total_hour_left = self.data.total_hours
        self.total_price = 0
        self.country_hours = [0,0,0,0,0]
       
    def channel_init(self):
        #add first channel
        self.channel1.__init__()
        self.total_price += self.channel1.package_price
        self.country_hours[self.channel1.country_number] += self.channel1.package_time
        #add a second channel
        self.channel2.__init__()
        while self.channel1.country_number == self.channel2.country_number:
            self.channel2.__init__()
        self.total_price += self.channel2.package_price
        self.country_hours[self.channel2.country_number] += self.channel2.package_time
        
        self.queue_append()
        
    # update package time of two channels
    # if one is below zero, fetch a new package from the queue
    def channel_check(self):
        self.channel1_activation[48-self.total_hour_left] += self.channel1.country_number
        self.channel2_activation[48-self.total_hour_left] += self.channel2.country_number
        self.channel1.package_time -= 1
        self.channel2.package_time -= 1
        
        if len(self.queue) < 1:
            return
        
        i = 0
        while i < len(self.queue) and (self.channel1.package_time == -1 or self.channel2.package_time == -1):
            
            new_package = self.queue[i]
            
            # if the package time is larger than timeLimit, continue
            if new_package.package_time > self.total_hour_left:
                i += 1
                continue
            
            # add package in queue to channels
            if self.channel1.package_time == -1 and self.channel2.package_time == -1:
                self.channel1 = new_package
            elif self.channel1.package_time == -1 and new_package.country_number != self.channel2.country_number:
                self.channel1 = new_package  
            elif self.channel2.package_time == -1 and new_package.country_number != self.channel1.country_number:
                self.channel2 = new_package
            else:
                i += 1
                continue
  
            self.total_price += new_package.package_price
            self.country_hours[new_package.country_number] += new_package.package_time
            self.queue.remove(self.queue[i])
                           
    # create a randomized new package and append it to queue
    def queue_append(self):
        new_package = Package()
        new_package.__init__()
        self.queue.append(new_package)
    
    def simulate(self):
        result = open("P02_output.txt", 'w')
        print("Simulation Start:\n")
        self.channel_init()
        while self.total_hour_left >= 0:
            self.queue_append()
            result.write("Current hour: %d\n" % (48 - self.total_hour_left))
            result.write("\tChannel: 1, country: %s, package type: %d, time remaining: %d\n" % (self.channel1.country_name,self.channel1.package_type, self.channel1.package_time))
            result.write("\tChannel: 2, country: %s, package type: %d, time remaining: %d\n" % (self.channel2.country_name,self.channel2.package_type, self.channel2.package_time))
            self.channel_check()
            self.total_hour_left -= 1
        result.write("\n\n")
        for country, hour in zip(self.data.country, self.country_hours):
            result.write("Transmission time of %s is %d hours.\n"%(country,hour))
        result.write("\n\nThe company earns $%d during this 48 hours."%(self.total_price))
        result.close()
        
    def plot_graph(self):
        # plot total hours
        plt.bar(self.data.country, self.country_hours)
        for x,y,s in zip(self.data.country,self.country_hours,self.country_hours):
            plt.text(x,y, s)
        plt.xlabel("Country")
        plt.ylabel("Hours")
        plt.title("Satellite simulation total price: $%d"%(self.total_price))
        plt.show()
        #plot activation graph
        time = []
        for i in range(49):
            time.append(i)
        plt.step(time,self.channel1_activation,label='channel 1')
        #plt.plot(time,self.channel1_activation,'C0-', alpha=1)
        plt.step(time,self.channel2_activation,label='channel 2')
        #plt.plot(time,self.channel2_activation,'C1-', alpha=1)
        plt.yticks(np.arange(5), self.data.country) 
        plt.show()

        
    def API(self):
        self.__init__()
        self.simulate()
        self.plot_graph()

def main():
    obj1 = Satellite()
    obj1.API()

if __name__ == '__main__':
    main()


        
            
        
        
















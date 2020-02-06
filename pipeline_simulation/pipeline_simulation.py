import numpy as np
import random as random
import copy
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

# constants
pump_count = 16 # gallon
tank_count = 16
pipeline_capacity = 200

# for optimization
duration = 48 # hours
mc_try = 500

tank_weight = 15
pump_weight = 1
switch_weight = 0.15

tank_target = 50
pipeline_target = 160


def init_normal(mean, std, count):
    array = np.random.normal(mean, std, count)
    for i in range(count):
        array[i] = int(round(array[i]))
    return array


class Simulation(object):
    def __init__(self):
        self.tank_level = init_normal(40, 10, tank_count)
        self.pump_volume = init_normal(12, 2, pump_count)

    def tank_update(self, level):
        input_hourly = init_normal(10, 3, tank_count)
        for i in range(tank_count):
            level[i] += input_hourly[i]
        return level

    def pump_update(self):
        self.pump_volume = init_normal(12, 2, pump_count)

    def simulate(self, threshold, interval):
        # initiate values of current simulation
        tank_level = copy.deepcopy(self.tank_level)
        tank_levels = tank_level
        tank_high_count = 0
        tank_low_count = 0
        pump_status = [False] * pump_count
        pipeline_volumes = [0]
        switch_count = 0
        time = 0

        # start simulation process
        while time < 48:
            # pour oil into tank
            tank_level = self.tank_update(tank_level)
            self.pump_update()

            # decide whether to turn on or off the pump for each tank
            pipeline_volume_current = 0
            sorted_index = np.argsort(tank_level)
            i = tank_count - 1

            if tank_level[sorted_index[0]] > 100:
                return -1

            while i >= 0:
                # tank_level[sorted_index[i]] is the current tank level
                index_i = sorted_index[i]
                pump_status_temp = pump_status[index_i]

                if i % interval == 0:
                    # turn off the pump if sum of pump capacity over pipeline capacity
                    if pipeline_volume_current + self.pump_volume[index_i] >= pipeline_capacity:
                        pump_status[index_i] = False
                    # turn on pump if tank level over threshold
                    elif tank_level[index_i] >= threshold:
                        pump_status[index_i] = True
                        tank_level[index_i] -= self.pump_volume[index_i]
                        pipeline_volume_current += self.pump_volume[index_i]
                    # turn off pump if below threshold
                    else:
                        pump_status[index_i] = False

                    if pump_status_temp ^ pump_status[index_i]:
                        switch_count += 1
                else:
                    if pump_status[index_i]:
                        tank_level[index_i] -= self.pump_volume[index_i]
                        pipeline_volume_current += self.pump_volume[index_i]
                tank_levels = np.append(tank_levels, tank_level[index_i])
                if tank_level[index_i] > 57:
                    tank_high_count += (tank_level[index_i] - 57)
                elif tank_level[index_i] < 40:
                    tank_low_count += (40 - tank_level[index_i])
                i -= 1

            pipeline_volumes = np.append(pipeline_volumes, pipeline_volume_current)
            time += 1

        # find out the loss function value
        tank_std = np.std(tank_levels)
        tank_err = abs(np.mean(tank_levels) - tank_target)
        tank_extreme = tank_high_count + tank_low_count
        eval_tank = (tank_std + tank_err * 10 + tank_extreme) * tank_weight / 10

        pump_std = np.std(pipeline_volumes)
        pump_err = abs(np.mean(pipeline_volumes) - pipeline_target)
        eval_pump = (pump_std + pump_err) * pump_weight

        eval_switch = switch_count * switch_weight

        evaluation = eval_tank + eval_pump + eval_switch

        return evaluation

    def mcmc(self):
        x = 50
        interval = 1
        evaluation = self.simulate(x, interval)

        x_best = x
        interval_best = interval
        evaluation_best = float("inf")

        for i in range(3000):
            # generate a candidate x from the pool
            x_candidate = x + random.uniform(-3, 3)
            interval_candidate = 1
            while interval_candidate == 0:
                interval_candidate = abs(interval + random.randrange(-1, 2))

            evaluation_new = self.simulate(x_candidate, interval_candidate)

            # calculate expect ratio
            alpha = evaluation / evaluation_new
            if alpha > 1:
                x_best = x_candidate
                interval_best = interval
                evaluation_best = evaluation_new
            # if the result is better, accept it, otherwise do not update x
            if alpha >= random.random():
                x = x_candidate
                interval = interval_candidate
                evaluation = evaluation_new

        print("best:",x_best, interval_best, evaluation_best)
        return x_best, interval_best

    def plot(self):
        # initiate values of current simulation
        threshold, interval = self.mcmc()
        tank_level = copy.deepcopy(self.tank_level)
        tank_levels = [tank_level]
        tank_high = []
        tank_low = []
        tank_mean = []
        pump_status = [False] * pump_count
        pipeline_volumes = []
        time = 0
        # write to file
        f = open("output.txt", "w")
        f.write("hour\t%d\n" % time)
        f.write("pump\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15\t16\t\n")
        f.write( "%s\t%s\n" % ('volume', '\t'.join(map(str, tank_level))))
        f.write("tank\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15\t16\t\n")
        f.write( "%s\t%s\n" % ('level', '\t'.join(map(str, np.multiply(pump_status, 1)))))
        f.write("----------------------------------------------------------------")
        f.write("----------------------------------------------------------------\n")
        # start simulation process
        while time < 48:
            # pour oil into tank
            tank_level = self.tank_update(tank_level)
            self.pump_update()

            # decide whether to turn on or off the pump for each tank
            pipeline_volume_current = 0
            sorted_index = np.argsort(tank_level)
            i = tank_count - 1
            while i >= 0:
                # tank_level[sorted_index[i]] is the current tank level
                index_i = sorted_index[i]
                if i % interval == 0:
                    # turn off the pump if sum of pump capacity over pipeline capacity
                    if pipeline_volume_current + self.pump_volume[index_i] >= pipeline_capacity:
                        pump_status[index_i] = False
                    # turn on pump if tank level over threshold
                    if tank_level[index_i] >= threshold:
                        pump_status[index_i] = True
                        tank_level[index_i] -= self.pump_volume[index_i]
                        pipeline_volume_current += self.pump_volume[index_i]
                    # turn off pump if below threshold
                    else:
                        pump_status[index_i] = False
                else:
                    if pump_status[index_i]:
                        tank_level[index_i] -= self.pump_volume[index_i]
                        pipeline_volume_current += self.pump_volume[index_i]

                i -= 1
                tank_levels = np.append(tank_levels, tank_level[i])

            tank_high.append(max(tank_level))
            tank_low.append(min(tank_level))
            tank_mean.append(np.mean(tank_level))
            pipeline_volumes = np.append(pipeline_volumes, pipeline_volume_current)
            time += 1
            f.write("hour\t%d\n" % time)
            f.write("pump\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15\t16\t\n")
            f.write("%s\t%s\n" % ('volume', '\t'.join(map(str, np.multiply(pump_status, 1)))))
            f.write("tank\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15\t16\t\n")
            f.write("%s\t%s\n" % ('level', '\t'.join(map(str, tank_level))))
            f.write("----------------------------------------------------------------")
            f.write("----------------------------------------------------------------\n")

        f.close()
        # plot high and low
        time = np.linspace(0, 47, 48)
        plt.plot(tank_high, marker='o', color='#FF7F50', label = 'high')
        plt.plot(tank_low, marker='o', color='#BDB76B', label = 'low')
        plt.plot(tank_mean, marker='o', color='#DBB403', label = 'mean')
        plt.xlabel('time')
        plt.ylabel('level %')
        plt.title('threshold = %.2f, interval = %d\ntank level mean = %.2f, standard deviation = %.2f' % (threshold, interval, np.mean(tank_levels), np.std(tank_levels)))
        plt.legend()
        plt.grid(True)
        plt.show()


        # plot pipeline volume
        plt.plot(time, pipeline_volumes, marker='x', color='#6495ED', label='pipeline volume')
        plt.xlabel('time')
        plt.ylabel('pipeline volume')
        plt.title('mean = %.2f, standard deviation = %.2f'% (np.mean(pipeline_volumes), np.std(pipeline_volumes)))
        plt.grid(True)
        plt.show()

        # plot normal distribution for tank level
        plt.hist(tank_levels, 50, facecolor= '#DEB887', histtype='bar')
        plt.xlabel('level %')
        plt.ylabel('frequency')
        plt.title('threshold = %.2f, interval = %d\ntank level mean = %.2f, standard deviation = %.2f' % (threshold, interval, np.mean(tank_levels), np.std(tank_levels)))
        plt.grid(True)
        plt.show()


def main():
    obj = Simulation()
    obj.plot()


if __name__ == "__main__":
    main()






















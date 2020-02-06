import numpy as np
import math
import matplotlib.pyplot as plt
import random
# constants
numPoints = 2000
lambda_max = 10

# define funciton
def poisson_distribution(x, lamb):
    return lamb ** x * np.exp(-lamb) / math.factorial(int(x))

# define x bound
xmin = 0
xmax = 20

# line plot
lines_x = [[]]
lines_y = [[]]

for lamb in range(1, lambda_max):
    # find ymin and ymax for current lamba
    ymin = 1000
    ymax = -1000
    for x in range(xmax):
        y = poisson_distribution(x, lamb)
        if y < ymin: ymin = y
        if y > ymax: ymax = y

    # for calculating integral
    total_rect_area = 0
    current_rect_area = (ymax - ymin) * 1
    total_int = 0.0
    current_int = 0.0

    # for line plotting
    plot_line_x = []
    plot_line_y = []

    # for scattering random points above and below the line
    ind_below_x = []
    ind_below_y = []
    ind_above_x = []
    ind_above_y = []

    # for every integer x to x + 1, use constant derivative instead of poisson distribution(x is integer only)
    # and then use random value to calculate integral of current x range
    for k in range(xmax):
        # ctr number for calculating current integral area
        ctr = 0

        # current poisson function value
        k_y = poisson_distribution(k, lamb)

        for j in range(numPoints):
            x = k + 1 * random.random() - 0.5
            y = ymin + (ymax - ymin) * random.random()

            if y <= k_y:
                ctr += 1  # area over x-axis is positive
                ind_below_x.append(x)
                ind_below_y.append(y)
            else:
                ind_above_x.append(x)
                ind_above_y.append(y)

        # calculate current integral
        current_int = current_rect_area * float(ctr) / numPoints
        total_int += current_int

        # add current x + 1 point for line plotting
        plot_line_x.append(k)
        plot_line_y.append(k_y)

    # print the integrals
    print("numerical integration for lambda = %d is %f " % (lamb, total_int))

    # for plotting sum image later
    lines_x.append(plot_line_x)
    lines_y.append(plot_line_y)

    # plotting current scatter points
    plt.ylim((0, 0.5))
    plt.xlim((0, 20))
    pts_below = plt.scatter(ind_below_x, ind_below_y, color="green", s=0.1)
    pts_above = plt.scatter(ind_above_x, ind_above_y, color="blue", s=0.1)
    plt.step(plot_line_x, plot_line_y, where='mid')
    plt.plot(plot_line_x, plot_line_y, 'C0o', color="red")
    plt.legend((pts_below, pts_above),
               ('Pts below the curve', 'Pts above the curve'),
               loc='upper right',
               ncol=3,
               fontsize=8)
    plt.title(("numerical integration for lambda at %d is %f " % (lamb, total_int)))
    plt.show()
    plt.savefig('img/monte_carlo_integration_%2d_step.png' % lamb)

# plotting sum image
labels = []
plt.ylim((0, 0.5))
plt.xlim((-1, 20))
for i in range(1, lambda_max):
    plt.plot(lines_x[i], lines_y[i])
    labels.append("lambda = %d" % i)
plt.legend(labels, loc='upper right')
plt.show()
plt.savefig('img/monte_carlo_integration_sum_step.png')

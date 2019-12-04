import operator
import random
import csv
import numpy as np
import eaneatGP
import init_conf
import os.path
from deap import base
from deap import creator
from deap import tools
from deap import gp
import gp_conf as neat_gp
from my_operators import safe_div, mylog, mypower2, mypower3, mysqrt, myexp
import sys


pset = gp.PrimitiveSet("MAIN", 34)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(safe_div, 2)
pset.addPrimitive(np.cos, 1)
pset.addPrimitive(np.sin, 1)
pset.addPrimitive(mylog, 1)
pset.addPrimitive(mypower2, 1)
pset.addPrimitive(mypower3, 1)
pset.addPrimitive(mysqrt, 1)
pset.addPrimitive(np.tan, 1)
pset.addPrimitive(np.tanh, 1)
pset.addEphemeralConstant("rand101", lambda: random.uniform(-1, 1))
pset.renameArguments(ARG0='x0',ARG1='x1', ARG2='x2', ARG3='x3', 
    ARG4='x4', ARG5='x5', ARG6='x6', ARG7='x7',  ARG8='x8',
    ARG9='x9', ARG10='x10', ARG11='x11', ARG12='x12',ARG13='x13', ARG14='x14', ARG15='x15', 
    ARG16='x16', ARG17='x17', ARG18='x18', ARG19='x19',  ARG20='x20',
    ARG21='x21', ARG22='x22', ARG23='x23', ARG24='x24',ARG25='x25', ARG26='x26', ARG27='x27', 
    ARG28='x28', ARG29='x29', ARG30='x30', ARG31='x31',  ARG32='x32',
    ARG33='x33', ARG34='x34', ARG35='x35')


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("FitnessTest", base.Fitness, weights=(-1.0,))
creator.create("Individual", neat_gp.PrimitiveTree, fitness=creator.FitnessMin, fitness_test=creator.FitnessTest)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genFull, pset=pset, min_=1, max_=3)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", init_conf.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def evalSymbReg(individual, test, points):
    func = toolbox.compile(expr=individual)
    # print(points)
    vector = points[34]#[data[8] for data in points]
    # print(vector)
    # sys.exit()
    result = np.sum((func(*np.asarray(points)[:34]) - vector)**2)
    return np.sqrt(result/len(points[0])),


def energy_coolng(n_corr, num_p, problem, name_database):
    n_archivot = './data_corridas/%s/test_%d_%d.txt' % (problem, num_p, n_corr)
    n_archivo = './data_corridas/%s/train_%d_%d.txt' % (problem, num_p, n_corr)
    print(os.path.exists(n_archivo))
    print(os.path.exists(n_archivot))
    if not (os.path.exists(n_archivo) or os.path.exists(n_archivot)):
        direccion = "./data_corridas/%s/%s.txt" %(problem, name_database)
        with open(direccion) as spambase:
            spamReader = csv.reader(spambase,  delimiter=',', skipinitialspace=True)
            num_c = sum(1 for line in open(direccion))
            print(num_c)
            # sys.exit()
            num_r = len(next(csv.reader(open(direccion), delimiter=',', skipinitialspace=True)))
            print(num_r)
            # sys.exit()
            Matrix = np.empty((num_r, num_c,))
            for row, c in zip(spamReader, range(num_c)):
                # print(row)
                for r in range(num_r):
                    try:
                        Matrix[r, c] = row[r]
                    except ValueError:
                        # print ('Line {r} is corrupt', r, c, row)
                        print ('Line {r} is corrupt', r, c)
                        Matrix[r, c] = -1
                        # break
            print('complete')
            # sys.exit()
        if not os.path.exists(n_archivo):
            long_train=int(len(Matrix.T)*.7)
            data_train = random.sample(Matrix.T, long_train)
            np.savetxt(n_archivo, data_train, delimiter=",", fmt="%s")
        if not os.path.exists(n_archivot):
            long_test=int(len(Matrix.T)*.3)
            data_test = random.sample(Matrix.T, long_test)
            np.savetxt(n_archivot, data_test, delimiter=",", fmt="%s")

    with open(n_archivo) as spambase:
        spamReader = csv.reader(spambase,  delimiter=',', skipinitialspace=True)
        num_c = sum(1 for line in open(n_archivo))
        num_r = len(next(csv.reader(open(n_archivo), delimiter=',', skipinitialspace=True)))
        Matrix = np.empty((num_r, num_c,))
        for row, c in zip(spamReader, range(num_c)):
            for r in range(num_r):
                try:
                    Matrix[r, c] = row[r]
                except ValueError:
                    print ('Line {r} is corrupt' , r)
                    break
        data_train=Matrix[:]
    with open(n_archivot) as spambase:
        spamReader = csv.reader(spambase,  delimiter=',', skipinitialspace=True)
        num_c = sum(1 for line in open(n_archivot))
        num_r = len(next(csv.reader(open(n_archivot), delimiter=',', skipinitialspace=True)))
        Matrix = np.empty((num_r, num_c,))
        for row, c in zip(spamReader, range(num_c)):
            for r in range(num_r):
                try:
                    Matrix[r, c] = row[r]
                except ValueError:
                    print ('Line {r} is corrupt' , r)
                    break
        data_test=Matrix[:]
    # data_train = data_train[0]
    # data_test = data_test[0]
    # sys.exit()
    toolbox.register("evaluate", evalSymbReg, test=False, points=data_train)
    toolbox.register("evaluate_test", evalSymbReg,  test=True, points=data_test)


def main(n_corr, num_p):
    problem = "Ionosphere"
    name_database = "ionosphere"
    pop_size = 100

    energy_coolng(n_corr, num_p, problem, name_database)


    toolbox.register("select",tools.selTournament, tournsize=3)
    toolbox.register("mate", neat_gp.cxSubtree)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=3)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(3)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", np.mean)
    mstats.register("std", np.std)
    mstats.register("min", np.min)
    mstats.register("max", np.max)
    cxpb = 0.7
    mutpb = 0.3
    ngen = 100
    params = ['best_of_each_specie', 2, 'yes']
    neat_cx = True
    neat_alg = True
    neat_pelit = 0.5
    neat_h = 0.15
    neat_beta = 0.5

    pop, log = eaneatGP.neat_GP(pop, toolbox, cxpb, mutpb, ngen, neat_alg, neat_cx, neat_h, neat_pelit, n_corr, num_p, params, problem, neat_beta, stats=mstats, halloffame=hof, verbose=True)
    return pop, log, hof


def run(number, problem):
    n = 1
    while n <= number:
        main(n, problem)
        n += 1


if __name__ == "__main__":
    n_corr_min = 1
    n_corr_max = 2
    num_p = 101
    while n_corr_min <= n_corr_max:
        main(n_corr_min, num_p)
        n_corr_min += 1

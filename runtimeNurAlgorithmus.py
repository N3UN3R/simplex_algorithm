from currentlyActiveCostDict import get_numpy_array_cost_matrix
from constraintMatrix import complete_constraint_matrix
from orderedDemandSupplyValues import get_ordered_consumers_demand, get_ordered_producers_supply
from scipy.optimize import linprog
from getHouseholdData import get_data_from_file

import time



def build_objective_function(costMatrix):
    """ function that builds the objective function for the opimization"""
    objective = costMatrix.flatten()

    return objective


def create_righthandSide_constraints(orderedProducersSupply,orderedConsumersDemand):
    """ function that creates the righthandSide constraints which are needed as Input
        for the algorithm"""
    righthandSide = []
    #add supplyValues as constraints
    """ hier muss noch was rein, falls kein producer vorhanden ist"""
    for producerId, supplyValue in orderedProducersSupply.items():
        righthandSide.append(supplyValue)
    #add demandValues as constraints
    for consumerId,demandValue in orderedConsumersDemand.items():
        righthandSide.append(demandValue)

    return righthandSide


def consumer_propFair_righthandside(orderedProducersSupply,orderedConsumersDemand,updatedTotalDemand,updatedTotalSupply):
    """ Function that creates righthandside constraints that ensure, that consumers
        don't get more than their proportional share.

        This has to be done when totalSupply<totalDemand"""
    righthandSide = []
    for producerId, supplyValue in orderedProducersSupply.items():
        righthandSide.append(supplyValue)

    for consumerId,demandValue in orderedConsumersDemand.items():
        #proportionalShare of a household is its (demand\totalDemand)*totalSupply
        proportionalShare = (demandValue/updatedTotalDemand)*updatedTotalSupply
        righthandSide.append(proportionalShare)

    return righthandSide


def producer_propFair_righthandside(orderedProducersSupply,orderedConsumersDemand,updatedTotalDemand,updatedTotalSupply):
    """ Function that creates righthandside constraints that ensure, that producers
        don't get more than their proportional share.

        This has to be done when totalSupply>totalDemand"""

    righthandSide = []
    for producerId, supplyValue in orderedProducersSupply.items():
        proportionalShare = (supplyValue/updatedTotalSupply)*updatedTotalDemand
        righthandSide.append(proportionalShare)

    for consumerId, demandValue in orderedConsumersDemand.items():
        righthandSide.append(demandValue)

    return righthandSide


def run_simplex_algorithm(household_data,assets,costMatrix):

    dataPrep_startTime  = time.time()
    orderedProducersSupply, updatedTotalSupply = get_ordered_producers_supply(household_data, assets)
    orderedConsumersDemand, updatedTotalDemand = get_ordered_consumers_demand(household_data,assets)

    """ righthandside constraints depend on the specific case
            check which case is the current one
                1. demand > supply
                2. demand = supply
                3. demand < supply """

    # case 1
    if updatedTotalDemand > updatedTotalSupply:
        b = consumer_propFair_righthandside(orderedProducersSupply, orderedConsumersDemand, updatedTotalDemand,
                                            updatedTotalSupply)
        #print("------------------------------------------------------------------------------------")
        #print("case 1: The total demand in the community is higher than total supply")

    # case 2:
    if updatedTotalDemand == updatedTotalSupply:
        b = create_righthandSide_constraints(orderedProducersSupply, orderedConsumersDemand)

        #print("------------------------------------------------------------------------------------")
        #print("case 2: Total demand equals total supply")

    # case 3:
    if updatedTotalDemand < updatedTotalSupply:
        b = producer_propFair_righthandside(orderedProducersSupply, orderedConsumersDemand, updatedTotalDemand,
                                                updatedTotalSupply)

       # print("------------------------------------------------------------------------------------")
      #  print("case 3: total demand in the community is lower than total supply")


    # objective function
    objective = build_objective_function(costMatrix)

    # lefthandSide constraints
   # A = complete_constraint_matrix(household_data)

    Aold = complete_constraint_matrix(household_data)

    A = Aold[:-1]

    bNew = b[:-1]

    dataPrep_endTime = time.time()

    timeForDataPrep = dataPrep_endTime - dataPrep_startTime

    start_time = time.time()
    # algorithm
    revisedSimplexResults = linprog(c=objective, A_eq=A, b_eq=bNew,
                                 method="revised simplex")
    end_time = time.time()

    # runtime
    runtime = end_time - start_time

    return revisedSimplexResults, runtime, timeForDataPrep



from getHouseholdData import get_data_from_file, get_current_consumer_list, get_current_producer_list
from currentlyActiveCostDict import get_numpy_array_cost_matrix, remove_inactive_consumers_as_possible_consumers
import numpy as np
import time
import json
from constraintMatrix import complete_constraint_matrix
from orderedDemandSupplyValues import get_ordered_consumers_demand, get_ordered_producers_supply
from scipy.optimize import linprog
import os


def build_objective_function(costMatrix):
    """ function that builds the objective function for the opimization
        returns the objective function as numpy array"""

    objective = costMatrix.flatten()

    return objective


def create_righthandSide_constraints(orderedProducersSupply,orderedConsumersDemand):
    """ function that creates the righthandSide constraints which are needed as Input
        for the algorithm
        returns the righthandSide constraints as numpy array"""

    righthandSide = []
    #add supplyValues as constraints
    for producerId, supplyValue in orderedProducersSupply.items():
        righthandSide.append(supplyValue)
    #add demandValues as constraints
    for consumerId,demandValue in orderedConsumersDemand.items():
        righthandSide.append(demandValue)

    return righthandSide


def consumer_propFair_righthandside(orderedProducersSupply,orderedConsumersDemand,updatedTotalDemand,updatedTotalSupply):
    """ Function that creates righthandside constraints that ensure, that consumers
        don't get more than their proportional share.
        This has to be done when totalSupply<totalDemand
        returns the righthandSide constraints as numpy array"""

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
        This has to be done when totalSupply>totalDemand
        returns the righthandSide constraints as numpy array"""

    righthandSide = []
    for producerId, supplyValue in orderedProducersSupply.items():
        proportionalShare = (supplyValue/updatedTotalSupply)*updatedTotalDemand
        righthandSide.append(proportionalShare)

    for consumerId, demandValue in orderedConsumersDemand.items():
        righthandSide.append(demandValue)

    return righthandSide


def run_revisedSimplex_algorithm(household_data,assets,costMatrix):
    """ function that contains the revised simplex algorithm
        returns revisedSimplexResults, runtime, timeForDataPrep """

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

    Aold = complete_constraint_matrix(household_data)

    A = Aold[:-1]

    bNew = b[:-1]

    dataPrep_endTime = time.time()

    timeForDataPrep = dataPrep_endTime - dataPrep_startTime

    start_time = time.time()
    # algorithm
    revisedSimplexResults = linprog(c=objective, A_eq=A, b_eq=bNew,
                                 method="simplex")
    end_time = time.time()

    # runtime
    runtime = end_time - start_time

    return revisedSimplexResults, runtime, timeForDataPrep






def main():

    # load pairsandReduction for tracking of used reductions
    with open('pairsAndReductions.json', 'r') as file:
        pairs_and_reductions = json.load(file)

    assets = 'AssetListe.json'

    data = '07_01_2020_13_00_00.json'

    household_data = get_data_from_file(data)

    # numbers of households
    numberOfProducers = len(get_current_producer_list(household_data))
    numberOfConsumers = len(get_current_consumer_list(household_data))

    # costMatrix
    costMatrix = get_numpy_array_cost_matrix(household_data, assets)

    #check if there is active producers
    if numberOfProducers > 0:

        # run simplex algorithm
        revisedSimplexResults, runtime, timeForDataPrep = run_revisedSimplex_algorithm(household_data, assets,
                                                                                      costMatrix)

        # values of simplex_results
        # x values of optimization this equals the traded amounts in between the households
        tradedAmounts_raw = revisedSimplexResults.x


        # total watthours traded
        totalTradedWatts = sum(tradedAmounts_raw)

        # getTotalCosts equals the objective function value
        totalCosts = revisedSimplexResults.fun

        #analysis which reductions have been used
        activeHouseholds = remove_inactive_consumers_as_possible_consumers(household_data, assets)
        indexedTradingpairs = {}
        rowCounter = 0
        # get indices of consumer producerIds
        for producerId, consumers in activeHouseholds.items():
            columnCounter = 0
            for consumerId, costs in consumers.items():
                index = (rowCounter, columnCounter)
                indexedTradingpairs[index] = (producerId, consumerId)
                columnCounter += 1
            rowCounter += 1

        # trade results
        tradeResults = tradedAmounts_raw.reshape(numberOfProducers, numberOfConsumers)
        tradingPairs = []  # tradingPairs are to track which pairs have traded with each other
        tradingCosts = []  # tradingCosts are to track maximal and minimal trading price
        tradedAmounts = {}

        # get trading pairs
        for index, amount in np.ndenumerate(tradeResults):
            if amount > float(0.000005):
                tradingPairs.append(indexedTradingpairs[index])
                tradingCosts.append(costMatrix[index])
                tradedAmounts[indexedTradingpairs[index]] = amount

        #track which reductions have been used
        used_reductions = {}
        konz_difference = []
        konz_differencePairs = []
        net_difference = []
        net_differencePairs = []
        localDistancePairs = []
        localDistance = []

        for matchedhouseholds in tradingPairs:
            producerId = matchedhouseholds[0]
            consumerId = matchedhouseholds[1]

            if pairs_and_reductions[producerId][consumerId]['lokalDistance'] == True:
                # this checks if this householdpair is already in the current statistic
                if matchedhouseholds not in localDistancePairs:
                    localDistancePairs.append(matchedhouseholds)
                    localDistance.append(1)

            if pairs_and_reductions[producerId][consumerId]['konzessionsDifference'] > 0:
                # this checks if this householdpair is already in the current statistic
                if matchedhouseholds not in konz_differencePairs:
                    konz_differencePairs.append(matchedhouseholds)
                    konz_difference.append(1)

            if pairs_and_reductions[producerId][consumerId]['netCostDifference'] > 0:
                # this checks if this householdpair is already in the current statistic
                if matchedhouseholds not in net_differencePairs:
                    net_differencePairs.append(matchedhouseholds)
                    net_difference.append(1)

        # used_reduction to track which price reduction have been used
        used_reductions['konzessionsDifference'] = sum(konz_difference)
        used_reductions['netCostDifference'] = sum(net_difference)
        used_reductions['lokalDistance'] = sum(localDistance)
        used_reductions['numberOfPairs'] = len(tradingPairs)

        # data for analysis
        results = {}
        results['totalCosts'] = totalCosts
        results['totalTradedWatts'] = totalTradedWatts
        results['averagePrice'] = totalCosts / totalTradedWatts
        results['maximumPrice'] = max(tradingCosts, default=0)
        results['minimumPrice'] = min(tradingCosts, default=0)
        results['runningTime'] = runtime
        results['dataPrepTime'] = timeForDataPrep
        results['numberOfProducers'] = numberOfProducers
        results['numberOfConsumers'] = numberOfConsumers
        results['usedReductions'] = used_reductions
        results['timestamp'] = household_data['time']
        results['tradedAmounts'] = tradedAmounts

        print(results)

    else:
        results = {}
        results['totalCosts'] = 0
        results['totalTradedWatts'] = 0
        results['averagePrice'] = 30
        results['maximumPrice'] = 30
        results['minimumPrice'] = 30
        results['runningTime'] = 0
        results['dataPrepTime'] = 0
        results['numberOfProducers'] = numberOfProducers
        results['numberOfConsumers'] = numberOfConsumers
        results['usedReductions'] = 0
        results['timestamp'] = household_data['time']
        results['tradedAmounts'] = 0

if __name__ == '__main__':
    main()
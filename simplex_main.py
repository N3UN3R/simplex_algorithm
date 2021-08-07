from runtimeNurAlgorithmus import run_simplex_algorithm
import csv
from getHouseholdData import get_data_from_file, get_current_consumer_list, get_current_producer_list
import os
from getHouseholdData import get_data_from_file, get_current_consumer_list, get_current_producer_list
from currentlyActiveCostDict import get_numpy_array_cost_matrix, remove_inactive_consumers_as_possible_consumers
import numpy as np
import time
import json
import os


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

    # Bedingung, dass der Algorithmus immer nur ausgeführt wird, wenn Producer vorhanden
    if numberOfProducers > 0:

        # run simplex algorithm
        simplexResults, runtime, timeForDataPrep = run_simplex_algorithm(household_data, assets,
                                                                                      costMatrix)

        # values of simplex_results
        # x values of optimization this equals the traded amounts in between the households
        tradedAmounts_raw = simplexResults.x


        # total watthours traded
        totalTradedWatts = sum(tradedAmounts_raw)

        # getTotalCosts equals the objective function value
        totalCosts = simplexResults.fun

        """ Analysis welche hebel genutzt wurden"""
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

        """ get tradingpairs"""
        # trade results
        tradeResults = tradedAmounts_raw.reshape(numberOfProducers, numberOfConsumers)
        tradingPairs = []  # tradingPairs are to track which pairs have traded with each other
        tradingCosts = []  # tradingCosts are to track maximal and minimal trading price
        tradedAmounts = {}

        # get trading pairs
        for index, amount in np.ndenumerate(tradeResults):
            # hier wird ein unterer Wert eingepackt. da viele Ergebnisse sehr klein und deshalb verfäschelnd sind
            if amount > float(0.000005):
                tradingPairs.append(indexedTradingpairs[index])
                tradingCosts.append(costMatrix[index])
                tradedAmounts[indexedTradingpairs[index]] = amount

        """ suche die jeweiligen Hebel aus """
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
                # this if checks if this householdpair is already in the current statistic
                if matchedhouseholds not in localDistancePairs:
                    localDistancePairs.append(matchedhouseholds)
                    localDistance.append(1)

            if pairs_and_reductions[producerId][consumerId]['konzessionsDifference'] > 0:
                # this if checks if this householdpair is already in the current statistic
                if matchedhouseholds not in konz_differencePairs:
                    konz_differencePairs.append(matchedhouseholds)
                    konz_difference.append(1)

            if pairs_and_reductions[producerId][consumerId]['netCostDifference'] > 0:
                # this if checks if this householdpair is already in the current statistic
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
        # to Do highest and lowest price
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
        # to Do highest and lowest price
        results['maximumPrice'] = 30
        results['minimumPrice'] = 30
        results['runningTime'] = 0
        results['dataPrepTime'] = timeForDataPrep
        results['numberOfProducers'] = numberOfProducers
        results['numberOfConsumers'] = numberOfConsumers
        results['usedReductions'] = 0
        results['timestamp'] = household_data['time']
        results['tradedAmounts'] = 0


if __name__ == '__main__':
    main()
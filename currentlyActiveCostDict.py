from getHouseholdData import get_current_consumer_list, get_current_producer_list, get_data_from_file
import json
import numpy as np

#data = '07_06_2020_13_00_00.json'

#household_data = get_data_from_file(data)

#file ='AssetListe.json'


def read_asset_list(assets):
    """ this function reads in a json file called assetListe.json.
    it returns a list of the meterids in assetliste.json"""
    with open(assets, 'r') as json_data:
        assetList_data = json.load(json_data)
        asset_ids = []

        for household in assetList_data['data']:
            if household['meterId'] != 'NO_METER_AVAILABLE':
                asset_ids.append(household['meterId'])

    return asset_ids


def non_active_consumers(household_data, assets):
    allMeterIds = read_asset_list(assets)

    consumerIds = get_current_consumer_list(household_data)

    nonActiveConsumers = list((set(allMeterIds)^set(consumerIds)))

    return nonActiveConsumers


def remove_inactive_prosumers_as_possible_producers(household_data):
    """ function that removes all prosumer entrys from cost dictionary that belong
        to currently inative prosumers"""

    with open('tradingCost_prosumers_to_all_households_nested.json') as file:
        cost_dictionary = json.load(file)

    #copy of cost dictionary is needed to remove keys
    active_cost_dictionary = cost_dictionary.copy()
    #list of active prosumers thus producers
    activeProsumers = get_current_producer_list(household_data)

    #remove all entrys from cost dictionary that belong to inactive prosumers
    for prosumerId, matchedhouseholds in cost_dictionary.items():
        if prosumerId not in activeProsumers:
            del active_cost_dictionary[prosumerId]

    return active_cost_dictionary


def remove_inactive_consumers_as_possible_consumers(household_data,assets):
    """ function that removes all cost dictionary entrys for prosumer households
        that are currently producing power and thus should be removed as possible
         consumers.
         It also removes all consumer households that are in the tradingCostDictionary,
          but not in the current input data"""
    # copy of dictionary is needed to remove keys
    cost_Dictionary = remove_inactive_prosumers_as_possible_producers(household_data).copy()

    for prosumerId,matchedhouseholds in cost_Dictionary.items():
        for meterId in non_active_consumers(household_data, assets):
            del cost_Dictionary[prosumerId][meterId]

    return cost_Dictionary


def get_numpy_array_cost_matrix(household_data, assets):
    """ this function gets the current cost-dictionary from remove active prosumers as
        possible consumers and transforms it into a numpy array which is needed for
        optimization with scipy

        columns are the number of consumers
        rows are the number of producers
        """

    cost_dictionary = remove_inactive_consumers_as_possible_consumers(household_data,assets)

    #producerKey is first key in active producers
    if len(get_current_producer_list(household_data)) >0:
        producerKey = get_current_producer_list(household_data)[0]

        #get a list of the nested dictionarys keys using first entry in active producers
        consumerIds = list(cost_dictionary[producerKey].keys())

    #making a numpy array with all costs
    costMatrix = np.array([[costs[householdId] for householdId in consumerIds] for meterId, costs in cost_dictionary.items()])

    return costMatrix


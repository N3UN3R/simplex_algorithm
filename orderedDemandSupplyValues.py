from getHouseholdData import get_current_producer_ids_to_supply_value, get_current_consumer_ids_to_demand_value
from collections import OrderedDict
from currentlyActiveCostDict import remove_inactive_consumers_as_possible_consumers


from getHouseholdData import get_data_from_file

#data = '07_06_2020_13_00_00.json'

#file ='AssetListe.json'

#household_data = get_data_from_file(data)

def ordered_producers_and_consumers(household_data, assets):
    """ function that creates a producer and a consumer list in the same order as the meterIds
        appear in the cost dictionary.
        This ensures that supply and demand restrictions really belong to the right row in the
        restrictions used in sciPy algorithms"""

    orderedProsumers = []
    for prosumerId,matchedhouseholds in remove_inactive_consumers_as_possible_consumers(household_data,assets).items():
        orderedProsumers.append(prosumerId)

    orderedConsumers = []
    #loop through the dictionary of possible consumers by using first entry as key to nested dictionarys
    if orderedProsumers:
        for consumerId, cost in remove_inactive_consumers_as_possible_consumers(household_data, assets)[orderedProsumers[0]].items():
            orderedConsumers.append(consumerId)
    #this should prevent an error when there is no currently active producers
    else:
        pass

    return orderedProsumers, orderedConsumers


def get_ordered_producers_supply(household_data,assets):
    """ function that returns current supply values of producers
        in the same order as they appear in the cost dictionary
         """
    #current apisupply values
    producerSupply, _ = get_current_producer_ids_to_supply_value(household_data)

    # list which contain prosumers  in the right order
    orderedProsumers, _ = ordered_producers_and_consumers(household_data,assets)

    #orderedDictionary to make sure order stays the same which cant be garanteed in a classic pyhton dictionary
    orderedProducersSupply = OrderedDict()

    supplyValues = []

    for prosumerId in orderedProsumers:
        orderedProducersSupply[prosumerId] = producerSupply[prosumerId]
        supplyValues.append(producerSupply[prosumerId])
    updatedTotalSupply = sum(supplyValues)

    return orderedProducersSupply, updatedTotalSupply


def get_ordered_consumers_demand(household_data,assets):
    """ function that returns current supply values of producers
         in the same order as they appear in the cost dictionary
          """
    #current api demand values
    consumerDemand, _ = get_current_consumer_ids_to_demand_value(household_data)

    # list which contain consumers  in the right order
    _, orderedConsumers = ordered_producers_and_consumers(household_data,assets)

    #orderedDictionary to make sure order stays the same which cant be garanteed in a classic pyhton dictionary
    orderedConsumersDemand = OrderedDict()

    demandValues = []

    for consumerId in orderedConsumers:
        orderedConsumersDemand[consumerId] = consumerDemand[consumerId]
        demandValues.append(consumerDemand[consumerId])
    updatedTotalDemand = sum(demandValues)

    return orderedConsumersDemand, updatedTotalDemand


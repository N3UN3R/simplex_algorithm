from getHouseholdData import get_current_producer_list, get_current_consumer_list
import numpy as np
from getHouseholdData import get_data_from_file



#data = '03_31_2019_23_45_00.json'
#data = '07_06_2020_13_00_00.json'
#print(get_data_from_file(data))

#household_data = get_data_from_file(data)


def generate_producer_constraints(household_data):
    """ function that creates constraint matrix for all producer constraints"""
    numberProducers = len(get_current_producer_list(household_data))
    numberConsumers = len(get_current_consumer_list(household_data))
    rows = numberConsumers + numberProducers
    columns = numberConsumers * numberProducers


    content = np.tile([1]*numberConsumers+[0]*columns,numberProducers)[:(-1*columns)]
    producerConstraints = content.reshape(numberProducers, columns)

    return producerConstraints


def generate_consumer_constraints(household_data):
    """ function that creates constraint matrix for all consumer constraints"""
    numberProducers = len(get_current_producer_list(household_data))
    numberConsumers = len(get_current_consumer_list(household_data))
    rows = numberConsumers + numberProducers
    columns = numberConsumers * numberProducers


    content = np.tile((([1]*1+[0]*(numberConsumers-1))*(numberProducers-1))+[1]*1+[0]*numberConsumers,numberConsumers)[:(-1*numberConsumers)]
    consumerConstraints = content.reshape(numberConsumers, columns)

    return consumerConstraints


def complete_constraint_matrix(household_data):
    """ function that add builds the full constraint matrix by adding the consumer
        and the producer constraints"""

    consumerConstraints = generate_consumer_constraints(household_data)
    producerConstraints = generate_producer_constraints(household_data)
    #np.vstack builds one array out of one array.
    constraints = np.vstack((producerConstraints,consumerConstraints))

    return constraints

from getHouseholdData import get_current_producer_list, get_current_consumer_list
import numpy as np
from getHouseholdData import get_data_from_file


def generate_producer_constraints(household_data):
    """ function that creates constraint matrix for all producer constraints
        returns the producer constraints as a numpy array"""
    numberProducers = len(get_current_producer_list(household_data))
    numberConsumers = len(get_current_consumer_list(household_data))
    rows = numberConsumers + numberProducers
    columns = numberConsumers * numberProducers

    content = np.tile([1]*numberConsumers+[0]*columns,numberProducers)[:(-1*columns)]
    producerConstraints = content.reshape(numberProducers, columns)

    return producerConstraints


def generate_consumer_constraints(household_data):
    """ function that creates constraint matrix for all consumer constraints
        returns the consumer constraints as a numpy array """
    numberProducers = len(get_current_producer_list(household_data))
    numberConsumers = len(get_current_consumer_list(household_data))
    rows = numberConsumers + numberProducers
    columns = numberConsumers * numberProducers

    content = np.tile((([1]*1+[0]*(numberConsumers-1))*(numberProducers-1))+[1]*1+[0]*numberConsumers,numberConsumers)[:(-1*numberConsumers)]
    consumerConstraints = content.reshape(numberConsumers, columns)

    return consumerConstraints


def complete_constraint_matrix(household_data):
    """ function that add builds the full constraint matrix by stacking the consumer
        and the producer constraints
        returns all needed constraints for a specific interval as a numpy array"""

    consumerConstraints = generate_consumer_constraints(household_data)
    producerConstraints = generate_producer_constraints(household_data)
    constraints = np.vstack((producerConstraints,consumerConstraints))

    return constraints
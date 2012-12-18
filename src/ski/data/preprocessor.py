'''
  Module providing functions for running steps on raw GPS data, prior to
  ski data processing

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (11 Dec 2012)
'''
import logging as log

from gpsdatum import GPSDatum
from linkednode import LinkedNode
import interpolator

convert_coords = True

def convert_tuples_to_linked_list(tupleList):
    '''
      Converts a list of GPS tuple objects into a linked list. GPS data is
      wrapped into GPSDatum objects.
      @param tupleList: a list of tuple data [(ts, (la, lo), (x, y), a, s)]
      @return: a LinkedNode object at the start of the linked list.
      @see: GPSDatum
    '''
    if type(tupleList) is not list:
        raise ValueError('Expected tuple list as argument')
    
    # Convert tuples into GPSDatum objects
    dList = [GPSDatum(d) for d in tupleList]
    
    # Reverse list, required for building list
    dList.reverse()
    
    firstNode = None
    for d in dList:
        # Create a new LinkedNode object
        newNode = LinkedNode(d, firstNode)
        firstNode = newNode
        
    return firstNode

def interpolate_list(firstNode):
    '''
      Interpolate a linked list of GPSDatum objects.  Interpolation happens
      'in-line'; no object is returned.
      @param firstNode: a LinkedNode object at the start of the linked list.
    '''
    if type(firstNode) is not LinkedNode:
        raise ValueError('Expected a LinkedNode object for interpolate_list')
    
    deltaF = interpolator.delta_pt
    interF = interpolator.linear_interpolate_pt
    interpolator.interpolate_list(firstNode, deltaF, interF)
    
    
def remove_outlyers(firstNode):
    '''
      Remove erroneous datum points from a linked list of GPSDatum object.
      Processing happens in-line; no object is returned.
      @param firstNode: a LinkedNode object at the start of the linked list.
    '''
    NotImplemented
    


def preprocess(data):
    '''
      Runs pre-processing steps on a list of GPS data.  Pre-processing steps include
        * Stage 1 interpolation
        * Outlyer removal
        * Stage 2 interpolation
      @param data: a list of GPS tuples
      @return: a list of pre-processed GPSDatum objects
    
    '''

    # Tuples to GPS datum objects
    # Array to linked list
    firstNode = convert_tuples_to_linked_list(data)
    
    # Interpolate
    interpolate_list(firstNode)
    print interpolator.counter
    log.info('First stage interpolation complete.')
    
    # Remove outlyers
    remove_outlyers(firstNode)
    log.info('Outlyer removal complete.')
    
    # Re-interpolate?
    interpolate_list(firstNode)
    log.info('Second state interpolation complete.')
    
    return firstNode.to_array()
    
    # To array of ski track points - move to process
    
    # Create track - move to process?
    
    
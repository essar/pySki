'''
  Implementation of a simple linked list.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (18 Dec 2012)
'''
class LinkedNode:
    '''
      Object that forms a linked list node.  Each node in a linked list
      contains a payload and reference to the next item in the list.
      @param obj: the payload of this node.
      @param nxt: the next item in the linked list.
    '''
    def __init__(self, obj=None, nxt=None):
        self.obj = obj
        self.nxt = nxt
    
    def __str__(self):
        return 'obj={0}; nxt={1}'.format(str(self.obj), str(self.nxt.obj) if self.nxt is not None else None)

    def to_array(self):
        # See if this can be done with list comprehension?
        out = [self.obj]
        o = self.nxt
        while o != None:
            out.append(o.obj)
            o = o.nxt
        return out
# author: O. Gourgue (University of Antwerp, Belgium)

import numpy as np
import sys

import ppmodules.selafin_io_pp as pps


################################################################################

class Selafin(object):

  def __init__(self, filename):

    """
    object to import and export selafin files
    example:

    from myselafin import Selafin
    slf = Selafin(filename)
    slf.import_header()
    v = slf.impor_data()

    """

    # open file
    slf = pps.ppSELAFIN(filename)

    # class atributes
    self.slf = slf


  ############################################################################

  def import_header(self):

    """
    import header of selafin file
    class attributes:
      - times: list of time steps
      - vnames: list of variable names
      - vunits: list of variable units
      - float_type
      - float_size
      - nelem: number of grid triangles
      - npoin: number of grid nodes
      - ndp
      - ikle: connectivity table (beware, first triangle id is 1, not 0)
      - ipobo
      - x: array with x-coordinates of grid nodes
      - y: array with y-coordinates of grid nodes
    """

    # class attributes
    slf = self.slf

    # read header
    slf.readHeader()
    slf.readTimes()

    # store into arrays
    times = slf.getTimes()
    vnames = slf.getVarNames()
    vunits = slf.getVarUnits()
    float_type, float_size = slf.getPrecision()
    nelem, npoin, ndp, ikle, ipobo, x, y = slf.getMesh()

    # class attributes
    self.times = times
    self.vnames = vnames
    self.vunits = vunits
    self.float_type = float_type
    self.float_size = float_size
    self.nelem = nelem
    self.npoin = npoin
    self.ndp = ndp
    self.ikle = ikle
    self.ipobo = ipobo
    self.x = x
    self.y = y


  ############################################################################

  def import_data(self, vname = None, step = None):

    """
    import data of selafin file
    input:
      - vname: (list of) variable name(s)
      - step: (list of) time step(s) - step = -1 for last time step
    output:
      - v: (list of) array(s) with data
           --> list if several variables (each item is a different variable)
           --> array shape = (number of grid nodes, number of time steps)
    """

    # class attributes
    slf = self.slf
    times = self.times
    vnames = self.vnames
    npoin = self.npoin

    # variables
    if vname is None:
      vname = vnames
    elif type(vname) is str:
      vname = [vname]

    # number of variables
    if type(vname) is str:
      nv = 1
    else:
      nv = len(vname)

    # indices of variables to keep
    vid = []
    for i in range(nv):
      vid.append(list(map(str.strip, vnames)).index(vname[i].strip()))
    vid = np.array(vid)

    # time steps
    if step is None:
      step = range(len(times))
    elif step == -1:
      step = [len(times) - 1]
    elif type(step) is int:
      step = [step]

    # number of time steps
    nt = len(step)

    # initialization of temporary array
    tmp = np.zeros((nt, nv, npoin))

    # read data
    for i in range(nt):
      slf.readVariables(step[i])
      tmp[i, :, :] = slf.getVarValues()[vid, :]

    # reshape data
    if nv == 1:
      if nt == 1:
        v = tmp[0, 0, :]
      else:
        v = tmp[:, 0, :].T
    else:
      v = []
      for i in range(nv):
        if nt == 1:
          v.append(tmp[0, i, :])
        else:
          v.append(tmp[:, i, :].T)

    # return data
    return v


  ############################################################################

  def export_header(self, vnames, vunits, ikle, ipobo, x, y, \
                    ndp = 3, float_type = 'f', float_size = 4):

    """
    export header in selafin file
    input:
      - vnames: list of variable names
      - vunits: list of variable units
      - nelem: number of grid triangles
      - npoin: number of grid nodes
      - ikle: connectivity table (beware, first triangle id is 1, not 0)
      - ipobo
      - x: array with x-coordinates of grid nodes
      - y: array with y-coordinates of grid nodes
      - float_type (optional)
      - float_size (optional)
      - ndp (optional)
    """

    # class attributes
    slf = self.slf

    # number of triangles
    nelem = ikle.shape[0]

    # number of nodes
    npoin = len(x)

    # write header
    slf.setPrecision(float_type, float_size)
    slf.setTitle('')
    slf.setVarNames(vnames)
    slf.setVarUnits(vunits)
    slf.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    slf.setMesh(nelem, npoin, ndp, ikle, ipobo, x, y)
    slf.writeHeader()

    # class attributes
    self.vnames = vnames
    self.vunits = vunits
    self.float_type = float_type
    self.float_size = float_size
    self.nelem = nelem
    self.npoin = npoin
    self.ndp = ndp
    self.ikle = ikle
    self.ipobo = ipobo
    self.x = x
    self.y = y


  ############################################################################

  def export_data(self, times, v):

    """
    export data in telemac file
    input:
      - times: (list of) time step(s)
      - v: (list of) array(s) with data
           --> list if several variables (each item is a different variable)
           --> array shape = (number of grid nodes, number of time steps)
    """

    # class attributes
    slf = self.slf
    vnames = self.vnames
    vunits = self.vunits
    npoin = self.npoin

    # number of variables
    if type(v) is list:
      nv = len(v)
    else:
      nv = 1

    # check number of variables
    if nv != len(vnames) or nv != len(vunits) or len(vnames) != len(vunits):
      print('number of variables do not match in v, vnames and vunits')
      sys.exit()

    # number of time steps
    if type(times) is not list:
      times = [times]
    nt = len(times)

    # check number of time steps
    if nv == 1:
      if (nt == 1 and v.ndim > 1) or (nt > 1 and v.shape[1] != nt):
        print('number of time steps do not match in times and v')
        sys.exit()
    else:
      if (nt == 1 and v[0].ndim > 1) or (nt > 1 and v[0].shape[1] != nt):
        print('number of time steps do not match in times and v')
        sys.exit()

    # reshape data
    tmp = np.zeros((nt, nv, npoin))
    if nv == 1:
      tmp[:, 0, :] = v.T
    else:
      for i in range(nv):
        tmp[:, i, :] = v[i].T

    # export data
    for i in range(nt):
      slf.writeVariables(times[i], tmp[i, :, :])


  ############################################################################

  def close(self):

    # class attributes
    slf = self.slf

    # close file
    slf.close()

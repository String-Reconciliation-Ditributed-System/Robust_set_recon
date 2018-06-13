from iblt import IBLT
from pyemd import emd, emd_samples
import numpy as np




if __name__ == "__main__":
# Toy Example
	Alice = np.array([1,2,9,12,33,0])
	Ali = np.array([1,2,9,12,33])
	Bob = np.array([1,2,9,10,12,28])
	print(emd_samples(Alice, Bob,bins=2))
	print(emd_samples(Alice, Ali,bins=2))
	#tb = IBLT(m,k,keysize,valsize,hashsize,hashfunc)




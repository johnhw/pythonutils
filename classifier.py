import numpy, math


class Som:
    def __init__(self, vector_length, dim_1, dim_2, adapt_rate = 0.002):    
        self.n_vectors = vector_length
        self.dim = dim_1 * dim_2        
        self.dim_1 = dim_1
        self.dim_2 = dim_2
                
        #random weight initialisation
        self.v = numpy.random.randn(self.dim, vector_length)*200
        
        #adaptation_rate
        self.adapt = adapt_rate
        self.orig_adapt = self.adapt
        
    def update(self, vector, neighbourhood):        
    
        #compute the difference
        repd = numpy.tile(vector, (self.dim, 1))
        diff = (repd - self.v) 
        diff = diff * diff
        s = numpy.sqrt(numpy.sum(diff, axis=1))
        winner = numpy.argmin(s)
                
        #compute position
        pos_x = winner % self.dim_1
        pos_y = winner / self.dim_1
        nsqrd = neighbourhood * neighbourhood
        moved = numpy.zeros((self.dim_1, self.dim_2))
   
        #update all values to move those nearest closer
        for i in range(self.dim_1):
            for j in range(self.dim_2):
                p = i+j*self.dim_1
                
                #distance
                d = (i-pos_x)*(i-pos_x) + (j-pos_y) * (j-pos_y)
                d1 = math.exp(-(d+1.0)/nsqrd)
                
                
                #save the adaptation weights for drawing to the screen
                adapt = self.adapt * d1
                moved[i,j] = adapt / self.orig_adapt
 
                self.v[p, :] = (1-adapt) * self.v[p,:] + (adapt) * vector        
        return moved


        
class KnnClassifier:
    def __init__(self, inputs, classes, k=12, distance_weighted=False, preloaded=None):
        
        self.train_data = []
        self.train_classes = []
        
        self.classes = classes
        self.k = k
        self.distance_weighted = distance_weighted
        
        self.last_entropy = 0
        
        if preloaded:
            infile = open(preloaded, 'r')
            (self.train_data, self.train_classes) = cPickle.load(infile)
            infile.close()
        
  
    def entropy(self, input):
        return self.last_entropy
            
            
    def train(self, save=None, iterations=0):        
        #convert all the data to an array
        self.train_data = numpy.array(self.train_data)
        if save:
            outfile = open(save, 'wb')
            cPickle.dump((self.train_data, self.train_classes), outfile)
            outfile.close()
        
        
    
    def classify(self, input):
        n = len(self.train_data)                 
        q = 0
                
        repmatrix = numpy.tile(input, (n,1) )        
        

        #compute euclidean distance
        diff = (self.train_data-repmatrix)
        sqr = (diff*diff)        
        sum = numpy.sum(sqr, axis=1)                
        sums = numpy.sqrt(sum)

        #get top k neighbours
        indices = numpy.argsort(sums)
     
        #do the vote
        votes = numpy.zeros((self.classes,))
        
        for i in range(self.k):            
        
            #get the class of the neighbour
            clas = self.train_classes[indices[i]]
        
            if self.distance_weighted:                                
                if sums[indices[i]]!=0:
                    votes[clas] += 1.0/((sums[indices[i]]+1))
            else:
                if sums[indices[i]]!=0:
                    votes[clas] += 1
        
        votes = votes / numpy.sum(votes)        
        x = numpy.clip(votes, 0.0001, 1.0)
        self.last_entropy = -numpy.sum(x*numpy.log(x))
     
        
        return numpy.argmax(votes)
    
    def add_training_data(self, input, target, train_outfile=None, test_outfile=None):    
        #construct ouputs from categorical variable
                   
        self.train_data.append(input)
        self.train_classes.append(target)
                
        if train_outfile:
            for i in input:
                train_outfile.write("%f " % (i,))
            train_outfile.write("\n")
        
        if test_outfile:            
            test_outfile.write("%f\n" % (target,))

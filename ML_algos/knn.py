import math
from collections import Counter, heapq

class KNNClassifier:
    def __init__(self, k=3):
        self.k = k
        self.X_train = None
        self.y_train = None
    
    def euclid(self, point1, point2):
        s = 0
        n = len(point1)

        for i in range(n):
            s += ((point1[i] - point2[i]) ** 2)
        
        return math.sqrt(s)
    
    def choose_cluster(self, neighbors):
        labels = [label for _, label in neighbors]
        most_common = Counter(labels).most_common(1)
        return most_common[0][0]
    
    def fit(self, X, y):
        self.X_train = X
        self.y_train = y
        minheap = []
        predictions = []
        
        n = len(X)
        if n != len(y):
            raise ValueError("Number of samples in X and y must be the same.")
        
        if n < self.k:
            raise ValueError("Number of samples must be at least k.")
        
        for i in range(n):
            if len(X[i]) != len(X[0]):
                raise ValueError("All samples must have the same number of features.")

        for i in range(n):
            for j in range(i + 1, n):
                dist = self.euclid(X[i], y[j])
                heapq.heappush(minheap, (dist, y[j]))
                if len(minheap) > self.k:
                    heapq.heappop(minheap)
            
            cluster = self.choose_cluster(minheap)
            minheap.clear()
            predictions.append(cluster)
        return predictions
    
    def predict(self, X):
        minheap = []
        predictions = []
        n = len(X)
        for i in range(n):
            for j in range(i + 1, n):
                dist = self.euclid(X[i], X[j])
                heapq.heappush(minheap, (dist, X[j]))
                if len(minheap) > self.k:
                    heapq.heappop(minheap)
            
            cluster = self.choose_cluster(minheap)
            minheap.clear()
            predictions.append(cluster)
        return predictions
        
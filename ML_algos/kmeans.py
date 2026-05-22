import math, random

class KMeans():
    def __init__(self, k = 3, max_iters = 100):
        self.k = k
        self.max_iters = max_iters
        self.centroids = None
    
    def euclid(self, point, centroid):
        s = 0
        n = len(point)

        for i in range(n):
            s += ((point[i] - centroid[i]) ** 2)
        
        return math.sqrt(s)

    def assign_clusters(self, X):
        """
        for each point in X assign a cluster based on the k nearest neighbors
        for each point in X calculate distance from each centroid and assign it to minimum distance centroid
        """
        clusters = []
        for point in X:
            min_dist = float('inf')
            cluster = None
            for i, centroid in enumerate(self.centroids):
                dist = self.euclid(point,centroid)
                if dist < min_dist:
                    min_dist = dist
                    cluster = i
            clusters.append(cluster)
        return clusters
    
    def update_centroids(self, X, clusters):
        """
        for each point get cluster
        for each cluster use all points in it to recompute mean,
        return new centroids
        """
        updated_centroids = []
        dims = len(X[0])
        for k in range(self.k):
            cluster_points = []

            for i, point in enumerate(X):
                if clusters[i] == k:
                    cluster_points.append(point)
            
            point_list = []
            for dim in range(dims): 
                sum = 0
                for point in cluster_points:
                    sum += point[dim]
                
                point_list.append(sum/len(cluster_points))
            
            updated_centroids.append(point_list)
        return updated_centroids
    
    def has_converged(self, old_centroids, new_centroids):
        for old, new in zip(old_centroids, new_centroids):
            if self.euclid(old, new) > 1e-4:
                return False
        return True

    def fit(self, X):
        """
        init random centroids
        compute labels for each point based on centroids
        update centroids based on new labels and mean
        """
        self.centroids = random.sample(X, self.k)

        labels = self.assign_clusters(X)

        new_centroids = self.update_centroids(X, labels)

        for _ in range(self.max_iters):
            if self.has_converged(self.centroids, new_centroids):
                break
            
            self.centroids = new_centroids
            labels = self.assign_clusters(X)
            new_centroids = self.update_centroids(X, labels)
        
        return labels

    def predict(self, X):
        """
        predict the cluster for each point in X
        """
        return self.assign_clusters(X)

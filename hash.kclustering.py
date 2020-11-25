import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

dataset=pd.read_csv('Mall_Customers.csv')
dataset.isnull().sum()

x=dataset.iloc[:,[3,4]].values

from sklearn.cluster import KMeans
wcss=[]
for i in range(1,11):
    kmeans=KMeans(n_clusters=i, init='k-means++', n_init=10, max_iter=300,random_state=0)
    kmeans.fit(x)
    wcss.append(kmeans.inertia_)
plt.plot(range(1,11), wcss)
plt.title('elbow method')
plt.ylabel('wcss')
plt.xlabel('number of clusters')
plt.show()

from sklearn.cluster import KMeans
kmeans=KMeans(n_clusters=5, init='k-means++', n_init=10, max_iter=300, random_state=0)
y_kmeans=kmeans.fit_predict(x)
#pickle.dump(kmeans, open('model.pkl','wb'))
"""
c=[12,500]
c=np.array(c).reshape(1,-1)
k=kmeans.predict(c)
"""

pickle.dump(kmeans, open('model.pkl','wb'))
plt.scatter(x[y_kmeans==0,0], x[y_kmeans==0,1], s=100 , color='red', label='standard')

plt.scatter(x[y_kmeans==1,0], x[y_kmeans==1,1], s=100 , color='blue', label='careless')

plt.scatter(x[y_kmeans==2,0], x[y_kmeans==2,1], s=100 , color='green', label='high')
plt.scatter(x[y_kmeans==3,0], x[y_kmeans==3,1], s=100 , color='magenta', label='sensible')

plt.scatter(x[y_kmeans==4,0], x[y_kmeans==4,1], s=100 , color='cyan', label='careful')
plt.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], s=300, color='yellow', label='centroids' )
plt.title('cluster of clients')
plt.ylabel('monthly expense')
plt.xlabel('monthly income')
plt.legend()
plt.show()

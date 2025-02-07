import numpy as np 
from sklearn.manifold import MDS
import os 
import argparse 
import pickle as pkl
import torch
import random


parser = argparse.ArgumentParser(description='parsing!!')
parser.add_argument('-input', required=True, type=str,
                    help='location of input folders with the pickle files of hidden units')
args = parser.parse_args()

def sim_normalize(mat):
    #make sim matrix and then normalizes it 
    eps  = torch.tensor(0.00000000001)
    sim = torch.matmul(mat, mat.t())
    mean = sim.mean(dim=0)
    std = sim.std(dim=0)
    sim =  (sim-mean)/(std+eps)
    return sim

def model_mat(mat1, mat2):
    N = mat1.shape[0]
    a = []
    for i in (range(N)):
    	a.append(torch.dot(mat1[i], mat2[i]))
    a = torch.tensor(a)
    return a.mean()

def extract_hidden(d):
	hd =  d[0]
	for i in range(len(hd)):
		hd[i] = torch.FloatTensor(hd[i])
	hd = torch.stack(hd,dim=0)
	print(hd.shape)
	return hd



print('Reading File!!!!')
models = list(os.listdir(args.input))

hidden_list=[]
with torch.no_grad():
	count=-1
	for m in models:
		count+=1
		print(count)
		with open(os.path.join(args.input, m), 'rb') as f:
			hidden_list.append(extract_hidden(pkl.load(f)))

	print('Normalizing the hidden states!!!!')
	for i in range(len(hidden_list)):
		l = [j for j in range(len(hidden_list[i].shape[0]))]
		hidden_list[i] =  sim_normalize(hidden_list[i][l])

	RSA =  torch.zeros((len(hidden_list), len(hidden_list)))

	print('Getting similarity matrix!!!!!!!!')
	for i in range(len(RSA)):
		for j in range(i, len(RSA)):
			RSA[i, j] = model_mat(hidden_list[i], hidden_list[j])

	for i in range(len(RSA)):
		for j in range(len(RSA)):
			if RSA[i, j].cpu().item()==0:
				RSA[i, j] =  RSA[j, i]

RSA = RSA.cpu().numpy() #numpy array 
print('Performing Scaling!!!!')
RSA =  MDS(n_components=2).fit_transform(RSA)

print('Done, now dumping!')
dump_dict={}
for i in range(len(RSA)):
	dump_dict[models[i]] = RSA[i]

with open('RSA.pkl', 'wb') as f:
	pkl.dump(dump_dict, f)

print('Done!')


